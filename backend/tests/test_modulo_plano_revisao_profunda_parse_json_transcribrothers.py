"""Testes do parse do plano JSON da revisão profunda (sem rede)."""

from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    extrair_primeiro_objeto_json_de_texto_llm_transcribrothers,
    parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers,
)


def test_extrair_json_de_cerca_tripla() -> None:
    raw = '```json\n{"topicos": [{"id": "a", "titulo_secao": "## X", "lacunas": [], "evidencias_transcricao": [], "prioridade": 1}]}\n```'
    s = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(raw)
    assert '"topicos"' in s


def test_parsear_plano_valido() -> None:
    txt = '{"topicos": [{"id": "t1", "titulo_secao": "## Passo", "lacunas": ["Falta Y"], "evidencias_transcricao": [{"citacao": "olá mundo"}], "prioridade": 2}]}'
    plano, serial = parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers(txt)
    assert len(plano.topicos) == 1
    assert plano.topicos[0].id == "t1"
    assert "Falta Y" in plano.topicos[0].lacunas
    assert len(serial) > 10


def test_parsear_plano_invalido_levanta_value_error() -> None:
    try:
        parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers("não é json")
    except ValueError as e:
        assert "JSON" in str(e) or "json" in str(e).lower()
    else:
        raise AssertionError("esperava ValueError")
