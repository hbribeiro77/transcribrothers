"""Segunda chamada ao modelo se ele marcou aplicar e não mandou tools."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    parsear_estado_resposta_modelo_chat_agente_transcribrothers,
    parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers,
    parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers,
    parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers,
    resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers,
)

MENSAGEM_RETRY_AGENTE_APLICANDO_SEM_FERRAMENTAS_TRANSCRIBROTHERS = (
    "Você escolheu aplicar neste turno e não preencheu tools. "
    "Devolva o JSON com estado=aplicando e ferramentas (ou tool_calls) agora. "
    "Se o documento precisa ficar independente do vídeo (tirar timestamps, legendas nas imagens), "
    "use sem_video. Para um bullet ou um parágrafo novo, edicao_parcial. "
    "Não adie para outro turno. Se não for alterar o documento, use estado=rascunho e ferramentas=[]."
)

_ChamarModelo = Callable[..., Awaitable[tuple[str, list[dict[str, Any]]]]]


def _quantidade_ferramentas_do_bruto_e_tool_calls_transcribrothers(
    bruto: str,
    tool_calls: list[dict[str, Any]] | None,
) -> int:
    json_tools = parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers(bruto)
    nativas = parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers(tool_calls)
    return max(len(json_tools), len(nativas))


async def obter_bruto_chat_agente_repetindo_se_aplicando_sem_ferramentas_transcribrothers(
    *,
    chamar_modelo: _ChamarModelo,
    mensagens: list[dict[str, str]],
) -> tuple[str, list[dict[str, Any]]]:
    bruto, tool_calls = await chamar_modelo(mensagens=mensagens)
    tool_calls = list(tool_calls or [])
    precisa = resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
        estado=parsear_estado_resposta_modelo_chat_agente_transcribrothers(bruto),
        quantidade_ferramentas=_quantidade_ferramentas_do_bruto_e_tool_calls_transcribrothers(
            bruto, tool_calls
        ),
        flag_executar=parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto),
    )
    if not precisa:
        return bruto, tool_calls
    mensagens_retry = list(mensagens)
    mensagens_retry.append({"role": "assistant", "content": bruto})
    mensagens_retry.append(
        {
            "role": "user",
            "content": MENSAGEM_RETRY_AGENTE_APLICANDO_SEM_FERRAMENTAS_TRANSCRIBROTHERS,
        }
    )
    return await chamar_modelo(mensagens=mensagens_retry)
