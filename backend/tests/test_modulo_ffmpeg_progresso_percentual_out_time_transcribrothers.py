"""Parsing de progresso ffmpeg (-progress) para % de encode."""

from __future__ import annotations

from transcribrothers_backend.modulo_util_parse_progresso_ffmpeg_out_time_para_percentual_transcribrothers import (
    percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers,
)


def test_percentual_a_partir_out_time_hms() -> None:
    pct = percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
        "out_time=00:00:05.000000",
        duracao_entrada_segundos=10.0,
    )
    assert pct == 50.0


def test_percentual_a_partir_out_time_us() -> None:
    pct = percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
        "out_time_us=5000000",
        duracao_entrada_segundos=10.0,
    )
    assert pct == 50.0


def test_percentual_out_time_ms_legado_em_microssegundos() -> None:
    pct = percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
        "out_time_ms=5000000",
        duracao_entrada_segundos=10.0,
    )
    assert pct == 50.0


def test_percentual_ignora_linha_irrelevante() -> None:
    assert (
        percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
            "frame=123",
            duracao_entrada_segundos=10.0,
        )
        is None
    )


def test_percentual_limita_a_100() -> None:
    pct = percentual_encode_ffmpeg_a_partir_linha_progresso_transcribrothers(
        "out_time=00:00:20.000000",
        duracao_entrada_segundos=10.0,
    )
    assert pct == 100.0
