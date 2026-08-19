"""Resolve cues com timeout no experimental e retoma o mux do vídeo narrado."""

from __future__ import annotations

import asyncio
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers import (
    diretorio_wavs_narracao_por_cue_do_work_transcribrothers,
    obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_diagnostico_tts_perfil_experimental_voz_transcribrothers import (
    CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    _TTS_SILENCIO_CUE_PULADA_SEGUNDOS,
    _TTS_VOICE,
    _gravar_pcm16_mono_como_wav_transcribrothers,
    _pcm16_silencio_mono_segundos_transcribrothers,
    obter_duracao_wav_pcm16_mono_segundos_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    normalizar_perfil_tts_narracao_transcribrothers,
    normalizar_ritmo_tts_narracao_transcribrothers,
    normalizar_temperatura_tts_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_CONCLUIDO,
    FASE_VIDEO_NARRADO_MUX_FFMPEG,
    _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers,
    _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers,
    _diretorio_assets_do_job,
    _diretorio_trabalho_job,
    _localizar_arquivo_video_entrada_no_diretorio_job,
)
from transcribrothers_backend.modulo_util_registrar_tempos_etapas_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS,
    fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers,
)

# Serializa commit da lista de pendentes + agendar mux (síntese TTS pode ser paralela).
_locks_resolucao_timeout_por_job: dict[str, asyncio.Lock] = {}
_lock_mapa_resolucao_timeout = asyncio.Lock()


async def _obter_lock_resolucao_timeout_job_transcribrothers(job_id: str) -> asyncio.Lock:
    async with _lock_mapa_resolucao_timeout:
        lock = _locks_resolucao_timeout_por_job.get(job_id)
        if lock is None:
            lock = asyncio.Lock()
            _locks_resolucao_timeout_por_job[job_id] = lock
        return lock


def ler_cues_pendentes_timeout_dos_steps_transcribrothers(
    steps: dict[str, Any],
) -> list[dict[str, Any]]:
    raw = steps.get(CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS)
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict) and isinstance(item.get("indice"), int):
            out.append(item)
    return out


def gravar_cues_pendentes_timeout_nos_steps_transcribrothers(
    steps: dict[str, Any],
    pendentes: list[dict[str, Any]],
) -> None:
    steps[CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS] = list(
        pendentes
    )


async def sintetizar_e_gravar_wav_definitivo_cue_experimental_uma_tentativa_transcribrothers(
    *,
    texto: str,
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    caminho_wav_saida: Path,
    voz: str = _TTS_VOICE,
    temperatura: float | None = None,
    ritmo: object = None,
) -> tuple[bool, str]:
    """
    Uma tentativa no motor experimental (via preview helper com perfil).
    Retorna (ok, mensagem). Em timeout/falha o WAV antigo permanece.
    """
    from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
        ErroTtsRespostaVaziaRetryavelTranscribrothers,
        _sintetizar_pcm16_trecho_tts_experimental_com_retry_e_diagnostico_transcribrothers,
        DiagnosticoTtsPerfilExperimentalVozTranscribrothers,
    )
    from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
        normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
        resolver_api_key_e_api_base_para_chamada_litellm,
        resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
    )
    import httpx

    texto_norm = " ".join((texto or "").split())
    if not texto_norm:
        return False, "Informe o texto da cue."
    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return False, "Proxy LiteLLM não configurado."
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return False, "LITELLM_ENDPOINT inválido."
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
        configuracao
    )
    diag = DiagnosticoTtsPerfilExperimentalVozTranscribrothers(quantidade_cues_total=1)
    lock = asyncio.Lock()
    try:
        pcm = await _sintetizar_pcm16_trecho_tts_experimental_com_retry_e_diagnostico_transcribrothers(
            texto=texto_norm,
            modelo=(modelo or "").strip(),
            api_key=api_key,
            base_v1=base_v1,
            httpx_verify=httpx_verify,
            voz=(voz or _TTS_VOICE).strip() or _TTS_VOICE,
            indice_cue=1,
            diagnostico=diag,
            lock_diagnostico=lock,
            max_tentativas=1,
            temperatura=temperatura,
            ritmo=ritmo,
        )
    except httpx.TimeoutException:
        return False, "Tempo esgotado na narração TTS (tente de novo ou edite o texto)."
    except ErroTtsRespostaVaziaRetryavelTranscribrothers as exc:
        return False, str(exc)
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return False, str(exc)
    caminho_wav_saida.parent.mkdir(parents=True, exist_ok=True)
    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_saida, pcm)
    dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_wav_saida)
    if dur < 0.2:
        return False, "Áudio gerado parece vazio ou curto demais."
    return True, "Cue narrada com sucesso."


