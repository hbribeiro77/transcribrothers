from __future__ import annotations

import asyncio
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
    gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers,
    extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers,
    limite_maximo_capturas_frames_tutorial_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
    apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers,
    carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers,
    gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
    normalizar_backend_transcricao_audio_configurado,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_download_google_drive_publico_arquivo_por_id import (
    ErroDownloadGoogleDrive,
    baixar_arquivo_google_drive_publico_por_id_para_caminho,
    max_bytes_da_config,
)
from transcribrothers_backend.modulo_metadados_google_drive_publico_arquivo_por_id import (
    extensao_sugerida_para_video_a_partir_do_mime,
    obter_metadados_google_drive_publico_por_id,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    amostrar_indices_por_limite_por_minuto,
    converter_wav_para_aac_m4a_para_caminho_transcribrothers,
    converter_wav_para_mp3_para_caminho_transcribrothers,
    converter_wav_para_opus_ogg_para_caminho_transcribrothers,
    extrair_audio_wav_de_video_para_caminho,
    reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
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
    deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers,
    deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers,
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)


class PipelineCanceladoPeloUsuarioTranscribrothers(Exception):
    """Fluxo interrompido após POST /api/jobs/{id}/cancel."""


def _levantar_se_cancelamento_pipeline_solicitado(job_id: str) -> None:
    if cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id):
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        raise PipelineCanceladoPeloUsuarioTranscribrothers()


def _instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(
    steps: dict[str, Any],
) -> str | None:
    raw = steps.get("tutorial_litellm_instrucao_prefixo_custom")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def _montar_snapshot_regeneracao_tutorial_transcribrothers(
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
) -> dict[str, Any]:
    return {
        "texto_completo": transcricao_corta.texto_completo,
        "idioma": transcricao_corta.idioma_detectado,
        "segmentos": [asdict(s) for s in transcricao_corta.segmentos],
        "caminhos_frames_rel_job": [[t, rel] for t, rel in rels],
    }


def _snapshot_dict_para_transcricao_e_rels(
    snap: dict[str, Any],
) -> tuple[ResultadoTranscricaoComSegmentos, list[tuple[float, str]]]:
    segmentos_raw = snap.get("segmentos") or []
    segmentos: list[SegmentoTranscricaoComTempo] = []
    for s in segmentos_raw:
        if not isinstance(s, dict):
            continue
        segmentos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=float(s.get("inicio_segundos", 0.0)),
                fim_segundos=float(s.get("fim_segundos", 0.0)),
                texto=str(s.get("texto") or ""),
            )
        )
    rels: list[tuple[float, str]] = []
    for pair in snap.get("caminhos_frames_rel_job") or []:
        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
            rels.append((float(pair[0]), str(pair[1])))
    texto = str(snap.get("texto_completo") or "")
    idioma = snap.get("idioma")
    idioma_s = str(idioma) if idioma is not None else None
    return (
        ResultadoTranscricaoComSegmentos(
            texto_completo=texto,
            segmentos=segmentos,
            idioma_detectado=idioma_s,
        ),
        rels,
    )


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


async def _atualizar_job(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    status: StatusJobTranscribrothers | None = None,
    error: str | None = None,
    limpar_mensagem_erro: bool = False,
    markdown: str | None = None,
    steps: dict[str, Any] | None = None,
) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            return
        if status is not None:
            row.status = status.value
        if limpar_mensagem_erro:
            row.error_message = None
        elif error is not None:
            row.error_message = error
        if markdown is not None:
            row.result_markdown = markdown
        if steps is not None:
            row.steps_json = steps
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()


