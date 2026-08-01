"""POST /api/jobs/{id}/preview-tts-cue-narracao."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_api_preview_tts_cue_narracao_texto_atual_job_transcribrothers import (
    ResultadoApiPreviewTtsCueNarracaoTranscribrothers,
)
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)


def test_preview_tts_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/00000000-0000-0000-0000-000000000000/preview-tts-cue-narracao",
            json={"indice": 0, "texto": "olá mundo teste"},
        )
    assert r.status_code == 404


def test_preview_tts_gera_wav_e_devolve_audio() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]

        async def _completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_completed())
        data_dir = Path(app.state.data_dir)
        preview_path = (
            data_dir
            / "jobs"
            / job_id
            / "wavs_narracao_por_cue"
            / "preview_cue_narracao_0000.wav"
        )
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_bytes(b"RIFF" + b"\x00" * 80)

        with patch(
            "transcribrothers_backend.main.gerar_arquivo_preview_tts_cue_narracao_job_transcribrothers",
            new=AsyncMock(
                return_value=ResultadoApiPreviewTtsCueNarracaoTranscribrothers(
                    caminho_wav=preview_path,
                    modelo="gemini/gemini-2.5-flash-preview-tts",
                    texto_caracteres=10,
                )
            ),
        ):
            r = client.post(
                f"/api/jobs/{job_id}/preview-tts-cue-narracao",
                json={
                    "indice": 0,
                    "texto": "texto novo da cue para previa",
                    "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                },
            )
        assert r.status_code == 200, r.text
        assert r.headers["content-type"].startswith("audio/")
        assert len(r.content) > 40
