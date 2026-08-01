"""Cues com janelas de vídeo a partir de âncoras ?t= no Markdown."""

from __future__ import annotations

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers,
    markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers,
    montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers,
)


def test_montar_cues_com_duas_ancoras_distribui_janelas_entre_timestamps() -> None:
    md = """# Tutorial

Clique em salvar.

![](assets/a.png)

[00:10](?t=10)

Abra o menu seguinte.

![](assets/b.png)

[00:40](?t=40)
"""
    assert markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers(md)
    res = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        md,
        duracao_video_segundos=120.0,
    )
    assert res.modo == "markdown_ancoras"
    assert res.quantidade_ancoras_markdown == 2
    assert len(res.cues) >= 2
    assert all(c.origem_ancora == "markdown_t" for c in res.cues)
    assert res.cues[0].inicio_video_segundos == 10.0
    assert res.cues[0].fim_video_segundos <= 40.0 + 1e-6
    assert any("salvar" in c.texto.lower() for c in res.cues)
    assert any("menu" in c.texto.lower() for c in res.cues)


def test_vtt_timeline_narracao_soma_duracoes_wav() -> None:
    res = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        "Primeira frase.\n\n[00:05](?t=5)\n\nSegunda frase.\n\n[00:20](?t=20)\n",
        duracao_video_segundos=60.0,
    )
    duracoes = [1.5, 2.5][: len(res.cues)]
    while len(duracoes) < len(res.cues):
        duracoes.append(1.0)
    vtt = converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
        list(res.cues),
        duracoes,
    )
    assert vtt[0].inicio_segundos == 0.0
    assert abs(vtt[-1].fim_segundos - sum(duracoes)) < 1e-6
