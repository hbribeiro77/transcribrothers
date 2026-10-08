import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from transcribrothers_backend.modulo_acumular_tool_calls_delta_sse_chat_completions_openai_transcribrothers import (
    acumular_tool_calls_delta_sse_chat_completions_openai_transcribrothers,
    extrair_delta_tool_calls_de_linha_sse_chat_completions_transcribrothers,
)
from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
    decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers,
    mesclar_ferramentas_json_e_tool_calls_openai_chat_agente_transcribrothers,
    parsear_estado_resposta_modelo_chat_agente_transcribrothers,
    parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers,
    resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers,
)
from transcribrothers_backend.modulo_incluir_plano_ask_no_contexto_turno_chat_agente_transcribrothers import (
    texto_plano_ask_para_contexto_agente_transcribrothers,
)
from transcribrothers_backend.modulo_retry_resposta_chat_agente_aplicando_sem_ferramentas_transcribrothers import (
    MENSAGEM_RETRY_AGENTE_APLICANDO_SEM_FERRAMENTAS_TRANSCRIBROTHERS,
    obter_bruto_chat_agente_repetindo_se_aplicando_sem_ferramentas_transcribrothers,
)
from transcribrothers_backend.modulo_schema_tools_openai_chat_agente_documento_job_transcribrothers import (
    schema_tools_openai_chat_agente_documento_job_transcribrothers,
)


def test_parseia_estado_aplicando_e_rascunho() -> None:
    assert (
        parsear_estado_resposta_modelo_chat_agente_transcribrothers(
            '{"texto":"ok","estado":"aplicando","ferramentas":[]}'
        )
        == "aplicando"
    )
    assert (
        parsear_estado_resposta_modelo_chat_agente_transcribrothers(
            '{"texto":"sugiro","estado":"rascunho","ferramentas":[]}'
        )
        == "rascunho"
    )
    assert (
        parsear_estado_resposta_modelo_chat_agente_transcribrothers('{"texto":"ok","ferramentas":[]}')
        is None
    )


def test_retry_so_quando_modelo_escolhe_aplicar_sem_tool() -> None:
    assert (
        resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
            estado="aplicando",
            quantidade_ferramentas=0,
            flag_executar=None,
        )
        is True
    )
    assert (
        resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
            estado="aplicando",
            quantidade_ferramentas=1,
            flag_executar=True,
        )
        is False
    )
    assert (
        resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
            estado="rascunho",
            quantidade_ferramentas=0,
            flag_executar=None,
        )
        is False
    )
    assert (
        resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
            estado=None,
            quantidade_ferramentas=0,
            flag_executar=True,
        )
        is True
    )
    assert (
        resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
            estado=None,
            quantidade_ferramentas=0,
            flag_executar=None,
        )
        is True
    )


def test_retry_chama_modelo_quando_estado_vem_omitido_sem_ferramenta() -> None:
    primeira = '{"texto":"Finalizando agora: removendo os timestamps.","ferramentas":[]}'
    segunda = (
        '{"texto":"Apliquei.","estado":"aplicando","ferramentas":['
        '{"nome":"sem_video","instrucoes":"Tire timestamps e ponha legendas."}]}'
    )
    chamar = AsyncMock(side_effect=[(primeira, []), (segunda, [])])

    async def rodar() -> tuple[str, list]:
        return await obter_bruto_chat_agente_repetindo_se_aplicando_sem_ferramentas_transcribrothers(
            chamar_modelo=chamar,
            mensagens=[{"role": "user", "content": "sim, continua até terminar"}],
        )

    bruto, _tool_calls = asyncio.run(rodar())
    assert chamar.await_count == 2
    assert "sem_video" in bruto


def test_estado_rascunho_nao_executa_mesmo_com_ferramentas() -> None:
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=None,
            quantidade_propostas=1,
            estado="rascunho",
        )
        is False
    )
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=None,
            quantidade_propostas=2,
            estado="aplicando",
        )
        is True
    )


def test_parseia_tool_calls_nativos_openai_como_edicao_parcial() -> None:
    ferramentas = parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers(
        [
            {
                "type": "function",
                "function": {
                    "name": "edicao_parcial",
                    "arguments": (
                        '{"titulo_secao_heading":"1. Visão Geral e Triagem Manual",'
                        '"instrucoes":"Tire os timestamps e acrescente legendas."}'
                    ),
                },
            }
        ]
    )
    assert len(ferramentas) == 1
    assert ferramentas[0]["nome"] == NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    assert ferramentas[0]["titulo_secao_heading"] == "1. Visão Geral e Triagem Manual"
    assert "legendas" in (ferramentas[0]["instrucoes"] or "")


