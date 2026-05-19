"""Testes da lógica de janelas e mesclagem por offset da transcrição multimodal."""

from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers import (
    _listar_janelas_temporais_segundos_para_transcricao_multimodal,
    _mesclar_resultados_transcricao_com_offset_temporal_segundos,
)


def test_listar_janelas_dez_minutos_em_cinco_minutos() -> None:
    janelas = _listar_janelas_temporais_segundos_para_transcricao_multimodal(600.0, 300.0)
    assert janelas == [(0.0, 300.0), (300.0, 300.0)]


def test_mesclar_apos_ordenar_por_offset_timeline_correta() -> None:
    r0 = ResultadoTranscricaoComSegmentos(
        texto_completo="a",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "a")],
        idioma_detectado="pt",
    )
    r1 = ResultadoTranscricaoComSegmentos(
        texto_completo="b",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "b")],
        idioma_detectado="pt",
    )
    pares_fora_de_ordem = [(300.0, r1), (0.0, r0)]
    ordenados = sorted(pares_fora_de_ordem, key=lambda item: item[0])
    mesclado = _mesclar_resultados_transcricao_com_offset_temporal_segundos(ordenados)
    assert mesclado.segmentos[0].inicio_segundos < mesclado.segmentos[1].inicio_segundos


def test_mesclar_dois_resultados_com_offset_preserva_tempos_absolutos() -> None:
    r0 = ResultadoTranscricaoComSegmentos(
        texto_completo="um",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "um")],
        idioma_detectado="pt",
    )
    r1 = ResultadoTranscricaoComSegmentos(
        texto_completo="dois",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 2.0, "dois")],
        idioma_detectado="pt",
    )
    mesclado = _mesclar_resultados_transcricao_com_offset_temporal_segundos(
        [(0.0, r0), (300.0, r1)]
    )
    assert len(mesclado.segmentos) == 2
    assert mesclado.segmentos[0].inicio_segundos == 0.0
    assert mesclado.segmentos[0].fim_segundos == 1.0
    assert mesclado.segmentos[1].inicio_segundos == 300.0
    assert mesclado.segmentos[1].fim_segundos == 302.0
    assert "um" in mesclado.texto_completo and "dois" in mesclado.texto_completo
