from transcribrothers_backend.modulo_aplicar_lote_edicoes_parciais_chat_agente_documento_transcribrothers import (
    aplicar_lote_edicoes_parciais_markdown_chat_agente_transcribrothers,
    classificar_operacoes_edicao_parcial_chat_agente_transcribrothers,
)
from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    escolher_propostas_ferramenta_chat_agente_transcribrothers,
)


_MD = """# Ata

## Contexto e problema

A Defensoria Pública busca massificar a atuação extrajudicial.

* **Problema A:** texto.

## O que foi discutido

* **Assistido Digital:** hub de autoatendimento.
* **Fluxo de Encaminhamento:** tarefas para câmaras.

## Requisitos / escopo mencionado

* **Etiquetas gerais:** já existem.

## Dúvidas em aberto

* **Prazo:** indefinido.
"""


def test_classifica_inserir_prosa_anexar_item_e_substituir_item() -> None:
    ops_contexto = classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
        titulo_secao_heading="Contexto e problema",
        instrucoes=(
            "No início da seção, antes do parágrafo sobre massificar, adicionar: "
            "'O tema chegou fragmentado [20:00](?t=20).' "
            "Também adicionar ao final como novo item na lista: "
            "'Já existe um defensor aplicando atendimento roteirizado [350:00](?t=350).'"
        ),
    )
    assert [op["operacao"] for op in ops_contexto] == ["inserir_prosa", "anexar_item"]

    ops_whats = classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
        titulo_secao_heading="O que foi discutido",
        instrucoes=(
            "No item 'Assistido Digital', após a frase sobre o hub, acrescentar: "
            "'Além do hub digital, o WhatsApp é cogitado [1020:00](?t=1020).'"
        ),
    )
    assert ops_whats[0]["operacao"] == "substituir_item"

    ops_req = classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
        titulo_secao_heading="Requisitos / escopo mencionado",
        instrucoes=(
            "Adicionar novo item à lista: "
            "'Possibilidade de os setores criarem etiquetas próprias [2109:00](?t=2109).'"
        ),
    )
    assert ops_req[0]["operacao"] == "anexar_item"


def test_lote_aplica_os_quatro_recortes_sem_apagar_os_outros_bullets() -> None:
    propostas = [
        {
            "nome": "edicao_parcial",
            "titulo_secao_heading": "Contexto e problema",
            "instrucoes": (
                "No início da seção, antes do parágrafo sobre massificar, adicionar: "
                "'O tema chegou fragmentado entre especialistas [20:00](?t=20).' "
                "Também adicionar como novo item na lista: "
                "'Um defensor já aplica atendimento roteirizado [350:00](?t=350).'"
            ),
        },
        {
            "nome": "edicao_parcial",
            "titulo_secao_heading": "O que foi discutido",
            "instrucoes": (
                "No item 'Assistido Digital', após a frase sobre o hub, acrescentar: "
                "'Além do hub digital, o WhatsApp é cogitado como canal alternativo [1020:00](?t=1020).'"
            ),
        },
        {
            "nome": "edicao_parcial",
            "titulo_secao_heading": "Requisitos / escopo mencionado",
            "instrucoes": (
                "Adicionar novo item à lista: "
                "'Setores podem criar etiquetas próprias [2109:00](?t=2109).'"
            ),
        },
        {
            "nome": "edicao_parcial",
            "titulo_secao_heading": "Dúvidas em aberto",
            "instrucoes": (
                "Adicionar novo item à lista: "
                "'Recebimento de documentos por e-mail vs. por ofício [4346:00](?t=4346).'"
            ),
        },
    ]
    saida = aplicar_lote_edicoes_parciais_markdown_chat_agente_transcribrothers(
        markdown=_MD,
        propostas=propostas,
    )
    md = saida["markdown"]
    assert "tema chegou fragmentado" in md
    assert "defensor já aplica atendimento roteirizado" in md
    assert "WhatsApp é cogitado" in md
    assert "etiquetas próprias" in md
    assert "e-mail vs. por ofício" in md
    assert "Fluxo de Encaminhamento" in md
    assert "Etiquetas gerais" in md
    assert "massificar a atuação extrajudicial" in md
    assert saida["quantidade_aplicada"] == 5


