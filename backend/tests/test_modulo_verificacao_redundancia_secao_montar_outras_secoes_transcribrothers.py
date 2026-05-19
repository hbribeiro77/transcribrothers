from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
)
from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
    montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers,
    parsear_resultado_verificacao_redundancia_secao_de_texto_llm_transcribrothers,
)


def test_montar_outras_secoes_exclui_secao_em_edicao():
    md = "# T\n\n## A\n\n1\n\n## B\n\n2\n\n## C\n\n3\n"
    sec_b = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
        md, titulo_secao_heading="## B"
    )
    outras, _ = montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers(
        md, sec_b, max_chars_por_secao=5000, max_secoes=10
    )
    headings = {o["heading"] for o in outras}
    assert headings == {"## A", "## C"}
    assert all("## B" not in o["markdown"] for o in outras)


def test_parse_json_redundancia_minimo():
    raw = '{"classificacao_global":"ok","mensagem_resumo":"tudo bem","itens":[]}'
    r = parsear_resultado_verificacao_redundancia_secao_de_texto_llm_transcribrothers(raw)
    assert r.classificacao_global == "ok"
