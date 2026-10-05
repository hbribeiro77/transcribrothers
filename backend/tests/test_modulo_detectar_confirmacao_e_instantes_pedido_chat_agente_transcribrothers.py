from transcribrothers_backend.modulo_detectar_confirmacao_e_instantes_pedido_chat_agente_transcribrothers import (
    detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers,
    extrair_instantes_segundos_mencionados_no_texto_chat_agente_transcribrothers,
    sintetizar_proposta_edicao_parcial_do_texto_agente_transcribrothers,
)


def test_detecta_pode_fazer_e_pode_prosseguir() -> None:
    assert detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers(
        "beleza, pode fazer"
    )
    assert detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers(
        "pode prosseguir"
    )
    assert detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers("aplica")
    assert not detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers(
        "isso deve estar na transcrição"
    )
    assert not detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers(
        "bola um texto e pega o frame"
    )


def test_extrai_instantes_do_texto_do_agente() -> None:
    texto = (
        "Vou pedir a captura no instante 758s. "
        "O intervalo vai de [735.000] a [768.500]. "
        "Indicar 748s para o servidor."
    )
    instantes = extrair_instantes_segundos_mencionados_no_texto_chat_agente_transcribrothers(texto)
    assert 758.0 in instantes
    assert 748.0 in instantes
    assert 735.0 in instantes


def test_sintetiza_edicao_parcial_com_heading_do_rascunho() -> None:
    texto = (
        'Sugiro adicionar ao final da seção **"3. Fluxo do Assistido (WhatsApp)"**.\n\n'
        "Rascunho:\n> Atenção: envio direto no chat."
    )
    proposta = sintetizar_proposta_edicao_parcial_do_texto_agente_transcribrothers(texto)
    assert proposta["nome"] == "edicao_parcial"
    assert proposta["titulo_secao_heading"] == "3. Fluxo do Assistido (WhatsApp)"
    assert "Atenção" in (proposta["instrucoes"] or "")
