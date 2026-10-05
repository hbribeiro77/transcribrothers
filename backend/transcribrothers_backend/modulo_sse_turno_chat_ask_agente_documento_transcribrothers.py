"""Gera linhas SSE de um turno de chat (deltas + evento final ou erro)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from transcribrothers_backend.modulo_coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers import (
    montar_linha_sse_evento_json_chat_ask_agente_transcribrothers,
)
from transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers import (
    ChatAskSemFonteError,
)


async def iterar_linhas_sse_turno_chat_ask_agente_transcribrothers(
    rodar_turno: Callable[[Callable[[str], Awaitable[None]]], Awaitable[dict[str, Any]]],
) -> AsyncIterator[str]:
    fila: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

    async def emitir(texto: str) -> None:
        await fila.put({"tipo": "delta", "texto": texto})

    async def rodar() -> None:
        try:
            final = await rodar_turno(emitir)
            evento = {"tipo": "final"}
            evento.update(final)
            await fila.put(evento)
        except ChatAskSemFonteError as exc:
            await fila.put({"tipo": "erro", "status": 409, "mensagem": str(exc)})
        except Exception as exc:
            await fila.put({"tipo": "erro", "status": 502, "mensagem": str(exc)})
        finally:
            await fila.put(None)

    tarefa = asyncio.create_task(rodar())
    try:
        while True:
            evento = await fila.get()
            if evento is None:
                break
            yield montar_linha_sse_evento_json_chat_ask_agente_transcribrothers(evento)
    finally:
        await tarefa
