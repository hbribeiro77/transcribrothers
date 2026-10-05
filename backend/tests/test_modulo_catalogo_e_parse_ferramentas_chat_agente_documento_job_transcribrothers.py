from types import SimpleNamespace

from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
    NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS,
    anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers,
    decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers,
    escolher_proposta_ferramenta_chat_agente_transcribrothers,
    limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers,
    parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers,
    parsear_ferramentas_resposta_modelo_chat_agente_transcribrothers,
    parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers,
)


def test_parseia_edicao_parcial_e_ignora_nome_desconhecido() -> None:
    ferramentas = parsear_ferramentas_resposta_modelo_chat_agente_transcribrothers(
        [
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Visão Geral",
                "instrucoes": "Inclua o parágrafo do chat e o frame.",
            },
            {"nome": "explodir_servidor"},
        ]
    )
    assert len(ferramentas) == 1
    assert ferramentas[0]["nome"] == NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    assert ferramentas[0]["titulo_secao_heading"] == "Visão Geral"
    assert "chat" in ferramentas[0]["instrucoes"]


def test_forcar_ferramenta_injeta_proposta_quando_modelo_omite() -> None:
    proposta = escolher_proposta_ferramenta_chat_agente_transcribrothers(
        ferramentas=[],
        forcar_ferramenta=NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS,
        mensagem_usuario="quero aprofundar o tom",
    )
    assert proposta is not None
    assert proposta["nome"] == NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS
    assert proposta["instrucoes"] == "quero aprofundar o tom"


def test_proposta_do_modelo_prevalece_sobre_forcar_se_o_nome_bate() -> None:
    proposta = escolher_proposta_ferramenta_chat_agente_transcribrothers(
        ferramentas=[
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Introdução",
                "instrucoes": "Deixe a intro mais curta.",
            }
        ],
        forcar_ferramenta="edicao_parcial",
        mensagem_usuario="encurta a intro",
    )
    assert proposta is not None
    assert proposta["titulo_secao_heading"] == "Introdução"
    assert proposta["instrucoes"] == "Deixe a intro mais curta."
    assert proposta["caminhos_imagens"] == []


def test_parseia_e_anexa_caminhos_imagens_na_edicao_parcial() -> None:
    ferramentas = parsear_ferramentas_resposta_modelo_chat_agente_transcribrothers(
        [
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "O que foi discutido",
                "instrucoes": "Aprofunde Assistido Digital.",
                "caminhos_imagens": ["assets/tela_chat_758.png", "assets/tela_chat_758.png"],
            }
        ]
    )
    assert ferramentas[0]["caminhos_imagens"] == ["assets/tela_chat_758.png"]
    proposta = escolher_proposta_ferramenta_chat_agente_transcribrothers(
        ferramentas=ferramentas,
        forcar_ferramenta=None,
        mensagem_usuario="aprofunda",
    )
    assert proposta is not None
    mesclada = anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers(
        proposta,
        ["assets/outra_tela.png"],
        ["assets/tela_chat_758.png"],
    )
    assert mesclada is not None
    assert mesclada["caminhos_imagens"] == [
        "assets/tela_chat_758.png",
        "assets/outra_tela.png",
    ]


def test_flag_executar_true_com_ferramentas_dispara_apply() -> None:
    bruto = (
        '{"texto":"Aplicando.","citacoes":[],"instantes_imagem_segundos":[],'
        '"executar":true,"ferramentas":[{"nome":"edicao_parcial",'
        '"titulo_secao_heading":"Visão Geral","instrucoes":"inclua"}]}'
    )
    assert parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto) is True
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=True,
            quantidade_propostas=1,
        )
        is True
    )


def test_flag_executar_false_nao_dispara_mesmo_com_ferramentas() -> None:
    bruto = '{"texto":"Só sugiro.","executar":false,"ferramentas":[{"nome":"edicao_parcial"}]}'
    assert parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto) is False
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=False,
            quantidade_propostas=1,
        )
        is False
    )


def test_sem_flag_executar_tool_vale_como_acao() -> None:
    assert parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(
        '{"texto":"ok","ferramentas":[]}'
    ) is None
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=None,
            quantidade_propostas=2,
        )
        is True
    )
    assert (
        decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
            flag_executar=None,
            quantidade_propostas=0,
        )
        is False
    )


def test_parseia_ferramenta_quando_modelo_usa_chave_tool_em_vez_de_nome() -> None:
    bruto = (
        "Combinado! Vou aplicar.\n\n"
        '{"texto":"Apliquei as edições.","executar":true,'
        '"ferramentas":[{"tool":"edicao_parcial",'
        '"titulo_secao_heading":"Decisões Tomadas",'
        '"instrucoes":"Adicionar novo bullet: \'**Extranet:** fica para depois.\'"}]}'
    )
    ferramentas = parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers(bruto)
    assert len(ferramentas) == 1
    assert ferramentas[0]["nome"] == NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    assert ferramentas[0]["titulo_secao_heading"] == "Decisões Tomadas"
    assert parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto) is True
    assert (
        limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers(bruto, bruto)
        == "Apliquei as edições."
    )


def test_parseia_lote_real_com_prosa_prefixada_chave_tool_e_cinco_edicoes() -> None:
    bruto = (
        "Combinado! Vou aplicar as seis inclusões nas seções correspondentes.\n\n"
        '{"texto":"Apliquei as edições combinadas.","citacoes":[],'
        '"instantes_imagem_segundos":[],"executar":true,"ferramentas":['
        '{"tool":"edicao_parcial","titulo_secao_heading":"O que foi discutido",'
        '"instrucoes":"No bullet Algoritmo, acrescentar o critério."},'
        '{"tool":"edicao_parcial","titulo_secao_heading":"Decisões Tomadas",'
        '"instrucoes":"Adicionar novo bullet da extranet."},'
        '{"tool":"edicao_parcial","titulo_secao_heading":"Dúvidas em Aberto",'
        '"instrucoes":"Adicionar feriado pós-homologação."},'
        '{"tool":"edicao_parcial","titulo_secao_heading":"Próximos Passos",'
        '"instrucoes":"Adicionar reforço da Laís."},'
        '{"tool":"edicao_parcial","titulo_secao_heading":"Requisitos e Escopo",'
        '"instrucoes":"Adicionar e-mails adiados para V2."}]}'
    )
    ferramentas = parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers(bruto)
    assert len(ferramentas) == 5
    assert all(item["nome"] == NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS for item in ferramentas)
    assert [item["titulo_secao_heading"] for item in ferramentas] == [
        "O que foi discutido",
        "Decisões Tomadas",
        "Dúvidas em Aberto",
        "Próximos Passos",
        "Requisitos e Escopo",
    ]
    assert parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto) is True
    assert (
        limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers(bruto, bruto)
        == "Apliquei as edições combinadas."
    )


def test_item_ja_executado_nao_repete_propostas_pendentes_no_historico_llm() -> None:
    from transcribrothers_backend.modulo_orquestrar_turno_chat_agente_job_transcribrothers import (
        _texto_assistente_com_propostas_pendentes_chat_agente_transcribrothers,
    )

    item = SimpleNamespace(
        texto="Apliquei.",
        executar_proposta=True,
        propostas_ferramenta=[{"nome": "edicao_parcial"}],
        proposta_ferramenta={"nome": "edicao_parcial"},
    )
    saida = _texto_assistente_com_propostas_pendentes_chat_agente_transcribrothers(item)
    assert saida == "Apliquei."
    assert "Propostas pendentes" not in saida
