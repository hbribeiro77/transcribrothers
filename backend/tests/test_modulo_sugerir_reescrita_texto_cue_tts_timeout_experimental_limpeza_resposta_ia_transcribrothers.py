"""Limpeza da sugestão de reescrita IA para cue com timeout TTS experimental."""

from __future__ import annotations

from transcribrothers_backend.modulo_sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers import (
    limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers,
)


def test_limpar_sugestao_texto_simples() -> None:
    assert (
        limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers(
            "  Olá, este é o texto reescrito.  "
        )
        == "Olá, este é o texto reescrito."
    )


def test_limpar_sugestao_remove_cerca_markdown() -> None:
    bruto = "```text\nNarração clara e objetiva.\n```"
    assert (
        limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers(bruto)
        == "Narração clara e objetiva."
    )


def test_limpar_sugestao_prefacia_usa_ultima_linha() -> None:
    bruto = "Aqui vai a sugestão:\nSugestão: texto final falável"
    assert (
        limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers(bruto)
        == "texto final falável"
    )


def test_limpar_sugestao_vazia() -> None:
    assert limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers("") == ""
    assert limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers("   ") == ""
