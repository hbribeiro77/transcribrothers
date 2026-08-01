"""Validação de janelas A+B antes do TTS."""

from __future__ import annotations

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
)
from transcribrothers_backend.modulo_validar_cues_janelas_video_antes_narracao_tts_transcribrothers import (
    validar_cues_janelas_video_antes_narracao_tts_transcribrothers,
)


def test_validacao_modo_markdown_ancoras_aceita_janelas_dentro_da_duracao() -> None:
    res = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="Passo um.",
                inicio_video_segundos=1.0,
                fim_video_segundos=5.0,
                origem_ancora="markdown_t",
                casado=True,
            )
        ],
        modo="markdown_ancoras",
        quantidade_ancoras_markdown=1,
        quantidade_casadas=1,
        quantidade_interpoladas=0,
    )
    out = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
        res,
        duracao_video_segundos=30.0,
    )
    assert out.ok is True


def test_validacao_modo_markdown_rejeita_janela_alem_do_video() -> None:
    res = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="Passo.",
                inicio_video_segundos=1.0,
                fim_video_segundos=99.0,
                origem_ancora="markdown_t",
                casado=True,
            )
        ],
        modo="markdown_ancoras",
        quantidade_ancoras_markdown=1,
        quantidade_casadas=1,
        quantidade_interpoladas=0,
    )
    out = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
        res,
        duracao_video_segundos=30.0,
    )
    assert out.ok is False
    assert out.motivo_rejeicao is not None
