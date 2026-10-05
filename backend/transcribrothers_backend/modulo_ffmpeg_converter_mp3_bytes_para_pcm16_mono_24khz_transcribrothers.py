"""Converte bytes MP3 em PCM16 LE mono 24 kHz via ffmpeg (stdin/stdout)."""

from __future__ import annotations

import subprocess

_SAMPLE_RATE_HZ = 24000
_TIMEOUT_SEGUNDOS = 60.0


def converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers(
    mp3_bytes: bytes,
    *,
    executavel_ffmpeg: str,
) -> bytes:
    if not (mp3_bytes or b""):
        raise RuntimeError("Áudio MP3 vazio; não há o que converter com ffmpeg.")
    exe = (executavel_ffmpeg or "").strip()
    if not exe:
        raise RuntimeError("ffmpeg não encontrado para converter o MP3 da ElevenLabs em PCM.")
    proc = subprocess.run(
        [
            exe,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            "pipe:0",
            "-ac",
            "1",
            "-ar",
            str(_SAMPLE_RATE_HZ),
            "-f",
            "s16le",
            "pipe:1",
        ],
        input=mp3_bytes,
        capture_output=True,
        check=False,
        timeout=_TIMEOUT_SEGUNDOS,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip()[:240]
        raise RuntimeError(
            f"ffmpeg falhou ao converter MP3 da ElevenLabs (código {proc.returncode})"
            + (f": {err}" if err else ".")
        )
    pcm = proc.stdout or b""
    if not pcm:
        raise RuntimeError("ffmpeg não devolveu PCM ao converter o MP3 da ElevenLabs.")
    return pcm
