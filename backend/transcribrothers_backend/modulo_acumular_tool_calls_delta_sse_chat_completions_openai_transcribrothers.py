"""Acumula delta.tool_calls do SSE OpenAI/LiteLLM (argumentos em pedaços)."""

from __future__ import annotations

import json
from typing import Any


def extrair_delta_tool_calls_de_linha_sse_chat_completions_transcribrothers(
    linha: str,
) -> list[dict[str, Any]]:
    cortada = (linha or "").strip()
    if not cortada.startswith("data:"):
        return []
    payload = cortada[5:].strip()
    if not payload or payload == "[DONE]":
        return []
    try:
        data = json.loads(payload)
        choice = data["choices"][0]
        delta = choice.get("delta") if isinstance(choice, dict) else None
        if not isinstance(delta, dict):
            return []
        bruto = delta.get("tool_calls")
        if not isinstance(bruto, list):
            return []
        return [item for item in bruto if isinstance(item, dict)]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return []


def acumular_tool_calls_delta_sse_chat_completions_openai_transcribrothers(
    acumulado: dict[int, dict[str, Any]],
    deltas: list[dict[str, Any]] | None,
) -> None:
    for item in deltas or []:
        try:
            indice = int(item.get("index", 0))
        except (TypeError, ValueError):
            continue
        atual = acumulado.setdefault(
            indice,
            {"type": "function", "function": {"name": "", "arguments": ""}},
        )
        if item.get("id"):
            atual["id"] = item["id"]
        if item.get("type"):
            atual["type"] = item["type"]
        funcao_delta = item.get("function")
        if not isinstance(funcao_delta, dict):
            continue
        funcao = atual.setdefault("function", {"name": "", "arguments": ""})
        nome = funcao_delta.get("name")
        if isinstance(nome, str) and nome:
            funcao["name"] = nome
        argumentos = funcao_delta.get("arguments")
        if isinstance(argumentos, str) and argumentos:
            funcao["arguments"] = (funcao.get("arguments") or "") + argumentos
