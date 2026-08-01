"""Pré-corte do mux narrado: só processa ~duração da fala, não a janela inteira."""

from __future__ import annotations

from pathlib import Path

import pytest

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    calcular_duracao_precorte_clip_janela_video_transcribrothers,
    montar_script_filter_complex_passagem_unica_retarget_transcribrothers,
)


def test_precorte_com_janela_muito_maior_que_fala_usa_so_duracao_do_wav() -> None:
    """Bug real: 320s de tela para 3s de TTS — deve cortar ~3s, não 320s."""
    dur = calcular_duracao_precorte_clip_janela_video_transcribrothers(
        100.0,
        420.0,  # janela de 320s
        duracao_audio_segundos=2.97,
    )
    assert dur == pytest.approx(2.97)
    assert dur < 5.0


def test_precorte_com_fala_maior_que_janela_usa_a_janela_inteira() -> None:
    """Depois o filter faz freeze até completar o WAV."""
    dur = calcular_duracao_precorte_clip_janela_video_transcribrothers(
        10.0,
        12.0,  # 2s de tela
        duracao_audio_segundos=5.0,
    )
    assert dur == pytest.approx(2.0)


def test_precorte_janela_curta_continua_minima_para_freeze() -> None:
    dur = calcular_duracao_precorte_clip_janela_video_transcribrothers(
        5.0,
        5.05,
        duracao_audio_segundos=3.0,
    )
    assert 0.05 < dur <= 0.35


def test_script_sem_setpts_de_compressao_quando_clip_casa_com_fala() -> None:
    """Clip ≈ WAV: play 1x, sem acelerar minutos de vídeo."""
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=3.0,
        )
    ]
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segs,
        duracoes_audio_segundos=[3.0],
    )
    assert "setpts=PTS-STARTPTS" in script
    assert "*PTS" not in script  # sem setpts=fator*PTS
    assert "trim=duration=3.000000" in script


def test_script_usa_tpad_ou_loop_quando_fala_maior_que_clip() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
        )
    ]
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segs,
        duracoes_audio_segundos=[5.0],
    )
    assert "tpad=" in script or "loop=" in script
