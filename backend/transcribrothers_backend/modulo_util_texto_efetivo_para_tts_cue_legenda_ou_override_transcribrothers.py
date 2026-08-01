"""Texto enviado ao TTS: override de pronúncia ou, se vazio, a legenda."""

from __future__ import annotations


def texto_efetivo_para_tts_cue_narracao_transcribrothers(
    *,
    texto_legenda: str,
    texto_tts: str = "",
) -> str:
    """
    Retorna o texto que a narração deve falar.

    - Se ``texto_tts`` tiver conteúdo (após trim), usa só ele (pronúncia ajustada).
    - Caso contrário, usa ``texto_legenda`` (comportamento padrão).
    """
    override = " ".join((texto_tts or "").replace("\r\n", "\n").replace("\r", "\n").split())
    if override:
        return override
    return " ".join((texto_legenda or "").replace("\r\n", "\n").replace("\r", "\n").split())
