"""Aplica várias edições parciais do chat no Markdown, sem apagar o resto da seção."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from transcribrothers_backend.modulo_montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers import (
    escolher_item_lista_mais_proximo_do_pedido_transcribrothers,
    listar_itens_lista_markdown_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
    substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
)

_RE_TRECHO_ASPAS_SIMPLES_TRANSCRIBROTHERS = re.compile(r"'([^']{8,})'")
_RE_TRECHO_ASPAS_DUPLO_TRANSCRIBROTHERS = re.compile(r'"([^"]{8,})"')
_RE_TRECHO_ASPAS_CURVAS_TRANSCRIBROTHERS = re.compile(r"[‘“]([^’”]{8,})[’”]")

OPERACAO_INSERIR_PROSA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS = "inserir_prosa"
OPERACAO_ANEXAR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS = "anexar_item"
OPERACAO_SUBSTITUIR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS = "substituir_item"


def extrair_trechos_entre_aspas_edicao_parcial_chat_agente_transcribrothers(texto: str) -> list[str]:
    return [trecho for _inicio, _fim, trecho in _iterar_trechos_entre_aspas_com_posicao_transcribrothers(texto)]


def _iterar_trechos_entre_aspas_com_posicao_transcribrothers(texto: str) -> list[tuple[int, int, str]]:
    saida: list[tuple[int, int, str]] = []
    vistos: set[str] = set()
    for padrao in (
        _RE_TRECHO_ASPAS_SIMPLES_TRANSCRIBROTHERS,
        _RE_TRECHO_ASPAS_DUPLO_TRANSCRIBROTHERS,
        _RE_TRECHO_ASPAS_CURVAS_TRANSCRIBROTHERS,
    ):
        for match in padrao.finditer(texto or ""):
            trecho = " ".join(match.group(1).split()).strip()
            if not trecho or trecho in vistos:
                continue
            vistos.add(trecho)
            saida.append((match.start(), match.end(), trecho))
    saida.sort(key=lambda item: item[0])
    return saida


def _trechos_conteudo_edicao_parcial_com_posicao_transcribrothers(
    ocorrencias: list[tuple[int, int, str]],
) -> list[tuple[int, int, str]]:
    longos = [item for item in ocorrencias if len(item[2]) >= 40]
    return longos or ocorrencias


def _tipo_operacao_pelo_contexto_antes_do_trecho_transcribrothers(contexto: str) -> str | None:
    baixo = (contexto or "").lower()
    if "no início" in baixo or "antes do parágrafo" in baixo:
        return OPERACAO_INSERIR_PROSA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    if (
        "novo item" in baixo
        or "novo bullet" in baixo
        or "adicionar novo item" in baixo
        or "adicionar à lista" in baixo
        or "adicionar a lista" in baixo
        or "adicionar ao final" in baixo
        or "acrescentar ao final" in baixo
        or "adicionar novo" in baixo
    ):
        return OPERACAO_ANEXAR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    if (
        "no item" in baixo
        or "no bullet" in baixo
        or "após a frase" in baixo
        or "depois da frase" in baixo
        or "ao final, acrescentar" in baixo
        or "acrescentar:" in baixo
    ):
        return OPERACAO_SUBSTITUIR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
    return None


def classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
    *,
    titulo_secao_heading: str | None,
    instrucoes: str,
) -> list[dict[str, str]]:
    texto = (instrucoes or "").strip()
    baixo = texto.lower()
    ocorrencias = _trechos_conteudo_edicao_parcial_com_posicao_transcribrothers(
        _iterar_trechos_entre_aspas_com_posicao_transcribrothers(texto)
    )
    if not ocorrencias:
        ocorrencias = [(0, texto)] if texto else []
    if not ocorrencias:
        return []

    inicio_secao = "no início" in baixo or "antes do parágrafo" in baixo
    novo_item = (
        "novo item" in baixo
        or "novo bullet" in baixo
        or "adicionar novo item" in baixo
        or "adicionar à lista" in baixo
        or "adicionar a lista" in baixo
        or "adicionar ao final" in baixo
        or "acrescentar ao final" in baixo
    )
    no_item = (
        "no item" in baixo
        or "no bullet" in baixo
        or "após a frase" in baixo
        or "depois da frase" in baixo
    )

    heading = (titulo_secao_heading or "").strip()

    def _op(tipo: str, trecho: str) -> dict[str, str]:
        return {
            "operacao": tipo,
            "titulo_secao_heading": heading,
            "trecho": trecho,
            "pedido": texto,
        }

    if inicio_secao and novo_item:
        fallbacks = [OPERACAO_INSERIR_PROSA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS] + [
            OPERACAO_ANEXAR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS
        ] * (len(ocorrencias) - 1)
    elif inicio_secao:
        fallbacks = [OPERACAO_INSERIR_PROSA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS] * len(ocorrencias)
    elif novo_item and not no_item:
        fallbacks = [OPERACAO_ANEXAR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS] * len(ocorrencias)
    else:
        fallbacks = [OPERACAO_SUBSTITUIR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS] * len(ocorrencias)

    operacoes: list[dict[str, str]] = []
    for indice, (posicao, _fim, trecho) in enumerate(ocorrencias):
        inicio_contexto = ocorrencias[indice - 1][1] if indice > 0 else 0
        contexto = texto[inicio_contexto:posicao]
        tipo = _tipo_operacao_pelo_contexto_antes_do_trecho_transcribrothers(contexto) or fallbacks[indice]
        operacoes.append(_op(tipo, trecho))
    return operacoes


def _secao_ja_contem_trecho_transcribrothers(corpo: str, trecho: str) -> bool:
    alvo = " ".join((trecho or "").split()).casefold()
    if not alvo:
        return False
    amostra = alvo[:80]
    return amostra in " ".join((corpo or "").split()).casefold()


def _inserir_prosa_no_corpo_secao_transcribrothers(corpo: str, trecho: str) -> str:
    linhas = (corpo or "").splitlines()
    if not linhas:
        return trecho
    if _secao_ja_contem_trecho_transcribrothers(corpo, trecho):
        return corpo
    insercao = ["", trecho] if linhas[0].startswith("## ") else [trecho]
    if len(linhas) == 1:
        return "\n".join(linhas + insercao + [""]).rstrip()
    return "\n".join(linhas[:1] + insercao + linhas[1:]).rstrip()


def _anexar_item_no_corpo_secao_transcribrothers(corpo: str, trecho: str) -> str:
    if _secao_ja_contem_trecho_transcribrothers(corpo, trecho):
        return corpo
    item = trecho if re.match(r"^\s*[-*]\s+", trecho) else f"* {trecho}"
    corpo_limpo = (corpo or "").rstrip()
    return f"{corpo_limpo}\n{item}"


def _acrescentar_trecho_no_item_ancora_transcribrothers(corpo: str, pedido: str, trecho: str) -> str:
    if _secao_ja_contem_trecho_transcribrothers(corpo, trecho):
        return corpo
    itens = listar_itens_lista_markdown_transcribrothers(corpo)
    ancora = escolher_item_lista_mais_proximo_do_pedido_transcribrothers(itens, pedido)
    if ancora is None and itens:
        ancora = itens[0]
    if ancora is None:
        return _anexar_item_no_corpo_secao_transcribrothers(corpo, trecho)
    linhas = (corpo or "").splitlines()
    saida: list[str] = []
    trocou = False
    for linha in linhas:
        if not trocou and linha.rstrip() == ancora.rstrip():
            saida.append(f"{linha.rstrip()} {trecho}")
            trocou = True
        else:
            saida.append(linha)
    if not trocou:
        return _anexar_item_no_corpo_secao_transcribrothers(corpo, trecho)
    return "\n".join(saida).rstrip()


def aplicar_operacao_edicao_parcial_no_markdown_chat_agente_transcribrothers(
    markdown: str,
    operacao: dict[str, str],
) -> str:
    heading = (operacao.get("titulo_secao_heading") or "").strip()
    trecho = (operacao.get("trecho") or "").strip()
    if not heading or not trecho:
        return markdown
    secao = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        markdown,
        titulo_secao_heading=heading,
        indice_secao=None,
    )
    corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(markdown, secao)
    tipo = operacao.get("operacao")
    if tipo == OPERACAO_INSERIR_PROSA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS:
        novo_corpo = _inserir_prosa_no_corpo_secao_transcribrothers(corpo, trecho)
    elif tipo == OPERACAO_ANEXAR_ITEM_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS:
        novo_corpo = _anexar_item_no_corpo_secao_transcribrothers(corpo, trecho)
    else:
        novo_corpo = _acrescentar_trecho_no_item_ancora_transcribrothers(
            corpo,
            (operacao.get("pedido") or f"{heading} {trecho}").strip(),
            trecho,
        )
    return substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers(markdown, secao, novo_corpo)


def instrucao_edicao_parcial_pede_reescrever_secao_nao_cirurgico_transcribrothers(
    proposta: dict[str, Any] | None,
) -> bool:
    if not isinstance(proposta, dict):
        return False
    if proposta.get("reescrever_secao") is True:
        return True
    instrucoes = proposta.get("instrucoes") or ""
    baixo = instrucoes.casefold()
    tira_tempo = "?t=" in instrucoes or "timestamp" in baixo or "[mm:ss]" in baixo
    remove = (
        "remover" in baixo
        or "tirar" in baixo
        or "tire " in baixo
        or "neutralizar" in baixo
    )
    if tira_tempo and remove:
        return True
    if "legenda" in baixo and "imagem" in baixo:
        return True
    return False


def lote_edicoes_parciais_deve_reescrever_secoes_nao_cirurgico_transcribrothers(
    propostas: list[dict[str, Any]] | None,
) -> bool:
    for item in propostas or []:
        if not isinstance(item, dict):
            continue
        if (item.get("nome") or "").strip() != "edicao_parcial":
            continue
        if instrucao_edicao_parcial_pede_reescrever_secao_nao_cirurgico_transcribrothers(item):
            return True
    return False


def aplicar_lote_edicoes_parciais_markdown_chat_agente_transcribrothers(
    *,
    markdown: str,
    propostas: list[dict[str, Any]],
) -> dict[str, Any]:
    atual = markdown or ""
    aplicacoes: list[dict[str, Any]] = []
    for proposta in propostas:
        if not isinstance(proposta, dict):
            continue
        if (proposta.get("nome") or "").strip() != "edicao_parcial":
            continue
        heading = (proposta.get("titulo_secao_heading") or "").strip()
        instrucoes = (proposta.get("instrucoes") or "").strip()
        for operacao in classificar_operacoes_edicao_parcial_chat_agente_transcribrothers(
            titulo_secao_heading=heading,
            instrucoes=instrucoes,
        ):
            antes = atual
            atual = aplicar_operacao_edicao_parcial_no_markdown_chat_agente_transcribrothers(
                atual,
                operacao,
            )
            aplicacoes.append(
                {
                    **operacao,
                    "aplicada": atual != antes,
                }
            )
    return {
        "markdown": atual,
        "aplicacoes": aplicacoes,
        "quantidade_aplicada": sum(1 for item in aplicacoes if item.get("aplicada")),
    }


def montar_preview_blob_lote_edicoes_parciais_chat_agente_transcribrothers(
    *,
    markdown_antes: str,
    resultado_lote: dict[str, Any],
) -> dict[str, Any]:
    from transcribrothers_backend.modulo_montar_pedido_edicao_parcial_cirurgica_chat_agente_transcribrothers import (
        resumir_alerta_se_edicao_removeu_itens_lista_transcribrothers,
    )

    md_depois = str(resultado_lote.get("markdown") or "")
    headings: list[str] = []
    for item in resultado_lote.get("aplicacoes") or []:
        if not isinstance(item, dict) or not item.get("aplicada"):
            continue
        heading = str(item.get("titulo_secao_heading") or "").strip()
        if heading and heading not in headings:
            headings.append(heading)
    titulo = headings[0] if len(headings) == 1 else "Várias seções"
    alerta = resumir_alerta_se_edicao_removeu_itens_lista_transcribrothers(
        markdown_antes,
        md_depois,
    )
    blob: dict[str, Any] = {
        "titulo_secao_heading": titulo,
        "indice_secao": -1,
        "secao_markdown_antes": markdown_antes,
        "secao_markdown_depois": md_depois,
        "markdown_completo_proposto": md_depois,
        "instrucoes_usadas": "Lote de edições parciais do chat.",
        "instrucoes_pedido_original": "Lote de edições parciais do chat.",
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "modo_escopo_edicao": "trecho_local",
        "edicao_cirurgica_chat_agente": True,
        "lote_edicoes_parciais": resultado_lote.get("aplicacoes") or [],
        "quantidade_aplicada": resultado_lote.get("quantidade_aplicada") or 0,
    }
    if alerta:
        blob["alerta_itens_lista_removidos"] = alerta
    return blob
