"""Testes de POST /api/jobs/projeto-em-branco."""

import asyncio
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_constante_markdown_inicial_projeto_em_branco_transcribrothers import (
    MARKDOWN_INICIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
)


def test_post_projeto_em_branco_cria_job_concluido_com_markdown_e_pasta() -> None:
    with TestClient(app) as client:
        r = client.post("/api/jobs/projeto-em-branco")
        assert r.status_code == 200, r.text
        body = r.json()
        job_id = body["id"]
        assert body["status"] == StatusJobTranscribrothers.completed.value
        assert body["source_kind"] == OrigemEntradaJobTranscribrothers.projeto_em_branco
        assert body["result_markdown"] == MARKDOWN_INICIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS
        assert body["steps_json"]["destino_apos_transcricao"] == "projeto_em_branco"
        assert body["steps_json"]["projeto_em_branco"] is True
        snap = body["steps_json"].get("regeneracao_tutorial_snapshot")
        assert isinstance(snap, dict)
        assert snap.get("snapshot_projeto_em_branco") is True
        assert snap.get("caminhos_frames_rel_job") == []

        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / job_id
        assert (work / "tutorial_gerado_transcribrothers.md").is_file()
        assert (work / "assets_exportados_para_markdown").is_dir()

        hist = client.get(f"/api/jobs/{job_id}/tutorial-markdown/historico-versoes")
        assert hist.status_code == 200
        versoes = hist.json()
        assert len(versoes) >= 1
        assert versoes[0]["origem"] == "projeto_em_branco"

        try:
            asyncio.run(_remover_job_se_existir_transcribrothers(app.state.session_factory, job_id))
            if work.exists():
                import shutil

                shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
