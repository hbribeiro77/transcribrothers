"""Verifica quais handlers de agente estão habilitados no job (pipeline custom com snapshot)."""

from __future__ import annotations

from typing import Any


def job_usa_snapshot_pipeline_custom_transcribrothers(steps: dict[str, Any] | None) -> bool:
    if not steps:
        return False
    return bool(str(steps.get("pipeline_custom_id") or "").strip())


def _mapa_agentes_custom_de_steps_transcribrothers(steps: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = steps.get("pipeline_custom_agentes")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for handler, cfg in raw.items():
        if isinstance(handler, str) and isinstance(cfg, dict):
            out[handler] = cfg
    return out


def handler_pipeline_custom_habilitado_no_job_transcribrothers(
    steps: dict[str, Any] | None,
    handler_chave: str,
) -> bool:
    """Sem pipeline custom no job, todos os handlers do molde podem rodar. Com custom, só os do snapshot."""
    if not job_usa_snapshot_pipeline_custom_transcribrothers(steps):
        return True
    assert steps is not None
    handler = handler_chave.strip()
    if not handler:
        return False
    return handler in _mapa_agentes_custom_de_steps_transcribrothers(steps)
