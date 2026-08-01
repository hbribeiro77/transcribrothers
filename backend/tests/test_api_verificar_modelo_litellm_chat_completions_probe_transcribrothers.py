"""POST /api/config/transcribrothers/verificar-modelo-litellm — probe barato de chat."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers import (
    ResultadoVerificacaoModeloLitellmProbeTranscribrothers,
)


def test_verificar_modelo_litellm_corpo_vazio_retorna_422() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/config/transcribrothers/verificar-modelo-litellm",
            json={"model": "   "},
        )
        assert r.status_code == 422


def test_verificar_modelo_litellm_sucesso_retorna_ok_true() -> None:
    resultado = ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
        ok=True,
        modelo="gemini/gemini-2.0-flash",
        mensagem="Modelo respondeu ao probe de chat.",
    )
    with patch(
        "transcribrothers_backend.main.verificar_modelo_litellm_via_chat_completions_probe_transcribrothers",
        new_callable=AsyncMock,
        return_value=resultado,
    ):
        with TestClient(app) as client:
            r = client.post(
                "/api/config/transcribrothers/verificar-modelo-litellm",
                json={"model": "gemini/gemini-2.0-flash"},
            )
        assert r.status_code == 200
        d = r.json()
        assert d["ok"] is True
        assert d["modelo"] == "gemini/gemini-2.0-flash"
        assert "respondeu" in d["mensagem"].lower()


def test_verificar_modelo_litellm_falha_retorna_ok_false_com_mensagem() -> None:
    resultado = ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
        ok=False,
        modelo="modelo/inexistente",
        mensagem="HTTP 404: model not found",
    )
    with patch(
        "transcribrothers_backend.main.verificar_modelo_litellm_via_chat_completions_probe_transcribrothers",
        new_callable=AsyncMock,
        return_value=resultado,
    ):
        with TestClient(app) as client:
            r = client.post(
                "/api/config/transcribrothers/verificar-modelo-litellm",
                json={"model": "modelo/inexistente"},
            )
        assert r.status_code == 200
        d = r.json()
        assert d["ok"] is False
        assert d["modelo"] == "modelo/inexistente"
        assert "404" in d["mensagem"]
