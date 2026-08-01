"""Manifest de janelas + diff de textos VTT para regeneração parcial de narração."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
    aplicar_textos_vtt_sobre_cues_janela_preservando_tempos_video_transcribrothers,
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    cues_janela_a_partir_manifest_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
    indices_cues_com_texto_diferente_do_manifest_transcribrothers,
    normalizar_texto_cue_para_comparacao_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_util_parsear_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers import (
    parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers,
)


def test_parsear_webvtt_em_cues_texto_basico() -> None:
    vtt = """WEBVTT

1
00:00:00.000 --> 00:00:01.500
Primeira frase

2
00:00:01.500 --> 00:00:03.000
Segunda frase
"""
    cues = parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers(vtt)
    assert len(cues) == 2
    assert cues[0].texto == "Primeira frase"
    assert cues[0].inicio_segundos == 0.0
    assert cues[1].texto == "Segunda frase"


def test_normalizar_e_diff_indices_sujos() -> None:
    assert normalizar_texto_cue_para_comparacao_narracao_transcribrothers("  A  B\n") == "A B"
    textos_manifest = ["um", "dois", "tres"]
    textos_vtt = ["um", "dois editado", "tres"]
    assert indices_cues_com_texto_diferente_do_manifest_transcribrothers(
        textos_manifest=textos_manifest,
        textos_desejados=textos_vtt,
    ) == [1]


def test_gravar_carregar_manifest_e_aplicar_textos_vtt(tmp_path: Path) -> None:
    cues = [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto="um",
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
            origem_ancora="markdown_t",
            casado=True,
        ),
        CueNarracaoComJanelaVideoTranscribrothers(
            texto="dois",
            inicio_video_segundos=2.0,
            fim_video_segundos=5.0,
            origem_ancora="markdown_t",
            casado=True,
        ),
    ]
    caminho = gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
        work=tmp_path,
        cues=cues,
    )
    assert caminho.name == NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS
    carregado = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(tmp_path)
    assert carregado is not None
    assert len(carregado) == 2
    cues_de_volta = cues_janela_a_partir_manifest_transcribrothers(carregado)
    novos = aplicar_textos_vtt_sobre_cues_janela_preservando_tempos_video_transcribrothers(
        cues_de_volta,
        ["um alterado", "dois"],
    )
    assert novos[0].texto == "um alterado"
    assert novos[0].inicio_video_segundos == 0.0
    assert novos[0].fim_video_segundos == 2.0
    assert novos[1].texto == "dois"
