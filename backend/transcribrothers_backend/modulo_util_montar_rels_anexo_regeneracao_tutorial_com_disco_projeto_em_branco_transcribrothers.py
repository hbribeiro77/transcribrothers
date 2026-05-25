"""Monta rels para anexar PNGs na regeneração (snapshot + disco em projeto em branco)."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
    montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers,
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_remover_referencias_imagens_assets_inexistentes_markdown_tutorial_transcribrothers import (
    caminho_asset_png_existe_no_diretorio_exportado_markdown_transcribrothers,
)


def _adicionar_rel_se_png_existe_no_disco_transcribrothers(
    nome_para_par: dict[str, tuple[float, str]],
    caminho_relativo: str,
    assets_dir: Path,
    t_segundos: float,
) -> None:
    norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(caminho_relativo)
    if norm is None:
        return
    nome = norm.split("/")[-1]
    if not nome or not caminho_asset_png_existe_no_diretorio_exportado_markdown_transcribrothers(
        assets_dir, norm
    ):
        return
    if nome not in nome_para_par:
        nome_para_par[nome] = (float(t_segundos), norm)


def montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers(
    *,
    markdown: str,
    rels_snapshot: list[tuple[float, str]],
    assets_dir: Path,
    caminhos_assets_png_contexto_fab_extra: list[str] | None,
    eh_projeto_em_branco: bool,
) -> list[tuple[float, str]]:
    nome_para_par: dict[str, tuple[float, str]] = {}
    for t, rel in rels_snapshot:
        _adicionar_rel_se_png_existe_no_disco_transcribrothers(nome_para_par, rel, assets_dir, t)

    if eh_projeto_em_branco:
        for i, rel_md in enumerate(
            listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(markdown)
        ):
            _adicionar_rel_se_png_existe_no_disco_transcribrothers(
                nome_para_par, rel_md, assets_dir, float(i) * 0.001
            )
        extras = caminhos_assets_png_contexto_fab_extra or []
        for i, rel_extra in enumerate(extras):
            _adicionar_rel_se_png_existe_no_disco_transcribrothers(
                nome_para_par,
                rel_extra,
                assets_dir,
                1000.0 + float(i) * 0.001,
            )

    return sorted(nome_para_par.values(), key=lambda par: float(par[0]))


def montar_rels_png_anexo_regeneracao_com_pool_disco_projeto_em_branco_transcribrothers(
    *,
    markdown: str,
    instrucoes_revisao_humana: str | None,
    rels_snapshot: list[tuple[float, str]],
    assets_dir: Path,
    caminhos_assets_png_contexto_fab_extra: list[str] | None,
    eh_projeto_em_branco: bool,
) -> list[tuple[float, str]]:
    pool = montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers(
        markdown=markdown,
        rels_snapshot=rels_snapshot,
        assets_dir=assets_dir,
        caminhos_assets_png_contexto_fab_extra=caminhos_assets_png_contexto_fab_extra,
        eh_projeto_em_branco=eh_projeto_em_branco,
    )
    return montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
        markdown=markdown,
        instrucoes_revisao_humana=instrucoes_revisao_humana,
        rels_completos_com_tempos=pool,
    )