def _reconstruir_wav_concatenado_das_cues_transcribrothers(
    *,
    work: Path,
    quantidade_cues: int,
    caminho_wav_concatenado: Path,
) -> list[float]:
    duracoes: list[float] = []
    pcm_total = bytearray()
    for i in range(quantidade_cues):
        caminho = obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, i)
        if caminho is None or not caminho.is_file():
            raise RuntimeError(f"Falta o WAV da cue {i + 1} para montar a narração.")
        with wave.open(str(caminho), "rb") as wf:
            pcm_total.extend(wf.readframes(wf.getnframes()))
        duracoes.append(obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho))
    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_concatenado, bytes(pcm_total))
    return duracoes


async def continuar_pipeline_video_narrado_apos_resolver_tts_timeout_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    """Retoma mux após todas as cues pendentes de timeout terem sido resolvidas."""
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_do_job(data_dir, job_id)
    try:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                return
            steps = dict(row.steps_json or {})

        pendentes = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
        if pendentes:
            raise RuntimeError(
                f"Ainda há {len(pendentes)} cue(s) com timeout pendente de reenvio."
            )

        cues = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
        if not cues:
            raise RuntimeError("Manifesto de cues/janelas ausente para continuar o mux.")

        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        if video is None:
            raise RuntimeError("Vídeo de entrada não encontrado no job.")

        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
        )

        caminho_wav = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        duracoes = _reconstruir_wav_concatenado_das_cues_transcribrothers(
            work=work,
            quantidade_cues=len(cues),
            caminho_wav_concatenado=caminho_wav,
        )
        cues_vtt = converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
            list(cues),
            list(duracoes),
        )
        caminho_vtt = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
            diretorio_assets=assets,
            cues=cues_vtt,
        )
        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        url_vtt = f"/api/jobs/{job_id}/assets/{caminho_vtt.name}?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": caminho_vtt.name,
            "url_asset": url_vtt,
            "timeline": "narracao_tts",
        }
        url_wav = f"/api/jobs/{job_id}/assets/{caminho_wav.name}?v={stamp_cache}"
        narracao_prev = dict(steps.get(CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS) or {})
        steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            **narracao_prev,
            "nome_arquivo": caminho_wav.name,
            "url_asset": url_wav,
            "quantidade_cues": len(cues),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "retomado_apos_timeout_manual": True,
        }
        gravar_cues_pendentes_timeout_nos_steps_transcribrothers(steps, [])

        _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
            steps,
            FASE_VIDEO_NARRADO_MUX_FFMPEG,
        )
        steps["video_narrado_mux_segmento_indice"] = 0
        steps["video_narrado_mux_segmento_total"] = len(cues)
        steps["video_narrado_mux_fase"] = "iniciando"
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
        )

        async def _progresso_mux(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
            )

        caminhos_wav = []
        for i in range(len(cues)):
            p = obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, i)
            if p is None:
                raise RuntimeError(f"Falta o WAV da cue {i + 1}.")
            caminhos_wav.append(p)

        segmentos = [
            SegmentoVideoNarradoRetargetTranscribrothers(
                caminho_wav=caminho_wav_cue,
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
            )
            for cue, caminho_wav_cue in zip(cues, caminhos_wav, strict=True)
        ]
        from transcribrothers_backend.modulo_persistencia_runtime_config_encode_video_narrado_sqlite_transcribrothers import (
            carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers,
        )

        prefs_encode = await carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers(
            session_factory
        )
        steps["video_narrado_mux_encode_resolucao"] = prefs_encode.resolucao
        steps["video_narrado_mux_encode_fps"] = int(prefs_encode.fps)
        caminho_mp4 = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=work,
            atualizar_progresso=_progresso_mux,
            preferencias_encode=prefs_encode,
            # Mesmo caminho da geração Markdown: enche o cache de segmentos.
            forcar_montagem_por_segmentos_com_cache=True,
        )
        url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_mp4.name,
            "url_download": url_mp4,
            "modo_montagem": "segmentos_retarget_audio",
            "quantidade_segmentos": len(segmentos),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
        }
        from transcribrothers_backend.modulo_salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers import (
            marcar_audio_mp4_sincronizado_com_projeto_editor_apos_remux_transcribrothers,
        )

        marcar_audio_mp4_sincronizado_com_projeto_editor_apos_remux_transcribrothers(steps)
        fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(steps)
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
        tempos = steps.get(CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS) or {}
        total_s = tempos.get("total_segundos") if isinstance(tempos, dict) else None
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": True,
            "mensagem": (
                f"Vídeo narrado pronto após resolver timeout(s) TTS manualmente "
                f"({len(cues)} cue(s))."
            ),
            "quantidade_cues": len(cues),
            "nome_arquivo_vtt": caminho_vtt.name,
            "url_asset_vtt": url_vtt,
            "nome_arquivo_wav": caminho_wav.name,
            "url_asset_wav": url_wav,
            "nome_arquivo_mp4": caminho_mp4.name,
            "url_download_mp4": url_mp4,
            "concluido_em": datetime.now(timezone.utc).isoformat(),
            "duracao_total_pipeline_segundos": total_s,
            "retomado_apos_timeout_manual": True,
        }
        from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
            tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers,
        )

        versao_snap = tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers(
            work=work,
            assets=assets,
            steps=steps,
            origem="retomada_apos_timeout_tts_manual",
        )
        if versao_snap:
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS][
                "versao_video_narrado_id"
            ] = versao_snap
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
        )
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        msg = str(e).strip() or type(e).__name__
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            steps = dict(row.steps_json or {}) if row else {}
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": False,
            "mensagem": f"Falha ao continuar após timeouts TTS: {msg}",
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=f"{type(e).__name__}: {msg}\n\n{tb}"[:65000],
        )


