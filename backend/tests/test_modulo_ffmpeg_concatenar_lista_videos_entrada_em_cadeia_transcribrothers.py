"""Concat em cadeia de N vídeos de entrada (ffmpeg mockado)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    PerfilStreamsMidiaEntradaTranscribrothers,
    ResultadoConcatenacaoVideosEntradaTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers import (
    concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers,
)


def _perfil() -> PerfilStreamsMidiaEntradaTranscribrothers:
    return PerfilStreamsMidiaEntradaTranscribrothers(
        codec_video="h264",
        largura=1920,
        altura=1080,
        taxa_fps="30/1",
        pix_fmt="yuv420p",
        codec_audio="aac",
        sample_rate_audio=48000,
        canais_audio=2,
    )


@pytest.mark.asyncio
async def test_lista_compativel_usa_um_unico_stream_copy(tmp_path: Path) -> None:
    caminhos = []
    for i in range(3):
        p = tmp_path / f"p{i}.mp4"
        p.write_bytes(bytes([i]) * 16)
        caminhos.append(p)
    saida = tmp_path / "out.mp4"

    async def _fake_ff(args: list[str], **_k) -> None:
        Path(args[-1]).write_bytes(b"NCOPY")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(side_effect=[_perfil(), _perfil(), _perfil()]),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers.executar_ffmpeg_com_argumentos",
        new=AsyncMock(side_effect=_fake_ff),
    ) as mock_ff:
        out = await concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers(
            caminhos_videos=caminhos,
            caminho_saida=saida,
        )

    assert out.modo == "stream_copy"
    assert out.caminho_saida == saida
    assert mock_ff.await_count == 1
    assert "concat" in mock_ff.await_args.args[0]


@pytest.mark.asyncio
async def test_lista_incompativel_usa_cadeia_par_a_par(tmp_path: Path) -> None:
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.mp4"
    c = tmp_path / "c.mp4"
    for p in (a, b, c):
        p.write_bytes(b"X" * 8)
    saida = tmp_path / "out.mp4"
    chamadas = {"n": 0}

    async def _fake_par(*, caminho_video_a, caminho_video_b, caminho_saida):
        chamadas["n"] += 1
        caminho_saida.write_bytes(f"P{chamadas['n']}".encode())
        return ResultadoConcatenacaoVideosEntradaTranscribrothers(
            caminho_saida=caminho_saida,
            modo="reencode",
        )

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        new=AsyncMock(
            side_effect=[
                _perfil(),
                PerfilStreamsMidiaEntradaTranscribrothers(
                    codec_video="h264",
                    largura=1280,
                    altura=720,
                    taxa_fps="30/1",
                    pix_fmt="yuv420p",
                    codec_audio="aac",
                    sample_rate_audio=48000,
                    canais_audio=2,
                ),
                _perfil(),
            ]
        ),
    ), patch(
        "transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers.concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers",
        new=AsyncMock(side_effect=_fake_par),
    ):
        out = await concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers(
            caminhos_videos=[a, b, c],
            caminho_saida=saida,
        )

    assert out.modo == "reencode"
    assert saida.is_file()
    assert chamadas["n"] == 2  # (a+b) depois (+c)
