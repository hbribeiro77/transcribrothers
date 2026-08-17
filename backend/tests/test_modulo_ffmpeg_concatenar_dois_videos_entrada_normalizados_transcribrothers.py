"""Concat de dois vídeos de entrada: stream copy rápido ou reencode (ffmpeg mockado)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    PerfilStreamsMidiaEntradaTranscribrothers,
    concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers,
    perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
)


def _perfil(
    *,
    codec_v: str = "h264",
    w: int = 1920,
    h: int = 1080,
    fps: str = "30/1",
    pix: str = "yuv420p",
    codec_a: str | None = "aac",
    sr: int | None = 48000,
    ch: int | None = 2,
) -> PerfilStreamsMidiaEntradaTranscribrothers:
    return PerfilStreamsMidiaEntradaTranscribrothers(
        codec_video=codec_v,
        largura=w,
        altura=h,
        taxa_fps=fps,
        pix_fmt=pix,
        codec_audio=codec_a,
        sample_rate_audio=sr,
        canais_audio=ch,
    )


def test_perfis_compativeis_quando_video_e_audio_iguais() -> None:
    assert perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(
        _perfil(),
        _perfil(),
    )


def test_perfis_incompativeis_quando_resolucao_difere() -> None:
    assert not perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(
        _perfil(w=1920, h=1080),
        _perfil(w=1280, h=720),
    )


def test_perfis_incompativeis_quando_um_tem_audio_e_outro_nao() -> None:
    assert not perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(
        _perfil(codec_a="aac", sr=48000, ch=2),
        _perfil(codec_a=None, sr=None, ch=None),
    )


@pytest.mark.asyncio
async def test_concat_usa_stream_copy_quando_compativeis(tmp_path: Path) -> None:
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.mp4"
    a.write_bytes(b"A" * 32)
    b.write_bytes(b"B" * 32)
    saida = tmp_path / "unificado.mp4"
    perfil = _perfil()

    async def _fake_ffmpeg(args: list[str], **_kwargs) -> None:
        Path(args[-1]).write_bytes(b"COPYOK")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[perfil, perfil]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.executar_ffmpeg_com_argumentos",
        new=AsyncMock(side_effect=_fake_ffmpeg),
    ) as mock_ff:
        out = await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
            caminho_video_a=a,
            caminho_video_b=b,
            caminho_saida=saida,
        )

    assert out.caminho_saida == saida
    assert out.modo == "stream_copy"
    assert saida.read_bytes() == b"COPYOK"
    assert mock_ff.await_count == 1
    args = mock_ff.await_args.args[0]
    assert "concat" in args and "copy" in args
    assert "-filter_complex" not in args


@pytest.mark.asyncio
async def test_concat_reencoda_quando_incompativeis(tmp_path: Path) -> None:
    a = tmp_path / "a.webm"
    b = tmp_path / "b.webm"
    a.write_bytes(b"A" * 32)
    b.write_bytes(b"B" * 32)
    saida = tmp_path / "unificado.mp4"

    async def _fake_ffmpeg(args: list[str], **_kwargs) -> None:
        Path(args[-1]).write_bytes(b"MP4FAKE")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[_perfil(w=1920), _perfil(w=1280)]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[True, True]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.executar_ffmpeg_com_argumentos",
        new=AsyncMock(side_effect=_fake_ffmpeg),
    ) as mock_ff:
        out = await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
            caminho_video_a=a,
            caminho_video_b=b,
            caminho_saida=saida,
        )

    assert out.modo == "reencode"
    assert out.caminho_saida == saida
    assert mock_ff.await_count == 3  # 2 normalizações + 1 concat


@pytest.mark.asyncio
async def test_concat_fallback_reencode_se_stream_copy_falhar(tmp_path: Path) -> None:
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.mp4"
    a.write_bytes(b"A" * 32)
    b.write_bytes(b"B" * 32)
    saida = tmp_path / "unificado.mp4"
    perfil = _perfil()
    chamadas = {"n": 0}

    async def _fake_ffmpeg(args: list[str], **_kwargs) -> None:
        chamadas["n"] += 1
        if chamadas["n"] == 1:
            raise ErroFfmpegTranscribrothers("concat copy falhou")
        Path(args[-1]).write_bytes(b"REENC")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[perfil, perfil]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[True, True]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.executar_ffmpeg_com_argumentos",
        new=AsyncMock(side_effect=_fake_ffmpeg),
    ) as mock_ff:
        out = await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
            caminho_video_a=a,
            caminho_video_b=b,
            caminho_saida=saida,
        )

    assert out.modo == "reencode"
    assert saida.read_bytes() == b"REENC"
    # 1 copy falhou + 2 norm + 1 concat = 4
    assert mock_ff.await_count == 4


@pytest.mark.asyncio
async def test_concatenar_falha_se_ffmpeg_nao_gerar_saida(tmp_path: Path) -> None:
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.mp4"
    a.write_bytes(b"A")
    b.write_bytes(b"B")
    saida = tmp_path / "out.mp4"

    async def _fake_parcial(args: list[str], **_kwargs) -> None:
        destino = Path(args[-1])
        if destino.name.startswith("norm_"):
            destino.write_bytes(b"TMP")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[_perfil(w=1920), _perfil(w=1280)]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.executar_ffmpeg_com_argumentos",
        new=AsyncMock(side_effect=_fake_parcial),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[True, True]),
    ), pytest.raises(RuntimeError, match="sem gerar"):
        await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
            caminho_video_a=a,
            caminho_video_b=b,
            caminho_saida=saida,
        )