async def _validar_job_aguardando_timeout_experimental_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    indice: int,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Retorna (steps, alvo_pendente, pendentes)."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise ValueError("Job não encontrado.")
        steps = dict(row.steps_json or {})
        fase = str(steps.get("pipeline_fase") or "")
        if fase != FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS:
            raise ValueError(
                "Este job não está aguardando resolução de timeout TTS experimental."
            )
        perfil = normalizar_perfil_tts_narracao_transcribrothers(
            steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS)
        )
        if perfil != PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS:
            raise ValueError("Retry manual de timeout só no perfil experimental_voz.")

        pendentes = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
        alvo = next((p for p in pendentes if int(p["indice"]) == int(indice)), None)
        if alvo is None:
            raise ValueError(f"Cue índice {indice} não está na lista de pendentes.")
        return steps, alvo, pendentes


async def _agendar_mux_se_pendentes_zeraram_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    pendentes: list[dict[str, Any]],
) -> bool:
    if pendentes:
        return False
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            steps = dict(row.steps_json or {})
            steps["pipeline_fase"] = FASE_VIDEO_NARRADO_MUX_FFMPEG
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
                **dict(
                    steps.get(CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS)
                    or {}
                ),
                "ok": False,
                "aguardando_resolucao_tts_timeout": False,
                "mensagem": "Timeouts TTS resolvidos; retomando montagem do vídeo…",
            }
            row.steps_json = steps
            row.status = StatusJobTranscribrothers.generating_tutorial.value
            row.error_message = None
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(row, "steps_json")
            row.updated_at = datetime.now(timezone.utc)
            await session.commit()
    asyncio.create_task(
        continuar_pipeline_video_narrado_apos_resolver_tts_timeout_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
        )
    )
    return True


