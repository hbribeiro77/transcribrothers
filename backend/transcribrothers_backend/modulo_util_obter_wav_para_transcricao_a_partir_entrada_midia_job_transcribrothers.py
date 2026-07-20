"""Obtém WAV para STT a partir de vídeo (ffmpeg) ou arquivo de áudio (normaliza/copia)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    extrair_audio_wav_de_video_para_caminho,
)


def localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(work: Path) -> tuple[Path | None, str]:
    """Retorna (caminho, tipo) com tipo video|audio; (None, '') se não achar."""
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        matches = sorted(work.glob(pattern))
        if matches:
            return matches[0], "video"
    for pattern in ("audio_entrada_arquivo_local.*",):
        matches = sorted(work.glob(pattern))
        if matches:
            return matches[0], "audio"
    return None, ""


def resolver_tipo_entrada_midia_do_steps_ou_disco_transcribrothers(
    steps: dict[str, Any],
    work: Path,
) -> str:
    tip = str(steps.get("tipo_entrada_midia") or "").strip()
    if tip in {"video", "audio"}:
        return tip
    _caminho, tip_disco = localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(work)
    return tip_disco or "video"


async def garantir_wav_para_transcricao_a_partir_entrada_midia_job_transcribrothers(
    *,
    work: Path,
    steps: dict[str, Any],
    caminho_wav_destino: Path,
    forcar_mono: bool = True,
    caminho_video_ja_resolvido: Path | None = None,
) -> Path:
    """
    Garante `caminho_wav_destino` pronto para STT.
    - vídeo: extrai com ffmpeg
    - áudio .wav: copia (ou re-extrai se precisar mono)
    - outros áudios: converte via ffmpeg (mesmo comando -i arquivo)
    """
    tipo = resolver_tipo_entrada_midia_do_steps_ou_disco_transcribrothers(steps, work)
    if tipo == "audio":
        entrada, _ = localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(work)
        if entrada is None:
            raise FileNotFoundError("Arquivo de áudio de entrada não encontrado no diretório do job.")
        caminho_wav_destino.parent.mkdir(parents=True, exist_ok=True)
        if entrada.suffix.lower() == ".wav" and not forcar_mono:
            shutil.copy2(entrada, caminho_wav_destino)
        else:
            # Reutiliza o extrator: ffmpeg -i áudio → pcm wav (funciona sem faixa de vídeo).
            await extrair_audio_wav_de_video_para_caminho(
                caminho_video=entrada,
                caminho_audio_wav=caminho_wav_destino,
                forcar_mono=forcar_mono,
            )
        steps["tipo_entrada_midia"] = "audio"
        steps["audio_entrada_filename"] = entrada.name
        return caminho_wav_destino

    video = caminho_video_ja_resolvido
    if video is None:
        video, _ = localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(work)
    if video is None:
        raise FileNotFoundError("Arquivo de vídeo de entrada não encontrado no diretório do job.")
    await extrair_audio_wav_de_video_para_caminho(
        caminho_video=video,
        caminho_audio_wav=caminho_wav_destino,
        forcar_mono=forcar_mono,
    )
    steps["tipo_entrada_midia"] = "video"
    return caminho_wav_destino
