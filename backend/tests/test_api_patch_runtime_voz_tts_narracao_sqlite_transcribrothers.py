"""Testes do PATCH/DELETE da voz TTS Gemini persistida em SQLite."""

from __future__ import annotations

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_patch_e_delete_voz_tts_narracao_runtime_reflete_no_get() -> None:
    with TestClient(app) as client:
        r0 = client.get("/api/config/transcribrothers")
        assert r0.status_code == 200
        base = r0.json()
        assert "voz_tts_narracao_efetiva" in base
        assert "voz_tts_narracao_vozes_disponiveis" in base
        assert isinstance(base["voz_tts_narracao_vozes_disponiveis"], list)
        assert len(base["voz_tts_narracao_vozes_disponiveis"]) == 30
        padrao = str(base.get("voz_tts_narracao_padrao_app") or "Kore")

        r1 = client.patch(
            "/api/config/transcribrothers/voz-tts-narracao-runtime",
            json={"voz": "Aoede"},
        )
        assert r1.status_code == 200, r1.text
        d1 = r1.json()
        assert d1["voz_tts_narracao_efetiva"] == "Aoede"
        assert d1["voz_tts_narracao_preferencia_sqlite_definida"] is True

        r2 = client.get("/api/config/transcribrothers")
        assert r2.status_code == 200
        assert r2.json()["voz_tts_narracao_efetiva"] == "Aoede"

        r3 = client.delete("/api/config/transcribrothers/voz-tts-narracao-runtime")
        assert r3.status_code == 200, r3.text
        d3 = r3.json()
        assert d3["voz_tts_narracao_efetiva"] == padrao
        assert d3["voz_tts_narracao_preferencia_sqlite_definida"] is False


def test_patch_voz_tts_narracao_runtime_rejeita_voz_desconhecida() -> None:
    with TestClient(app) as client:
        r = client.patch(
            "/api/config/transcribrothers/voz-tts-narracao-runtime",
            json={"voz": "Siri"},
        )
        assert r.status_code == 400, r.text
