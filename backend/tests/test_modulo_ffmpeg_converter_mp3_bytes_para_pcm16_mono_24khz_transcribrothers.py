"""Converte MP3 da ElevenLabs em PCM16 mono 24 kHz (mesmo formato do TTS Gemini)."""

from unittest.mock import MagicMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_converter_mp3_bytes_para_pcm16_mono_24khz_transcribrothers import (
    converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers,
)


def test_ffmpeg_mp3_para_pcm16_usa_stdin_e_devolve_stdout() -> None:
    fake = MagicMock()
    fake.returncode = 0
    fake.stdout = b"\x01\x00\x02\x00"
    fake.stderr = b""
    with patch("subprocess.run", return_value=fake) as run:
        pcm = converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers(
            b"ID3mp3",
            executavel_ffmpeg="ffmpeg",
        )
    assert pcm == b"\x01\x00\x02\x00"
    args = run.call_args.args[0]
    assert args[0] == "ffmpeg"
    assert "-ar" in args and "24000" in args
    assert "-f" in args and "s16le" in args
    assert run.call_args.kwargs["input"] == b"ID3mp3"


def test_ffmpeg_mp3_para_pcm16_falha_se_returncode_nao_zero() -> None:
    fake = MagicMock()
    fake.returncode = 1
    fake.stdout = b""
    fake.stderr = b"bad mp3"
    with patch("subprocess.run", return_value=fake):
        with pytest.raises(RuntimeError, match="ffmpeg"):
            converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers(
                b"xx",
                executavel_ffmpeg="ffmpeg",
            )
