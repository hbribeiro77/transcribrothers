"""Converte Markdown do tutorial em texto plano adequado para narração TTS."""

from __future__ import annotations

import re

_RE_FENCE_CODIGO = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_RE_CODIGO_INLINE = re.compile(r"`([^`]+)`")
_RE_IMAGEM = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_RE_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_RE_LINK_TEMPORAL_SOLTO = re.compile(r"\?\s*t=\d+(?:\.\d+)?", re.IGNORECASE)
_RE_HEADING = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_RE_CITACAO = re.compile(r"^>\s?", re.MULTILINE)
_RE_LISTA = re.compile(r"^[\s]*[-*+]\s+", re.MULTILINE)
_RE_LISTA_NUM = re.compile(r"^[\s]*\d+\.\s+", re.MULTILINE)
_RE_NEGRITO_ITALICO = re.compile(r"(\*\*|__)(.*?)\1")
_RE_ITALICO = re.compile(r"(\*|_)(.*?)\1")
_RE_HTML = re.compile(r"<[^>]+>")
_RE_ESPACOS = re.compile(r"[ \t]+")
_RE_LINHAS_VAZIAS = re.compile(r"\n{3,}")


def extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(
    markdown: str | None,
) -> str:
    """Remove imagens, código, URLs e marcações; mantém o texto narrável."""
    if markdown is None:
        return ""
    t = str(markdown)
    if not t.strip():
        return ""

    t = _RE_FENCE_CODIGO.sub(" ", t)
    t = _RE_IMAGEM.sub(" ", t)
    t = _RE_LINK.sub(r"\1", t)
    t = _RE_LINK_TEMPORAL_SOLTO.sub(" ", t)
    t = _RE_CODIGO_INLINE.sub(r"\1", t)
    t = _RE_HTML.sub(" ", t)
    t = _RE_HEADING.sub("", t)
    t = _RE_CITACAO.sub("", t)
    t = _RE_LISTA.sub("", t)
    t = _RE_LISTA_NUM.sub("", t)
    t = _RE_NEGRITO_ITALICO.sub(r"\2", t)
    t = _RE_ITALICO.sub(r"\2", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    linhas = [_RE_ESPACOS.sub(" ", ln).strip() for ln in t.split("\n")]
    linhas = [ln for ln in linhas if ln]
    texto = "\n".join(linhas)
    texto = _RE_LINHAS_VAZIAS.sub("\n\n", texto).strip()
    return texto
