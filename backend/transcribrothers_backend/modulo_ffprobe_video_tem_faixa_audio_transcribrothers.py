"""Detecta se o container de vídeo possui ao menos uma faixa de áudio (ffprobe)."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    resolver_caminho_ffprobe_transcribrothers,
)


def _executar_ffprobe_streams_audio_sync(
    executavel_ffprobe: str,
    caminho_video: str,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            executavel_ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            caminho_video,
        ],
        capture_output=True,
        check=False,
    )


async def video_tem_faixa_audio_via_ffprobe_transcribrothers(caminho_video: Path) -> bool:
    executavel = resolver_caminho_ffprobe_transcribrothers()
    if not executavel:
        return False
    proc = await asyncio.to_thread(_executar_ffprobe_streams_audio_sync, executavel, str(caminho_video))
    if proc.returncode != 0:
        return False
    saida = (proc.stdout or b"").decode(errors="replace").strip()
    return bool(saida)