def test_mescla_tool_calls_quando_json_vem_sem_ferramentas() -> None:
    nativas = parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers(
        [
            {
                "function": {
                    "name": "edicao_parcial",
                    "arguments": '{"titulo_secao_heading":"Introdução","instrucoes":"Encurte."}',
                }
            }
        ]
    )
    mescladas = mesclar_ferramentas_json_e_tool_calls_openai_chat_agente_transcribrothers(
        ferramentas_json=[],
        ferramentas_tool_calls=nativas,
    )
    assert len(mescladas) == 1
    assert mescladas[0]["titulo_secao_heading"] == "Introdução"


def test_schema_tools_openai_tem_as_tres_ferramentas_do_agente() -> None:
    nomes = [item["function"]["name"] for item in schema_tools_openai_chat_agente_documento_job_transcribrothers()]
    assert nomes == ["edicao_parcial", "revisao_profunda", "sem_video"]


def test_acumula_argumentos_de_tool_call_em_deltas_sse() -> None:
    linhas = [
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"c1","type":"function","function":{"name":"edicao_parcial","arguments":""}}]}}]}',
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\\"titulo_secao_heading\\":\\"Visão Geral\\","}}]}}]}',
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"\\"instrucoes\\":\\"inclua.\\"}"}}]}}]}',
        "data: [DONE]",
    ]
    acumulado: dict[int, dict] = {}
    for linha in linhas:
        delta = extrair_delta_tool_calls_de_linha_sse_chat_completions_transcribrothers(linha)
        acumular_tool_calls_delta_sse_chat_completions_openai_transcribrothers(acumulado, delta)
    ferramentas = parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers(
        list(acumulado.values())
    )
    assert ferramentas[0]["titulo_secao_heading"] == "Visão Geral"
    assert ferramentas[0]["instrucoes"] == "inclua."


def test_retry_chama_modelo_de_novo_quando_primeira_resposta_aplica_sem_tool() -> None:
    primeira = '{"texto":"Aplicando agora.","estado":"aplicando","ferramentas":[]}'
    segunda = (
        '{"texto":"Apliquei na seção 1.","estado":"aplicando","ferramentas":['
        '{"nome":"edicao_parcial","titulo_secao_heading":"1. Visão Geral e Triagem Manual",'
        '"instrucoes":"Remova timestamps e acrescente legendas."}]}'
    )
    chamar = AsyncMock(side_effect=[(primeira, []), (segunda, [])])
    mensagens = [{"role": "user", "content": "pode fazer"}]

    async def rodar() -> tuple[str, list]:
        return await obter_bruto_chat_agente_repetindo_se_aplicando_sem_ferramentas_transcribrothers(
            chamar_modelo=chamar,
            mensagens=mensagens,
        )

    bruto, tool_calls = asyncio.run(rodar())
    assert chamar.await_count == 2
    assert "1. Visão Geral e Triagem Manual" in bruto
    segunda_mensagens = chamar.await_args_list[1].kwargs["mensagens"]
    assert segunda_mensagens[-1]["role"] == "user"
    assert segunda_mensagens[-1]["content"] == MENSAGEM_RETRY_AGENTE_APLICANDO_SEM_FERRAMENTAS_TRANSCRIBROTHERS
    assert tool_calls == []


def test_retry_nao_repete_quando_ja_veio_com_ferramenta() -> None:
    bruto_ok = (
        '{"texto":"Aplicando.","estado":"aplicando","ferramentas":['
        '{"nome":"edicao_parcial","titulo_secao_heading":"Intro","instrucoes":"x"}]}'
    )
    chamar = AsyncMock(return_value=(bruto_ok, []))

    async def rodar() -> tuple[str, list]:
        return await obter_bruto_chat_agente_repetindo_se_aplicando_sem_ferramentas_transcribrothers(
            chamar_modelo=chamar,
            mensagens=[{"role": "user", "content": "aplica"}],
        )

    asyncio.run(rodar())
    assert chamar.await_count == 1


def test_plano_ask_entra_no_contexto_quando_ultimo_rascunho_nao_tem_tool() -> None:
    historico = [
        SimpleNamespace(
            papel="assistente",
            modo="ask",
            texto="Sugestão: tirar timestamps e pôr legendas em cada imagem.",
            proposta_ferramenta=None,
            propostas_ferramenta=None,
        )
    ]
    plano = texto_plano_ask_para_contexto_agente_transcribrothers(historico)
    assert plano is not None
    assert "timestamps" in plano
    assert "legendas" in plano


def test_plano_ask_ignora_turnos_do_agente_e_pega_o_ask_anterior() -> None:
    historico = [
        SimpleNamespace(
            papel="assistente",
            modo="ask",
            texto="Sugestão: tirar timestamps.",
            proposta_ferramenta=None,
            propostas_ferramenta=None,
        ),
        SimpleNamespace(
            papel="agente",
            modo="agente",
            texto="Beleza, aplicando agora.",
            proposta_ferramenta=None,
            propostas_ferramenta=None,
        ),
    ]
    plano = texto_plano_ask_para_contexto_agente_transcribrothers(historico)
    assert plano == "Sugestão: tirar timestamps."
