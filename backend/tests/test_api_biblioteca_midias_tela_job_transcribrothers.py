"""API biblioteca-midias-tela: listar, upload, servir e apagar."""

from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_biblioteca_midias_tela_job_transcribrothers import (
    ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
    listar_itens_biblioteca_midias_tela_do_work_transcribrothers,
)


def test_api_biblioteca_midias_tela_listar_upload_servir_e_apagar(tmp_path: Path) -> None:
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
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"ENTRADA" + b"x" * 40)

        async def _ok() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_ok())

        lista_vazia = client.get(f"/api/jobs/{job_id}/biblioteca-midias-tela")
        assert lista_vazia.status_code == 200, lista_vazia.text
        corpo0 = lista_vazia.json()
        assert corpo0["entrada"]["id"] == ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS
        assert corpo0["itens"] == []

        upload = client.post(
            f"/api/jobs/{job_id}/biblioteca-midias-tela",
            files={"video": ("demo_extra.mp4", BytesIO(b"BROLL" + b"y" * 80), "video/mp4")},
        )
        assert upload.status_code == 200, upload.text
        item = upload.json()["item"]
        id_midia = item["id"]
        assert id_midia.startswith("m")
        assert item["nome_original"] == "demo_extra.mp4"
        assert item["eh_entrada"] is False

        lista = client.get(f"/api/jobs/{job_id}/biblioteca-midias-tela")
        assert lista.status_code == 200
        assert len(lista.json()["itens"]) == 1
        assert listar_itens_biblioteca_midias_tela_do_work_transcribrothers(work)

        stream = client.get(f"/api/jobs/{job_id}/biblioteca-midias-tela/arquivo/{id_midia}")
        assert stream.status_code == 200
        assert stream.content.startswith(b"BROLL")

        apagar = client.delete(f"/api/jobs/{job_id}/biblioteca-midias-tela/{id_midia}")
        assert apagar.status_code == 200
        assert listar_itens_biblioteca_midias_tela_do_work_transcribrothers(work) == []
        assert (
            client.get(f"/api/jobs/{job_id}/biblioteca-midias-tela/arquivo/{id_midia}").status_code
            == 404
        )
