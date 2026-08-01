"""Registro de duração por etapa do pipeline de vídeo narrado."""

from __future__ import annotations

from transcribrothers_backend.modulo_util_registrar_tempos_etapas_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS,
    fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers,
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers,
    mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers,
    total_segundos_pipeline_tempos_video_narrado_transcribrothers,
)


def test_mapear_fase_para_id_etapa() -> None:
    assert (
        mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers(
            "video_narrado_alinhando_legendas"
        )
        == "alinhamento_legendas"
    )
    assert (
        mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers("video_narrado_gerando_tts")
        == "narracao_tts"
    )
    assert mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers("video_narrado_concluido") is None


def test_iniciar_e_fechar_etapas_acumula_duracoes() -> None:
    steps: dict = {}
    t0 = 1000.0
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        etapa_id="alinhamento_legendas",
        agora_epoch=t0,
    )
    fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        agora_epoch=t0 + 2.5,
    )
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        etapa_id="narracao_tts",
        agora_epoch=t0 + 2.5,
    )
    fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        agora_epoch=t0 + 12.5,
    )
    bloco = steps[CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS]
    assert bloco["etapas"]["alinhamento_legendas"]["duracao_segundos"] == 2.5
    assert bloco["etapas"]["narracao_tts"]["duracao_segundos"] == 10.0
    assert total_segundos_pipeline_tempos_video_narrado_transcribrothers(steps) == 12.5
    assert bloco["total_segundos"] == 12.5


def test_transicao_fecha_anterior_ao_iniciar_proxima() -> None:
    steps: dict = {}
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        etapa_id="validacao_legendas",
        agora_epoch=10.0,
    )
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        etapa_id="mux_video",
        agora_epoch=15.0,
    )
    bloco = steps[CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS]
    assert bloco["etapas"]["validacao_legendas"]["duracao_segundos"] == 5.0
    assert bloco["etapa_atual"] == "mux_video"
    assert "duracao_segundos" not in bloco["etapas"]["mux_video"]
