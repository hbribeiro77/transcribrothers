"""Conversão VTT → ASS com PlayRes para queima de legendas."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
)
from transcribrothers_backend.modulo_util_converter_webvtt_em_arquivo_ass_legendas_queimadas_playres_1080_transcribrothers import (
    converter_conteudo_webvtt_para_conteudo_ass_legendas_queimadas_transcribrothers,
    formatar_timestamp_ass_centissegundos_transcribrothers,
    gravar_arquivo_ass_a_partir_webvtt_legendas_queimadas_transcribrothers,
)


def test_formatar_timestamp_ass_centissegundos() -> None:
    assert formatar_timestamp_ass_centissegundos_transcribrothers(0) == "0:00:00.00"
    assert formatar_timestamp_ass_centissegundos_transcribrothers(65.5) == "0:01:05.50"


def test_converter_vtt_gera_playres_1080_e_margens_largas() -> None:
    vtt = (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:02.000\n"
        "Olá mundo da legenda\n"
    )
    ass = converter_conteudo_webvtt_para_conteudo_ass_legendas_queimadas_transcribrothers(vtt)
    assert "PlayResX: 1920" in ass
    assert "PlayResY: 1080" in ass
    assert "MarginL, MarginR, MarginV" in ass or ",40,40,28," in ass
    assert "Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,Olá mundo da legenda" in ass
    assert "Style: Default,Arial,48,&H00FFFFFF" in ass
    assert ",40,40,28,1" in ass


def test_converter_respeita_preferencia_720p() -> None:
    vtt = "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOi\n"
    ass = converter_conteudo_webvtt_para_conteudo_ass_legendas_queimadas_transcribrothers(
        vtt,
        preferencias=PreferenciasEncodeVideoNarradoTranscribrothers(resolucao="720p", fps=30),
    )
    assert "PlayResX: 1280" in ass
    assert "PlayResY: 720" in ass
    assert ",36,&H00FFFFFF" in ass


def test_gravar_arquivo_ass(tmp_path: Path) -> None:
    vtt = tmp_path / "a.vtt"
    ass_path = tmp_path / "a.ass"
    vtt.write_text(
        "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nTexto\n",
        encoding="utf-8",
    )
    gravar_arquivo_ass_a_partir_webvtt_legendas_queimadas_transcribrothers(vtt, ass_path)
    assert ass_path.is_file()
    texto = ass_path.read_text(encoding="utf-8")
    assert "PlayResX: 1920" in texto
    assert "Texto" in texto
