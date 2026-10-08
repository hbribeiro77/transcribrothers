import json

import pytest

from transcribrothers_backend.modulo_resolver_texto_chat_litellm_quando_content_vazio_com_tool_calls_transcribrothers import (
    resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers,
)


def test_content_vazio_com_tool_calls_vira_rascunho_com_plano_na_bolha() -> None:
    bruto = resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers(
        "",
        [
            {
                "type": "function",
                "function": {"name": "sem_video", "arguments": '{"instrucoes":"tire timestamps"}'},
            }
        ],
    )
    data = json.loads(bruto)
    assert data["estado"] == "rascunho"
    assert data["executar"] is False
    assert "não alterei" in data["texto"].casefold() or "ainda não" in data["texto"].casefold()
    assert "tire timestamps" in data["texto"]
    assert data["ferramentas"] == []


def test_content_vazio_com_edicao_parcial_cita_a_secao_no_plano() -> None:
    bruto = resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers(
        "",
        [
            {
                "function": {
                    "name": "edicao_parcial",
                    "arguments": (
                        '{"titulo_secao_heading":"1. Visão Geral",'
                        '"instrucoes":"Inclua o filtro de triagem."}'
                    ),
                }
            }
        ],
    )
    data = json.loads(bruto)
    assert data["estado"] == "rascunho"
    assert data["executar"] is False
    assert "1. Visão Geral" in data["texto"]
    assert "filtro de triagem" in data["texto"]


def test_content_preenchido_prevalece_mesmo_com_tool_calls() -> None:
    bruto = resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers(
        '{"texto":"Sugiro um ajuste.","estado":"rascunho","ferramentas":[]}',
        [{"function": {"name": "edicao_parcial"}}],
    )
    assert "Sugiro um ajuste" in bruto


def test_content_vazio_sem_tool_calls_levanta_o_erro_conhecido() -> None:
    with pytest.raises(RuntimeError, match="conteúdo vazio"):
        resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers("", [])
