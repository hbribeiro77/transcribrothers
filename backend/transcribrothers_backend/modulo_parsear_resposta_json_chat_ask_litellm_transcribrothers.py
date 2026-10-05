"""Parse da resposta JSON do modelo no chat Ask (texto, citações, instantes de imagem)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    extrair_primeiro_objeto_json_de_texto_llm_transcribrothers,
)

_TIPOS_CITACAO_VALIDOS = frozenset({"transcricao", "markdown"})


@dataclass(frozen=True)
class CitacaoChatAskTranscribrothers:
    tipo: str
    rotulo: str
    instante_segundos: float | None
    heading: str | None


@dataclass(frozen=True)
class RespostaModeloChatAskTranscribrothers:
    texto: str
    citacoes: list[CitacaoChatAskTranscribrothers]
    instantes_imagem_segundos: list[float]


def _fallback_resposta_texto_bruto(texto_bruto: str) -> RespostaModeloChatAskTranscribrothers:
    return RespostaModeloChatAskTranscribrothers(
        texto=(texto_bruto or "").strip(),
        citacoes=[],
        instantes_imagem_segundos=[],
    )


def _instante_numerico_valido(valor: object) -> float | None:
    if not isinstance(valor, (int, float)):
        return None
    if isinstance(valor, bool):
        return None
    f = float(valor)
    if not math.isfinite(f) or f < 0:
        return None
    return f


def _parsear_citacao(item: object) -> CitacaoChatAskTranscribrothers | None:
    if not isinstance(item, dict):
        return None
    tipo_raw = item.get("tipo")
    tipo = str(tipo_raw).strip() if tipo_raw is not None else ""
    if tipo not in _TIPOS_CITACAO_VALIDOS:
        tipo = "markdown"
    rotulo_raw = item.get("rotulo")
    rotulo = str(rotulo_raw).strip() if rotulo_raw is not None else ""
    instante: float | None = None
    if "instante_segundos" in item:
        instante = _instante_numerico_valido(item.get("instante_segundos"))
    heading_raw = item.get("heading")
    heading: str | None
    if heading_raw is None:
        heading = None
    else:
        s = str(heading_raw).strip()
        heading = s or None
    return CitacaoChatAskTranscribrothers(
        tipo=tipo,
        rotulo=rotulo,
        instante_segundos=instante,
        heading=heading,
    )


def _parsear_instantes_imagem(valor: object) -> list[float]:
    if not isinstance(valor, list):
        return []
    out: list[float] = []
    for el in valor:
        n = _instante_numerico_valido(el)
        if n is not None:
            out.append(n)
    return out


def parsear_resposta_json_chat_ask_litellm_transcribrothers(
    texto_bruto: str,
) -> RespostaModeloChatAskTranscribrothers:
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data: Any = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError):
        return _fallback_resposta_texto_bruto(texto_bruto)
    if not isinstance(data, dict):
        return _fallback_resposta_texto_bruto(texto_bruto)

    texto_raw = data.get("texto")
    texto = str(texto_raw) if texto_raw is not None else ""

    citacoes: list[CitacaoChatAskTranscribrothers] = []
    raw_citacoes = data.get("citacoes")
    if isinstance(raw_citacoes, list):
        for item in raw_citacoes:
            cit = _parsear_citacao(item)
            if cit is not None:
                citacoes.append(cit)

    instantes = _parsear_instantes_imagem(data.get("instantes_imagem_segundos"))

    return RespostaModeloChatAskTranscribrothers(
        texto=texto,
        citacoes=citacoes,
        instantes_imagem_segundos=instantes,
    )
