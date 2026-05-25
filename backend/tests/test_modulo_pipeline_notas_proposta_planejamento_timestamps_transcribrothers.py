"""Unitário: candidatos do rascunho de notas → resolver timestamps (mock planejador)."""

from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)


@pytest.mark.asyncio
async def test_planejador_notas_modo_filtra_candidatos_do_rascunho() -> None:
    md = "# Proposta\n\nDiscussão em [01:00](?t=60) e slide em [02:30](?t=150)."
    candidatos = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
        md,
        duracao_video_segundos=300.0,
        margem_minima_segundos_entre_links_temporais=1.0,
    )
    assert 60.0 in candidatos
    assert 150.0 in candidatos

    transcricao = ResultadoTranscricaoComSegmentos(texto_completo="fala", segmentos=[], idioma_detectado="pt")

    with patch(
        "transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers.litellm_chat_completions_texto_simples_transcribrothers",
        new_callable=AsyncMock,
        return_value='{"instantes_segundos_para_capturar": [150], "mensagem_resumo": "Slide principal"}',
    ):
        from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
            planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers,
        )
        from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
            ConfiguracaoAmbienteTranscribrothers,
        )

        cfg = ConfiguracaoAmbienteTranscribrothers()

        escolhidos, meta = await planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers(
            markdown_rascunho_tutorial=md,
            candidatos_segundos=candidatos,
            transcricao=transcricao,
            duracao_video_segundos=300.0,
            margem_minima_segundos_entre_links=1.0,
            max_capturas_apos_limites=8,
            modelo_litellm="test-model",
            api_key="k",
            api_base="http://localhost",
            configuracao=cfg,
            modo_notas_proposta_funcionalidade=True,
        )

    assert meta.get("planejamento_executado") is True
    assert escolhidos == [150.0]

    timestamps = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
        markdown_rascunho_tutorial=md,
        transcricao=transcricao,
        duracao_video_segundos=300.0,
        max_frames_per_minute=4,
        tutorial_max_frames_total=12,
        margem_minima_segundos_entre_links_temporais=1.0,
        timestamps_pre_planejados=escolhidos,
    )
    assert timestamps == [150.0]