def test_classifica_acrescentar_no_bullet_e_novo_bullet_na_mesma_instrucao() -> None:
    ops = classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
        titulo_secao_heading="O que foi discutido",
        instrucoes=(
            "No bullet 'Algoritmo de Distribuição', ao final, acrescentar: "
            "'O critério de desempate considera uma janela móvel de dois meses: "
            'quem recebeu menos vagas no período deve ter prioridade ("quem pegou zero").\' '
            "Em seguida, adicionar um novo bullet: "
            "'**Validação do Algoritmo:** os cenários de teste devem ser fixos e determinísticos.'"
        ),
    )
    assert [op["operacao"] for op in ops] == ["substituir_item", "anexar_item"]
    assert "janela móvel" in ops[0]["trecho"]
    assert "Validação do Algoritmo" in ops[1]["trecho"]


def test_lote_aplica_acrescentar_e_novo_bullet_sem_apagar_os_outros() -> None:
    propostas = [
        {
            "nome": "edicao_parcial",
            "titulo_secao_heading": "O que foi discutido",
            "instrucoes": (
                "No bullet 'Assistido Digital', ao final, acrescentar: "
                "'O critério de desempate considera uma janela móvel de dois meses.' "
                "Em seguida, adicionar um novo bullet: "
                "'**Validação do Algoritmo:** cenários de teste devem ser fixos.'"
            ),
        }
    ]
    saida = aplicar_lote_edicoes_parciais_markdown_chat_agente_transcribrothers(
        markdown=_MD,
        propostas=propostas,
    )
    md = saida["markdown"]
    assert "janela móvel de dois meses" in md
    assert "Validação do Algoritmo" in md
    assert "Fluxo de Encaminhamento" in md
    assert saida["quantidade_aplicada"] == 2


def test_escolher_propostas_devolve_todas_as_edicoes_parciais() -> None:
    propostas = escolher_propostas_ferramenta_chat_agente_transcribrothers(
        ferramentas=[
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Contexto e problema",
                "instrucoes": "um",
            },
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Dúvidas em aberto",
                "instrucoes": "dois",
            },
        ],
        forcar_ferramenta=None,
        mensagem_usuario="inclui os pontos",
    )
    assert len(propostas) == 2
    assert propostas[0]["titulo_secao_heading"] == "Contexto e problema"
    assert propostas[1]["titulo_secao_heading"] == "Dúvidas em aberto"


def test_lote_que_remove_timestamp_e_pede_legenda_deve_reescrever_secao() -> None:
    from transcribrothers_backend.modulo_aplicar_lote_edicoes_parciais_chat_agente_documento_transcribrothers import (
        lote_edicoes_parciais_deve_reescrever_secoes_nao_cirurgico_transcribrothers,
    )

    assert lote_edicoes_parciais_deve_reescrever_secoes_nao_cirurgico_transcribrothers(
        [
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "1. Visão Geral e Triagem Manual",
                "instrucoes": (
                    "Remover os links de tempo '[00:47](?t=47)' do texto corrido. "
                    "Adicionar uma legenda curta abaixo de cada imagem."
                ),
            }
        ]
    )
    assert not lote_edicoes_parciais_deve_reescrever_secoes_nao_cirurgico_transcribrothers(
        [
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Contexto e problema",
                "instrucoes": (
                    "Adicionar ao final da lista: "
                    "'**Filtros de Triagem:** o defensor filtra por etiqueta.'"
                ),
            }
        ]
    )
    assert lote_edicoes_parciais_deve_reescrever_secoes_nao_cirurgico_transcribrothers(
        [
            {
                "nome": "edicao_parcial",
                "reescrever_secao": True,
                "titulo_secao_heading": "Introdução",
                "instrucoes": "Deixe a intro mais curta.",
            }
        ]
    )
