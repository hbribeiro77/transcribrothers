"""Converte linhas `-progress` do ffmpeg (`out_time*` ) em percentual 0–100."""

from __future__ import annotations

import re

_RE_OUT_TIME_US = re.compile(r"^out_time_us=(\d+)\s*$")
_RE_OUT_TIME_MS = re.compile(r"^out_time_ms=(\d+)\s*$")
_RE_OUT_TIME = re.compile(r"^out_time=(\d+):(\d+):(\d+(?:\.\d+)?)\s*$")


def percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
    linha: str,
    *,
    duracao_entrada_segundos: float,
) -> float | None:
    """
    Se a linha for out_time / out_time_us / out_time_ms, devolve percentual 0–100.
    Caso contrário, None.

    Nota: em algumas versões o ffmpeg emitia `out_time_ms` em microssegundos
    (nome enganoso); usamos heurística quando o valor em ms ultrapassa a duração.
    """
    dur = float(duracao_entrada_segundos)
    if dur <= 0:
        return None
    texto = (linha or "").strip()
    m = _RE_OUT_TIME.match(texto)
    if m:
        h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        out_s = h * 3600 + mi * 60 + s
    else:
        m_us = _RE_OUT_TIME_US.match(texto)
        if m_us:
            out_s = int(m_us.group(1)) / 1_000_000.0
        else:
            m_ms = _RE_OUT_TIME_MS.match(texto)
            if not m_ms:
                return None
            bruto = int(m_ms.group(1))
            como_ms = bruto / 1000.0
            # Legado: valor em «ms» na verdade era us (ex.: 5_000_000 ≈ 5s).
            out_s = como_ms if como_ms <= dur * 1.5 else bruto / 1_000_000.0
    pct = (out_s / dur) * 100.0
    return round(min(100.0, max(0.0, pct)), 1)
