"""API midia-fonte: listar, servir e limpar cache."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)


def test_api_midia_fonte_listar_servir_e_limpar_cache(tmp_path: Path) -> None:
    with (
        patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            side_effect=lambda _d, jid: tmp_path / "jobs" / jid,
        ),
        TestClient(app) as client,
    ):
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        work = tmp_path / "jobs" / job_id
        work.mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"VID" + b"x" * 100)
        (work / "audio_extraido_para_transcricao.wav").write_bytes(b"WAV" + b"y" * 50)
        cache = work / "segmentos_video_narrado_retarget"
        cache.mkdir()
        (cache / "seg.mp4").write_bytes(b"CACHE")

        async def _ok() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_ok())

        lista = client.get(f"/api/jobs/{job_id}/midia-fonte")
        assert lista.status_code == 200, lista.text
        corpo = lista.json()
        assert corpo["cache_bytes"] == 5
        assert len(corpo["itens"]) >= 2

        wav = client.get(
            f"/api/jobs/{job_id}/midia-fonte/arquivo/audio_extraido_para_transcricao.wav"
        )
        assert wav.status_code == 200
        assert wav.content.startswith(b"WAV")

        bloqueado = client.get(f"/api/jobs/{job_id}/midia-fonte/arquivo/nao_existe.bin")
        assert bloqueado.status_code == 404

        limpar = client.post(f"/api/jobs/{job_id}/midia-fonte/limpar-cache")
        assert limpar.status_code == 200
        assert limpar.json()["cache_bytes"] == 0
        assert not cache.exists()
        assert (work / "video_entrada_arquivo_local.mp4").is_file()
