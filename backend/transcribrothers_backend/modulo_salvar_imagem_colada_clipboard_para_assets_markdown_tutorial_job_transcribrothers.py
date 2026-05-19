"""Grava imagem da área de transferência em assets/ do job (mesmo destino dos frames manuais)."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_constante_prefixo_nome_arquivo_imagem_colada_clipboard_markdown_tutorial_transcribrothers import (
    ORIGEM_REGISTRO_FRAME_MANUAL_CLIPBOARD_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
    PREFIXO_NOME_ARQUIVO_IMAGEM_COLADA_CLIPBOARD_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    executar_ffmpeg_com_argumentos,
)
from transcribrothers_backend.modulo_util_formatar_timestamp_segundos_para_snippet_markdown_link_temporal_transcribrothers import (
    montar_snippet_markdown_insercao_imagem_colada_clipboard_markdown_tutorial_transcribrothers,
)


def _extensao_entrada_a_partir_tipo_mime_imagem_colada_transcribrothers(tipo_mime: str) -> str:
    mime = (tipo_mime or "").split(";")[0].strip().lower()
    if mime in ("image/jpeg", "image/jpg"):
        return ".jpg"
    if mime == "image/webp":
        return ".webp"
    if mime == "image/gif":
        return ".gif"
    if mime == "image/bmp":
        return ".bmp"
    return ".png"


async def _converter_arquivo_imagem_para_png_com_ffmpeg_transcribrothers(
    caminho_entrada: Path,
    caminho_saida_png: Path,
    largura_maxima_saida_pixeis: int | None,
) -> None:
    args = ["-y", "-i", str(caminho_entrada)]
    if largura_maxima_saida_pixeis is not None and largura_maxima_saida_pixeis > 0:
        w = int(largura_maxima_saida_pixeis)
        args.extend(["-vf", f"scale=min({w}\\,iw):-2"])
    args.append(str(caminho_saida_png))
    await executar_ffmpeg_com_argumentos(args)
    if not caminho_saida_png.is_file() or caminho_saida_png.stat().st_size <= 0:
        raise RuntimeError(f"ffmpeg não gerou PNG válido: {caminho_saida_png}")


async def salvar_imagem_colada_clipboard_para_assets_markdown_tutorial_job_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    conteudo_bytes: bytes,
    tipo_mime: str,
    indice_nome_arquivo: int,
    largura_maxima_saida_pixeis: int | None = None,
) -> tuple[str, str, str]:
    """
    Persiste PNG em `assets_exportados_para_markdown/`.

    Retorna: (nome_arquivo, caminho_relativo assets/..., snippet_markdown).
    """
    if not conteudo_bytes:
        raise ValueError("Imagem vazia na área de transferência.")

    pasta_temp = diretorio_trabalho_job / "imagens_coladas_clipboard_temporario"
    assets_dir = diretorio_trabalho_job / "assets_exportados_para_markdown"
    pasta_temp.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    ms = int(time.time() * 1000)
    ext_entrada = _extensao_entrada_a_partir_tipo_mime_imagem_colada_transcribrothers(tipo_mime)
    nome_png = (
        f"{PREFIXO_NOME_ARQUIVO_IMAGEM_COLADA_CLIPBOARD_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS}"
        f"_indice_{int(indice_nome_arquivo):04d}_ms_{ms:013d}.png"
    )
    destino_png = assets_dir / nome_png

    if ext_entrada == ".png" and largura_maxima_saida_pixeis is None:
        destino_png.write_bytes(conteudo_bytes)
    else:
        entrada_temp = pasta_temp / f"entrada_{ms}{ext_entrada}"
        entrada_temp.write_bytes(conteudo_bytes)
        await _converter_arquivo_imagem_para_png_com_ffmpeg_transcribrothers(
            entrada_temp,
            destino_png,
            largura_maxima_saida_pixeis,
        )

    caminho_relativo = f"assets/{nome_png}"
    snippet = montar_snippet_markdown_insercao_imagem_colada_clipboard_markdown_tutorial_transcribrothers(
        caminho_relativo_assets=caminho_relativo,
    )
    return nome_png, caminho_relativo, snippet


def mesclar_registro_imagem_colada_clipboard_no_steps_json_transcribrothers(
    steps_json: dict,
    *,
    nome_arquivo: str,
    caminho_relativo: str,
) -> dict:
    return mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers(
        steps_json,
        timestamp_segundos_solicitado=0.0,
        timestamp_segundos_efetivo=0.0,
        nome_arquivo=nome_arquivo,
        caminho_relativo=caminho_relativo,
        origem=ORIGEM_REGISTRO_FRAME_MANUAL_CLIPBOARD_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
    )
