"""Normalização das vozes Gemini TTS (2.5)."""

from __future__ import annotations

import pytest

from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
    listar_vozes_tts_gemini_disponiveis_transcribrothers,
    montar_preferencias_voz_tts_narracao_transcribrothers,
    normalizar_voz_tts_gemini_transcribrothers,
)


def test_lista_tem_30_vozes_incluindo_kore() -> None:
    lista = listar_vozes_tts_gemini_disponiveis_transcribrothers()
    assert len(lista) == 30
    ids = {v["id"] for v in lista}
    assert "Kore" in ids
    assert "Aoede" in ids
    assert "Charon" in ids


def test_normaliza_case_insensitive() -> None:
    assert normalizar_voz_tts_gemini_transcribrothers("aoede") == "Aoede"
    assert normalizar_voz_tts_gemini_transcribrothers("") == VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS


def test_rejeita_voz_desconhecida() -> None:
    with pytest.raises(ValueError, match="não é uma das"):
        montar_preferencias_voz_tts_narracao_transcribrothers(voz="Siri")
