from __future__ import annotations

from typing import Any


def job_steps_indicam_notas_proposta_funcionalidade_transcribrothers(steps: dict[str, Any] | None) -> bool:
    if not steps:
        return False
    return steps.get("destino_apos_transcricao") == "notas_proposta_funcionalidade"
