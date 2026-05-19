"""Remove `![](assets/…png)` e link temporal `?t=` logo abaixo, se existir."""

from __future__ import annotations

import re

from transcribrothers_backend.modulo_util_nomenclatura_e_metadados_anotacao_imagens_tutorial_assets_png_transcribrothers import (
    nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers,
)

_RE_LINHA_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"!\[[^\]]*]\(\s*([^)]+?)\s*\)")
_RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"^\s*\[[^\]]*]\(\?t=[^)]+\)\s*$")


def _normalizar_caminho_asset_na_referencia_markdown_transcribrothers(raw: str) -> str:
    caminho = raw.strip().strip('"').strip("'")
    if "?" in caminho:
        caminho = caminho.split("?", 1)[0].strip()
    if "#" in caminho:
        caminho = caminho.split("#", 1)[0].strip()
    return caminho.replace("\\", "/").lstrip("./")


def _resolver_nome_original_a_partir_referencia_assets_transcribrothers(nome_na_referencia: str) -> str:
    n = nome_na_referencia.strip()
    if ".anotado.png" in n.lower():
        return n[: -len(".anotado.png")] + ".png"
    return n


def _linha_markdown_referencia_imagem_asset_tutorial_transcribrothers(
    linha: str,
    nome_arquivo_original: str,
) -> bool:
    correspondencia = _RE_LINHA_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.search(linha)
    if not correspondencia:
        return False
    caminho = _normalizar_caminho_asset_na_referencia_markdown_transcribrothers(correspondencia.group(1))
    if not caminho.lower().endswith(".png"):
        return False
    nome_na_referencia = caminho.rsplit("/", 1)[-1]
    nome_resolvido = _resolver_nome_original_a_partir_referencia_assets_transcribrothers(nome_na_referencia)
    return nome_resolvido == nome_arquivo_original


def markdown_tutorial_referencia_imagem_asset_transcribrothers(
    markdown: str,
    nome_arquivo_original: str,
) -> bool:
    if not (markdown or "").strip():
        return False
    for linha in markdown.replace("\r\n", "\n").split("\n"):
        if _linha_markdown_referencia_imagem_asset_tutorial_transcribrothers(linha, nome_arquivo_original):
            return True
    return False


def remover_referencia_imagem_asset_do_markdown_tutorial_transcribrothers(
    markdown: str,
    nome_arquivo_original: str,
) -> str:
    linhas = markdown.replace("\r\n", "\n").split("\n")
    linhas_filtradas: list[str] = []
    indice = 0

    while indice < len(linhas):
        linha = linhas[indice]

        if not _linha_markdown_referencia_imagem_asset_tutorial_transcribrothers(linha, nome_arquivo_original):
            linhas_filtradas.append(linha)
            indice += 1
            continue

        indice += 1

        while indice < len(linhas) and linhas[indice].strip() == "":
            indice += 1

        if (
            indice < len(linhas)
            and _RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS.match(linhas[indice])
        ):
            indice += 1
            while indice < len(linhas) and linhas[indice].strip() == "":
                indice += 1

    texto = "\n".join(linhas_filtradas)
    while "\n\n\n" in texto:
        texto = texto.replace("\n\n\n", "\n\n")
    return texto.rstrip()


def nome_arquivo_png_original_valido_para_exclusao_asset_tutorial_transcribrothers(nome: str) -> bool:
    return nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome)
