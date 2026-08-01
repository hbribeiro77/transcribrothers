"""Filtra trechos sem conteúdo falável (ex.: «).», «…», «1).») antes do TTS."""

from __future__ import annotations

import re
import unicodedata

_RE_LETRAS = re.compile(r"[^\W\d_]", re.UNICODE)
_MINIMO_LETRAS_NARRAVEIS = 3


def contar_letras_unicode_transcribrothers(texto: str) -> int:
    return len(_RE_LETRAS.findall(texto or ""))


def texto_e_narravel_para_tts_transcribrothers(
    texto: str | None,
    *,
    minimo_letras: int = _MINIMO_LETRAS_NARRAVEIS,
) -> bool:
    """
    True se o trecho tem letras suficientes para o modelo TTS.
    Rejeita pontuação solta, números+pontos (ex.: «2).») e só símbolos.
    """
    t = (texto or "").strip()
    if not t:
        return False
    # Normaliza espaços; ignora categorias de pontuação/símbolos ao contar letras.
    t_norm = unicodedata.normalize("NFKC", t)
    return contar_letras_unicode_transcribrothers(t_norm) >= max(1, int(minimo_letras))


def filtrar_trechos_narraveis_para_tts_transcribrothers(
    trechos: list[str],
    *,
    minimo_letras: int = _MINIMO_LETRAS_NARRAVEIS,
) -> tuple[list[str], list[str]]:
    """Devolve (narráveis, descartados)."""
    ok: list[str] = []
    descartados: list[str] = []
    for bruto in trechos:
        t = (bruto or "").strip()
        if not t:
            continue
        if texto_e_narravel_para_tts_transcribrothers(t, minimo_letras=minimo_letras):
            ok.append(t)
        else:
            descartados.append(t)
    return ok, descartados


def preview_trecho_tts_para_progresso_ui_transcribrothers(
    texto: str,
    *,
    max_chars: int = 72,
) -> str:
    p = re.sub(r"\s+", " ", (texto or "").strip())
    if len(p) > max_chars:
        return p[: max_chars - 1] + "…"
    return p