async def _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
    markdown_tutorial: str,
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> None:
    """Grava `steps_json.verificacao_sustentacao_tutorial` e fases de progresso; não altera o Markdown."""
    from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
        blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers,
        executar_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers,
    )

    async with session_factory() as session:
        from transcribrothers_backend.modulo_persistencia_runtime_config_verificacao_sustentacao_tutorial_sqlite_transcribrothers import (
            verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers,
        )

        desativada_efetiva, sqlite_definido = (
            await verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
                session,
                configuracao,
            )
        )

    if desativada_efetiva:
        motivo = (
            "desativada_definicao_persistente_interface"
            if sqlite_definido
            else "desativada_por_configuracao_ambiente"
        )
        steps["verificacao_sustentacao_tutorial"] = (
            blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(motivo=motivo)
        )
        return

    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_litellm"
    await _atualizar_job(session_factory, job_id, steps=dict(steps))

    def _levantar_cancelamento_verificacao_transcribrothers() -> None:
        _levantar_se_cancelamento_pipeline_solicitado(job_id)

    ver = await executar_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers(
        configuracao=configuracao,
        markdown_tutorial=markdown_tutorial,
        transcricao_corta=transcricao_corta,
        rels=rels,
        modelo_litellm=modelo_litellm,
        api_key_litellm=api_key_litellm,
        api_base_litellm=api_base_litellm,
        http_verify_litellm=http_verify_litellm,
        levantar_se_cancelado=_levantar_cancelamento_verificacao_transcribrothers,
        steps_para_log_decisoes_ia=steps,
    )
    steps["verificacao_sustentacao_tutorial"] = ver
    steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_concluida"
    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    await _atualizar_job(session_factory, job_id, steps=dict(steps))


async def _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
    markdown_tutorial: str,
    assets_dir: Path,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> str:
    from transcribrothers_backend.modulo_verificacao_imagens_duplicadas_tutorial_markdown_litellm_visao_lotes_transcribrothers import (
        executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_no_markdown_transcribrothers,
    )

    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    steps["pipeline_fase"] = "verificacao_imagens_duplicadas_tutorial_litellm_visao"
    await _atualizar_job(session_factory, job_id, steps=dict(steps))

    md_atualizado, blob = await executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_no_markdown_transcribrothers(
        configuracao=configuracao,
        markdown_tutorial=markdown_tutorial,
        diretorio_assets_absoluto=assets_dir,
        modelo_litellm=modelo_litellm,
        api_key_litellm=api_key_litellm,
        api_base_litellm=api_base_litellm,
        http_verify_litellm=http_verify_litellm,
        levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
        steps_para_log_decisoes_ia=steps,
    )
    steps["verificacao_imagens_duplicadas_tutorial"] = blob
    steps["pipeline_fase"] = "verificacao_imagens_duplicadas_tutorial_concluida"
    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    await _atualizar_job(session_factory, job_id, steps=dict(steps))
    return md_atualizado


