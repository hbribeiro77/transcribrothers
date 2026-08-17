"""POST /api/preview-tts-amostra-voz-narracao."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_api_preview_tts_amostra_voz_narracao_transcribrothers import (
    ResultadoApiPreviewTtsAmostraVozNarracaoTranscribrothers,
)


def test_preview_tts_amostra_voz_rejeita_voz_desconhecida() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/preview-tts-amostra-voz-narracao",
            json={"voz": "Siri"},
        )
    assert r.status_code == 400, r.text


def test_preview_tts_amostra_voz_gera_wav_e_devolve_audio() -> None:
    with TestClient(app) as client:
        data_dir = Path(app.state.data_dir)
        preview_path = data_dir / "tmp_preview_tts_amostra_voz_narracao" / "amostra_Aoede.wav"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_bytes(b"RIFF" + b"\x00" * 80)

        mock_gerar = AsyncMock(
            return_value=ResultadoApiPreviewTtsAmostraVozNarracaoTranscribrothers(
                caminho_wav=preview_path,
                modelo="gemini/gemini-2.5-flash-preview-tts",
                voz="Aoede",
                texto_caracteres=40,
            )
        )
        with patch(
            "transcribrothers_backend.main.gerar_arquivo_preview_tts_amostra_voz_narracao_transcribrothers",
            new=mock_gerar,
        ):
            r = client.post(
                "/api/preview-tts-amostra-voz-narracao",
                json={
                    "voz": "Aoede",
                    "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                    "perfil_tts": "experimental_voz",
                    "temperatura_tts": 0.6,
                    "ritmo_tts": "lento",
                },
            )
        assert r.status_code == 200, r.text
        assert r.headers["content-type"].startswith("audio/")
        assert len(r.content) > 40
        assert mock_gerar.await_args.kwargs["perfil_tts"] == "experimental_voz"
        assert mock_gerar.await_args.kwargs["temperatura_tts"] == 0.6
        assert mock_gerar.await_args.kwargs["ritmo_tts"] == "lento"
