"""PATCH provedor TTS e GET vozes ElevenLabs."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_patch_provedor_elevenlabs_reflete_no_get() -> None:
    with TestClient(app) as client:
        r = client.patch(
            "/api/config/transcribrothers/provedor-tts-narracao-runtime",
            json={
                "provedor": "elevenlabs",
                "modelo_elevenlabs": "eleven_v4",
                "voz_elevenlabs": "voz-teste-1",
            },
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["tts_provedor_efetivo"] == "elevenlabs"
        assert d["modelo_tts_elevenlabs_efetivo"] == "eleven_v4"
        assert d["voz_tts_elevenlabs_efetiva"] == "voz-teste-1"
        assert d["elevenlabs_modelos"] == ["eleven_v4"]
        r2 = client.delete("/api/config/transcribrothers/provedor-tts-narracao-runtime")
        assert r2.status_code == 200, r2.text
        assert r2.json()["tts_provedor_efetivo"] == "litellm"


def test_get_vozes_elevenlabs_devolve_lista_mockada() -> None:
    with patch(
        "transcribrothers_backend.main.listar_vozes_elevenlabs_via_get_v1_voices_transcribrothers",
        new_callable=AsyncMock,
        return_value=[{"id": "abc", "estilo": "Rachel"}],
    ):
        with TestClient(app) as client:
            r = client.get("/api/config/transcribrothers/vozes-tts-elevenlabs")
    assert r.status_code == 200
    assert r.json()["vozes"] == [{"id": "abc", "estilo": "Rachel"}]
