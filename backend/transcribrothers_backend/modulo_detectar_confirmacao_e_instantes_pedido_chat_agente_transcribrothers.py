"""Confirmação do usuário e instantes citados no texto do Agente."""

from __future__ import annotations

import re
from typing import Any

from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
)

_PADRAO_CONFIRMACAO_PEDIDO_CHAT_AGENTE_TRANSCRIBROTHERS = re.compile(
    r"^(beleza[,!.]?\s*)?(pode\s+(fazer|prosseguir|aplicar|seguir)|faz(er)?(\s+isso)?|"
    r"aplica(r)?(\s+isso)?|confirmo|manda)\s*[.!]*$",
    re.IGNORECASE,
)
_PADRAO_INSTANTE_COM_SUFIXO_S_TRANSCRIBROTHERS = re.compile(
    r"(?<!\d)(\d+(?:[.,]\d+)?)\s*s\b",
    re.IGNORECASE,
)
_PADRAO_INSTANTE_ENTRE_COLCHETES_TRANSCRIBROTHERS = re.compile(
    r"\[(\d+(?:[.,]\d+)?)(?::\d+(?:[.,]\d+)?)?\]",
)
_PADRAO_HEADING_ENTRE_NEGRITO_ASPAS_TRANSCRIBROTHERS = re.compile(
    r"\*\*[\"“]([^\"”]+)[\"”]\*\*"
)
_TETO_INSTANTE_SEGUNDOS_CHAT_AGENTE_TRANSCRIBROTHERS = 20_000.0


def detectar_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers(texto: str) -> bool:
    return bool(
        _PADRAO_CONFIRMACAO_PEDIDO_CHAT_AGENTE_TRANSCRIBROTHERS.match((texto or "").strip())
    )


def _instante_valido_chat_agente_transcribrothers(bruto: str) -> float | None:
    try:
        valor = float(bruto.replace(",", "."))
    except ValueError:
        return None
    if valor < 0 or valor > _TETO_INSTANTE_SEGUNDOS_CHAT_AGENTE_TRANSCRIBROTHERS:
        return None
    return valor


def extrair_instantes_segundos_mencionados_no_texto_chat_agente_transcribrothers(
    texto: str,
) -> list[float]:
    vistos: set[float] = set()
    saida: list[float] = []
    for padrao in (
        _PADRAO_INSTANTE_COM_SUFIXO_S_TRANSCRIBROTHERS,
        _PADRAO_INSTANTE_ENTRE_COLCHETES_TRANSCRIBROTHERS,
    ):
        for match in padrao.finditer(texto or ""):
            valor = _instante_valido_chat_agente_transcribrothers(match.group(1))
            if valor is None or valor in vistos:
                continue
            vistos.add(valor)
            saida.append(valor)
    return saida


def sintetizar_proposta_edicao_parcial_do_texto_agente_transcribrothers(
    texto: str,
) -> dict[str, Any]:
    heading = None
    match = _PADRAO_HEADING_ENTRE_NEGRITO_ASPAS_TRANSCRIBROTHERS.search(texto or "")
    if match:
        heading = match.group(1).strip() or None
    return {
        "nome": NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
        "titulo_secao_heading": heading,
        "instrucoes": (texto or "").strip() or None,
        "caminhos_imagens": [],
    }


def localizar_ultimo_item_agente_com_texto_no_historico_transcribrothers(
    itens: list[Any],
) -> Any | None:
    for item in reversed(itens):
        papel = getattr(item, "papel", None)
        texto = getattr(item, "texto", "") or ""
        if papel == "agente" and texto.strip() and getattr(item, "estado", None) != "gerando":
            return item
    return None
