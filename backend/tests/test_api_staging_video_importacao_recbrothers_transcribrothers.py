"""Testes de staging de vídeo para importação RecBrothers."""

import asyncio
import shutil
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
def test_staging_upload_get_video_e_consume_em_jobs_upload() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    with TestClient(app) as client:
        r_up = client.post(
            "/api/staging/upload",
            files={"video": ("recbrothers-teste.webm", conteudo, "video/webm")},
        )
        assert r_up.status_code == 200, r_up.text
        body = r_up.json()
        staging_id = body["staging_id"]
        assert body["filename"] == "recbrothers-teste.webm"
        assert body["size_bytes"] == len(conteudo)

        r_meta = client.get(f"/api/staging/{staging_id}")
        assert r_meta.status_code == 200
        meta = r_meta.json()
        assert meta["staging_id"] == staging_id
        assert meta["ext"] == ".webm"

        r_video = client.get(f"/api/staging/{staging_id}/video")
        assert r_video.status_code == 200
        assert r_video.content == conteudo

        with (
            patch(
                "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
                return_value=True,
            ),
            patch(
                "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
                return_value=True,
            ),
            patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
        ):
            r_job = client.post(
                "/api/jobs/upload",
                data={
                    "staging_id": staging_id,
                    "destino_apos_transcricao": "gerar_tutorial",
                },
            )
        assert r_job.status_code == 200, r_job.text
        job_id = r_job.json()["id"]

        r_meta_apos = client.get(f"/api/staging/{staging_id}")
        assert r_meta_apos.status_code == 404

        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / job_id
        video_job = work / "video_entrada_arquivo_local.webm"
        assert video_job.is_file()
        assert video_job.read_bytes() == conteudo

        try:
            asyncio.run(_remover_job_se_existir(app.state.session_factory, job_id))
            if work.exists():
                shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass


def test_staging_nao_encontrado_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.get("/api/staging/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404


async def _remover_job_se_existir(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
