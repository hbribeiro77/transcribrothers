"""Partir texto, alinhar a segmentos STT e gerar VTT."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    gerar_conteudo_vtt_a_partir_cues_legendas_transcribrothers,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)


def test_partir_texto_em_frases() -> None:
    texto = "Primeira frase. Segunda frase! Terceira?"
    frases = partir_texto_plano_em_frases_para_legendas_transcribrothers(texto)
    assert len(frases) == 3
    assert frases[0].startswith("Primeira")
    assert frases[1].startswith("Segunda")


def test_alinhar_frases_casa_com_segmentos_e_interpola_gap() -> None:
    segmentos = [
        SegmentoTranscricaoComTempo(0.0, 2.0, "abra o menu principal"),
        SegmentoTranscricaoComTempo(2.0, 4.0, "clique em salvar agora"),
        SegmentoTranscricaoComTempo(4.0, 6.0, "confirme a operacao"),
    ]
    frases = [
        "Abra o menu principal do sistema.",
        "Texto sem parecido nenhum xyzabc.",
        "Clique em salvar agora.",
    ]
    resultado = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
        frases,
        segmentos,
    )
    assert len(resultado.cues) == 3
    assert resultado.cues[0].casado is True
    assert resultado.cues[0].inicio_segundos == 0.0
    assert resultado.cues[2].casado is True
    assert resultado.quantidade_casadas >= 2
    assert resultado.percentual_casado > 0


def test_gerar_e_gravar_vtt(tmp_path: Path) -> None:
    segmentos = [
        SegmentoTranscricaoComTempo(1.0, 3.5, "ola mundo"),
    ]
    resultado = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
        ["Olá mundo."],
        segmentos,
    )
    conteudo = gerar_conteudo_vtt_a_partir_cues_legendas_transcribrothers(resultado.cues)
    assert conteudo.startswith("WEBVTT")
    assert "-->" in conteudo
    assert "Olá mundo" in conteudo

    path = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
        diretorio_assets=tmp_path,
        cues=resultado.cues,
    )
    assert path.name == NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    assert path.is_file()
    assert "WEBVTT" in path.read_text(encoding="utf-8")


def test_alinhar_com_duracao_video_descarta_segmentos_fantasma_e_clampa_cues() -> None:
    segmentos = [
        SegmentoTranscricaoComTempo(0.0, 2.0, "abra o menu principal"),
        SegmentoTranscricaoComTempo(2.0, 4.0, "clique em salvar agora"),
        SegmentoTranscricaoComTempo(280.0, 300.0, "segmento fantasma fora do video"),
    ]
    frases = [
        "Abra o menu principal do sistema.",
        "Clique em salvar agora.",
        "Frase extra sem match que nao deve passar de 60s.",
    ]
    resultado = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
        frases,
        segmentos,
        duracao_video_segundos=60.0,
    )
    assert resultado.cues
    assert all(c.fim_segundos <= 60.0 + 1e-6 for c in resultado.cues)
    assert all(c.inicio_segundos < 60.0 for c in resultado.cues)
    assert max(c.fim_segundos for c in resultado.cues) < 100.0


def test_interpolacao_usa_teto_duracao_nao_ultimo_segmento_fantasma() -> None:
    segmentos = [
        SegmentoTranscricaoComTempo(0.0, 2.0, "ola mundo completo"),
        SegmentoTranscricaoComTempo(200.0, 250.0, "cauda fantasma longa"),
    ]
    frases = [
        "Olá mundo completo.",
        "Texto interpolado sem similaridade xyzzy.",
        "Outro texto interpolado qwerty.",
    ]
    resultado = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
        frases,
        segmentos,
        duracao_video_segundos=30.0,
    )
    assert resultado.cues
    assert max(c.fim_segundos for c in resultado.cues) <= 30.0 + 1e-6
