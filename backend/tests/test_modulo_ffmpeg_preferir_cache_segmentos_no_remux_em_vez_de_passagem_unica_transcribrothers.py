"""Remux/edições: preferir segmentos+cache (só reencode o que mudou) em vez de passagem única."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    contar_segmentos_com_mp4_cache_retarget_disponivel_transcribrothers,
    deve_usar_montagem_por_segmentos_com_cache_em_vez_de_passagem_unica_transcribrothers,
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)


def _tocar(caminho: Path, conteudo: bytes = b"x") -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)


def test_contar_hits_cache_segmentos_retarget_transcribrothers(tmp_path: Path) -> None:
    video = tmp_path / "v.mp4"
    wav_a = tmp_path / "a.wav"
    wav_b = tmp_path / "b.wav"
    work = tmp_path / "work"
    _tocar(video, b"video")
    _tocar(wav_a, b"wav-a")
    _tocar(wav_b, b"wav-b")
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=wav_a, inicio_video_segundos=0.0, fim_video_segundos=1.0
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=wav_b, inicio_video_segundos=1.0, fim_video_segundos=2.0
        ),
    ]
    duracoes = [1.0, 1.0]
    hits0, total0 = contar_segmentos_com_mp4_cache_retarget_disponivel_transcribrothers(
        caminho_video=video,
        segmentos=segs,
        duracoes_audio_segundos=duracoes,
        diretorio_trabalho=work,
    )
    assert total0 == 2
    assert hits0 == 0

    from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
        calcular_chave_cache_segmento_retarget_audio_transcribrothers,
    )

    chave = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=segs[0],
        duracao_audio_segundos=1.0,
    )
    cache = work / "segmentos_video_narrado_retarget" / f"segmento_cache_{chave[:24]}.mp4"
    _tocar(cache, b"mp4-seg")

    hits1, total1 = contar_segmentos_com_mp4_cache_retarget_disponivel_transcribrothers(
        caminho_video=video,
        segmentos=segs,
        duracoes_audio_segundos=duracoes,
        diretorio_trabalho=work,
    )
    assert total1 == 2
    assert hits1 == 1


def test_deve_usar_cache_quando_ha_hits_ou_forcado_transcribrothers() -> None:
    assert deve_usar_montagem_por_segmentos_com_cache_em_vez_de_passagem_unica_transcribrothers(
        hits_cache=0, total_segmentos=5, forcar_montagem_por_segmentos_com_cache=False
    ) is False
    assert deve_usar_montagem_por_segmentos_com_cache_em_vez_de_passagem_unica_transcribrothers(
        hits_cache=1, total_segmentos=5, forcar_montagem_por_segmentos_com_cache=False
    ) is True
    assert deve_usar_montagem_por_segmentos_com_cache_em_vez_de_passagem_unica_transcribrothers(
        hits_cache=0, total_segmentos=5, forcar_montagem_por_segmentos_com_cache=True
    ) is True
    assert deve_usar_montagem_por_segmentos_com_cache_em_vez_de_passagem_unica_transcribrothers(
        hits_cache=5, total_segmentos=5, forcar_montagem_por_segmentos_com_cache=False
    ) is True


@pytest.mark.asyncio
async def test_montar_com_forcar_cache_nao_usa_passagem_unica_transcribrothers(tmp_path: Path) -> None:
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

    async def _fake_gerar(*, caminho_video, segmento, caminho_mp4_saida, preferencias_encode=None):  # noqa: ANN001
        del caminho_video, segmento, preferencias_encode
        caminho_mp4_saida.parent.mkdir(parents=True, exist_ok=True)
        caminho_mp4_saida.write_bytes(b"mp4-segmento")

    async def _fake_ffmpeg(args):  # noqa: ANN001
        Path(args[-1]).write_bytes(b"mp4-final")

    with (
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "segmentos_aceitam_montagem_passagem_unica_transcribrothers",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "_montar_passagem_unica_filter_complex_transcribrothers",
            new=AsyncMock(side_effect=AssertionError("não deveria usar passagem única")),
        ) as mock_unica,
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "obter_duracao_wav_pcm16_mono_segundos_transcribrothers",
            return_value=1.0,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "_gerar_segmento_mp4_retarget_audio_via_ffmpeg_transcribrothers",
            new=AsyncMock(side_effect=_fake_gerar),
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "executar_ffmpeg_com_argumentos",
            new=AsyncMock(side_effect=_fake_ffmpeg),
        ),
    ):
        saida = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=out_dir,
            forcar_montagem_por_segmentos_com_cache=True,
        )
        assert saida.is_file()
        mock_unica.assert_not_awaited()


@pytest.mark.asyncio
async def test_montar_com_hit_cache_pula_passagem_unica_mesmo_sem_forcar_transcribrothers(
    tmp_path: Path,
) -> None:
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

    from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
        calcular_chave_cache_segmento_retarget_audio_transcribrothers,
    )

    chave = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
        caminho_video=video,
        segmento=segmentos[0],
        duracao_audio_segundos=1.0,
    )
    cache = work / "segmentos_video_narrado_retarget" / f"segmento_cache_{chave[:24]}.mp4"
    _tocar(cache, b"mp4-seg-cache")

    async def _fake_ffmpeg(args):  # noqa: ANN001
        Path(args[-1]).write_bytes(b"mp4-final")

    with (
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "segmentos_aceitam_montagem_passagem_unica_transcribrothers",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "_montar_passagem_unica_filter_complex_transcribrothers",
            new=AsyncMock(side_effect=AssertionError("não deveria usar passagem única")),
        ) as mock_unica,
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "obter_duracao_wav_pcm16_mono_segundos_transcribrothers",
            return_value=1.0,
        ),
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "_gerar_segmento_mp4_retarget_audio_via_ffmpeg_transcribrothers",
            new=AsyncMock(side_effect=AssertionError("não deveria reencode segmento em cache")),
        ) as mock_gerar,
        patch(
            "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers."
            "executar_ffmpeg_com_argumentos",
            new=AsyncMock(side_effect=_fake_ffmpeg),
        ),
    ):
        saida = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=out_dir,
            forcar_montagem_por_segmentos_com_cache=False,
        )
        assert saida.is_file()
        mock_unica.assert_not_awaited()
        mock_gerar.assert_not_awaited()