async def executar_pipeline_job_transcricao_tutorial_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    video: Path | None = None
    audio = work / "audio_extraido_para_transcricao.wav"
    frames_dir = work / "frames_png_capturados_para_tutorial"
    assets_dir = work / "assets_exportados_para_markdown"
    steps: dict[str, Any] = {}

    async def marcar(s: StatusJobTranscribrothers, extra: dict[str, Any] | None = None) -> None:
        nonlocal steps
        if extra:
            steps = {**steps, **extra}
        await _atualizar_job(session_factory, job_id, status=s, steps=steps)

    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            file_id = job.file_id
            api_key = configuracao.google_drive_api_key
            source_kind = job.source_kind or OrigemEntradaJobTranscribrothers.drive
            job_steps = dict(job.steps_json or {})
            steps = steps_json_job_para_reexecucao_pipeline_transcribrothers(job_steps)
            modelo_litellm = (job_steps.get("litellm_model") or configuracao.litellm_model or "").strip()
            api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(
                configuracao
            )
            overrides_tm = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(
                session
            )

        configuracao_exec_transcricao_mm = aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
            configuracao,
            overrides_tm,
        )

        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
            configuracao
        )

        def _resumo_httpx_verify_para_steps_json(v: bool | str) -> str:
            if v is True:
                return "true"
            if v is False:
                return "false"
            return f"ca_bundle_file:{Path(v).name}"

        steps["litellm_httpx_verify_diagnostico"] = _resumo_httpx_verify_para_steps_json(
            http_verify_litellm
        )
        steps["litellm_http_verify_ssl_configurado_bool"] = bool(configuracao.litellm_http_verify_ssl)
        steps["litellm_ssl_ca_bundle_configurado_bool"] = bool(
            (configuracao.litellm_ssl_ca_bundle or "").strip()
        )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "metadados_job_carregados"

        await marcar(StatusJobTranscribrothers.downloading)
        work.mkdir(parents=True, exist_ok=True)

        if source_kind == OrigemEntradaJobTranscribrothers.upload_local:
            candidatos = sorted(work.glob("video_entrada_arquivo_local.*"))
            video = next((p for p in candidatos if p.is_file()), None)
            if video is None:
                raise FileNotFoundError(
                    "Vídeo enviado não encontrado no diretório do job (esperado video_entrada_arquivo_local.*)."
                )
            steps["source"] = OrigemEntradaJobTranscribrothers.upload_local
            steps["upload_ok"] = True
            steps["video_filename"] = video.name
        else:
            try:
                meta = await obter_metadados_google_drive_publico_por_id(
                    file_id=file_id, api_key=api_key
                )
                ext = extensao_sugerida_para_video_a_partir_do_mime(
                    str(meta.get("mimeType") or "")
                )
                video = work / f"video_entrada_google_drive.{ext}"
                steps["drive_mime_type"] = meta.get("mimeType")
                steps["drive_name"] = meta.get("name")
            except Exception:  # noqa: BLE001
                video = work / "video_entrada_google_drive.mp4"
            if deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers(video, steps):
                steps["source"] = OrigemEntradaJobTranscribrothers.drive
                steps["download_ok"] = True
                steps["video_entrada_reutilizado_retry"] = True
                steps["video_filename"] = video.name
                steps["pipeline_fase"] = "video_entrada_reutilizado_sem_redownload"
            else:
                await baixar_arquivo_google_drive_publico_por_id_para_caminho(
                    file_id=file_id,
                    api_key=api_key,
                    destino=video,
                    max_bytes=max_bytes_da_config(configuracao),
                )
                steps["source"] = OrigemEntradaJobTranscribrothers.drive
                steps["download_ok"] = True
                steps.pop("video_entrada_reutilizado_retry", None)
                steps["video_filename"] = video.name

        assert video is not None

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        await marcar(StatusJobTranscribrothers.extracting_audio)
        if deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(audio, steps):
            steps["pipeline_fase"] = "audio_wav_reutilizado_sem_reextrair"
            steps["audio_ok"] = True
            steps["audio_wav_reutilizado_retry"] = True
        else:
            steps["pipeline_fase"] = "ffmpeg_extrair_audio"
            steps.pop("audio_wav_reutilizado_retry", None)
            await extrair_audio_wav_de_video_para_caminho(
                caminho_video=video,
                caminho_audio_wav=audio,
                forcar_mono=bool(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_mono),
            )
            steps["audio_ok"] = True

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        await marcar(StatusJobTranscribrothers.transcribing)
        steps["pipeline_fase"] = "transcrevendo_audio"
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
                httpx_timeout_connect_segundos=float(
                    configuracao.litellm_http_timeout_connect_segundos
                ),
                httpx_timeout_read_segundos=float(
                    configuracao.litellm_http_timeout_read_segundos
                ),
                usar_response_format_json_object=configuracao.transcricao_litellm_chat_json_object_response_format,
                formato_input_audio_inline=fmt_inline,
            )
            steps["transcricao_backend"] = TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO
            steps["transcricao_modelo"] = modelo_tr
        else:
            whisper_key, whisper_base = (
                resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel(
                    configuracao
                )
            )
            transcriber = TranscriberOpenAIWhisperComSegmentos(
                api_key=whisper_key,
                base_url=whisper_base,
                httpx_verify=http_verify_litellm,
            )
            steps["transcricao_backend"] = "openai_whisper"
        _levantar_se_cancelamento_pipeline_solicitado(job_id)
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
                    steps=steps,
                ):
                    steps["transcricao_multimodal_audio_codificado_ok"] = True
                    steps["transcricao_multimodal_audio_codificado_reutilizado_retry"] = True
                elif fmt_mm == "mp3":
                    await converter_wav_para_mp3_para_caminho_transcribrothers(
                        caminho_wav_entrada=audio,
                        caminho_mp3_saida=audio_para_multimodal,
                        bitrate_kbps=br_mm,
                        forcar_mono=mono_mm,
                    )
                    steps["transcricao_multimodal_audio_codificado_ok"] = True
                    steps.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
                elif fmt_mm == "opus":
                    await converter_wav_para_opus_ogg_para_caminho_transcribrothers(
                        caminho_wav_entrada=audio,
                        caminho_opus_saida=audio_para_multimodal,
                        bitrate_kbps=br_mm,
                        forcar_mono=mono_mm,
                    )
                    steps["transcricao_multimodal_audio_codificado_ok"] = True
                    steps.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
                else:
                    await converter_wav_para_aac_m4a_para_caminho_transcribrothers(
                        caminho_wav_entrada=audio,
                        caminho_m4a_saida=audio_para_multimodal,
                        bitrate_kbps=br_mm,
                        forcar_mono=mono_mm,
                    )
                    steps["transcricao_multimodal_audio_codificado_ok"] = True
                    steps.pop("transcricao_multimodal_audio_codificado_reutilizado_retry", None)
            steps["transcricao_multimodal_formato_audio_inline"] = fmt_mm
            steps["transcricao_multimodal_audio_bitrate_kbps"] = br_mm
            steps["transcricao_multimodal_audio_mono"] = mono_mm

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
                steps["transcricao_multimodal_checkpoint_trechos_salvos"] = len(mapa_janelas_ja_feitas)
                steps["transcricao_multimodal_retomada_trechos"] = len(mapa_janelas_ja_feitas)
                steps["transcricao_multimodal_mensagem_retomada"] = (
                    f"Retomando com {len(mapa_janelas_ja_feitas)} trecho(s) já transcrito(s); "
                    "os demais seguem em seguida."
                )
                await _atualizar_job(session_factory, job_id, steps=steps)

            async def atualizar_progresso_transcricao_janelas(sub: dict[str, Any]) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                nonlocal steps
                steps = {**steps, **sub}
                await _atualizar_job(session_factory, job_id, steps=steps)

            async def apos_janela_nova_salvar_checkpoint_transcribrothers(
                indice_base_zero: int,
                inicio_seg: float,
                duracao_seg: float,
                resultado_parcial: ResultadoTranscricaoComSegmentos,
                duracao_inferencia_seg: float,
            ) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                nonlocal steps
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
                steps["transcricao_multimodal_checkpoint_trechos_salvos"] = int(n_salvos)
                await _atualizar_job(session_factory, job_id, steps=steps)

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
                steps.pop(k, None)
        else:
            transcricao = await transcriber.transcrever_arquivo_audio_com_segmentos(audio)
        steps["transcricao_segmentos"] = len(transcricao.segmentos)
        steps["pipeline_fase"] = "transcricao_concluida"

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        dur = await obter_duracao_video_segundos_via_ffprobe(video)
        prefixo = "screenshot_tutorial_transcribrothers"
        largura_png = (
            int(configuracao.tutorial_frame_max_width_px)
            if configuracao.tutorial_frame_max_width_px > 0
            else None
        )
        captura_sob_demanda = bool(configuracao.tutorial_captura_frames_sob_demanda)
        steps["tutorial_captura_frames_sob_demanda"] = captura_sob_demanda
        rels: list[tuple[float, str]] = []
        md_rascunho: str | None = None

        if captura_sob_demanda:
            _levantar_se_cancelamento_pipeline_solicitado(job_id)
            await marcar(StatusJobTranscribrothers.generating_tutorial)
            steps["pipeline_fase"] = "gerando_rascunho_tutorial_sem_imagens"
            steps["geracao_tutorial_litellm_total_imagens"] = 0
            md_rascunho = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
                transcricao=transcricao,
                caminhos_frames_rel_job=[],
                modelo=modelo_litellm,
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                enviar_screenshots_png_como_imagens_multimodais=False,
                httpx_timeout_connect_segundos=float(
                    configuracao.litellm_http_timeout_connect_segundos
                ),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                instrucao_prefixo_litellm_custom=INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
                steps_para_log_decisoes_ia=steps,
                log_etapa_geracao_tutorial="geracao_rascunho_tutorial_sem_imagens",
            )
            steps["tutorial_rascunho_sem_imagens_ok"] = True

            margem_links = float(
                configuracao_exec_transcricao_mm.tutorial_margem_minima_segundos_entre_links_temporais_captura
            )
            candidatos_captura = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
                md_rascunho,
                duracao_video_segundos=dur,
                margem_minima_segundos_entre_links_temporais=margem_links,
            )
            steps["frames_candidatos_rascunho_total"] = len(candidatos_captura)
            max_capturas_teto = limite_maximo_capturas_frames_tutorial_transcribrothers(
                dur if dur > 0 else 1.0,
                max_frames_per_minute=configuracao_exec_transcricao_mm.max_frames_per_minute,
                tutorial_max_frames_total=configuracao_exec_transcricao_mm.tutorial_max_frames_total,
            )
            timestamps_pre_planejados: list[float] | None = None
            if candidatos_captura:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "planejando_instantes_captura_frames_tutorial"
                await _atualizar_job(session_factory, job_id, steps=steps)
                escolhidos, meta_planej = (
                    await planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers(
                        markdown_rascunho_tutorial=md_rascunho,
                        candidatos_segundos=candidatos_captura,
                        transcricao=transcricao,
                        duracao_video_segundos=dur,
                        margem_minima_segundos_entre_links=margem_links,
                        max_capturas_apos_limites=max_capturas_teto,
                        modelo_litellm=modelo_litellm,
                        api_key=api_key_litellm,
                        api_base=api_base_litellm,
                        httpx_verify=http_verify_litellm,
                        configuracao=configuracao_exec_transcricao_mm,
                        steps_para_log_decisoes_ia=steps,
                    )
                )
                steps["planejamento_instantes_captura_frames"] = meta_planej
                timestamps_pre_planejados = escolhidos

            timestamps_captura = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
                markdown_rascunho_tutorial=md_rascunho,
                transcricao=transcricao,
                duracao_video_segundos=dur,
                max_frames_per_minute=configuracao_exec_transcricao_mm.max_frames_per_minute,
                tutorial_max_frames_total=configuracao_exec_transcricao_mm.tutorial_max_frames_total,
                margem_minima_segundos_entre_links_temporais=margem_links,
                timestamps_pre_planejados=timestamps_pre_planejados,
            )
            steps["frames_planejados_captura_sob_demanda"] = len(timestamps_captura)

            async def _progresso_captura_sob_demanda(indice: int, total: int, t_seg: float) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "capturando_frame_png_sob_demanda"
                steps["captura_frame_indice"] = indice
                steps["captura_frames_total"] = total
                steps["captura_frame_timestamp_segundos"] = round(float(t_seg), 2)
                await _atualizar_job(session_factory, job_id, steps=steps)

            await marcar(StatusJobTranscribrothers.capturing_frames)
            steps["pipeline_fase"] = "capturando_frames_png_sob_demanda"
            rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
                caminho_video=video,
                timestamps_segundos=timestamps_captura,
                duracao_video_segundos=dur,
                frames_dir=frames_dir,
                assets_dir=assets_dir,
                prefixo_nome_arquivo=prefixo,
                largura_maxima_saida_pixeis=largura_png,
                ao_atualizar_progresso_captura=_progresso_captura_sob_demanda,
            )
        else:
            await marcar(StatusJobTranscribrothers.capturing_frames)
            steps["pipeline_fase"] = "capturando_frames_png"
            n_seg = len(transcricao.segmentos)
            indices_segmentos = list(range(n_seg)) if n_seg else []
            if not indices_segmentos and dur > 0:
                indices_segmentos = [0]
                transcricao = ResultadoTranscricaoComSegmentos(
                    texto_completo=transcricao.texto_completo or "Sem fala detectada.",
                    segmentos=[
                        SegmentoTranscricaoComTempo(
                            inicio_segundos=0.0,
                            fim_segundos=max(1.0, dur),
                            texto="Conteúdo visual (sem segmentos de fala).",
                        )
                    ],
                    idioma_detectado=transcricao.idioma_detectado,
                )
                n_seg = 1
                indices_segmentos = [0]
            indices_segmentos = amostrar_indices_por_limite_por_minuto(
                n_itens=n_seg,
                max_por_minuto=configuracao.max_frames_per_minute,
                duracao_video_segundos=dur
                if dur > 0
                else max(
                    1.0,
                    transcricao.segmentos[-1].fim_segundos if transcricao.segmentos else 1.0,
                ),
            )
            indices_segmentos = reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers(
                indices_segmentos,
                configuracao.tutorial_max_frames_total,
            )
            timestamps_legado = [
                max(0.0, (transcricao.segmentos[i].inicio_segundos + transcricao.segmentos[i].fim_segundos) / 2.0)
                for i in indices_segmentos
                if i < len(transcricao.segmentos)
            ]

            async def _progresso_captura_legado(indice: int, total: int, t_seg: float) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "capturando_frame_png_individual"
                steps["captura_frame_indice"] = indice
                steps["captura_frames_total"] = total
                steps["captura_frame_timestamp_segundos"] = round(float(t_seg), 2)
                await _atualizar_job(session_factory, job_id, steps=steps)

            rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
                caminho_video=video,
                timestamps_segundos=timestamps_legado,
                duracao_video_segundos=dur,
                frames_dir=frames_dir,
                assets_dir=assets_dir,
                prefixo_nome_arquivo=prefixo,
                largura_maxima_saida_pixeis=largura_png,
                ao_atualizar_progresso_captura=_progresso_captura_legado,
            )

        steps["frames_capturados"] = len(rels)
        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        transcricao_para_tutorial = transcricao
        steps["regeneracao_tutorial_snapshot"] = _montar_snapshot_regeneracao_tutorial_transcribrothers(
            transcricao_para_tutorial,
            rels,
        )
        steps["pipeline_fase"] = "gerando_tutorial_http_chat_completions"
        steps["geracao_tutorial_litellm_total_imagens"] = 0
        await marcar(StatusJobTranscribrothers.generating_tutorial)

        instrucao_final = _instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(
            steps
        )
        instrucoes_revisao_final: str | None = None
        if captura_sob_demanda and md_rascunho:
            instrucoes_revisao_final = (
                INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS
            )

        md = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
            transcricao=transcricao_para_tutorial,
            caminhos_frames_rel_job=rels,
            modelo=modelo_litellm,
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            enviar_screenshots_png_como_imagens_multimodais=False,
            bloco_markdown_tutorial_atual_para_contexto_em_revisao=md_rascunho
            if captura_sob_demanda
            else None,
            instrucoes_revisao_humana=instrucoes_revisao_final,
            httpx_timeout_connect_segundos=float(
                configuracao.litellm_http_timeout_connect_segundos
            ),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            instrucao_prefixo_litellm_custom=instrucao_final,
            steps_para_log_decisoes_ia=steps,
        )
        md = await _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            assets_dir=assets_dir,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        await _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            transcricao_corta=transcricao_para_tutorial,
            rels=rels,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        caminho_md = work / "tutorial_gerado_transcribrothers.md"
        caminho_md.write_text(md, encoding="utf-8")
        steps["tutorial_ok"] = True

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            markdown=md,
            steps=steps,
        )
        from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
            ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        )
        from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
            inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers,
        )

        await inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers(
            session_factory,
            job_id=job_id,
            conteudo_markdown=md,
            origem=ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        )
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        steps["pipeline_fase"] = "cancelado_pelo_usuario"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.cancelled,
            error="Cancelado pelo usuário.",
            steps=steps,
        )
    except ErroDownloadGoogleDrive as e:
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=str(e),
            steps=steps,
        )
    except ErroFfmpegTranscribrothers as e:
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=str(e),
            steps=steps,
        )
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        msg_curta = str(e).strip() or repr(e)
        steps_com_diagnostico = {
            **steps,
            "error_traceback": tb[:32000],
            "error_type": type(e).__name__,
            "error_repr": repr(e),
        }
        texto_erro_ui = (
            f"{type(e).__name__}: {msg_curta}\n\n"
            f"--- traceback (servidor; copie para o suporte) ---\n{tb}"
        )
        if len(texto_erro_ui) > 65000:
            texto_erro_ui = texto_erro_ui[:65000] + "\n...[truncado]"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui,
            steps=steps_com_diagnostico,
        )


