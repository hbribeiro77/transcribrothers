"""Pedido de edição parcial vindo do chat: âncora num item, resto da seção intacto."""

from __future__ import annotations

import re
from typing import Any

from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
    _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers,
    normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers,
)

_RE_ITEM_LISTA_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"^\s*[-*]\s+\S")
_RE_NEGRITO_ITEM_LISTA_TRANSCRIBROTHERS = re.compile(r"\*\*([^*]+)\*\*")


def contar_itens_lista_markdown_transcribrothers(markdown: str) -> int:
    return len(listar_itens_lista_markdown_transcribrothers(markdown))


def listar_itens_lista_markdown_transcribrothers(markdown: str) -> list[str]:
    return [
        linha.rstrip()
        for linha in (markdown or "").splitlines()
        if _RE_ITEM_LISTA_MARKDOWN_TRANSCRIBROTHERS.match(linha)
    ]


def _pontuar_item_contra_pedido_transcribrothers(item: str, pedido: str) -> float:
    norm_item = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(item)
    norm_pedido = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(pedido)
    if not norm_item or not norm_pedido:
        return 0.0
    negrito = _RE_NEGRITO_ITEM_LISTA_TRANSCRIBROTHERS.search(item)
    if negrito:
        rotulo = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(negrito.group(1))
        if rotulo and rotulo in norm_pedido:
            return 1.0
    tok_i = _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers(norm_item)
    tok_p = _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers(norm_pedido)
    if not tok_i or not tok_p:
        return 0.0
    return len(tok_i & tok_p) / max(len(tok_p), 1)


def escolher_item_lista_mais_proximo_do_pedido_transcribrothers(
    itens: list[str],
    texto_pedido: str,
) -> str | None:
    melhor: str | None = None
    melhor_score = 0.0
    for item in itens:
        score = _pontuar_item_contra_pedido_transcribrothers(item, texto_pedido)
        if score > melhor_score:
            melhor_score = score
            melhor = item
    if melhor is None or melhor_score < 0.12:
        return None
    return melhor


def _normalizar_caminhos_imagens_pedido_transcribrothers(caminhos: list[str] | None) -> list[str]:
    saida: list[str] = []
    vistos: set[str] = set()
    for cru in caminhos or []:
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(str(cru))
        if not norm or norm in vistos:
            continue
        vistos.add(norm)
        saida.append(norm)
    return saida


def montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers(
    *,
    markdown: str,
    titulo_secao_heading: str | None,
    texto_rascunho: str,
    caminhos_imagens: list[str] | None = None,
) -> dict[str, Any]:
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown)
    if not secoes:
        raise ValueError("O documento não tem seções «##» para edição parcial.")
    if (titulo_secao_heading or "").strip():
        secao = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
            markdown,
            titulo_secao_heading=titulo_secao_heading,
            indice_secao=None,
        )
    else:
        secao = secoes[0]
        melhor_item_global = None
        melhor_secao = secao
        melhor_score = 0.0
        for candidata in secoes:
            corpo_c = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(markdown, candidata)
            for item in listar_itens_lista_markdown_transcribrothers(corpo_c):
                score = _pontuar_item_contra_pedido_transcribrothers(item, texto_rascunho)
                if score > melhor_score:
                    melhor_score = score
                    melhor_item_global = item
                    melhor_secao = candidata
        secao = melhor_secao
        if melhor_item_global and melhor_score >= 0.12:
            ancora = melhor_item_global
        else:
            ancora = None
    corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(markdown, secao)
    itens = listar_itens_lista_markdown_transcribrothers(corpo)
    ancora = escolher_item_lista_mais_proximo_do_pedido_transcribrothers(itens, texto_rascunho)
    if ancora is None and itens:
        ancora = itens[0]
    if ancora is None:
        raise ValueError(
            "Não achei um item de lista na seção para ancorar a edição. "
            "Escolha o trecho na edição parcial manual."
        )
    caminhos = _normalizar_caminhos_imagens_pedido_transcribrothers(caminhos_imagens)
    linhas_img = "\n".join(f"![]({rel})" for rel in caminhos)
    bloco_img = (
        "\n\nInclua esta(s) imagem(ns) com o caminho literal, sem inventar nome:\n" + linhas_img
        if linhas_img
        else ""
    )
    rascunho = (texto_rascunho or "").strip()
    instrucoes = (
        "Substitua SOMENTE o trecho âncora (este item da lista). "
        "Não apague nem reescreva os outros bullets desta seção.\n\n"
        f"Novo texto para este item:\n{rascunho}"
        f"{bloco_img}"
    )
    return {
        "titulo_secao_heading": secao.linha_heading,
        "modo_escopo_edicao": "trecho_local",
        "trecho_ancora": ancora,
        "instrucoes": instrucoes,
        "caminhos_imagens": caminhos,
    }


def resumir_alerta_se_edicao_removeu_itens_lista_transcribrothers(
    markdown_antes: str,
    markdown_depois: str,
) -> str | None:
    n_antes = contar_itens_lista_markdown_transcribrothers(markdown_antes)
    n_depois = contar_itens_lista_markdown_transcribrothers(markdown_depois)
    if n_antes >= 2 and n_depois <= n_antes - 2:
        return (
            f"A prévia perdeu itens de lista ({n_antes} → {n_depois}). "
            "Confira antes de aplicar: a edição parcial não deveria apagar os outros bullets."
        )
    return None
