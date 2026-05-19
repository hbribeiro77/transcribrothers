"""Testes do parser JSON da verificação de sustentação tutorial vs transcrição."""

import json

import pytest

from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
    parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers,
)


def test_parsear_verificacao_sustentacao_json_valido_transcribrothers() -> None:
    raw = """```json
{
  "classificacao_global": "atencao",
  "mensagem_resumo": "Um passo pode não estar na transcrição.",
  "itens": [
    {
      "trecho_ou_tema": "Clicar em «Exportar»",
      "classificacao": "incerto",
      "justificativa_curta": "A transcrição não menciona exportação explicitamente.",
      "citacao_transcricao_opcional": ""
    }
  ]
}
```"""
    r = parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers(raw)
    assert r.classificacao_global == "atencao"
    assert len(r.itens) == 1
    assert r.itens[0].classificacao == "incerto"


def test_parsear_verificacao_sustentacao_json_invalido_levanta_value_error_transcribrothers() -> None:
    with pytest.raises((ValueError, json.JSONDecodeError)):
        parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers("não é json")
