"""Voz efetiva por cue: Gemini conhecido ou identificador de outro provedor (ElevenLabs)."""

from __future__ import annotations

from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
    normalizar_voz_tts_gemini_transcribrothers,
)


def normalizar_voz_tts_efetiva_para_cue_transcribrothers(voz: str, voz_padrao: str) -> str:
    """Mantém voice_id da ElevenLabs; só normaliza nomes Gemini."""
    candidata = (voz or "").strip() or (voz_padrao or "").strip()
    if not candidata:
        return VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    try:
        return normalizar_voz_tts_gemini_transcribrothers(candidata)
    except ValueError:
        return candidata
