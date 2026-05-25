"""Prepara Markdown do tutorial para página wiki GitLab (anexos em /wikis/attachments)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    upload_arquivo_png_anexo_wiki_gitlab_projeto_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
)
from transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers import (
    reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers,
    resolver_arquivo_png_no_disco_para_caminho_assets_markdown_tutorial_transcribrothers,
)


async def preparar_conteudo_markdown_pagina_wiki_gitlab_com_upload_imagens_assets_png_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    markdown: str,
    diretorio_assets: Path,
    steps_json: dict[str, Any] | None,
    *,
    incluir_imagens_png_markdown: bool,
) -> tuple[str, int, int]:
    """
    Devolve (markdown_para_wiki, quantidade_imagens_enviadas, quantidade_imagens_ignoradas).
    """
    texto = (markdown or "").strip()
    if not texto or not incluir_imagens_png_markdown:
        return markdown, 0, 0

    caminhos = listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(texto)
    if not caminhos:
        return markdown, 0, 0

    mapa_url: dict[str, str] = {}
    enviadas = 0
    ignoradas = 0

    for caminho in caminhos:
        path = resolver_arquivo_png_no_disco_para_caminho_assets_markdown_tutorial_transcribrothers(
            diretorio_assets,
            caminho,
            steps_json,
        )
        if path is None or not path.is_file():
            ignoradas += 1
            continue
        if caminho in mapa_url:
            continue
        bytes_png = path.read_bytes()
        nome_upload = path.name
        url_wiki = await upload_arquivo_png_anexo_wiki_gitlab_projeto_transcribrothers(
            cfg,
            conteudo_png=bytes_png,
            nome_arquivo=nome_upload,
        )
        mapa_url[caminho] = url_wiki
        enviadas += 1

    markdown_wiki = reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers(
        texto,
        mapa_url,
    )
    return markdown_wiki, enviadas, ignoradas
