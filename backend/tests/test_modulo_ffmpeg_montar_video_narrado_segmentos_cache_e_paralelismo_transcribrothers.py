"""Cache de segmentos retarget + paralelismo na montagem do MP4 narrado."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    calcular_chave_cache_segmento_retarget_audio_transcribrothers,
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)


def _tocar(caminho: Path, conteudo: bytes = b"x") -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)


def test_chave_cache_igual_para_mesmos_metadados(tmp_path: Path) -> None:
    video = tmp_path / "v.mp4"
    wav = tmp_path / "a.wav"
    _tocar(video, b"video")
    _tocar(wav, b"audio")
    seg = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav,
        inicio_video_segundos=1.0,
        fim_video_segundos=2.5,
    )
    a = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg,
        duracao_audio_segundos=1.5,
    )
    b = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg,
        duracao_audio_segundos=1.5,
    )
    assert a == b
    assert len(a) >= 16


def test_chave_cache_muda_quando_wav_muda(tmp_path: Path) -> None:
    video = tmp_path / "v.mp4"
    wav = tmp_path / "a.wav"
    _tocar(video, b"video")
    _tocar(wav, b"audio1")
    seg = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav,
        inicio_video_segundos=0.0,
        fim_video_segundos=1.0,
    )
    antes = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg,
        duracao_audio_segundos=1.0,
    )
    _tocar(wav, b"audio2-diferente")
    depois = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg,
        duracao_audio_segundos=1.0,
    )
    assert antes != depois


def test_chave_cache_estavel_quando_wav_so_muda_de_caminho(tmp_path: Path) -> None:
    """Excluir/reordenar cue não pode invalidar cache só porque o path do WAV mudou."""
    import os
    import shutil

    video = tmp_path / "v.mp4"
    wav_a = tmp_path / "prep" / "cue_densa_0005_idx_0005.wav"
    wav_b = tmp_path / "prep" / "cue_densa_0004_idx_0004.wav"
    _tocar(video, b"video")
    _tocar(wav_a, b"RIFF" + b"\x00" * 80)
    shutil.copy2(wav_a, wav_b)
    # Garante mtime idêntico (Windows às vezes arredonda no copy).
    mtime = wav_a.stat().st_mtime_ns
    os.utime(wav_b, ns=(mtime, mtime))

    seg_a = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav_a,
        inicio_video_segundos=10.0,
        fim_video_segundos=12.0,
    )
    seg_b = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav_b,
        inicio_video_segundos=10.0,
        fim_video_segundos=12.0,
    )
    chave_a = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg_a,
        duracao_audio_segundos=2.0,
    )
    chave_b = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=seg_b,
        duracao_audio_segundos=2.0,
    )
    assert chave_a == chave_b


@pytest.mark.asyncio
async def test_montar_reusa_cache_e_nao_chama_ffmpeg_de_novo(tmp_path: Path) -> None:
    video = tmp_path / "entrada.mp4"
    wav = tmp_path / "cue.wav"
    work = tmp_path / "work"
    out_dir = tmp_path / "out"
    _tocar(video, b"fake-video")
    _tocar(wav, b"RIFF....WAVEfmt ")

    segmentos = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=wav,
            inicio_video_segundos=0.0,
            fim_video_segundos=1.0,
        )
    ]

    async def _fake_gerar(  # noqa: ANN001
        *,
        caminho_video,
        segmento,
        caminho_mp4_saida,
        preferencias_encode=None,
    ):
        del caminho_video, segmento, preferencias_encode
        caminho_mp4_saida.parent.mkdir(parents=True, exist_ok=True)
        caminho_mp4_saida.write_bytes(b"mp4-segmento")

    async def _fake_concat(args):  # noqa: ANN001
        Path(args[-1]).write_bytes(b"mp4-final")

    with (
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "segmentos_aceitam_montagem_passagem_unica_transcribrothers",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "obter_duracao_wav_pcm16_mono_segundos_transcribrothers",
            return_value=1.0,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "_gerar_segmento_mp4_retarget_audio_via_ffmpeg_transcribrothers",
            new=AsyncMock(side_effect=_fake_gerar),
        ) as mock_gerar,
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "executar_ffmpeg_com_argumentos",
            new=AsyncMock(side_effect=_fake_concat),
        ),
    ):
        saida1 = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=out_dir,
            paralelismo_encode=2,
        )
        assert saida1.is_file()
        assert mock_gerar.await_count == 1

        mock_gerar.reset_mock()
        saida2 = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=out_dir,
            paralelismo_encode=2,
        )
        assert saida2.is_file()
        assert mock_gerar.await_count == 0
