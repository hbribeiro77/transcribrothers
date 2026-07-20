"""Carrega transcrição do snapshot em disco para reprocessamento pós-transcrição (gerar outro formato)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)


def snapshot_transcricao_disponivel_no_work_transcribrothers(work: Path) -> bool:
    return carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work) is not None


def carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers(
    work: Path,
    steps: dict[str, Any],
) -> ResultadoTranscricaoComSegmentos:
    snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work)
    if snap is None:
        raise RuntimeError(
            "Snapshot de transcrição não encontrado no diretório do job. "
            "Não é possível gerar outro formato sem retranscrever."
        )
    steps["transcricao_snapshot_finalizada_em_disco"] = True
    steps["transcricao_segmentos"] = len(snap.segmentos)
    steps["pipeline_fase"] = "transcricao_reutilizada_gerar_outro_formato"
    return snap


def finalizar_reprocessamento_pos_transcricao_nos_steps_transcribrothers(steps: dict[str, Any]) -> None:
    steps.pop("reprocessamento_pos_transcricao_apenas", None)
