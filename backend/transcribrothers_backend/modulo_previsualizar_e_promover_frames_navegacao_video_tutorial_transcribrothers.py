"""Prévia de frames para ‹ › na modal: pasta temporária, sem gravar em assets até promover."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_constante_chave_steps_json_frames_manuais_capturados_video_tutorial_transcribrothers import (
    PREFIXO_NOME_ARQUIVO_FRAME_MANUAL_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    capturar_frames_png_do_video_nos_timestamps_segundos,
    limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)

NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS = (
    "frames_previsualizacao_navegacao_tutorial"
)
PREFIXO_NOME_ARQUIVO_PREVIEW_NAVEGACAO_FRAME_TUTORIAL_TRANSCRIBROTHERS = (
    "preview_navegacao_frame_tutorial"
)
_RE_INDICE_PNG = re.compile(r"_indice_\d+\.png$", re.IGNORECASE)


def diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(
    diretorio_trabalho_job: Path,
) -> Path:
    return diretorio_trabalho_job / NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS


def _nome_arquivo_seguro_preview_ou_asset_transcribrothers(nome: str) -> str | None:
    bruto = Path(str(nome or "").strip()).name
    if not bruto or ".." in bruto:
        return None
    if "/" in bruto or "\\" in bruto:
        return None
    if not re.match(r"^[a-zA-Z0-9._-]+$", bruto):
        return None
    return bruto


async def capturar_frames_previsualizacao_navegacao_video_tutorial_transcribrothers(
    *,
    caminho_video: Path,
    diretorio_trabalho_job: Path,
    timestamps_segundos: list[float],
    largura_maxima_saida_pixeis: int | None = None,
) -> list[dict[str, Any]]:
    """Extrai PNGs só na pasta de prévia. Não copia para assets nem altera steps_json."""
    dur = await obter_duracao_video_segundos_via_ffprobe(caminho_video)
    preview_dir = diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(
        diretorio_trabalho_job
    )
    preview_dir.mkdir(parents=True, exist_ok=True)
    timestamps_efetivos: list[float] = []
    for bruto in timestamps_segundos:
        t = limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
            float(bruto),
            dur,
        )
        timestamps_efetivos.append(t)
    if not timestamps_efetivos:
        return []
    deslocamento = len(list(preview_dir.glob("*.png")))
    caminhos = await capturar_frames_png_do_video_nos_timestamps_segundos(
        caminho_video=caminho_video,
        timestamps_segundos=timestamps_efetivos,
        diretorio_saida_frames=preview_dir,
        prefixo_nome_arquivo_longo_descritivo=PREFIXO_NOME_ARQUIVO_PREVIEW_NAVEGACAO_FRAME_TUTORIAL_TRANSCRIBROTHERS,
        largura_maxima_saida_pixeis=largura_maxima_saida_pixeis,
        deslocamento_indice_nome_arquivo=deslocamento,
    )
    itens: list[dict[str, Any]] = []
    for solicitado, efetivo, caminho in zip(
        timestamps_segundos, timestamps_efetivos, caminhos, strict=False
    ):
        itens.append(
            {
                "timestamp_segundos_solicitado": float(solicitado),
                "timestamp_segundos_efetivo": float(efetivo),
                "nome_arquivo": caminho.name,
            }
        )
    return itens


def promover_frame_previsualizacao_para_assets_tutorial_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    nome_arquivo_preview: str,
    indice_nome_arquivo_asset: int,
) -> tuple[str, str]:
    nome = _nome_arquivo_seguro_preview_ou_asset_transcribrothers(nome_arquivo_preview)
    if not nome:
        raise FileNotFoundError("Nome de arquivo de prévia inválido.")
    origem = diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(
        diretorio_trabalho_job
    ) / nome
    if not origem.is_file():
        raise FileNotFoundError(f"Prévia não encontrada: {nome}")
    nome_dest = nome
    prefixo_prev = PREFIXO_NOME_ARQUIVO_PREVIEW_NAVEGACAO_FRAME_TUTORIAL_TRANSCRIBROTHERS
    if nome_dest.startswith(prefixo_prev):
        nome_dest = (
            PREFIXO_NOME_ARQUIVO_FRAME_MANUAL_VIDEO_TUTORIAL_TRANSCRIBROTHERS
            + nome_dest[len(prefixo_prev) :]
        )
    indice = max(0, int(indice_nome_arquivo_asset))
    nome_dest = _RE_INDICE_PNG.sub(f"_indice_{indice:04d}.png", nome_dest)
    assets = diretorio_trabalho_job / "assets_exportados_para_markdown"
    assets.mkdir(parents=True, exist_ok=True)
    destino = assets / nome_dest
    shutil.copy2(origem, destino)
    return destino.name, f"assets/{destino.name}"


def descartar_arquivos_previsualizacao_navegacao_frame_tutorial_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    nomes_para_apagar: list[str],
    nomes_protegidos: list[str] | None = None,
) -> None:
    """Apaga só arquivos da pasta de prévia. Nunca toca em assets do documento."""
    preview_dir = diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(
        diretorio_trabalho_job
    )
    if not preview_dir.is_dir():
        return
    protegidos = {
        n for n in (_nome_arquivo_seguro_preview_ou_asset_transcribrothers(x) for x in (nomes_protegidos or [])) if n
    }
    for bruto in nomes_para_apagar:
        nome = _nome_arquivo_seguro_preview_ou_asset_transcribrothers(bruto)
        if not nome or nome in protegidos:
            continue
        caminho = preview_dir / nome
        if caminho.is_file() and caminho.resolve().parent == preview_dir.resolve():
            caminho.unlink()
