"""Upload direto de vídeo com destino reproducao_bug (JSON de cliques opcional)."""

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_staging_video_importacao_recbrothers_transcribrothers import (
    NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS,
)


def _patch_credenciais_e_pipeline() -> tuple:
    return (
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
    )


def test_upload_reproducao_bug_video_local_sem_staging_sem_cliques_retorna_200() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 128
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    with TestClient(app) as client, p1, p2, p3:
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "reproducao_bug"},
            files={"video": ("bug-local.webm", conteudo, "video/webm")},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["steps_json"]["destino_apos_transcricao"] == "reproducao_bug"
    assert body["steps_json"].get("reproducao_bug_sem_json_cliques") is True
    assert body["steps_json"].get("reproducao_bug_total_cliques") == 0


def test_upload_reproducao_bug_com_cliques_json_opcional_grava_arquivo_no_job() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 128
    cliques_payload = json.dumps(
        {"cliques": [{"tRelativoMs": 1200, "url": "https://exemplo.test/pagina"}]},
    ).encode("utf-8")
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    with TestClient(app) as client, p1, p2, p3:
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "reproducao_bug"},
            files={
                "video": ("bug-com-json.webm", conteudo, "video/webm"),
                "cliques_json": ("cliques.json", cliques_payload, "application/json"),
            },
        )
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]
    assert r.json()["steps_json"].get("reproducao_bug_total_cliques") == 1
    assert "reproducao_bug_sem_json_cliques" not in r.json()["steps_json"]

    data_dir: Path = app.state.data_dir
    cliques_job = data_dir / "jobs" / job_id / NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS
    assert cliques_job.is_file()
    try:
        asyncio.run(_remover_job_se_existir(app.state.session_factory, job_id))
    finally:
        import shutil

        shutil.rmtree(data_dir / "jobs" / job_id, ignore_errors=True)


def test_staging_sem_cliques_aceita_destino_reproducao_bug() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    with TestClient(app) as client:
        r_st = client.post(
            "/api/staging/upload",
            data={"modo_recbrothers": "demonstracao_bug"},
            files={"video": ("bug.webm", conteudo, "video/webm")},
        )
        assert r_st.status_code == 200, r_st.text
        staging_id = r_st.json()["staging_id"]
        assert r_st.json()["cliques_json_presente"] is False

        p1, p2, p3 = _patch_credenciais_e_pipeline()
        with p1, p2, p3:
            r_job = client.post(
                "/api/jobs/upload",
                data={
                    "staging_id": staging_id,
                    "destino_apos_transcricao": "reproducao_bug",
                },
            )
        assert r_job.status_code == 200, r_job.text
        assert r_job.json()["steps_json"].get("reproducao_bug_sem_json_cliques") is True


async def _remover_job_se_existir(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
