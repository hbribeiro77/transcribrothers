"""Validação determinística de cues antes da narração TTS."""

from __future__ import annotations

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
    ResultadoAlinhamentoLegendasTranscribrothers,
)
from transcribrothers_backend.modulo_validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers import (
    validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers,
)


def _resultado(
    cues: list[CueLegendaAlinhadaTranscribrothers],
) -> ResultadoAlinhamentoLegendasTranscribrothers:
    casadas = sum(1 for c in cues if c.casado)
    return ResultadoAlinhamentoLegendasTranscribrothers(
        cues=cues,
        quantidade_casadas=casadas,
        quantidade_interpoladas=len(cues) - casadas,
    )


def test_validar_cues_ok_caso_saudavel() -> None:
    cues = [
        CueLegendaAlinhadaTranscribrothers("a", 0.0, 2.0, True),
        CueLegendaAlinhadaTranscribrothers("b", 2.0, 4.0, True),
        CueLegendaAlinhadaTranscribrothers("c", 4.0, 6.0, True),
        CueLegendaAlinhadaTranscribrothers("d", 6.0, 8.0, False),
    ]
    r = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        _resultado(cues),
        duracao_video_segundos=60.0,
    )
    assert r.ok is True
    assert r.motivo_rejeicao is None


def test_validar_cues_rejeita_alem_da_duracao() -> None:
    cues = [
        CueLegendaAlinhadaTranscribrothers("a", 0.0, 2.0, True),
        CueLegendaAlinhadaTranscribrothers("b", 50.0, 70.0, True),
    ]
    r = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        _resultado(cues),
        duracao_video_segundos=60.0,
    )
    assert r.ok is False
    assert r.motivo_rejeicao is not None
    assert "duração" in r.motivo_rejeicao.lower() or "ultrapass" in r.motivo_rejeicao.lower()


def test_validar_cues_rejeita_percentual_casado_baixo() -> None:
    cues = [
        CueLegendaAlinhadaTranscribrothers(f"i{i}", float(i), float(i) + 0.5, False)
        for i in range(10)
    ]
    # só 1 casada em 10 = 10%
    cues[0] = CueLegendaAlinhadaTranscribrothers("a", 0.0, 1.0, True)
    r = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        _resultado(cues),
        duracao_video_segundos=60.0,
    )
    assert r.ok is False
    assert "casaram" in (r.motivo_rejeicao or "").lower() or "%" in (r.motivo_rejeicao or "")


def test_validar_cues_rejeita_sequencia_interpolada_longa() -> None:
    cues = [
        CueLegendaAlinhadaTranscribrothers("casada", 0.0, 1.0, True),
        *[
            CueLegendaAlinhadaTranscribrothers(f"gap{i}", float(i + 1), float(i + 2), False)
            for i in range(7)
        ],
        CueLegendaAlinhadaTranscribrothers("casada2", 20.0, 22.0, True),
        CueLegendaAlinhadaTranscribrothers("casada3", 22.0, 24.0, True),
    ]
    # 3 casadas e ~70%? 3/10 = 30% — passa % mas falha na sequência de 7 interpoladas
    r = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        _resultado(cues),
        duracao_video_segundos=60.0,
    )
    assert r.ok is False
    assert "interpolad" in (r.motivo_rejeicao or "").lower()


def test_validar_cues_rejeita_lista_vazia() -> None:
    r = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        _resultado([]),
        duracao_video_segundos=60.0,
    )
    assert r.ok is False
