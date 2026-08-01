"""Queima de legendas VTT no MP4 narrado (download com legenda embutida)."""

from __future__ import annotations

import os
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers import (
    NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS,
    NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS,
    escapar_texto_caminho_posix_para_filtro_subtitles_ffmpeg_transcribrothers,
    montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers,
    obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers,
    queimar_legendas_vtt_no_video_mp4_via_ffmpeg_transcribrothers,
    video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def test_escapar_texto_caminho_posix_escapa_drive_letter_com_barra_dupla() -> None:
    escapado = escapar_texto_caminho_posix_para_filtro_subtitles_ffmpeg_transcribrothers(
        "D:/jobs/abc/legenda's.vtt"
    )
    assert escapado == "D\\\\:/jobs/abc/legenda\\'s.vtt"


def test_montar_filtro_vf_scale_antes_de_ass() -> None:
    filtro = montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers(
        NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS
    )
    assert filtro.startswith("scale=")
    assert ",fps=30," in filtro or ",fps=30" in filtro
    assert "1080" in filtro
    assert filtro.endswith(f",ass={NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS}")
    assert "force_style" not in filtro
    assert "subtitles=" not in filtro


def test_montar_filtro_vf_rejeita_nome_relativo_com_pasta() -> None:
    with pytest.raises(ValueError, match="sem pastas"):
        montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers("pasta/legenda.ass")


def test_cache_legendas_queimadas_atualizado_quando_saida_mais_nova(tmp_path: Path) -> None:
    video = tmp_path / "v.mp4"
    vtt = tmp_path / "l.vtt"
    saida = tmp_path / "out.mp4"
    video.write_bytes(b"a")
    vtt.write_bytes(b"b")
    saida.write_bytes(b"c")
    assert video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
        caminho_video_mp4=video,
        caminho_vtt=vtt,
        caminho_saida=saida,
    )


def test_cache_legendas_queimadas_desatualizado_quando_vtt_mais_novo(tmp_path: Path) -> None:
    video = tmp_path / "v.mp4"
    vtt = tmp_path / "l.vtt"
    saida = tmp_path / "out.mp4"
    video.write_bytes(b"a")
    saida.write_bytes(b"c")
    vtt.write_bytes(b"b")
    agora = time.time()
    os.utime(saida, (agora - 100, agora - 100))
    os.utime(video, (agora - 50, agora - 50))
    os.utime(vtt, (agora, agora))
    assert not video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
        caminho_video_mp4=video,
        caminho_vtt=vtt,
        caminho_saida=saida,
    )


@pytest.mark.asyncio
async def test_queimar_legendas_usa_ass_relativo_apos_scale_e_cwd_saida(
    tmp_path: Path,
) -> None:
    from transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers import (
        NOME_ARQUIVO_MP4_TEMPORARIO_QUEIMA_LEGENDAS_TRANSCRIBROTHERS,
    )

    video = tmp_path / "video.mp4"
    vtt = tmp_path / "legendas.vtt"
    saida = tmp_path / "out.mp4"
    video.write_bytes(b"fake")
    vtt.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOi\n", encoding="utf-8")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers.executar_ffmpeg_com_argumentos",
        new_callable=AsyncMock,
    ) as mock_ff:
        async def _fake(args: list[str], *, cwd: Path | None = None) -> None:
            assert cwd == tmp_path.resolve()
            destino = Path(args[-1])
            assert destino.name == NOME_ARQUIVO_MP4_TEMPORARIO_QUEIMA_LEGENDAS_TRANSCRIBROTHERS
            assert not saida.is_file()
            # ASS temporário deve existir no momento do ffmpeg.
            assert (tmp_path / NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS).is_file()
            destino.write_bytes(b"mp4")

        mock_ff.side_effect = _fake
        with patch(
            "transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers.resolver_encoder_video_montagem_narrado_transcribrothers",
            return_value="libx264",
        ):
            caminho = await queimar_legendas_vtt_no_video_mp4_via_ffmpeg_transcribrothers(
                caminho_video_mp4=video,
                caminho_vtt=vtt,
                caminho_saida=saida,
            )

    assert caminho == saida
    assert saida.is_file()
    assert saida.read_bytes() == b"mp4"
    assert not (tmp_path / NOME_ARQUIVO_MP4_TEMPORARIO_QUEIMA_LEGENDAS_TRANSCRIBROTHERS).is_file()
    args = mock_ff.await_args.args[0]
    assert "-vf" in args
    idx = args.index("-vf")
    vf = args[idx + 1]
    assert vf.startswith("scale=")
    assert f",ass={NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS}" in vf
    assert "force_style" not in vf
    assert "-c:a" in args and "copy" in args
    assert "-c:v" in args and "libx264" in args
    assert not (tmp_path / NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS).is_file()


@pytest.mark.asyncio
async def test_obter_ou_gerar_reutiliza_cache_sem_chamar_ffmpeg(tmp_path: Path) -> None:
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    video = work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    vtt = assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    saida = work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS
    video.write_bytes(b"v")
    vtt.write_bytes(b"t")
    saida.write_bytes(b"cached")

    with patch(
        "transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers.queimar_legendas_vtt_no_video_mp4_via_ffmpeg_transcribrothers",
        new_callable=AsyncMock,
    ) as mock_queim:
        caminho = await obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers(
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
        )
    mock_queim.assert_not_awaited()
    assert caminho == saida
    assert saida.read_bytes() == b"cached"


@pytest.mark.asyncio
async def test_obter_ou_gerar_falha_sem_video(tmp_path: Path) -> None:
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
        "WEBVTT\n", encoding="utf-8"
    )
    with pytest.raises(FileNotFoundError, match="vídeo narrado"):
        await obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers(
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
        )