def _resposta_resolucao_pendente_timeout_transcribrothers(
    *,
    ok: bool,
    mensagem: str,
    indice: int,
    pendentes_restantes: int,
    pipeline_continuada: bool,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "mensagem": (
            f"{mensagem} Montagem do vídeo retomada."
            if ok and pipeline_continuada
            else mensagem
        ),
        "indice": indice,
        "pendentes_restantes": pendentes_restantes,
        "pipeline_continuada": pipeline_continuada,
        "pipeline_fase": (
            FASE_VIDEO_NARRADO_MUX_FFMPEG
            if pipeline_continuada
            else FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS
        ),
    }


async def resolver_cue_tts_pendente_timeout_experimental_job_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    indice: int,
    texto: str,
    voz: str | None = None,
) -> dict[str, Any]:
    """
    Reenvia uma cue pendente (1 tentativa). Se a lista zerar, agenda o mux.
    """
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    steps, alvo, pendentes = await _validar_job_aguardando_timeout_experimental_transcribrothers(
        job_id=job_id,
        session_factory=session_factory,
        indice=indice,
    )

    modelo = str(
        steps.get("pipeline_video_narrado_modelo_tts")
        or (steps.get(CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS) or {}).get("modelo")
        or ""
    ).strip()
    if not modelo:
        raise ValueError("Modelo TTS ausente nos steps do job.")

    voz_efetiva = (voz or alvo.get("voz") or steps.get("pipeline_video_narrado_voz_tts") or _TTS_VOICE)
    voz_efetiva = str(voz_efetiva).strip() or _TTS_VOICE
    dir_wavs = diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work)
    caminho_wav = dir_wavs / f"cue_narracao_{int(indice):04d}.wav"

    temperatura_efetiva = normalizar_temperatura_tts_narracao_transcribrothers(
        steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS)
    )
    ritmo_efetivo = normalizar_ritmo_tts_narracao_transcribrothers(
        steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS)
    )
    ok, mensagem = await sintetizar_e_gravar_wav_definitivo_cue_experimental_uma_tentativa_transcribrothers(
        texto=texto,
        modelo=modelo,
        configuracao=configuracao,
        caminho_wav_saida=caminho_wav,
        voz=voz_efetiva,
        temperatura=temperatura_efetiva,
        ritmo=ritmo_efetivo,
    )
    if not ok:
        return _resposta_resolucao_pendente_timeout_transcribrothers(
            ok=False,
            mensagem=mensagem,
            indice=indice,
            pendentes_restantes=len(pendentes),
            pipeline_continuada=False,
        )

    lock = await _obter_lock_resolucao_timeout_job_transcribrothers(job_id)
    async with lock:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                raise ValueError("Job não encontrado.")
            steps = dict(row.steps_json or {})
            pendentes_atuais = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
            if not any(int(p["indice"]) == int(indice) for p in pendentes_atuais):
                return _resposta_resolucao_pendente_timeout_transcribrothers(
                    ok=True,
                    mensagem="Cue já não estava pendente (resolvida em paralelo).",
                    indice=indice,
                    pendentes_restantes=len(pendentes_atuais),
                    pipeline_continuada=False,
                )
            pendentes = [p for p in pendentes_atuais if int(p["indice"]) != int(indice)]
            gravar_cues_pendentes_timeout_nos_steps_transcribrothers(steps, pendentes)
            from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
                CueNarracaoComJanelaVideoTranscribrothers,
                carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
                gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
            )

            cues = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
            if 0 <= int(indice) < len(cues):
                antiga = cues[int(indice)]
                texto_novo = " ".join((texto or "").split())
                cues[int(indice)] = CueNarracaoComJanelaVideoTranscribrothers(
                    texto=texto_novo,
                    inicio_video_segundos=antiga.inicio_video_segundos,
                    fim_video_segundos=antiga.fim_video_segundos,
                    origem_ancora=antiga.origem_ancora,
                    casado=antiga.casado,
                    sem_narracao=antiga.sem_narracao,
                    voz_tts=voz_efetiva,
                    texto_tts=texto_novo,
                )
                gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
                    work=work,
                    cues=cues,
                )
            row.steps_json = steps
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(row, "steps_json")
            await session.commit()

        pipeline_continuada = await _agendar_mux_se_pendentes_zeraram_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            pendentes=pendentes,
        )
    return _resposta_resolucao_pendente_timeout_transcribrothers(
        ok=True,
        mensagem=mensagem,
        indice=indice,
        pendentes_restantes=len(pendentes),
        pipeline_continuada=pipeline_continuada,
    )


