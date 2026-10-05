"""GET /api/config/transcribrothers/modelos-litellm-no-proxy — catálogo do proxy cruzado com a allowlist."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_catalogo_modelos_litellm_proxy_classificacao_e_allowlist_transcribrothers import (
    CatalogoModelosLitellmProxyTranscribrothers,
    ItemCatalogoModeloLitellmProxyTranscribrothers,
)
from transcribrothers_backend.modulo_listar_modelos_litellm_no_proxy_via_get_v1_models_transcribrothers import (
    FalhaListarModelosLitellmProxyTranscribrothers,
)


def test_api_modelos_litellm_no_proxy_retorna_catalogo_cruzado_com_allowlist() -> None:
    catalogo = CatalogoModelosLitellmProxyTranscribrothers(
        modelos=[
            ItemCatalogoModeloLitellmProxyTranscribrothers(
                id="gemini/gemini-3.8-flash",
                owned_by="openai",
                categoria="chat",
                util_para_tutorial=True,
                na_allowlist=False,
            ),
            ItemCatalogoModeloLitellmProxyTranscribrothers(
                id="azure_ai/embed-v-4-0",
                owned_by="openai",
                categoria="embedding",
                util_para_tutorial=False,
                na_allowlist=False,
            ),
        ],
        allowlist_ausente_no_proxy=["glm-5.2"],
    )
    with patch(
        "transcribrothers_backend.main.obter_catalogo_modelos_litellm_no_proxy_transcribrothers",
        new_callable=AsyncMock,
        return_value=catalogo,
    ):
        with TestClient(app) as client:
            r = client.get("/api/config/transcribrothers/modelos-litellm-no-proxy")
    assert r.status_code == 200
    d = r.json()
    assert d["allowlist_ausente_no_proxy"] == ["glm-5.2"]
    assert d["modelos"][0]["id"] == "gemini/gemini-3.8-flash"
    assert d["modelos"][0]["util_para_tutorial"] is True
    assert d["modelos"][1]["categoria"] == "embedding"


def test_api_modelos_litellm_no_proxy_falha_proxy_retorna_502() -> None:
    with patch(
        "transcribrothers_backend.main.obter_catalogo_modelos_litellm_no_proxy_transcribrothers",
        new_callable=AsyncMock,
        side_effect=FalhaListarModelosLitellmProxyTranscribrothers("O proxy recusou (HTTP 502)"),
    ):
        with TestClient(app) as client:
            r = client.get("/api/config/transcribrothers/modelos-litellm-no-proxy")
    assert r.status_code == 502
    assert "proxy" in r.json()["detail"].lower()
