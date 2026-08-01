"""Limpeza IA tenta outro modelo de chat se o primeiro falhar no proxy."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers,
    listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers,
)


def test_lista_candidatos_chat_exclui_tts_e_prioriza_litellm_model() -> None:
    cfg = MagicMock()
    cfg.litellm_model = "openai/gpt-4o-mini"
    with patch(
        "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
        "listar_modelos_litellm_provisionados_para_interface",
        return_value=[
            "azure_ai/claude-sonnet-4-6",
            "gemini/gemini-2.5-flash-preview-tts",
            "openai/gpt-4o-mini",
        ],
    ):
        cand = listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers(cfg)
    assert cand[0] == "openai/gpt-4o-mini"
    assert "azure_ai/claude-sonnet-4-6" in cand
    assert "gemini/gemini-2.5-flash-preview-tts" not in cand


@pytest.mark.asyncio
async def test_limpeza_tenta_segundo_modelo_quando_primeiro_retorna_400() -> None:
    cfg = MagicMock()
    cfg.litellm_model = "azure_ai/claude-sonnet-4-6"
    originais = [
        "Agora disponível no portal institucional [01:13](",
        "distribuição em lote [01:49](",
    ]
    respostas = {
        "azure_ai/claude-sonnet-4-6": RuntimeError(
            "Chat LiteLLM falhou (HTTP 400). Trecho: vector_store_ids: Extra inputs are not permitted"
        ),
        "openai/gpt-4o-mini": (
            '{"cues":[{"indice":0,"texto":"Agora disponível no portal institucional"},'
            '{"indice":1,"texto":"distribuição em lote"}]}'
        ),
    }

    async def _fake_chat(**kwargs):
        modelo = kwargs["modelo"]
        valor = respostas[modelo]
        if isinstance(valor, Exception):
            raise valor
        return valor

    mock_chat = AsyncMock(side_effect=_fake_chat)

    with (
        patch(
            "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
            "listar_modelos_litellm_provisionados_para_interface",
            return_value=["azure_ai/claude-sonnet-4-6", "openai/gpt-4o-mini"],
        ),
        patch(
            "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
            "resolver_api_key_e_api_base_para_chamada_litellm",
            return_value=("sk", "https://proxy.exemplo/v1"),
        ),
        patch(
            "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
            "resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
            "litellm_chat_completions_texto_simples_transcribrothers",
            new=mock_chat,
        ),
    ):
        resultado = await limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers(
            textos=originais,
            configuracao=cfg,
        )

    assert resultado.ok is True
    assert resultado.usou_fallback_originais is False
    assert resultado.modelo == "openai/gpt-4o-mini"
    assert resultado.textos[0] == "Agora disponível no portal institucional"
    assert resultado.textos[1] == "distribuição em lote"
    assert "[01:13](" not in resultado.textos[0]
    assert len(resultado.alteracoes) == 2
    assert resultado.alteracoes[0].antes.endswith("[01:13](")
    assert resultado.alteracoes[0].depois == "Agora disponível no portal institucional"
    assert mock_chat.await_count == 2
