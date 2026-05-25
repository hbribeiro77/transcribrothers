"""Testes de staging com JSON de cliques e destino reproducao_bug."""

import asyncio
import json
import shutil
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)


def test_staging_upload_com_cliques_e_job_reproducao_bug() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    cliques_payload = json.dumps(
        {
            "versao": 1,
            "cliques": [
                {
                    "tRelativoMs": 500,
                    "xNorm": 0.5,
                    "yNorm": 0.5,
                    "url": "https://exemplo.test/",
                },
            ],
        },
    ).encode("utf-8")

    with TestClient(app) as client:
        r_up = client.post(
            "/api/staging/upload",
            data={"modo_recbrothers": "demonstracao_bug"},
            files={
                "video": ("recbrothers-bug.webm", conteudo, "video/webm"),
                "cliques_json": ("cliques.json", cliques_payload, "application/json"),
            },
        )
        assert r_up.status_code == 200, r_up.text
        body = r_up.json()
        assert body["cliques_json_presente"] is True
        assert body["total_cliques"] == 1
        staging_id = body["staging_id"]

        r_meta = client.get(f"/api/staging/{staging_id}")
        assert r_meta.status_code == 200
        assert r_meta.json()["total_cliques"] == 1

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
                    "destino_apos_transcricao": "reproducao_bug",
                },
            )
        assert r_job.status_code == 200, r_job.text
        job_id = r_job.json()["id"]
        assert r_job.json()["steps_json"]["destino_apos_transcricao"] == "reproducao_bug"

        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / job_id
        cliques_job = work / "cliques_demonstracao_bug_recbrothers.json"
        assert cliques_job.is_file()

        try:
            asyncio.run(_remover_job_se_existir(app.state.session_factory, job_id))
            if work.exists():
                shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass


async def _remover_job_se_existir(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
