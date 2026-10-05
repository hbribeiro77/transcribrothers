"""GET /v1/models no proxy LiteLLM para o catálogo da gaveta de configurações."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_listar_modelos_litellm_no_proxy_via_get_v1_models_transcribrothers import (
    FalhaListarModelosLitellmProxyTranscribrothers,
    obter_catalogo_modelos_litellm_no_proxy_transcribrothers,
)


def _cfg_proxy() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk-teste",
        litellm_endpoint="https://proxy.exemplo",
        litellm_http_verify_ssl=False,
    )


def _resposta_http(status: int, payload: dict) -> httpx.Response:
    req = httpx.Request("GET", "https://proxy.exemplo/v1/models")
    return httpx.Response(status, json=payload, request=req)


def _patch_async_client(mock_client: AsyncMock):
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    return patch(
        "transcribrothers_backend.modulo_listar_modelos_litellm_no_proxy_via_get_v1_models_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    )


@pytest.mark.asyncio
async def test_listar_modelos_proxy_sem_credencial_levanta_falha() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="",
        litellm_endpoint="",
        openai_api_key="",
    )
    with pytest.raises(FalhaListarModelosLitellmProxyTranscribrothers, match="não configurado"):
        await obter_catalogo_modelos_litellm_no_proxy_transcribrothers(
            configuracao=cfg,
            allowlist=["gemini/gemini-3.1-flash-lite"],
        )


@pytest.mark.asyncio
async def test_listar_modelos_proxy_get_v1_models_monta_catalogo_com_allowlist() -> None:
    payload = {
        "object": "list",
        "data": [
            {"id": "gemini/gemini-3.8-flash", "owned_by": "openai"},
            {"id": "azure_ai/embed-v-4-0", "owned_by": "openai"},
        ],
    }
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=_resposta_http(200, payload))
    with _patch_async_client(mock_client):
        catalogo = await obter_catalogo_modelos_litellm_no_proxy_transcribrothers(
            configuracao=_cfg_proxy(),
            allowlist=["gemini/gemini-3.8-flash", "glm-5.2"],
        )
    assert mock_client.get.await_args.args[0] == "https://proxy.exemplo/v1/models"
    headers = mock_client.get.await_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk-teste"
    por_id = {m.id: m for m in catalogo.modelos}
    assert por_id["gemini/gemini-3.8-flash"].util_para_tutorial is True
    assert por_id["gemini/gemini-3.8-flash"].na_allowlist is True
    assert por_id["azure_ai/embed-v-4-0"].util_para_tutorial is False
    assert catalogo.allowlist_ausente_no_proxy == ["glm-5.2"]


@pytest.mark.asyncio
async def test_listar_modelos_proxy_http_erro_levanta_falha_com_status() -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=_resposta_http(502, {"error": "bad gateway"}))
    with _patch_async_client(mock_client):
        with pytest.raises(FalhaListarModelosLitellmProxyTranscribrothers, match="HTTP 502"):
            await obter_catalogo_modelos_litellm_no_proxy_transcribrothers(
                configuracao=_cfg_proxy(),
                allowlist=[],
            )
