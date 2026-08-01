"""POST /api/jobs/{id}/gerar-narracao-tts-markdown."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    ResultadoNarracaoTtsWavTranscribrothers,
)


def test_gerar_narracao_tts_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/00000000-0000-0000-0000-000000000000/gerar-narracao-tts-markdown",
            json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
        )
    assert r.status_code == 404


def test_gerar_narracao_tts_sucesso_com_mock(tmp_path_factory) -> None:
    resultado = ResultadoNarracaoTtsWavTranscribrothers(
        ok=True,
        mensagem="Narração TTS gerada com sucesso.",
        nome_arquivo=NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        texto_caracteres=42,
        texto_truncado=False,
    )

    # Cria job real mínimo via projeto em branco + patch markdown
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200, criado.text
        job_id = criado.json()["id"]

        with patch(
            "transcribrothers_backend.main.gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers",
            new_callable=AsyncMock,
            return_value=resultado,
        ), patch(
            "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
            return_value="gemini/gemini-2.5-flash-preview-tts",
        ):
            r = client.post(
                f"/api/jobs/{job_id}/gerar-narracao-tts-markdown",
                json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
            )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["ok"] is True
        assert d["nome_arquivo"] == NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        assert "narracao" in d["url_asset"]

        job = client.get(f"/api/jobs/{job_id}").json()
        assert job["steps_json"].get("narracao_tts_documento", {}).get("nome_arquivo") == (
            NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        )
