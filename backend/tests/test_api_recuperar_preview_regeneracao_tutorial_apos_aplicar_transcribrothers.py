"""Testes de POST /api/jobs/{id}/regenerate-tutorial/recuperar-preview-do-historico."""

import asyncio

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
    CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
)


async def _inserir_job_regeneracao_ja_aplicada_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: teste.mp4",
                file_id="-",
                error_message=None,
                result_markdown="# tutorial aplicado",
                steps_json={
                    "regeneracao_apenas_markdown": True,
                    "regeneracao_tutorial_aplicada_em": "2026-05-20T12:00:00+00:00",
                    "pipeline_fase": "regeneracao_tutorial_concluida",
                },
            )
        )
        await session.commit()


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()


def test_recuperar_preview_retorna_409_quando_regeneracao_ja_foi_aplicada() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        try:
            asyncio.run(_inserir_job_regeneracao_ja_aplicada_transcribrothers(sf, jid))
            r = client.post(f"/api/jobs/{jid}/regenerate-tutorial/recuperar-preview-do-historico")
            assert r.status_code == 409
            assert "já foi aplicada" in r.json()["detail"].lower()
            get_job = client.get(f"/api/jobs/{jid}")
            assert get_job.status_code == 200
            assert get_job.json()["result_markdown"] == "# tutorial aplicado"
            assert (
                CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS
                not in (get_job.json().get("steps_json") or {})
            )
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))
