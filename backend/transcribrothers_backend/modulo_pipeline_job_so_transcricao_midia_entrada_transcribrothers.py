"""Pipeline curto: entrada vídeo/áudio → WAV → STT → Markdown da transcrição → completed."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_transcrever_audio_wav_janelas_multimodal_ou_whisper_transcribrothers import (
    transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_util_obter_wav_para_transcricao_a_partir_entrada_midia_job_transcribrothers import (
    garantir_wav_para_transcricao_a_partir_entrada_midia_job_transcribrothers,
    localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers,
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)


class PipelineSoTranscricaoCanceladoPeloUsuarioTranscribrothers(Exception):
    pass


def _levantar_se_cancelamento_so_transcricao(job_id: str) -> None:
    if cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id):
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        raise PipelineSoTranscricaoCanceladoPeloUsuarioTranscribrothers()


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def montar_markdown_resultado_so_transcricao_transcribrothers(
    *,
    texto_completo: str,
    segmentos: list[Any],
) -> str:
    linhas = ["# Transcrição", ""]
    corpo = (texto_completo or "").strip() or "Sem fala detectada."
    linhas.append(corpo)
    linhas.append("")
    if segmentos:
        linhas.extend(["## Segmentos", ""])
        for seg in segmentos:
            ini = getattr(seg, "inicio_segundos", None)
            fim = getattr(seg, "fim_segundos", None)
            texto = (getattr(seg, "texto", None) or "").strip()
            if ini is None or fim is None:
                if texto:
                    linhas.append(f"- {texto}")
                continue
            linhas.append(f"- [{float(ini):.1f}s–{float(fim):.1f}s] {texto}")
        linhas.append("")
    return "\n".join(linhas)


async def _atualizar_job_so_transcricao(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    status: StatusJobTranscribrothers | None = None,
    steps: dict[str, Any] | None = None,
    result_markdown: str | None = None,
    error_message: str | None = None,
) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            return
        if status is not None:
            row.status = status.value
        if steps is not None:
            row.steps_json = steps
        if result_markdown is not None:
            row.result_markdown = result_markdown
        if error_message is not None:
            row.error_message = error_message
        await session.commit()


async def executar_pipeline_job_so_transcricao_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    audio = work / "audio_extraido_para_transcricao.wav"
    steps: dict[str, Any] = {}

    async def marcar(s: StatusJobTranscribrothers, extra: dict[str, Any] | None = None) -> None:
        nonlocal steps
        if extra:
            steps = {**steps, **extra}
        await _atualizar_job_so_transcricao(session_factory, job_id, status=s, steps=steps)

    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            job_steps = dict(job.steps_json or {})
            steps = steps_json_job_para_reexecucao_pipeline_transcribrothers(job_steps)
            overrides_tm = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(
                session
            )

        configuracao_exec = aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
            configuracao,
            overrides_tm,
        )
        http_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["destino_apos_transcricao"] = "so_transcricao"
        steps["pipeline_fase"] = "metadados_job_carregados"
        steps["source"] = OrigemEntradaJobTranscribrothers.upload_local

        work.mkdir(parents=True, exist_ok=True)
        entrada, tipo = localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(work)
        if entrada is None:
            raise FileNotFoundError(
                "Arquivo de entrada (vídeo ou áudio) não encontrado no diretório do job."
            )
        steps["tipo_entrada_midia"] = tipo or str(steps.get("tipo_entrada_midia") or "video")
        steps["upload_ok"] = True
        if tipo == "audio":
            steps["audio_entrada_filename"] = entrada.name
        else:
            steps["video_filename"] = entrada.name

        await marcar(StatusJobTranscribrothers.extracting_audio)
        if deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(audio, steps):
            steps["pipeline_fase"] = "audio_wav_reutilizado_sem_reextrair"
            steps["audio_ok"] = True
            steps["audio_wav_reutilizado_retry"] = True
        else:
            steps["pipeline_fase"] = (
                "normalizar_audio_entrada" if steps["tipo_entrada_midia"] == "audio" else "ffmpeg_extrair_audio"
            )
            steps.pop("audio_wav_reutilizado_retry", None)
            await garantir_wav_para_transcricao_a_partir_entrada_midia_job_transcribrothers(
                work=work,
                steps=steps,
                caminho_wav_destino=audio,
                forcar_mono=bool(configuracao_exec.transcricao_multimodal_audio_mono),
                caminho_video_ja_resolvido=entrada if tipo == "video" else None,
            )
            steps["audio_ok"] = True

        dur = await obter_duracao_video_segundos_via_ffprobe(entrada)
        if dur > 0:
            steps["duracao_video_segundos"] = round(float(dur), 3)

        await marcar(StatusJobTranscribrothers.transcribing)

        async def ao_persistir(st: dict[str, Any]) -> None:
            await _atualizar_job_so_transcricao(session_factory, job_id, steps=st)

        transcricao = await transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers(
            work=work,
            audio=audio,
            configuracao=configuracao,
            configuracao_exec_transcricao_mm=configuracao_exec,
            http_verify_litellm=http_verify,
            steps=steps,
            ao_persistir_steps=ao_persistir,
            levantar_se_cancelado=lambda: _levantar_se_cancelamento_so_transcricao(job_id),
            pipeline_fase_inicial="transcrevendo_audio",
        )

        md = montar_markdown_resultado_so_transcricao_transcribrothers(
            texto_completo=transcricao.texto_completo,
            segmentos=list(transcricao.segmentos or []),
        )
        steps["pipeline_fase"] = "so_transcricao_concluida"
        steps["pode_gerar_outro_formato"] = True
        await _atualizar_job_so_transcricao(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            steps=steps,
            result_markdown=md,
            error_message=None,
        )
    except PipelineSoTranscricaoCanceladoPeloUsuarioTranscribrothers:
        steps["pipeline_fase"] = "cancelado_pelo_usuario"
        await _atualizar_job_so_transcricao(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.cancelled,
            steps=steps,
            error_message="Cancelado pelo usuário.",
        )
    except Exception as e:  # noqa: BLE001
        steps["pipeline_fase"] = "falhou"
        steps["error_type"] = type(e).__name__
        steps["error_repr"] = repr(e)
        await _atualizar_job_so_transcricao(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            steps=steps,
            error_message=str(e),
        )
