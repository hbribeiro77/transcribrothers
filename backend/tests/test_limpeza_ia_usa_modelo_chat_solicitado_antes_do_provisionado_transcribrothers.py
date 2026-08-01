"""Limpeza IA prioriza o modelo de chat enviado pela UI, não o 1º provisionado."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers,
    listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers,
)


def test_candidato_solicitado_pela_ui_vem_antes_do_sonnet_provisionado() -> None:
    cfg = MagicMock()
    cfg.litellm_model = "azure_ai/claude-sonnet-4-6"
    with patch(
        "transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers."
        "listar_modelos_litellm_provisionados_para_interface",
        return_value=["azure_ai/claude-sonnet-4-6", "openai/gpt-4o-mini"],
    ):
        cand = listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers(
            cfg,
            "openai/gpt-4o-mini",
        )
    assert cand[0] == "openai/gpt-4o-mini"


@pytest.mark.asyncio
async def test_limpeza_chama_primeiro_o_modelo_chat_da_ui() -> None:
    cfg = MagicMock()
    cfg.litellm_model = "azure_ai/claude-sonnet-4-6"
    mock_chat = AsyncMock(
        return_value='{"cues":[{"indice":0,"texto":"frase limpa"}]}'
    )
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
        r = await limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers(
            textos=["frase limpa [01:13]("],
            configuracao=cfg,
            modelo_chat="openai/gpt-4o-mini",
        )
    assert r.ok
    assert r.modelo == "openai/gpt-4o-mini"
    assert mock_chat.await_args.kwargs["modelo"] == "openai/gpt-4o-mini"
