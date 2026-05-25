"""Testes de GET /api/jobs e DELETE /api/jobs/{id} (lista e limpeza)."""

import asyncio

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)


def test_get_api_jobs_retorna_lista() -> None:
    with TestClient(app) as client:
        r = client.get("/api/jobs?limit=5")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        if len(body) > 0:
            item = body[0]
            assert "id" in item and "status" in item
            assert "tem_resultado_markdown" in item
            assert "titulo_tutorial_markdown_h1" in item


def test_get_api_jobs_inclui_titulo_h1_quando_markdown_tem_h1() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        try:
            asyncio.run(_inserir_job_completo_para_teste_exclusao_transcribrothers(sf, jid))
            r = client.get("/api/jobs?limit=200")
            assert r.status_code == 200
            body = r.json()
            match = next((x for x in body if x["id"] == jid), None)
            assert match is not None
            assert match.get("titulo_tutorial_markdown_h1") == "teste exclusão"
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))


def test_delete_job_inexistente_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.delete("/api/jobs/00000000-0000-4000-8000-000000000099")
        assert r.status_code == 404


async def _inserir_job_completo_para_teste_exclusao_transcribrothers(
    session_factory,
    job_id: str,
) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.drive,
                drive_url="https://example.invalid/test-list-delete",
                file_id="x",
                error_message=None,
                result_markdown="# teste exclusão",
                steps_json={},
            )
        )
        await session.commit()


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()


async def _inserir_job_em_transcribing_para_teste_exclusao_forcada_transcribrothers(
    session_factory,
    job_id: str,
) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.transcribing.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: teste.mp4",
                file_id="-",
                error_message=None,
                result_markdown=None,
                steps_json={"pipeline_fase": "transcrevendo_audio"},
            )
        )
        await session.commit()


def test_delete_job_em_transcribing_apaga_registo_e_get_fica_404() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        try:
            asyncio.run(_inserir_job_em_transcribing_para_teste_exclusao_forcada_transcribrothers(sf, jid))
            r = client.delete(f"/api/jobs/{jid}")
            assert r.status_code == 200
            assert r.json() == {"ok": True}
            assert client.get(f"/api/jobs/{jid}").status_code == 404
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))


def test_delete_job_completo_apaga_registo_e_get_fica_404() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        try:
            asyncio.run(_inserir_job_completo_para_teste_exclusao_transcribrothers(sf, jid))
            r1 = client.get(f"/api/jobs/{jid}")
            assert r1.status_code == 200
            r2 = client.delete(f"/api/jobs/{jid}")
            assert r2.status_code == 200
            assert r2.json() == {"ok": True}
            r3 = client.get(f"/api/jobs/{jid}")
            assert r3.status_code == 404
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))
