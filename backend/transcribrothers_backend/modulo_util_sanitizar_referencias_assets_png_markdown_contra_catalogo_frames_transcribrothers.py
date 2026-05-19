"""Corrige ou remove `![](assets/….png)` que não existem no catálogo de frames do job."""

from __future__ import annotations

import re
from typing import Any

from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)

_RE_IMAGEM_MARKDOWN_COM_ALT_TRANSCRIBROTHERS = re.compile(
    r"!\[([^\]]*)\]\(\s*([^)]+?)\s*\)",
)
_RE_MS_NO_NOME_FRAME_PNG_TRANSCRIBROTHERS = re.compile(
    r"_frame_no_offset_ms_(\d{10})_",
)
_RE_T_SEGUNDOS_EM_URL_OU_TEXTO_TRANSCRIBROTHERS = re.compile(r"\?t=(\d+(?:\.\d+)?)")


def _nome_arquivo_de_rel_asset_transcribrothers(rel: str) -> str:
    return rel.strip().replace("\\", "/").split("/")[-1]


def construir_catalogo_permitido_e_mapa_ms_para_asset_png_transcribrothers(
    rels_completos_com_tempos: list[tuple[float, str]],
) -> tuple[set[str], dict[int, str]]:
    """Conjunto de `assets/….png` válidos e mapa ms (do nome) → caminho canónico."""
    permitidos: set[str] = set()
    por_ms: dict[int, str] = {}
    for t, rel in rels_completos_com_tempos:
        norm = rel if rel.startswith("assets/") else f"assets/{_nome_arquivo_de_rel_asset_transcribrothers(rel)}"
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(norm)
        if not norm:
            continue
        permitidos.add(norm)
        m = _RE_MS_NO_NOME_FRAME_PNG_TRANSCRIBROTHERS.search(_nome_arquivo_de_rel_asset_transcribrothers(norm))
        if m:
            por_ms[int(m.group(1))] = norm
        else:
            por_ms.setdefault(int(round(float(t) * 1000)), norm)
    return permitidos, por_ms


def _resolver_caminho_asset_por_ms_ou_tempo_segundos_transcribrothers(
    *,
    por_ms: dict[int, str],
    ms_no_nome: int | None,
    t_segundos: float | None,
) -> str | None:
    if ms_no_nome is not None and ms_no_nome in por_ms:
        return por_ms[ms_no_nome]
    if t_segundos is None or not por_ms:
        return None
    alvo_ms = int(round(t_segundos * 1000))
    if alvo_ms in por_ms:
        return por_ms[alvo_ms]
    melhor: str | None = None
    menor_dist = float("inf")
    for ms, rel in por_ms.items():
        dist = abs(ms - alvo_ms)
        if dist < menor_dist:
            menor_dist = dist
            melhor = rel
    if melhor is not None and menor_dist <= 2500:
        return melhor
    return None


def sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers(
    markdown: str,
    rels_completos_com_tempos: list[tuple[float, str]],
) -> tuple[str, list[dict[str, Any]]]:
    """
    - Mantém caminhos que existem no catálogo.
    - Se o modelo inventou sufixo (ex. `_exemplo_bloqueio_01`) mas o ms bate, substitui pelo ficheiro real.
    - Se houver `?t=` no link e ms não bater, tenta o frame mais próximo (≤ 2,5 s).
    - Caso contrário remove a linha da imagem (evita link quebrado no preview).
    """
    if not (markdown or "").strip() or not rels_completos_com_tempos:
        return markdown, []

    permitidos, por_ms = construir_catalogo_permitido_e_mapa_ms_para_asset_png_transcribrothers(
        rels_completos_com_tempos
    )
    ajustes: list[dict[str, Any]] = []

    def _substituir(match: re.Match[str]) -> str:
        alt = match.group(1)
        raw_path = match.group(2)
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(raw_path)
        if norm and norm in permitidos:
            return match.group(0)

        nome = _nome_arquivo_de_rel_asset_transcribrothers(norm or raw_path)
        ms_no_nome: int | None = None
        m_ms = _RE_MS_NO_NOME_FRAME_PNG_TRANSCRIBROTHERS.search(nome)
        if m_ms:
            ms_no_nome = int(m_ms.group(1))

        t_seg: float | None = None
        m_t = _RE_T_SEGUNDOS_EM_URL_OU_TEXTO_TRANSCRIBROTHERS.search(raw_path)
        if m_t:
            try:
                t_seg = float(m_t.group(1))
            except ValueError:
                t_seg = None

        corrigido = _resolver_caminho_asset_por_ms_ou_tempo_segundos_transcribrothers(
            por_ms=por_ms,
            ms_no_nome=ms_no_nome,
            t_segundos=t_seg,
        )
        if corrigido:
            ajustes.append(
                {
                    "acao": "substituido",
                    "de": norm or raw_path.strip(),
                    "para": corrigido,
                }
            )
            return f"![{alt}]({corrigido})"

        ajustes.append(
            {
                "acao": "removido",
                "de": norm or raw_path.strip(),
                "para": None,
            }
        )
        return ""

    saida = _RE_IMAGEM_MARKDOWN_COM_ALT_TRANSCRIBROTHERS.sub(_substituir, markdown)
    saida = re.sub(r"\n{3,}", "\n\n", saida)
    return saida, ajustes
