"""Flags em memória para cancelamento cooperativo de jobs (mesmo processo uvicorn)."""

from __future__ import annotations

_jobs_com_cancelamento_solicitado: set[str] = set()


def marcar_cancelamento_pipeline_solicitado_para_job_transcribrothers(job_id: str) -> None:
    _jobs_com_cancelamento_solicitado.add(job_id)


def cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id: str) -> bool:
    return job_id in _jobs_com_cancelamento_solicitado


def limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id: str) -> None:
    _jobs_com_cancelamento_solicitado.discard(job_id)
