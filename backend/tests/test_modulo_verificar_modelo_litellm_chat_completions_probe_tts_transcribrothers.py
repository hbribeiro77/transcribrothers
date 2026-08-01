"""Probe de modelo LiteLLM: ramo TTS (modalities/audio) vs chat texto."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers import (
    modelo_litellm_parece_tts_pelo_slug_transcribrothers,
    verificar_modelo_litellm_via_chat_completions_probe_transcribrothers,
)


def _cfg_proxy() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk-teste",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )


def _resposta_http(status: int, payload: dict) -> httpx.Response:
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    return httpx.Response(status, json=payload, request=req)


@pytest.mark.parametrize(
    ("slug", "esperado"),
    [
        ("gemini/gemini-2.5-flash-preview-tts", True),
        ("gemini/gemini-2.5-flash-preview-tts-preview", True),
        ("vertex_ai/gemini-2.5-pro-preview-tts", True),
        ("gemini/gemini-3.1-flash-tts-preview", True),
        ("gemini/gemini-2.0-flash", False),
        ("openai/gpt-4o-mini", False),
        ("", False),
    ],
)
def test_modelo_litellm_parece_tts_pelo_slug(slug: str, esperado: bool) -> None:
    assert modelo_litellm_parece_tts_pelo_slug_transcribrothers(slug) is esperado


@pytest.mark.asyncio
async def test_probe_tts_envia_modalities_audio_e_aceita_resposta_com_audio() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "audio": {"data": "AAAA", "format": "pcm16"},
                }
            }
        ]
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta_http(200, payload))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    ):
        r = await verificar_modelo_litellm_via_chat_completions_probe_transcribrothers(
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=_cfg_proxy(),
        )

    assert r.ok is True
    assert "tts" in r.mensagem.lower() or "áudio" in r.mensagem.lower() or "audio" in r.mensagem.lower()
    kwargs = mock_client.post.await_args.kwargs
    corpo = kwargs["json"]
    assert corpo["modalities"] == ["audio"]
    assert corpo["audio"]["format"] == "pcm16"
    assert corpo["audio"]["voice"]
    assert "allowed_openai_params" in corpo
    assert "audio" in corpo["allowed_openai_params"]
    assert "modalities" in corpo["allowed_openai_params"]


@pytest.mark.asyncio
async def test_probe_chat_texto_nao_envia_modalities_audio() -> None:
    payload = {
        "choices": [{"message": {"role": "assistant", "content": "ok"}}],
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta_http(200, payload))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    ):
        r = await verificar_modelo_litellm_via_chat_completions_probe_transcribrothers(
            modelo="gemini/gemini-2.0-flash",
            configuracao=_cfg_proxy(),
        )

    assert r.ok is True
    assert "chat" in r.mensagem.lower()
    corpo = mock_client.post.await_args.kwargs["json"]
    assert "modalities" not in corpo
    assert "audio" not in corpo


@pytest.mark.asyncio
async def test_probe_tts_sem_audio_na_resposta_retorna_ok_false() -> None:
    payload = {
        "choices": [{"message": {"role": "assistant", "content": ""}}],
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta_http(200, payload))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    ):
        r = await verificar_modelo_litellm_via_chat_completions_probe_transcribrothers(
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=_cfg_proxy(),
        )

    assert r.ok is False
    assert "áudio" in r.mensagem.lower() or "audio" in r.mensagem.lower()
