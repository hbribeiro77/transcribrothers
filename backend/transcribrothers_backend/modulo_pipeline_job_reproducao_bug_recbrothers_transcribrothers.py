"""Pipeline de job com destino `reproducao_bug` (vídeo RecBrothers + JSON de cliques + LLM)."""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers import (
    gerar_markdown_reproducao_bug_recbrothers_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    extrair_audio_wav_de_video_para_caminho,
)
from transcribrothers_backend.modulo_ffprobe_video_tem_faixa_audio_transcribrothers import (
    video_tem_faixa_audio_via_ffprobe_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    PipelineCanceladoPeloUsuarioTranscribrothers,
    _atualizar_job,
    _diretorio_trabalho_job,
    _levantar_se_cancelamento_pipeline_solicitado,
    _montar_snapshot_regeneracao_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_transcrever_audio_wav_janelas_multimodal_ou_whisper_transcribrothers import (
    transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_staging_video_importacao_recbrothers_transcribrothers import (
    NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)

_MARGEM_DEDUPE_CLIQUES_MS = 400
_MAX_CLIQUES_CAPTURA_FRAMES = 48


def _carregar_cliques_reproducao_bug_do_job_opcional(work: Path) -> list[dict[str, Any]]:
    caminho = work / NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS
    if not caminho.is_file():
        return []
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if isinstance(dados, dict) and isinstance(dados.get("cliques"), list):
        return [c for c in dados["cliques"] if isinstance(c, dict)]
    if isinstance(dados, list):
        return [c for c in dados if isinstance(c, dict)]
    raise ValueError("Formato de cliques inválido no job.")


def _carregar_cliques_reproducao_bug_do_job(work: Path) -> list[dict[str, Any]]:
    cliques = _carregar_cliques_reproducao_bug_do_job_opcional(work)
    if not cliques:
        raise FileNotFoundError(
            f"Arquivo de cliques não encontrado no job ({NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS}). "
            "Importe do RecBrothers com modo demonstrar bug ou envie o JSON no upload."
        )
    return cliques


def _montar_pseudo_cliques_a_partir_de_rels_transcribrothers(
    rels: list[tuple[float, str]],
) -> list[dict[str, Any]]:
    return [
        {"tRelativoMs": int(round(float(t) * 1000.0)), "origem": "inferido_pipeline"}
        for t, _rel in rels
    ]


def _deduplicar_cliques_por_tempo_relativo_ms_transcribrothers(
    cliques: list[dict[str, Any]],
    *,
    margem_ms: int = _MARGEM_DEDUPE_CLIQUES_MS,
) -> list[dict[str, Any]]:
    ordenados = sorted(cliques, key=lambda c: float(c.get("tRelativoMs", c.get("tsAbsoluto", 0)) or 0))
    saida: list[dict[str, Any]] = []
    ultimo_ms = -10_000.0
    for clique in ordenados:
        t_ms = float(clique.get("tRelativoMs", 0) or 0)
        if saida and t_ms - ultimo_ms < margem_ms:
            continue
        saida.append(clique)
        ultimo_ms = t_ms
    return saida[:_MAX_CLIQUES_CAPTURA_FRAMES]


async def executar_pipeline_job_reproducao_bug_recbrothers_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    audio = work / "audio_extraido_para_transcricao.wav"
    frames_dir = work / "frames_png_capturados_reproducao_bug"
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
            job_steps = dict(job.steps_json or {})
            steps = steps_json_job_para_reexecucao_pipeline_transcribrothers(job_steps)
            modelo_litellm = (job_steps.get("litellm_model") or configuracao.litellm_model or "").strip()
            api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
            overrides_tm = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(session)

        configuracao_exec_transcricao_mm = aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
            configuracao,
            overrides_tm,
        )
        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)

        steps["destino_apos_transcricao"] = "reproducao_bug"
        steps["pipeline_fase"] = "reproducao_bug_inicio"
        await marcar(StatusJobTranscribrothers.downloading)

        candidatos = sorted(work.glob("video_entrada_arquivo_local.*"))
        video = next((p for p in candidatos if p.is_file()), None)
        if video is None:
            raise FileNotFoundError("Vídeo do job não encontrado (video_entrada_arquivo_local.*).")

        cliques_brutos = _carregar_cliques_reproducao_bug_do_job_opcional(work)
        cliques = _deduplicar_cliques_por_tempo_relativo_ms_transcribrothers(cliques_brutos)
        sem_json_cliques = not cliques
        if sem_json_cliques:
            steps["reproducao_bug_sem_json_cliques"] = True
            steps["reproducao_bug_total_cliques"] = 0
        else:
            steps.pop("reproducao_bug_sem_json_cliques", None)
            steps["reproducao_bug_total_cliques"] = len(cliques)

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        tem_audio = await video_tem_faixa_audio_via_ffprobe_transcribrothers(video)
        steps["video_tem_faixa_audio_ffprobe"] = tem_audio
        transcricao = ResultadoTranscricaoComSegmentos(
            texto_completo="",
            segmentos=[],
            idioma_detectado=None,
        )

        if tem_audio:
            await marcar(StatusJobTranscribrothers.extracting_audio)
            steps["pipeline_fase"] = "ffmpeg_extrair_audio"
            try:
                await extrair_audio_wav_de_video_para_caminho(
                    caminho_video=video,
                    caminho_audio_wav=audio,
                    forcar_mono=bool(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_mono),
                )
            except ErroFfmpegTranscribrothers as e:
                steps["audio_extracao_falhou"] = str(e)
                tem_audio = False
            else:
                steps["audio_ok"] = True
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                await marcar(StatusJobTranscribrothers.transcribing)

                async def ao_persistir_steps_transcricao_transcribrothers(st: dict[str, Any]) -> None:
                    await _atualizar_job(
                        session_factory,
                        job_id,
                        status=StatusJobTranscribrothers.transcribing,
                        steps=st,
                    )

                transcricao = await transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers(
                    work=work,
                    audio=audio,
                    configuracao=configuracao,
                    configuracao_exec_transcricao_mm=configuracao_exec_transcricao_mm,
                    http_verify_litellm=http_verify_litellm,
                    steps=steps,
                    ao_persistir_steps=ao_persistir_steps_transcricao_transcribrothers,
                    levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
                    pipeline_fase_inicial="transcrevendo_audio_opcional",
                )
        else:
            steps["pipeline_fase"] = "sem_faixa_audio_pulando_transcricao"

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        dur = await obter_duracao_video_segundos_via_ffprobe(video)
        if dur > 0:
            steps["duracao_video_segundos"] = round(float(dur), 3)
        if cliques:
            timestamps = [
                max(0.0, float(c.get("tRelativoMs", 0) or 0) / 1000.0) for c in cliques
            ]
            steps["pipeline_fase"] = "capturando_frames_nos_cliques"
        else:
            steps["pipeline_fase"] = "inferindo_instantes_captura_sem_json_cliques"
            timestamps = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
                markdown_rascunho_tutorial="",
                transcricao=transcricao,
                duracao_video_segundos=dur,
                max_frames_per_minute=int(configuracao.max_frames_per_minute),
                tutorial_max_frames_total=int(configuracao.tutorial_max_frames_total),
            )
            steps["reproducao_bug_timestamps_inferidos"] = len(timestamps)
        await marcar(StatusJobTranscribrothers.generating_tutorial)
        largura_png = (
            int(configuracao.tutorial_frame_max_width_px)
            if configuracao.tutorial_frame_max_width_px > 0
            else None
        )
        rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
            caminho_video=video,
            timestamps_segundos=timestamps,
            duracao_video_segundos=dur,
            frames_dir=frames_dir,
            assets_dir=assets_dir,
            prefixo_nome_arquivo="screenshot_reproducao_bug_recbrothers",
            largura_maxima_saida_pixeis=largura_png,
        )
        steps["reproducao_bug_frames_capturados"] = len(rels)

        if sem_json_cliques:
            cliques = _montar_pseudo_cliques_a_partir_de_rels_transcribrothers(rels)

        _levantar_se_cancelamento_pipeline_solicitado(job_id)
        steps["pipeline_fase"] = "gerando_markdown_reproducao_bug_litellm"
        md = await gerar_markdown_reproducao_bug_recbrothers_com_litellm_transcribrothers(
            cliques=cliques,
            transcricao=transcricao,
            caminhos_frames_rel_job=rels,
            modelo=modelo_litellm,
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            diretorio_assets_absoluto=assets_dir,
            steps_para_log_decisoes_ia=steps,
            sem_json_cliques_recbrothers=sem_json_cliques,
        )
        steps["regeneracao_tutorial_snapshot"] = _montar_snapshot_regeneracao_tutorial_transcribrothers(
            transcricao,
            rels,
        )
        steps["pipeline_fase"] = "reproducao_bug_concluida"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            markdown=md,
            steps=steps,
        )
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
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
        }
        texto_erro_ui = f"{type(e).__name__}: {msg_curta}\n\n--- traceback ---\n{tb}"
        if len(texto_erro_ui) > 65000:
            texto_erro_ui = texto_erro_ui[:65000] + "\n...[truncado]"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui,
            steps=steps_com_diagnostico,
        )
