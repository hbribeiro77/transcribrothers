from transcribrothers_backend.modulo_cliente_litellm_regeneracao_secao_markdown_tutorial_transcribrothers import (
    extrair_timestamps_segundos_do_markdown_secao_transcribrothers,
    filtrar_segmentos_transcricao_proximos_a_timestamps_secao_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def test_filtrar_segmentos_sem_timestamps_na_secao_devolve_todos():
    tr = ResultadoTranscricaoComSegmentos(
        texto_completo="a b",
        segmentos=[
            SegmentoTranscricaoComTempo(0.0, 1.0, "a"),
            SegmentoTranscricaoComTempo(10.0, 12.0, "b"),
        ],
        idioma_detectado="pt",
    )
    out = filtrar_segmentos_transcricao_proximos_a_timestamps_secao_transcribrothers(tr, [])
    assert len(out) == 2


def test_extrair_timestamps_de_links_temporais_na_secao():
    md = "## Passo\n\nVeja [1:05](?t=65) e [2:00](?t=120).\n"
    assert extrair_timestamps_segundos_do_markdown_secao_transcribrothers(md) == [65.0, 120.0]
