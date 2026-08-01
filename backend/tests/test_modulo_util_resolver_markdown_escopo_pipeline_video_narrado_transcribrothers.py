"""Markdown de escopo parcial vs documento completo no vídeo narrado."""

from __future__ import annotations

from transcribrothers_backend.modulo_util_resolver_markdown_escopo_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS,
    resolver_markdown_para_pipeline_video_narrado_transcribrothers,
)


def test_usa_escopo_quando_presente_em_steps() -> None:
    md = resolver_markdown_para_pipeline_video_narrado_transcribrothers(
        result_markdown="# Completo\n\n## A\n\nx",
        steps={
            CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS: {
                "markdown": "## A\n\nx",
                "modo": "secoes",
            }
        },
    )
    assert md == "## A\n\nx"


def test_cai_no_result_markdown_sem_escopo() -> None:
    md = resolver_markdown_para_pipeline_video_narrado_transcribrothers(
        result_markdown="# Completo",
        steps={},
    )
    assert md == "# Completo"
