"""Passagem única ffmpeg (filter_complex) para montar vídeo narrado."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    montar_script_filter_complex_passagem_unica_retarget_transcribrothers,
    segmentos_aceitam_montagem_passagem_unica_transcribrothers,
)


def test_segmentos_curtos_aceitam_passagem_unica_com_freeze() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=1.0,
            fim_video_segundos=1.1,  # 0.1s — freeze no filter
        )
    ]
    assert segmentos_aceitam_montagem_passagem_unica_transcribrothers(
        segs,
        duracoes_audio_segundos=[1.0],
    )


def test_segmentos_normais_aceitam_passagem_unica() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("b.wav"),
            inicio_video_segundos=5.0,
            fim_video_segundos=8.0,
        ),
    ]
    assert segmentos_aceitam_montagem_passagem_unica_transcribrothers(
        segs,
        duracoes_audio_segundos=[1.5, 2.0],
    )


def test_audio_sem_duracao_rejeita_passagem_unica() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
        )
    ]
    assert not segmentos_aceitam_montagem_passagem_unica_transcribrothers(
        segs,
        duracoes_audio_segundos=[0.01],
    )


def test_script_filter_complex_play_1x_e_concat() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=1.0,
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("b.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=1.5,
        ),
    ]
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segs,
        duracoes_audio_segundos=[1.0, 1.5],
    )
    assert "[0:v]trim=duration=1.000000" in script
    assert "[2:v]trim=duration=1.500000" in script
    assert "[1:a]atrim=" in script
    assert "concat=n=2:v=1:a=1[vout][aout]" in script
    assert "[v0][a0][v1][a1]" in script
    # Não comprime vídeo com setpts=fator*PTS
    assert "*PTS" not in script
    # Padrão de encode do app: 1080p @ 30 fps
    assert "fps=30" in script
    assert "1080" in script


def test_script_filter_complex_usa_freeze_em_janela_curta() -> None:
    segs = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("a.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=0.12,
        ),
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=Path("b.wav"),
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
        ),
    ]
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segs,
        duracoes_audio_segundos=[1.2, 2.0],
    )
    assert "loop=loop=-1:size=1:start=0" in script
    assert "[0:v]trim=start=0:end=0.05" in script
    assert "[2:v]trim=duration=2.000000" in script
    assert "concat=n=2:v=1:a=1[vout][aout]" in script
