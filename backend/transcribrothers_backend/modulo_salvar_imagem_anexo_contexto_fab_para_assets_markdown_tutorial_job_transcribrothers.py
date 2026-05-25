"""Grava imagem anexada no FAB (projeto em branco) em assets_exportados_para_markdown/."""

from __future__ import annotations

import time
from pathlib import Path

from transcribrothers_backend.modulo_constante_prefixo_nome_arquivo_imagem_anexo_contexto_fab_projeto_em_branco_transcribrothers import (
    PREFIXO_NOME_ARQUIVO_IMAGEM_ANEXO_CONTEXTO_FAB_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_salvar_imagem_colada_clipboard_para_assets_markdown_tutorial_job_transcribrothers import (
    _converter_arquivo_imagem_para_png_com_ffmpeg_transcribrothers,
    _extensao_entrada_a_partir_tipo_mime_imagem_colada_transcribrothers,
)


async def salvar_imagem_anexo_contexto_fab_para_assets_markdown_tutorial_job_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    conteudo_bytes: bytes,
    tipo_mime: str,
    largura_maxima_saida_pixeis: int | None = None,
) -> tuple[str, str]:
    """Retorna (nome_arquivo, caminho_relativo assets/...)."""
    if not conteudo_bytes:
        raise ValueError("Imagem vazia.")

    pasta_temp = diretorio_trabalho_job / "imagens_anexo_fab_contexto_temporario"
    assets_dir = diretorio_trabalho_job / "assets_exportados_para_markdown"
    pasta_temp.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    ms = int(time.time() * 1000)
    ext_entrada = _extensao_entrada_a_partir_tipo_mime_imagem_colada_transcribrothers(tipo_mime)
    nome_png = f"{PREFIXO_NOME_ARQUIVO_IMAGEM_ANEXO_CONTEXTO_FAB_PROJETO_EM_BRANCO_TRANSCRIBROTHERS}_ms_{ms:013d}.png"
    destino_png = assets_dir / nome_png

    entrada_temp = pasta_temp / f"entrada_{ms}{ext_entrada}"
    entrada_temp.write_bytes(conteudo_bytes)
    try:
        await _converter_arquivo_imagem_para_png_com_ffmpeg_transcribrothers(
            entrada_temp,
            destino_png,
            largura_maxima_saida_pixeis,
        )
    finally:
        entrada_temp.unlink(missing_ok=True)

    caminho_rel = f"assets/{nome_png}"
    return nome_png, caminho_rel
