"""Mux: cópia do vídeo com áudio trocado pela narração TTS."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
    substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers,
)


@pytest.mark.asyncio
async def test_substituir_audio_chama_ffmpeg_com_map_e_shortest(tmp_path: Path) -> None:
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    wav = tmp_path / "narracao_tts_documento.wav"
    video.write_bytes(b"fake")
    wav.write_bytes(b"RIFF")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers.executar_ffmpeg_com_argumentos",
        new_callable=AsyncMock,
    ) as mock_ff:
        async def _fake_ffmpeg(args: list[str]) -> None:
            # Simula criação do arquivo de saída
            out = Path(args[-1])
            out.write_bytes(b"mp4fake")

        mock_ff.side_effect = _fake_ffmpeg

        caminho = await substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers(
            caminho_video=video,
            caminho_narracao_wav=wav,
            diretorio_saida=tmp_path,
        )

    assert caminho.name == NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    assert caminho.is_file()
    args = mock_ff.await_args.args[0]
    assert "-i" in args
    assert str(video) in args
    assert str(wav) in args
    assert "-map" in args
    assert "0:v:0" in args
    assert "1:a:0" in args
    assert "-c:v" in args and "copy" in args
    assert "-shortest" in args


@pytest.mark.asyncio
async def test_substituir_audio_falha_se_video_ausente(tmp_path: Path) -> None:
    wav = tmp_path / "narracao_tts_documento.wav"
    wav.write_bytes(b"RIFF")
    with pytest.raises(FileNotFoundError, match="vídeo"):
        await substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers(
            caminho_video=tmp_path / "nao_existe.mp4",
            caminho_narracao_wav=wav,
            diretorio_saida=tmp_path,
        )


@pytest.mark.asyncio
async def test_substituir_audio_falha_se_narracao_ausente(tmp_path: Path) -> None:
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"fake")
    with pytest.raises(FileNotFoundError, match="narração"):
        await substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers(
            caminho_video=video,
            caminho_narracao_wav=tmp_path / "faltando.wav",
            diretorio_saida=tmp_path,
        )
