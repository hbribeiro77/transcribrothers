"""Vozes prebuilt do Gemini TTS (2.5 Flash/Pro) e normalização da preferência."""

from __future__ import annotations

from dataclasses import dataclass

# Doc: https://ai.google.dev/gemini-api/docs/speech-generation — 30 vozes.
# Estilos em pt-BR para a UI (tradução livre dos rótulos da doc).
VOZES_TTS_GEMINI_COM_ESTILO_TRANSCRIBROTHERS: tuple[tuple[str, str], ...] = (
    ("Zephyr", "Brilhante"),
    ("Puck", "Animada"),
    ("Charon", "Informativa"),
    ("Kore", "Firme"),
    ("Fenrir", "Excitável"),
    ("Leda", "Jovem"),
    ("Orus", "Firme"),
    ("Aoede", "Leve / breezy"),
    ("Callirrhoe", "Descontraída"),
    ("Autonoe", "Brilhante"),
    ("Enceladus", "Sussurrada"),
    ("Iapetus", "Clara"),
    ("Umbriel", "Descontraída"),
    ("Algieba", "Suave"),
    ("Despina", "Suave"),
    ("Erinome", "Clara"),
    ("Algenib", "Raspada"),
    ("Rasalgethi", "Informativa"),
    ("Laomedeia", "Animada"),
    ("Achernar", "Suave"),
    ("Alnilam", "Firme"),
    ("Schedar", "Equilibrada"),
    ("Gacrux", "Madura"),
    ("Pulcherrima", "Direta"),
    ("Achird", "Amigável"),
    ("Zubenelgenubi", "Casual"),
    ("Vindemiatrix", "Gentil"),
    ("Sadachbia", "Viva"),
    ("Sadaltager", "Conhecedora"),
    ("Sulafat", "Calorosa"),
)

VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS = "Kore"

_IDS_VOZES = frozenset(v for v, _ in VOZES_TTS_GEMINI_COM_ESTILO_TRANSCRIBROTHERS)


@dataclass(frozen=True)
class PreferenciasVozTtsNarracaoTranscribrothers:
    voz: str


def preferencias_voz_tts_narracao_padrao_transcribrothers() -> PreferenciasVozTtsNarracaoTranscribrothers:
    return PreferenciasVozTtsNarracaoTranscribrothers(voz=VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS)


def listar_vozes_tts_gemini_disponiveis_transcribrothers() -> list[dict[str, str]]:
    return [{"id": vid, "estilo": estilo} for vid, estilo in VOZES_TTS_GEMINI_COM_ESTILO_TRANSCRIBROTHERS]


def normalizar_voz_tts_gemini_transcribrothers(valor: object) -> str:
    texto = str(valor or "").strip()
    if not texto:
        return VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    # Match case-insensitive ao id oficial.
    for vid in _IDS_VOZES:
        if vid.lower() == texto.lower():
            return vid
    raise ValueError(
        f"Voz TTS «{texto}» não é uma das {len(_IDS_VOZES)} vozes prebuilt do Gemini. "
        f"Exemplos: Kore, Aoede, Charon, Puck."
    )


def montar_preferencias_voz_tts_narracao_transcribrothers(
    *,
    voz: object,
) -> PreferenciasVozTtsNarracaoTranscribrothers:
    return PreferenciasVozTtsNarracaoTranscribrothers(
        voz=normalizar_voz_tts_gemini_transcribrothers(voz),
    )
