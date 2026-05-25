"""Snapshot mínimo de regeneração para projetos em branco (sem vídeo nem transcrição)."""

from __future__ import annotations

from typing import Any


def job_steps_indicam_projeto_em_branco_transcribrothers(steps: dict[str, Any] | None) -> bool:
    if not steps:
        return False
    if steps.get("projeto_em_branco") is True:
        return True
    if steps.get("destino_apos_transcricao") == "projeto_em_branco":
        return True
    if steps.get("source") == "projeto_em_branco":
        return True
    snap = steps.get("regeneracao_tutorial_snapshot")
    return isinstance(snap, dict) and snap.get("snapshot_projeto_em_branco") is True


def montar_snapshot_regeneracao_tutorial_minimo_projeto_em_branco_transcribrothers() -> dict[str, Any]:
    return {
        "texto_completo": "",
        "idioma": None,
        "segmentos": [],
        "caminhos_frames_rel_job": [],
        "snapshot_projeto_em_branco": True,
    }


def garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers(
    steps: dict[str, Any],
) -> dict[str, Any]:
    """Inclui snapshot vazio se o job for em branco e ainda não tiver um."""
    if not job_steps_indicam_projeto_em_branco_transcribrothers(steps):
        return steps
    snap = steps.get("regeneracao_tutorial_snapshot")
    if isinstance(snap, dict):
        return steps
    out = dict(steps)
    out["regeneracao_tutorial_snapshot"] = (
        montar_snapshot_regeneracao_tutorial_minimo_projeto_em_branco_transcribrothers()
    )
    return out