async def executar_regeneracao_apenas_tutorial_markdown_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    revisao_profunda_multifase: bool = False,
) -> None:
    """Reexecuta só o LLM do tutorial usando snapshot + PNGs já gerados no disco."""
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    steps: dict[str, Any] = {}
    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            job_steps = dict(job.steps_json or {})
            snap = job_steps.get("regeneracao_tutorial_snapshot")
            steps = {**job_steps}

        if not isinstance(snap, dict):
            raise RuntimeError(
                "Snapshot de regeneração ausente: só é possível após captura de telas no pipeline completo."
            )

        transcricao_corta, rels = _snapshot_dict_para_transcricao_e_rels(snap)
        if not rels:
            raise RuntimeError("Snapshot sem referências a frames (assets).")

        assets_dir = work / "assets_exportados_para_markdown"
        for _t, rel in rels:
            nome = rel.split("/")[-1]
            if not nome or not (assets_dir / nome).is_file():
                raise RuntimeError(
                    f"Imagem do tutorial não encontrada no servidor (esperado em assets): {nome}"
                )

        api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(
            configuracao
        )
        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
            configuracao
        )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "regenerando_somente_tutorial_litellm"
        steps["regeneracao_apenas_markdown"] = True
        steps["regeneracao_instrucoes_usadas"] = bool((instrucoes_revisao_humana or "").strip())
        steps["revisao_profunda_multifase_agendada"] = bool(revisao_profunda_multifase)

        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
            FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps.pop("regeneracao_tutorial_aplicada_em", None)

        md_atual = (job.result_markdown or "").strip()
        rels_anexo_regeneracao = montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
            markdown=md_atual,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            rels_completos_com_tempos=rels,
        )
        usar_visao_regeneracao = bool(rels_anexo_regeneracao)
        steps["geracao_tutorial_litellm_total_imagens"] = (
            len(rels_anexo_regeneracao) if usar_visao_regeneracao else 0
        )

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
            steps=steps,
        )

        if revisao_profunda_multifase:
            from transcribrothers_backend.modulo_pipeline_regeneracao_tutorial_revisao_profunda_multifase_litellm_transcribrothers import (
                gerar_markdown_tutorial_via_revisao_profunda_multifase_litellm_transcribrothers,
            )

            md = await gerar_markdown_tutorial_via_revisao_profunda_multifase_litellm_transcribrothers(
                job_id=job_id,
                session_factory=session_factory,
                configuracao=configuracao,
                steps_mutavel=steps,
                transcricao_corta=transcricao_corta,
                rels=rels,
                assets_dir=assets_dir,
                md_atual_inicial=md_atual,
                rels_anexo_regeneracao=rels_anexo_regeneracao,
                usar_visao_regeneracao=usar_visao_regeneracao,
                instrucoes_revisao_humana=instrucoes_revisao_humana,
                modelo_litellm=modelo_litellm.strip(),
                api_key_litellm=api_key_litellm,
                api_base_litellm=api_base_litellm,
                http_verify_litellm=http_verify_litellm,
            )
        else:
            md = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
                transcricao=transcricao_corta,
                caminhos_frames_rel_job=rels,
                modelo=modelo_litellm.strip(),
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                instrucoes_revisao_humana=instrucoes_revisao_humana,
                httpx_timeout_connect_segundos=float(
                    configuracao.litellm_http_timeout_connect_segundos
                ),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                diretorio_assets_absoluto=assets_dir if usar_visao_regeneracao else None,
                enviar_screenshots_png_como_imagens_multimodais=usar_visao_regeneracao,
                markdown_para_decidir_quais_pngs_anexar=None,
                rels_png_anexo_ja_resolvidos=rels_anexo_regeneracao if usar_visao_regeneracao else None,
                bloco_markdown_tutorial_atual_para_contexto_em_revisao=md_atual if md_atual else None,
                instrucao_prefixo_litellm_custom=_instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(
                    steps
                ),
                steps_para_log_decisoes_ia=steps,
                log_etapa_geracao_tutorial="regeneracao_tutorial_markdown",
            )
        md = await _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            assets_dir=assets_dir,
            modelo_litellm=modelo_litellm.strip(),
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        await _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            transcricao_corta=transcricao_corta,
            rels=rels,
            modelo_litellm=modelo_litellm.strip(),
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        md_proposto = (md or "").strip()
        if not md_proposto:
            raise RuntimeError("Regeneração devolveu Markdown vazio.")

        preview_blob: dict[str, Any] = {
            "markdown_antes": md_atual,
            "markdown_depois": md_proposto,
            "markdown_completo_proposto": md_proposto,
            "instrucoes_usadas": (instrucoes_revisao_humana or "").strip(),
            "instrucoes_pedido_original": (instrucoes_revisao_humana or "").strip(),
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "revisao_profunda_multifase": bool(revisao_profunda_multifase),
        }
        ver_sust = steps.get("verificacao_sustentacao_tutorial")
        if isinstance(ver_sust, dict):
            preview_blob["verificacao_sustentacao_tutorial"] = ver_sust

        steps[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS] = (
            preview_blob
        )
        steps["pipeline_fase"] = FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS
        steps["revisao_profunda_multifase"] = bool(revisao_profunda_multifase)

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
            steps=steps,
        )
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        steps["pipeline_fase"] = "cancelado_pelo_usuario"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.cancelled,
            error="Cancelado pelo usuário.",
            steps=steps,
        )
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        msg_curta = str(e).strip() or repr(e)
        steps_com_diagnostico = {
            **steps,
            "error_traceback": tb[:32000],
            "error_type": type(e).__name__,
            "error_repr": repr(e),
        }
        texto_erro_ui = (
            f"{type(e).__name__}: {msg_curta}\n\n"
            f"--- traceback (servidor; copie para o suporte) ---\n{tb}"
        )
        if len(texto_erro_ui) > 65000:
            texto_erro_ui = texto_erro_ui[:65000] + "\n...[truncado]"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui,
            steps=steps_com_diagnostico,
        )


def agendar_regeneracao_apenas_tutorial_markdown_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    revisao_profunda_multifase: bool = False,
) -> None:
    asyncio.create_task(
        executar_regeneracao_apenas_tutorial_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            modelo_litellm=modelo_litellm,
            revisao_profunda_multifase=revisao_profunda_multifase,
        )
    )


def agendar_pipeline_job_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    asyncio.create_task(
        executar_pipeline_job_transcricao_tutorial_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
        )
    )
