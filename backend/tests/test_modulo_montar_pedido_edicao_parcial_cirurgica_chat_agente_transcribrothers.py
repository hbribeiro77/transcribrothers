from transcribrothers_backend.modulo_montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers import (
    contar_itens_lista_markdown_transcribrothers,
    montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers,
    resumir_alerta_se_edicao_removeu_itens_lista_transcribrothers,
)


_MD = """# Ata

## O que foi discutido

* **Assistido Digital:** menção breve.
* **Fluxo de Encaminhamento:** O uso de tarefas para câmaras [764:00](?t=764).
* **Gestão de Ofícios:** controle de prazos [1737:00](?t=1737).
* **Pessoa Jurídica e Coletivos:** CNPJ [3428:00](?t=3428).
* **Indicadores:** Termos de Entendimento [2320:00](?t=2320).

## Outra

texto
"""


def test_pedido_cirurgico_ancora_so_o_bullet_assistido_digital() -> None:
    pedido = montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers(
        markdown=_MD,
        titulo_secao_heading="O que foi discutido",
        texto_rascunho=(
            "Aprofunde o bullet Assistido Digital. "
            "Rascunho: o assistido tenta enviar direto no chat."
        ),
        caminhos_imagens=["assets/tela_chat_758.png"],
    )
    assert pedido["modo_escopo_edicao"] == "trecho_local"
    assert "Assistido Digital" in pedido["trecho_ancora"]
    assert "Fluxo de Encaminhamento" not in pedido["trecho_ancora"]
    assert "não apague" in pedido["instrucoes"].lower() or "somente" in pedido["instrucoes"].lower()
    assert "![](assets/tela_chat_758.png)" in pedido["instrucoes"]
    assert pedido["caminhos_imagens"] == ["assets/tela_chat_758.png"]


def test_alerta_quando_sumiram_tres_bullets() -> None:
    antes = _MD
    depois = """## O que foi discutido

* **Assistido Digital:** texto longo novo.
"""
    alerta = resumir_alerta_se_edicao_removeu_itens_lista_transcribrothers(antes, depois)
    assert alerta is not None
    assert "4" in alerta or "itens" in alerta.lower()


def test_conta_cinco_itens_na_secao() -> None:
    assert contar_itens_lista_markdown_transcribrothers(_MD) == 5
