"""Testes do planejamento de timestamps para captura sob demanda."""

from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers,
    limite_maximo_capturas_frames_tutorial_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def _transcricao_com_n_segmentos(n: int) -> ResultadoTranscricaoComSegmentos:
    segs = [
        SegmentoTranscricaoComTempo(
            inicio_segundos=float(i * 10),
            fim_segundos=float(i * 10 + 5),
            texto=f"trecho {i}",
        )
        for i in range(n)
    ]
    return ResultadoTranscricaoComSegmentos(
        texto_completo=" ".join(s.texto for s in segs),
        segmentos=segs,
        idioma_detectado="pt",
    )


def test_limite_por_minuto_e_teto_total() -> None:
    assert limite_maximo_capturas_frames_tutorial_transcribrothers(
        120.0,
        max_frames_per_minute=12,
        tutorial_max_frames_total=0,
    ) == 24
    assert (
        limite_maximo_capturas_frames_tutorial_transcribrothers(
            120.0,
            max_frames_per_minute=12,
            tutorial_max_frames_total=8,
        )
        == 8
    )


def test_dedupe_margem_entre_links_temporais() -> None:
    md = "## Passo\n[00:01](?t=1.0) [00:02](?t=2.5) [00:10](?t=10.0).\n"
    ts2 = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
        md,
        duracao_video_segundos=120.0,
        margem_minima_segundos_entre_links_temporais=2.0,
    )
    assert ts2 == [1.0, 10.0]
    ts5 = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
        md,
        duracao_video_segundos=120.0,
        margem_minima_segundos_entre_links_temporais=5.0,
    )
    assert ts5 == [1.0, 10.0]


def test_resolver_usa_timestamps_pre_planejados() -> None:
    md = "## Passo 1\nVeja [00:12](?t=12.5) e depois [01:00](?t=60.0).\n"
    ts = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
        markdown_rascunho_tutorial=md,
        transcricao=_transcricao_com_n_segmentos(50),
        duracao_video_segundos=120.0,
        max_frames_per_minute=12,
        tutorial_max_frames_total=0,
        timestamps_pre_planejados=[12.5],
    )
    assert ts == [12.5]
    assert 60.0 not in ts


def test_resolver_usa_timestamps_do_markdown_rascunho() -> None:
    md = "## Passo 1\nVeja [00:12](?t=12.5) e depois [01:00](?t=60.0).\n"
    ts = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
        markdown_rascunho_tutorial=md,
        transcricao=_transcricao_com_n_segmentos(50),
        duracao_video_segundos=120.0,
        max_frames_per_minute=12,
        tutorial_max_frames_total=0,
    )
    assert 12.5 in ts
    assert 60.0 in ts
    assert len(ts) <= 24


def test_resolver_fallback_segmentos_se_rascunho_sem_links_temporais() -> None:
    md = "## Passo\nSó texto, sem link temporal.\n"
    ts = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
        markdown_rascunho_tutorial=md,
        transcricao=_transcricao_com_n_segmentos(30),
        duracao_video_segundos=300.0,
        max_frames_per_minute=6,
        tutorial_max_frames_total=10,
    )
    assert len(ts) >= 1
    assert len(ts) <= 10
