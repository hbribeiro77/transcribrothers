"""Transcrição de áudio WAV extraído do vídeo: janelas multimodal (formato/trecho do usuário) ou Whisper."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    converter_wav_para_aac_m4a_para_caminho_transcribrothers,
    converter_wav_para_mp3_para_caminho_transcribrothers,
    converter_wav_para_opus_ogg_para_caminho_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
    apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers,
    carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers,
    gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
    normalizar_backend_transcricao_audio_configurado,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    TranscriberOpenAIWhisperComSegmentos,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    TranscriberLiteLLmMultimodalAudioJsonSegmentos,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers import (
    listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers,
    transcrever_wav_litellm_multimodal_em_janelas_com_callback_progresso_transcribrothers,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers,
)


async def transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers(
    *,
    work: Path,
    audio: Path,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    configuracao_exec_transcricao_mm: ConfiguracaoAmbienteTranscribrothers,
    http_verify_litellm: bool | str,
    steps: dict[str, Any],
    ao_persistir_steps: Callable[[dict[str, Any]], Awaitable[None]],
    levantar_se_cancelado: Callable[[], None],
    pipeline_fase_inicial: str = "transcrevendo_audio",
) -> ResultadoTranscricaoComSegmentos:
    """
    Caminho único de transcrição para todos os destinos (tutorial, bug, notas, …).

    Multimodal: janelas configuráveis (formato inline, duração, paralelismo, checkpoint).
    Whisper: arquivo WAV inteiro.
    """
    steps_mut = steps
    steps_mut["pipeline_fase"] = pipeline_fase_inicial

    backend_tr = normalizar_backend_transcricao_audio_configurado(configuracao)
    if backend_tr == TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO:
        modelo_tr = resolver_modelo_para_transcricao_litellm_multimodal_audio(configuracao)
        if not modelo_tr:
            raise RuntimeError(
                "TRANSCRICAO_LITELLM_MODELO vazio e nenhum modelo gemini/ encontrado em "
                "LITELLM_MODELOS_PROVISIONADOS ou LITELLM_MODEL."
            )
        ak_tr, ab_tr = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
        if not ak_tr:
            raise RuntimeError("LITELLM_API_KEY é obrigatória para transcrição multimodal.")
        fmt_inline = str(
            configuracao_exec_transcricao_mm.transcricao_multimodal_formato_audio_inline or "wav"
        ).strip().lower()
        if fmt_inline not in ("wav", "mp3", "opus", "aac"):
            fmt_inline = "wav"
        transcriber = TranscriberLiteLLmMultimodalAudioJsonSegmentos(
            model=modelo_tr,
            api_key=ak_tr,
            api_base=ab_tr,
            httpx_verify=http_verify_litellm,
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            usar_response_format_json_object=configuracao.transcricao_litellm_chat_json_object_response_format,
            formato_input_audio_inline=fmt_inline,
        )
        steps_mut["transcricao_backend"] = TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO
        steps_mut["transcricao_modelo"] = modelo_tr
    else:
        whisper_key, whisper_base = resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel(
            configuracao
        )
        transcriber = TranscriberOpenAIWhisperComSegmentos(
            api_key=whisper_key,
            base_url=whisper_base,
            httpx_verify=http_verify_litellm,
        )
        steps_mut["transcricao_backend"] = "openai_whisper"

    levantar_se_cancelado()

    if backend_tr == TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO:
        janela_seg = float(configuracao_exec_transcricao_mm.transcricao_multimodal_janela_segundos)
        dir_janelas = work / "midia_janelas_transcricao_litellm_multimodal_temp"
        fmt_mm = str(
            configuracao_exec_transcricao_mm.transcricao_multimodal_formato_audio_inline or "wav"
        ).strip().lower()
        if fmt_mm not in ("wav", "mp3", "opus", "aac"):
            fmt_mm = "wav"
        mono_mm = bool(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_mono)
        br_mm = int(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_bitrate_kbps)
        audio_para_multimodal = audio
        if fmt_mm == "mp3":
            audio_para_multimodal = work / "audio_extraido_para_transcricao_multimodal_inline.mp3"
        elif fmt_mm == "opus":
            audio_para_multimodal = work / "audio_extraido_para_transcricao_multimodal_inline.opus"
        elif fmt_mm == "aac":
            audio_para_multimodal = work / "audio_extraido_para_transcricao_multimodal_inline.m4a"
        if fmt_mm in ("mp3", "opus", "aac"):
            if deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers(
                audio_para_multimodal,
                formato_audio_inline=fmt_mm,
                audio_bitrate_kbps=int(br_mm),
                audio_mono=bool(mono_mm),
                steps=steps_mut,
            ):
                steps_mut["transcricao_multimodal_audio_codificado_ok"] = True
                steps_mut["transcricao_multimodal_audio_codificado_reutilizado_retry"] = True
            elif fmt_mm == "mp3":
                await converter_wav_para_mp3_para_caminho_transcribrothers(
                    caminho_wav_entrada=audio,
                    caminho_mp3_saida=audio_para_multimodal,
                    bitrate_kbps=br_mm,
                    forcar_mono=mono_mm,
                )
                steps_mut["transcricao_multimodal_audio_codificado_ok"] = True
                steps_mut.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
            elif fmt_mm == "opus":
                await converter_wav_para_opus_ogg_para_caminho_transcribrothers(
                    caminho_wav_entrada=audio,
                    caminho_opus_saida=audio_para_multimodal,
                    bitrate_kbps=br_mm,
                    forcar_mono=mono_mm,
                )
                steps_mut["transcricao_multimodal_audio_codificado_ok"] = True
                steps_mut.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
            else:
                await converter_wav_para_aac_m4a_para_caminho_transcribrothers(
                    caminho_wav_entrada=audio,
                    caminho_m4a_saida=audio_para_multimodal,
                    bitrate_kbps=br_mm,
                    forcar_mono=mono_mm,
                )
                steps_mut["transcricao_multimodal_audio_codificado_ok"] = True
                steps_mut.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
        steps_mut["transcricao_multimodal_formato_audio_inline"] = fmt_mm
        steps_mut["transcricao_multimodal_audio_bitrate_kbps"] = br_mm
        steps_mut["transcricao_multimodal_audio_mono"] = mono_mm

        dur_audio_mm = await obter_duracao_video_segundos_via_ffprobe(audio_para_multimodal)
        janelas_mm = listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers(
            float(dur_audio_mm),
            float(janela_seg),
        )
        total_janelas_mm = len(janelas_mm)
        br_ck = br_mm
        meta_checkpoint_mm: dict[str, Any] = {
            "versao": CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
            "janela_segundos": float(janela_seg),
            "total_janelas": int(total_janelas_mm),
            "formato_audio_inline": str(fmt_mm),
            "audio_bitrate_kbps": int(br_ck),
            "audio_mono": bool(mono_mm),
            "modelo_transcricao": str(modelo_tr).strip(),
            "duracao_audio_ffprobe": round(float(dur_audio_mm), 2),
            "tamanho_bytes_audio_fonte": int(audio_para_multimodal.stat().st_size)
            if audio_para_multimodal.is_file()
            else 0,
        }
        carregado_ck = carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers(
            work,
            caminho_audio_fonte=audio_para_multimodal,
            janela_segundos=float(janela_seg),
            formato_audio_inline=str(fmt_mm),
            audio_bitrate_kbps=int(br_ck),
            audio_mono=bool(mono_mm),
            modelo_transcricao=str(modelo_tr).strip(),
            duracao_audio_ffprobe_atual=float(dur_audio_mm),
            total_janelas_esperado=int(total_janelas_mm),
        )
        mapa_janelas_ja_feitas: dict[int, ResultadoTranscricaoComSegmentos] = {}
        registros_tempo_inferencia_previos: list[dict[str, Any]] = []
        if carregado_ck is not None:
            mapa_janelas_ja_feitas, registros_tempo_inferencia_previos = carregado_ck
            steps_mut["transcricao_multimodal_checkpoint_trechos_salvos"] = len(mapa_janelas_ja_feitas)
            steps_mut["transcricao_multimodal_retomada_trechos"] = len(mapa_janelas_ja_feitas)
            steps_mut["transcricao_multimodal_mensagem_retomada"] = (
                f"Retomando com {len(mapa_janelas_ja_feitas)} trecho(s) já transcrito(s); "
                "os demais seguem em seguida."
            )
            await ao_persistir_steps(steps_mut)

        async def atualizar_progresso_transcricao_janelas(sub: dict[str, Any]) -> None:
            levantar_se_cancelado()
            merged = {**steps_mut, **sub}
            steps_mut.clear()
            steps_mut.update(merged)
            await ao_persistir_steps(steps_mut)

        async def apos_janela_nova_salvar_checkpoint_transcribrothers(
            indice_base_zero: int,
            inicio_seg: float,
            duracao_seg: float,
            resultado_parcial: ResultadoTranscricaoComSegmentos,
            duracao_inferencia_seg: float,
        ) -> None:
            levantar_se_cancelado()
            registro_t = {
                "indice": int(indice_base_zero) + 1,
                "inicio_segundos": round(float(inicio_seg), 2),
                "fim_segundos": round(float(inicio_seg + duracao_seg), 2),
                "duracao_inferencia_segundos": round(float(duracao_inferencia_seg), 2),
            }
            n_salvos = gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers(
                work,
                meta_fixa=meta_checkpoint_mm,
                indice_janela_base_zero=int(indice_base_zero),
                resultado_janela=resultado_parcial,
                registro_tempo_inferencia=registro_t,
            )
            steps_mut["transcricao_multimodal_checkpoint_trechos_salvos"] = int(n_salvos)
            await ao_persistir_steps(steps_mut)

        transcricao = await transcrever_wav_litellm_multimodal_em_janelas_com_callback_progresso_transcribrothers(
            transcriber=transcriber,
            caminho_audio_completo=audio_para_multimodal,
            formato_audio_inline=fmt_mm,
            bitrate_audio_kbps=int(br_mm),
            forcar_mono=mono_mm,
            janela_segundos=janela_seg,
            diretorio_temporario_janelas=dir_janelas,
            atualizar_progresso=atualizar_progresso_transcricao_janelas,
            max_janelas_em_paralelo=int(
                configuracao_exec_transcricao_mm.transcricao_multimodal_janelas_paralelas_maxima
            ),
            janelas_ja_concluidas=mapa_janelas_ja_feitas or None,
            registros_tempo_inferencia_iniciais=registros_tempo_inferencia_previos or None,
            apos_persistir_janela_nova_concluida=apos_janela_nova_salvar_checkpoint_transcribrothers,
        )
        apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers(work)
        for k in (
            "transcricao_multimodal_checkpoint_trechos_salvos",
            "transcricao_multimodal_retomada_trechos",
            "transcricao_multimodal_mensagem_retomada",
            "transcricao_multimodal_retomando_trechos",
        ):
            steps_mut.pop(k, None)
    else:
        transcricao = await transcriber.transcrever_arquivo_audio_com_segmentos(audio)

    steps_mut["transcricao_segmentos"] = len(transcricao.segmentos)
    steps_mut["pipeline_fase"] = "transcricao_concluida"
    await ao_persistir_steps(steps_mut)
    return transcricao
