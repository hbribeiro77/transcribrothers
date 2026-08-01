"""Resolve qual Markdown usar no pipeline de vídeo narrado (documento ou escopo parcial)."""

from __future__ import annotations

from typing import Any

CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_markdown_escopo"
)


def resolver_markdown_para_pipeline_video_narrado_transcribrothers(
    *,
    result_markdown: str,
    steps: dict[str, Any] | None,
) -> str:
    """
    Preferência: texto em steps (escopo parcial enviado no agendamento).
    Senão: Markdown completo do job.
    """
    if isinstance(steps, dict):
        bruto = steps.get(CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS)
        if isinstance(bruto, dict):
            texto = bruto.get("markdown")
            if isinstance(texto, str) and texto.strip():
                return texto.strip()
        elif isinstance(bruto, str) and bruto.strip():
            return bruto.strip()
    return (result_markdown or "").strip()
