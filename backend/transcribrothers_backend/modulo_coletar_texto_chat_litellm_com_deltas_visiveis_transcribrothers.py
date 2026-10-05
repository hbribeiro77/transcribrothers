"""Acumula o stream do chat e emite só o campo `texto` visível."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from transcribrothers_backend.modulo_extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers import (
    extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers,
)


def montar_linha_sse_evento_json_chat_ask_agente_transcribrothers(evento: dict[str, Any]) -> str:
    return f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"


async def coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers(
    pedacos: AsyncIterator[str],
    emitir_delta_texto: Callable[[str], Awaitable[None]] | None = None,
) -> str:
    acumulado = ""
    visivel_anterior = ""
    async for pedaco in pedacos:
        if not pedaco:
            continue
        acumulado += pedaco
        visivel = extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers(acumulado)
        if emitir_delta_texto is not None and visivel and visivel != visivel_anterior:
            await emitir_delta_texto(visivel)
            visivel_anterior = visivel
    return acumulado
