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


def test_validacao_edicoes_modal_aceita_janela_alem_da_entrada_se_origem_biblioteca_mais_longa() -> None:
    """Cue com B-roll maior que a entrada não deve falhar contra a duração da entrada."""
    res = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="Trecho longo.",
                inicio_video_segundos=0.0,
                fim_video_segundos=105.1,
                origem_ancora="edicao_modal",
                casado=True,
                id_fonte_video="mabcdef12",
            )
        ],
        modo="edicoes_modal_narrado",
        quantidade_ancoras_markdown=0,
        quantidade_casadas=1,
        quantidade_interpoladas=0,
    )
    out = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
        res,
        duracao_video_segundos=72.1,
        duracao_por_id_fonte_video={
            "entrada": 72.1,
            "mabcdef12": 120.0,
        },
    )
    assert out.ok is True


def test_validacao_edicoes_modal_rejeita_se_ultrapassa_a_origem_da_biblioteca() -> None:
    res = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="Trecho longo demais.",
                inicio_video_segundos=0.0,
                fim_video_segundos=130.0,
                origem_ancora="edicao_modal",
                casado=True,
                id_fonte_video="mabcdef12",
            )
        ],
        modo="edicoes_modal_narrado",
        quantidade_ancoras_markdown=0,
        quantidade_casadas=1,
        quantidade_interpoladas=0,
    )
    out = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
        res,
        duracao_video_segundos=72.1,
        duracao_por_id_fonte_video={
            "entrada": 72.1,
            "mabcdef12": 120.0,
        },
    )
    assert out.ok is False
    assert out.motivo_rejeicao is not None
    assert "120.0" in (out.motivo_rejeicao or "")


def test_validar_janelas_permite_sobreposicao_temporal_entre_origens_diferentes() -> None:
    from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
        JanelaVideoCueEntradaTranscribrothers,
        validar_janelas_video_cues_sem_sobreposicao_transcribrothers,
    )

    validar_janelas_video_cues_sem_sobreposicao_transcribrothers(
        [
            JanelaVideoCueEntradaTranscribrothers(0.0, 10.0),
            JanelaVideoCueEntradaTranscribrothers(5.0, 15.0),
        ],
        ids_fonte_video=["entrada", "mabcdef12"],
        duracoes_video_por_indice=[72.0, 120.0],
    )
