"""Pré-corte de janelas em clips pequenos antes da passagem única (mux narrado)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    calcular_duracao_precorte_clip_janela_video_transcribrothers,
    montar_script_filter_complex_passagem_unica_retarget_transcribrothers,
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)


def test_duracao_precorte_fala_maior_que_janela_usa_tamanho_da_janela() -> None:
    assert calcular_duracao_precorte_clip_janela_video_transcribrothers(
        1.0,
        3.5,
        duracao_audio_segundos=10.0,
    ) == pytest.approx(2.5)


def test_duracao_precorte_janela_curta_fica_limitada_e_positiva() -> None:
    dur = calcular_duracao_precorte_clip_janela_video_transcribrothers(
        5.0,
        5.05,
        duracao_audio_segundos=3.0,
    )
    assert 0.05 < dur <= 0.35


def test_script_passagem_unica_com_clips_precorte_usa_duracao_do_clip_desde_zero() -> None:
    """Após pré-corte, o filter trata o vídeo como começando em t=0."""
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=1.5,
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("b.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=0.12,  # curto → freeze
        ),
    ]
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segs,
        duracoes_audio_segundos=[1.5, 2.0],
    )
    assert "[0:v]trim=duration=" in script
    assert "loop=loop=-1:size=1:start=0" in script
    assert "concat=n=2:v=1:a=1[vout][aout]" in script


@pytest.mark.asyncio
async def test_montar_precorta_clips_antes_do_encode_unico(tmp_path: Path) -> None:
    video = tmp_path / "origem_longa.mp4"
    wav_a = tmp_path / "a.wav"
    wav_b = tmp_path / "b.wav"
    work = tmp_path / "work"
    out_dir = tmp_path / "out"
    video.write_bytes(b"fake-video-grande")
    wav_a.write_bytes(b"RIFF....WAVEfmt ")
    wav_b.write_bytes(b"RIFF....WAVEfmt ")

    segmentos = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=wav_a,
            inicio_video_segundos=10.0,
            fim_video_segundos=12.0,
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=wav_b,
            inicio_video_segundos=40.0,
            fim_video_segundos=43.0,
        ),
    ]

    fases: list[str] = []

    async def _progresso(payload: dict) -> None:  # noqa: ANN001
        fase = payload.get("video_narrado_mux_fase")
        if isinstance(fase, str):
            fases.append(fase)

    async def _fake_ffmpeg(args: list[str]) -> None:
        saida = Path(args[-1])
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_bytes(b"mp4")

    mod = (
        "transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers"
    )
    mock_ff = AsyncMock(side_effect=_fake_ffmpeg)
    with (
        patch(f"{mod}.obter_duracao_wav_pcm16_mono_segundos_transcribrothers", return_value=1.0),
        patch(f"{mod}.resolver_encoder_video_montagem_narrado_transcribrothers", return_value="libx264"),
        patch(f"{mod}.executar_ffmpeg_com_argumentos", new=mock_ff),
    ):
        saida = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=out_dir,
            atualizar_progresso=_progresso,
        )

    assert saida.is_file()
    assert "precorte" in fases
    assert "passagem_unica" in fases
    # 2 pré-cortes + 1 encode final (passagem única)
    assert mock_ff.await_count >= 3

    args_todos = [c.args[0] for c in mock_ff.await_args_list]
    args_precorte = [a for a in args_todos if "-filter_complex_script" not in a]
    assert len(args_precorte) >= 2
    for args in args_precorte:
        assert "-ss" in args
        assert "-t" in args
        assert str(video) in args
        assert str(wav_a) not in args
        assert str(wav_b) not in args

    args_encode = next(a for a in args_todos if "-filter_complex_script" in a)
    assert str(video) not in args_encode
    assert any("clip_precorte_" in str(a) for a in args_encode)
