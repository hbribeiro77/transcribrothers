from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers,
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
    montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers,
    montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers,
    montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers,
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)


def test_normalizar_caminho_png_assets() -> None:
    assert (
        normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers("./assets/x.png")
        == "assets/x.png"
    )
    assert normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers("https://x/y.png") is None


def test_listar_ordem_primeira_ocorrencia() -> None:
    md = "a ![](assets/b.png) c ![](assets/a.png) ![](assets/b.png)"
    assert listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(md) == [
        "assets/b.png",
        "assets/a.png",
    ]


def test_montar_rels_ordem_markdown() -> None:
    rels_full = [
        (1.0, "assets/a.png"),
        (2.0, "assets/b.png"),
        (3.0, "assets/c.png"),
    ]
    md = "![](assets/c.png)\n![](assets/a.png)"
    out = montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers(
        markdown=md,
        rels_completos_com_tempos=rels_full,
    )
    assert out == [(3.0, "assets/c.png"), (1.0, "assets/a.png")]


def test_montar_rels_markdown_mais_caminho_extra_em_instrucoes() -> None:
    rels_full = [(1.0, "assets/a.png"), (2.0, "assets/b.png"), (3.0, "assets/c.png")]
    md = "![](assets/c.png)\n![](assets/a.png)"
    out = montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
        markdown=md,
        instrucoes_revisao_humana="Veja também assets/b.png",
        rels_completos_com_tempos=rels_full,
    )
    assert out == [(3.0, "assets/c.png"), (1.0, "assets/a.png"), (2.0, "assets/b.png")]


def test_montar_rels_figura_na_instrucao_nao_duplica_ordem_markdown() -> None:
    rels_full = [(1.0, "assets/a.png"), (2.0, "assets/b.png")]
    md = "![](assets/b.png)\n![](assets/a.png)"
    out_md = montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers(
        markdown=md,
        rels_completos_com_tempos=rels_full,
    )
    out_mix = montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
        markdown=md,
        instrucoes_revisao_humana="Ajuste Figura 1 e imagem 2",
        rels_completos_com_tempos=rels_full,
    )
    assert out_mix == out_md
    rels_full = [(9.0, "assets/x.png")]
    out = montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
        markdown="Sem imagem aqui.",
        instrucoes_revisao_humana="Veja assets/x.png",
        rels_completos_com_tempos=rels_full,
    )
    assert out == [(9.0, "assets/x.png")]


def test_extrair_timestamps_segundos_do_markdown_edicao_secao() -> None:
    md = "Passo [01:30](?t=90) e [02:00](?t=120.5)"
    assert extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers(md) == [
        90.0,
        120.5,
    ]


def test_montar_catalogo_completo_e_visao_prioriza_imagem_da_secao() -> None:
    rels = [(10.0, "assets/a.png"), (100.0, "assets/b.png"), (200.0, "assets/c.png")]
    md_secao = "## Passo\n![](assets/b.png)\n[01:40](?t=100)"
    visao, catalogo = montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
        markdown_tutorial_completo=md_secao,
        markdown_escopo_edicao=md_secao,
        instrucoes_revisor="Melhore o texto.",
        rels_completos_com_tempos=rels,
        timestamps_escopo_segundos=[100.0],
    )
    assert len(catalogo) == 3
    assert catalogo[0]["arquivo_relativo_markdown"] == "assets/a.png"
    assert catalogo[0]["indice_catalogo"] == 1
    nomes_visao = [rel for _, rel in visao]
    assert "assets/b.png" in nomes_visao


def test_montar_visao_inclui_frames_na_janela_temporal() -> None:
    rels = [(50.0, "assets/antes.png"), (100.0, "assets/no.png"), (250.0, "assets/depois.png")]
    md_secao = "Trecho [01:40](?t=100)"
    visao, _ = montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
        markdown_tutorial_completo=md_secao,
        markdown_escopo_edicao=md_secao,
        instrucoes_revisor="Detalhe.",
        rels_completos_com_tempos=rels,
        timestamps_escopo_segundos=[100.0],
        margem_janela_temporal_segundos=120.0,
    )
    nomes = {rel for _, rel in visao}
    assert "assets/antes.png" in nomes
    assert "assets/no.png" in nomes
    assert "assets/depois.png" not in nomes


def test_montar_visao_pedido_imagem_adiciona_candidatos() -> None:
    rels = [(0.0, "assets/f0.png"), (30.0, "assets/f30.png"), (60.0, "assets/f60.png")]
    md_secao = "Texto sem imagem [00:30](?t=30)"
    visao, catalogo = montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
        markdown_tutorial_completo=md_secao,
        markdown_escopo_edicao=md_secao,
        instrucoes_revisor="Inclua uma imagem do momento em que abro o menu.",
        rels_completos_com_tempos=rels,
        timestamps_escopo_segundos=[30.0],
    )
    assert len(catalogo) == 3
    assert len(visao) == 3


def test_montar_visao_no_maximo_cinco_candidatos_mesmo_com_muitos_na_janela() -> None:
    rels = [(float(i), f"assets/f{i:02d}.png") for i in range(0, 40, 2)]
    md_secao = "Passos [01:00](?t=60) e [02:00](?t=120)"
    visao, catalogo = montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
        markdown_tutorial_completo=md_secao,
        markdown_escopo_edicao=md_secao,
        instrucoes_revisor="Adicione um frame adequado.",
        rels_completos_com_tempos=rels,
        timestamps_escopo_segundos=[60.0, 120.0],
    )
    assert len(catalogo) == 20
    assert len(visao) <= 5
    assert len(visao) >= 3
