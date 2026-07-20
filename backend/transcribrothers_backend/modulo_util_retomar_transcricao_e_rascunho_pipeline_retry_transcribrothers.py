"""Carrega transcrição/rascunho já prontos no disco para não repetir etapas pesadas no retry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_rascunho_notas_proposta_sem_imagens_do_work_se_existir_transcribrothers,
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)


def steps_indicam_transcricao_ja_concluida_no_pipeline_transcribrothers(steps: dict[str, Any]) -> bool:
    if int(steps.get("transcricao_segmentos") or 0) > 0:
        return True
    fase = str(steps.get("pipeline_fase") or "").strip()
    return fase in (
        "transcricao_concluida",
        "gerando_rascunho_notas_proposta",
        "gerando_rascunho_tutorial_sem_imagens",
        "planejando_instantes_captura_notas_proposta",
        "capturando_frames_notas_proposta",
        "gerando_markdown_notas_proposta_litellm",
        "notas_proposta_concluida",
    )


def tentar_carregar_transcricao_finalizada_para_retry_pipeline_transcribrothers(
    diretorio_trabalho_job: Path,
    steps: dict[str, Any],
) -> ResultadoTranscricaoComSegmentos | None:
    """
    Atalho síncrono: só o snapshot em disco (recuperação completa com checkpoint é assíncrona em
    `tentar_recuperar_transcricao_automatica_antes_de_reexecutar_pipeline_transcribrothers`).
    """
    snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
    if snap is not None:
        return snap
    if not steps_indicam_transcricao_ja_concluida_no_pipeline_transcribrothers(steps):
        return None
    return None


def tentar_carregar_rascunho_notas_proposta_para_retry_pipeline_transcribrothers(
    diretorio_trabalho_job: Path,
    steps: dict[str, Any],
) -> str | None:
    if not bool(steps.get("notas_proposta_rascunho_sem_imagens_ok")):
        return None
    return carregar_rascunho_notas_proposta_sem_imagens_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
