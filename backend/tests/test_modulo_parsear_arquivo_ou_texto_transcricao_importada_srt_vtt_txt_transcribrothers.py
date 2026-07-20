import pytest

from transcribrothers_backend.modulo_util_parsear_arquivo_ou_texto_transcricao_importada_srt_vtt_txt_transcribrothers import (
    ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers,
    parsear_arquivo_ou_texto_transcricao_importada_transcribrothers,
)


def test_parsear_texto_puro_transcribrothers() -> None:
    r = parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(texto="  Olá mundo  ")
    assert r.texto_completo == "Olá mundo"
    assert len(r.segmentos) == 1


def test_parsear_texto_vazio_rejeita_transcribrothers() -> None:
    with pytest.raises(ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers):
        parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(texto="   ")


def test_parsear_srt_com_segmentos_transcribrothers() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,500
Primeira fala

2
00:00:03,000 --> 00:00:04,000
Segunda fala
"""
    r = parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(
        nome_arquivo="fala.srt",
        conteudo_arquivo=srt.encode("utf-8"),
    )
    assert len(r.segmentos) == 2
    assert r.segmentos[0].inicio_segundos == 1.0
    assert "Primeira" in r.texto_completo


def test_parsear_vtt_com_segmentos_transcribrothers() -> None:
    vtt = """WEBVTT

00:00:00.000 --> 00:00:01.000
Oi

00:00:01.500 --> 00:00:02.000
Tudo bem
"""
    r = parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(
        nome_arquivo="a.vtt",
        conteudo_arquivo=vtt,
    )
    assert len(r.segmentos) == 2
    assert "Oi" in r.texto_completo


def test_parsear_extensao_invalida_rejeita_transcribrothers() -> None:
    with pytest.raises(ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers, match="Extensão"):
        parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(
            nome_arquivo="x.exe",
            conteudo_arquivo=b"nada",
        )
