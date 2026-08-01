"""Parte texto plano em frases/blocos adequados a cues de legenda."""

from __future__ import annotations

import re

from transcribrothers_backend.modulo_util_filtrar_trechos_narraveis_para_tts_transcribrothers import (
    texto_e_narravel_para_tts_transcribrothers,
)

_RE_SENTENCA = re.compile(
    r"[^.!?…\n]+[.!?…]+(?:\s+|$)|[^.!?…\n]+(?:\n+|$)",
    re.UNICODE,
)


def partir_texto_plano_em_frases_para_legendas_transcribrothers(texto: str) -> list[str]:
    """Divide o texto em frases curtas para alinhamento e VTT (descarta lixo não narrável)."""
    bruto = (texto or "").strip()
    if not bruto:
        return []
    frases: list[str] = []
    for m in _RE_SENTENCA.finditer(bruto):
        trecho = re.sub(r"\s+", " ", m.group(0)).strip()
        if trecho:
            frases.append(trecho)
    if not frases and bruto:
        frases.append(re.sub(r"\s+", " ", bruto))
    # Evita cues enormes: quebra frases > 180 chars em pedaços por vírgula/espaço
    out: list[str] = []
    for f in frases:
        if len(f) <= 180:
            if texto_e_narravel_para_tts_transcribrothers(f):
                out.append(f)
            continue
        partes = re.split(r"(?<=[,;:])\s+", f)
        buf = ""
        for p in partes:
            candidato = f"{buf} {p}".strip() if buf else p
            if len(candidato) <= 180:
                buf = candidato
            else:
                if buf and texto_e_narravel_para_tts_transcribrothers(buf):
                    out.append(buf)
                buf = p
        if buf and texto_e_narravel_para_tts_transcribrothers(buf):
            out.append(buf)
    return out
