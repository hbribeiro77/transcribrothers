"""Substitui `![](assets/…png)` por links `/uploads/…` do GitLab após upload dos PNGs do job."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_cliente_gitlab_upload_arquivo_markdown_projeto_transcribrothers import (
    upload_arquivo_png_markdown_gitlab_projeto_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_nomenclatura_e_metadados_anotacao_imagens_tutorial_assets_png_transcribrothers import (
    derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers,
    nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers,
    resolver_nome_arquivo_png_para_exibicao_no_tutorial_transcribrothers,
)

_RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"!\[([^\]]*)\]\(\s*([^)]+?)\s*\)")


def resolver_arquivo_png_no_disco_para_caminho_assets_markdown_tutorial_transcribrothers(
    diretorio_assets: Path,
    caminho_relativo_assets: str,
    steps_json: dict[str, Any] | None,
) -> Path | None:
    """Resolve `assets/foo.png` para o arquivo no disco (original ou versão anotada exibida)."""
    nome = caminho_relativo_assets.strip().replace("\\", "/").split("/")[-1]
    if not nome:
        return None
    assets = diretorio_assets.resolve()
    if not assets.is_dir():
        return None

    candidato_direto = assets / nome
    if candidato_direto.is_file():
        return candidato_direto

    nome_original = nome
    if nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome):
        nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome)
        anotado_existe = (assets / nome_anotado).is_file()
        nome_exibir = resolver_nome_arquivo_png_para_exibicao_no_tutorial_transcribrothers(
            nome_original,
            steps_json,
            arquivo_anotado_existe=anotado_existe,
        )
        path_exibir = assets / nome_exibir
        if path_exibir.is_file():
            return path_exibir

    if candidato_direto.is_file():
        return candidato_direto
    return None


def reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers(
    markdown: str,
    mapa_caminho_assets_para_url_gitlab: dict[str, str],
) -> str:
    if not mapa_caminho_assets_para_url_gitlab:
        return markdown

    substituicoes: list[tuple[int, int, str, str]] = []
    for m in _RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.finditer(markdown):
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(m.group(2))
        if norm is None:
            continue
        url_gitlab = mapa_caminho_assets_para_url_gitlab.get(norm)
        if not url_gitlab:
            continue
        substituicoes.append((m.start(), m.end(), m.group(1), url_gitlab))

    saida = markdown
    for inicio, fim, texto_alt, url_gitlab in sorted(substituicoes, key=lambda t: t[0], reverse=True):
        trecho = f"![{texto_alt}]({url_gitlab})"
        saida = saida[:inicio] + trecho + saida[fim:]
    return saida


async def preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    markdown: str,
    diretorio_assets: Path,
    steps_json: dict[str, Any] | None,
    *,
    incluir_imagens_png_markdown: bool,
    project_path_gitlab: str | None = None,
) -> tuple[str, int, int]:
    """
    Devolve (markdown_para_issue, quantidade_imagens_enviadas, quantidade_imagens_ignoradas).
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
        url_gitlab = await upload_arquivo_png_markdown_gitlab_projeto_transcribrothers(
            cfg,
            conteudo_png=bytes_png,
            nome_arquivo=nome_upload,
            project_path_gitlab=project_path_gitlab,
        )
        mapa_url[caminho] = url_gitlab
        enviadas += 1

    markdown_gitlab = reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers(
        texto,
        mapa_url,
    )
    return markdown_gitlab, enviadas, ignoradas
