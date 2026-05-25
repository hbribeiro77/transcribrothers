"""Remove do Markdown referências `![](assets/…png)` cujo arquivo não existe no disco."""

from __future__ import annotations

import re
from pathlib import Path

from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)

_RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"!\[[^\]]*\]\(\s*([^)]+?)\s*\)")


def caminho_asset_png_existe_no_diretorio_exportado_markdown_transcribrothers(
    diretorio_assets: Path,
    caminho_relativo_assets: str,
) -> bool:
    nome = caminho_relativo_assets.strip().replace("\\", "/").split("/")[-1]
    return (diretorio_assets / nome).is_file()


def listar_caminhos_assets_png_em_markdown_que_existem_no_disco_transcribrothers(
    markdown: str,
    diretorio_assets: Path,
) -> list[str]:
    from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
        listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
    )

    todos = listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(markdown)
    return [
        c
        for c in todos
        if caminho_asset_png_existe_no_diretorio_exportado_markdown_transcribrothers(diretorio_assets, c)
    ]


def remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers(
    markdown: str,
    diretorio_assets: Path,
) -> tuple[str, int]:
    """
    Remove linhas que são só `![](assets/foo.png)` quando foo.png não existe.
    Devolve (markdown_limpo, quantidade_de_linhas_removidas).
    """
    if not (markdown or "").strip():
        return markdown, 0
    assets = diretorio_assets.resolve()
    linhas_out: list[str] = []
    removidas = 0
    for linha in markdown.splitlines(keepends=True):
        stripped = linha.strip()
        m = _RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.fullmatch(stripped)
        if m:
            norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(m.group(1))
            if norm and not caminho_asset_png_existe_no_diretorio_exportado_markdown_transcribrothers(
                assets, norm
            ):
                removidas += 1
                continue
        linhas_out.append(linha)
    return "".join(linhas_out), removidas
