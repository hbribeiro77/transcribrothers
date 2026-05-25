"""Limites e normalização de anexos do FAB (projeto em branco)."""

from __future__ import annotations

from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)

LIMITE_CAMINHOS_ASSETS_PNG_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS = 16
LIMITE_TEXTOS_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS = 4
LIMITE_CARACTERES_POR_TEXTO_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS = 48_000
LIMITE_CARACTERES_TOTAL_TEXTOS_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS = 96_000


def normalizar_caminhos_assets_png_contexto_fab_pedido_transcribrothers(
    valores: list[str] | None,
) -> list[str]:
    if not valores:
        return []
    saida: list[str] = []
    vistos: set[str] = set()
    for raw in valores:
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(str(raw))
        if norm is None or norm in vistos:
            continue
        vistos.add(norm)
        saida.append(norm)
        if len(saida) >= LIMITE_CAMINHOS_ASSETS_PNG_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS:
            break
    return saida


def normalizar_textos_contexto_fab_pedido_transcribrothers(
    valores: list[str] | None,
) -> list[str]:
    if not valores:
        return []
    saida: list[str] = []
    total = 0
    for raw in valores:
        t = (raw or "").replace("\r\n", "\n").strip()
        if not t:
            continue
        if len(t) > LIMITE_CARACTERES_POR_TEXTO_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS:
            t = t[: LIMITE_CARACTERES_POR_TEXTO_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS] + "…"
        restante = LIMITE_CARACTERES_TOTAL_TEXTOS_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS - total
        if restante <= 0:
            break
        if len(t) > restante:
            t = t[:restante] + "…"
        saida.append(t)
        total += len(t)
        if len(saida) >= LIMITE_TEXTOS_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS:
            break
    return saida
