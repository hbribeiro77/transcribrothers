"""GET /api/jobs/{id}/imagens-tutorial/lista-assets — lista PNGs originais em assets/."""

import asyncio
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)


def test_lista_assets_job_inexistente_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.get("/api/jobs/00000000-0000-4000-8000-000000000099/imagens-tutorial/lista-assets")
        assert r.status_code == 404


def test_lista_assets_retorna_png_do_disco_e_flag_referenciado_no_markdown() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_com_markdown_e_png_transcribrothers(sf, jid, data_dir))
            r = client.get(f"/api/jobs/{jid}/imagens-tutorial/lista-assets")
            assert r.status_code == 200
            body = r.json()
            assert "itens" in body
            nomes = [x["nome_arquivo_original"] for x in body["itens"]]
            assert "captura_01.png" in nomes
            item = next(x for x in body["itens"] if x["nome_arquivo_original"] == "captura_01.png")
            assert item["referenciado_no_markdown"] is True
            assert item["tem_arquivo_anotado"] is False
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))
            work = data_dir / "jobs" / jid
            if work.is_dir():
                import shutil

                shutil.rmtree(work, ignore_errors=True)


async def _inserir_job_com_markdown_e_png_transcribrothers(session_factory, job_id: str, data_dir: Path) -> None:
    work = data_dir / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "captura_01.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01")
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: test.mp4",
                file_id="-",
                error_message=None,
                result_markdown="# t\n\n![](assets/captura_01.png)",
                steps_json={},
            )
        )
        await session.commit()


def test_delete_asset_remove_arquivo_e_referencia_markdown() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_com_markdown_e_png_transcribrothers(sf, jid, data_dir))
            r = client.delete(f"/api/jobs/{jid}/assets/captura_01.png")
            assert r.status_code == 200
            body = r.json()
            assert "captura_01.png" not in (body.get("result_markdown") or "")
            assert not (data_dir / "jobs" / jid / "assets_exportados_para_markdown" / "captura_01.png").is_file()
            r2 = client.get(f"/api/jobs/{jid}/imagens-tutorial/lista-assets")
            assert r2.json()["itens"] == []
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))
            work = data_dir / "jobs" / jid
            if work.is_dir():
                import shutil

                shutil.rmtree(work, ignore_errors=True)


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
