"""Testes da verificação de imagens duplicadas (lotes e Markdown)."""

from transcribrothers_backend.modulo_verificacao_imagens_duplicadas_tutorial_markdown_litellm_visao_lotes_transcribrothers import (
    listar_indices_lotes_sobrepostos_verificacao_imagens_duplicadas_transcribrothers,
    montar_mapa_canonico_assets_png_apos_uniao_grupos_duplicatas_transcribrothers,
    parsear_resultado_lote_imagens_duplicadas_visao_de_texto_resposta_llm_transcribrothers,
    remover_linhas_imagens_duplicadas_markdown_tutorial_transcribrothers,
)


def test_parse_json_resposta_lote_como_texto() -> None:
    raw = '{"grupos_visualmente_iguais":[[1,2]],"mensagem_resumo":"iguais"}'
    r = parsear_resultado_lote_imagens_duplicadas_visao_de_texto_resposta_llm_transcribrothers(raw)
    assert r.grupos_visualmente_iguais == [[1, 2]]
    assert r.mensagem_resumo == "iguais"


def test_lotes_sobrepostos_max_quatro() -> None:
    lotes = listar_indices_lotes_sobrepostos_verificacao_imagens_duplicadas_transcribrothers(10)
    assert all(len(l) <= 4 for l in lotes)
    assert lotes[0] == [0, 1, 2, 3]
    assert 3 in lotes[1]


def test_mapa_canonico_uniao_transitiva() -> None:
    paths = ["assets/a.png", "assets/b.png", "assets/c.png", "assets/d.png"]
    mapa = montar_mapa_canonico_assets_png_apos_uniao_grupos_duplicatas_transcribrothers(
        paths,
        [("assets/a.png", "assets/b.png"), ("assets/b.png", "assets/c.png")],
    )
    assert mapa["assets/a.png"] == "assets/a.png"
    assert mapa["assets/c.png"] == "assets/a.png"
    assert mapa["assets/d.png"] == "assets/d.png"


def test_remove_linha_imagem_duplicada() -> None:
    md = (
        "# T\n\n"
        "![](assets/a.png)\n\n"
        "texto\n\n"
        "![](assets/b.png)\n"
    )
    mapa = {"assets/a.png": "assets/a.png", "assets/b.png": "assets/a.png"}
    out, n = remover_linhas_imagens_duplicadas_markdown_tutorial_transcribrothers(md, mapa)
    assert n == 1
    assert "assets/a.png" in out
    assert "assets/b.png" not in out
