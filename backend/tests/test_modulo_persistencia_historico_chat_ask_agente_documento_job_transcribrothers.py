from pathlib import Path

from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
    ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
    TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS,
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers,
    carregar_historico_chat_ask_agente_do_work_transcribrothers,
)


def _item(texto: str) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    return ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel="usuario",
        modo="ask",
        texto=texto,
        criado_em="2026-10-03T12:00:00+00:00",
        citacoes=[],
        imagens=[],
        estado=None,
        tipo_pipeline=None,
    )


def test_carregar_historico_ausente_devolve_lista_vazia(tmp_path: Path) -> None:
    assert carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path) == []


def test_anexar_item_persiste_e_rele(tmp_path: Path) -> None:
    saida = anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, _item("oi"))
    assert len(saida) == 1
    assert saida[0].texto == "oi"
    assert carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)[0].texto == "oi"


def test_anexar_item_persiste_proposta_ferramenta(tmp_path: Path) -> None:
    item = ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel="agente",
        modo="agente",
        texto="sugiro a Visão Geral",
        criado_em="2026-10-04T12:00:00+00:00",
        citacoes=[],
        imagens=[],
        estado=None,
        tipo_pipeline=None,
        proposta_ferramenta={
            "nome": "edicao_parcial",
            "titulo_secao_heading": "Visão Geral",
            "instrucoes": "inclua o parágrafo",
        },
        propostas_ferramenta=[
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Visão Geral",
                "instrucoes": "inclua o parágrafo",
            },
            {
                "nome": "edicao_parcial",
                "titulo_secao_heading": "Dúvidas em aberto",
                "instrucoes": "e-mail vs ofício",
            },
        ],
    )
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, item)
    lido = carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)[0]
    assert lido.proposta_ferramenta is not None
    assert lido.proposta_ferramenta["nome"] == "edicao_parcial"
    assert lido.propostas_ferramenta is not None
    assert len(lido.propostas_ferramenta) == 2
    assert lido.executar_proposta is False


def test_anexar_item_persiste_executar_proposta(tmp_path: Path) -> None:
    item = ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel="agente",
        modo="agente",
        texto="Apliquei as quatro edições.",
        criado_em="2026-10-04T18:00:00+00:00",
        citacoes=[],
        imagens=[],
        estado=None,
        tipo_pipeline=None,
        proposta_ferramenta={"nome": "edicao_parcial"},
        executar_proposta=True,
    )
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, item)
    lido = carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)[0]
    assert lido.executar_proposta is True


def test_anexar_acima_do_teto_descarta_os_mais_antigos(tmp_path: Path) -> None:
    for i in range(TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS + 3):
        anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, _item(f"m{i}"))
    itens = carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)
    assert len(itens) == TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS
    assert itens[0].texto == "m3"
    assert itens[-1].texto == "m42"
