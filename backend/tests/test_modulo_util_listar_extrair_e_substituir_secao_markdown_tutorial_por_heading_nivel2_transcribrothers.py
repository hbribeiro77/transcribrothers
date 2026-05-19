import pytest

from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers,
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
    substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers,
)


def test_listar_duas_secoes_nivel2():
    md = "# Título\n\nIntro.\n\n## Primeira\n\nA.\n\n## Segunda\n\nB.\n"
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
    assert len(secoes) == 2
    assert secoes[0].linha_heading == "## Primeira"
    assert secoes[1].linha_heading == "## Segunda"
    assert extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(md, secoes[0]) == "## Primeira\n\nA."
    assert extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(md, secoes[1]) == "## Segunda\n\nB."


def test_substituir_secao_preserva_resto():
    md = "# T\n\n## A\n\nold\n\n## B\n\nkeep\n"
    sec = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        md, titulo_secao_heading="## A"
    )
    novo = substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers(
        md, sec, "## A\n\nnew text"
    )
    assert "new text" in novo
    assert "keep" in novo
    assert "old" not in novo


def test_mesclar_resposta_llm():
    md = "# T\n\n## X\n\n1\n\n## Y\n\n2\n"
    sec = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        md, indice_secao=0
    )
    out = validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers(
        md, sec, "## X\n\nreescrito"
    )
    assert "reescrito" in out
    assert "## Y\n\n2" in out


def test_resolver_heading_aproximado_quando_ia_varia_artigo():
    md = "# T\n\n## Configuração das Colunas\n\nCorpo.\n\n## Outra\n\nX.\n"
    sec = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        md, titulo_secao_heading="## Configuração de Colunas"
    )
    assert sec.linha_heading == "## Configuração das Colunas"


def test_reconciliar_heading_interpretado_com_secoes():
    md = "# T\n\n## Personalização da Lista de Pastas\n\nA.\n"
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
    linha = reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers(
        "## Personalização da Lista de Pastas",
        secoes,
    )
    assert linha == "## Personalização da Lista de Pastas"
    linha2 = reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers(
        "Personalização da Lista de Pastas",
        secoes,
    )
    assert linha2 == "## Personalização da Lista de Pastas"


def test_rejeita_heading_errado_na_secao_nova():
    md = "## A\n\nx\n\n## B\n\ny\n"
    sec = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        md, titulo_secao_heading="## A"
    )
    with pytest.raises(ValueError, match="não corresponde"):
        substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers(
            md, sec, "## B\n\nz"
        )