async def descartar_cue_tts_pendente_timeout_experimental_job_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    indice: int,
) -> dict[str, Any]:
    """
    Não narrar cue com timeout: confirma silêncio no slot, marca sem_narracao,
    remove da lista. Se zerar, agenda o mux.
    """
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    await _validar_job_aguardando_timeout_experimental_transcribrothers(
        job_id=job_id,
        session_factory=session_factory,
        indice=indice,
    )

    dir_wavs = diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work)
    dir_wavs.mkdir(parents=True, exist_ok=True)
    caminho_wav = dir_wavs / f"cue_narracao_{int(indice):04d}.wav"
    pcm_silencio = _pcm16_silencio_mono_segundos_transcribrothers(
        _TTS_SILENCIO_CUE_PULADA_SEGUNDOS
    )
    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav, pcm_silencio)

    lock = await _obter_lock_resolucao_timeout_job_transcribrothers(job_id)
    async with lock:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                raise ValueError("Job não encontrado.")
            steps = dict(row.steps_json or {})
            pendentes_atuais = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
            if not any(int(p["indice"]) == int(indice) for p in pendentes_atuais):
                return _resposta_resolucao_pendente_timeout_transcribrothers(
                    ok=True,
                    mensagem="Cue já não estava pendente (resolvida em paralelo).",
                    indice=indice,
                    pendentes_restantes=len(pendentes_atuais),
                    pipeline_continuada=False,
                )
            pendentes = [p for p in pendentes_atuais if int(p["indice"]) != int(indice)]
            gravar_cues_pendentes_timeout_nos_steps_transcribrothers(steps, pendentes)

            narracao_prev = dict(steps.get(CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS) or {})
            puladas_prev = list(narracao_prev.get("previews_cues_puladas") or [])
            from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
                CueNarracaoComJanelaVideoTranscribrothers,
                carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
                gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
            )

            cues = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
            preview_pulada = f"cue {int(indice) + 1} (não narrar — timeout)"
            if 0 <= int(indice) < len(cues):
                antiga = cues[int(indice)]
                cues[int(indice)] = CueNarracaoComJanelaVideoTranscribrothers(
                    texto=antiga.texto,
                    inicio_video_segundos=antiga.inicio_video_segundos,
                    fim_video_segundos=antiga.fim_video_segundos,
                    origem_ancora=antiga.origem_ancora,
                    casado=antiga.casado,
                    sem_narracao=True,
                    voz_tts=antiga.voz_tts,
                    texto_tts=antiga.texto_tts,
                )
                gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
                    work=work,
                    cues=cues,
                )
                preview_pulada = (antiga.texto or preview_pulada)[:80]
            if preview_pulada not in puladas_prev:
                puladas_prev.append(preview_pulada)
            steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
                **narracao_prev,
                "quantidade_cues_puladas": len(puladas_prev),
                "previews_cues_puladas": puladas_prev,
            }

            row.steps_json = steps
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(row, "steps_json")
            await session.commit()

        pipeline_continuada = await _agendar_mux_se_pendentes_zeraram_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            pendentes=pendentes,
        )
    return _resposta_resolucao_pendente_timeout_transcribrothers(
        ok=True,
        mensagem="Cue mantida sem narração (silêncio).",
        indice=indice,
        pendentes_restantes=len(pendentes),
        pipeline_continuada=pipeline_continuada,
    )
