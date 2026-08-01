"""Parser WebVTT → lista de cues (tempo + texto) para o pipeline de narração."""

from __future__ import annotations

import re
from dataclasses import dataclass

_RE_TEMPO_SETA = re.compile(
    r"^(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3}|\d{1,2}:\d{2}[.,]\d{1,3})\s*-->\s*"
    r"(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3}|\d{1,2}:\d{2}[.,]\d{1,3})"
)


@dataclass(frozen=True)
class CueTextoWebVttPipelineNarracaoTranscribrothers:
    inicio_segundos: float
    fim_segundos: float
    texto: str


def _parsear_timestamp_webvtt_para_segundos_transcribrothers(bruto: str) -> float | None:
    s = (bruto or "").strip().replace(",", ".")
    partes = s.split(":")
    if len(partes) < 2 or len(partes) > 3:
        return None
    try:
        if len(partes) == 3:
            horas = float(partes[0])
            minutos = float(partes[1])
            segundos = float(partes[2])
        else:
            horas = 0.0
            minutos = float(partes[0])
            segundos = float(partes[1])
    except ValueError:
        return None
    return horas * 3600.0 + minutos * 60.0 + segundos


def parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers(
    conteudo_vtt: str,
) -> list[CueTextoWebVttPipelineNarracaoTranscribrothers]:
    texto = (conteudo_vtt or "").replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    if not texto.strip():
        return []
    cues: list[CueTextoWebVttPipelineNarracaoTranscribrothers] = []
    for bloco_bruto in texto.split("\n\n"):
        linhas = [ln.rstrip() for ln in bloco_bruto.split("\n") if ln.strip()]
        if not linhas:
            continue
        primeira = linhas[0].strip()
        if re.match(r"^WEBVTT\b", primeira, flags=re.IGNORECASE):
            continue
        if re.match(r"^(NOTE|STYLE|REGION)\b", primeira, flags=re.IGNORECASE):
            continue
        idx_seta = next((i for i, ln in enumerate(linhas) if "-->" in ln), -1)
        if idx_seta < 0:
            continue
        m = _RE_TEMPO_SETA.match(linhas[idx_seta].strip())
        if not m:
            continue
        inicio = _parsear_timestamp_webvtt_para_segundos_transcribrothers(m.group(1))
        fim = _parsear_timestamp_webvtt_para_segundos_transcribrothers(m.group(2))
        if inicio is None or fim is None:
            continue
        corpo = "\n".join(linhas[idx_seta + 1 :])
        corpo = re.sub(r"</?[^>]+>", "", corpo).strip()
        corpo = " ".join(corpo.split())
        if not corpo:
            continue
        cues.append(
            CueTextoWebVttPipelineNarracaoTranscribrothers(
                inicio_segundos=inicio,
                fim_segundos=max(inicio, fim),
                texto=corpo,
            )
        )
    return cues
