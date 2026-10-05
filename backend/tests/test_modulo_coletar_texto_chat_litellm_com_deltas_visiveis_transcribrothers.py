import asyncio

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_em_stream_transcribrothers import (
    extrair_delta_content_de_linha_sse_chat_completions_transcribrothers,
)
from transcribrothers_backend.modulo_coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers import (
    coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers,
    montar_linha_sse_evento_json_chat_ask_agente_transcribrothers,
)


def test_emite_deltas_so_quando_o_texto_visivel_cresce() -> None:
    visto: list[str] = []

    async def emitir(texto: str) -> None:
        visto.append(texto)

    async def pedacos():
        for parte in ('{"tex', 'to":"Olá ', '**mundo**."}'):
            yield parte

    async def rodar() -> str:
        return await coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers(
            pedacos(),
            emitir_delta_texto=emitir,
        )

    bruto = asyncio.run(rodar())
    assert bruto == '{"texto":"Olá **mundo**."}'
    assert visto == ["Olá ", "Olá **mundo**."]


def test_monta_linha_sse_com_data_json() -> None:
    linha = montar_linha_sse_evento_json_chat_ask_agente_transcribrothers(
        {"tipo": "delta", "texto": "Oi"}
    )
    assert linha == 'data: {"tipo": "delta", "texto": "Oi"}\n\n'


def test_extrai_delta_content_de_linha_sse_openai() -> None:
    assert (
        extrair_delta_content_de_linha_sse_chat_completions_transcribrothers(
            'data: {"choices":[{"delta":{"content":"Olá"}}]}'
        )
        == "Olá"
    )
    assert extrair_delta_content_de_linha_sse_chat_completions_transcribrothers("data: [DONE]") == ""


def test_coleta_sem_callback_ainda_acumula() -> None:
    async def pedacos():
        yield '{"texto":"ok"}'

    bruto = asyncio.run(coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers(pedacos()))
    assert bruto == '{"texto":"ok"}'
