import json

from transcribrothers_backend.modulo_interpretacao_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers import (
    parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers,
)


def test_parse_json_objeto_direto():
    raw = json.dumps(
        {
            "modo_escopo_edicao": "trecho_local",
            "trecho_ancora": "Visão Geral do Fluxo\nParágrafo exemplo aqui.",
            "instrucoes_revisor_limpas": "Intro mais detalhada.",
            "titulo_secao_heading": "## Visão geral",
            "confianca": "alta",
            "explicacao_curta": "Só o bloco da visão geral.",
        },
        ensure_ascii=False,
    )
    parsed = parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers(raw)
    assert parsed.modo_escopo_edicao == "trecho_local"
    assert "Visão Geral" in (parsed.trecho_ancora or "")


def test_parse_json_em_cerca_markdown():
    inner = {
        "modo_escopo_edicao": "a_partir_de",
        "trecho_ancora": "Dinâmica do Processo",
        "instrucoes_revisor_limpas": "Detalhar com exemplos.",
        "titulo_secao_heading": None,
        "confianca": "media",
        "explicacao_curta": "A partir da dinâmica.",
    }
    raw = "```json\n" + json.dumps(inner, ensure_ascii=False) + "\n```"
    parsed = parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers(raw)
    assert parsed.modo_escopo_edicao == "a_partir_de"
