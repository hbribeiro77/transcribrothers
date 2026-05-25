"""Pool de rels com fab_ctx e POST fab-anexos-contexto-imagem (projeto em branco)."""

import asyncio
import base64
import shutil
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_constante_prefixo_nome_arquivo_imagem_anexo_contexto_fab_projeto_em_branco_transcribrothers import (
    PREFIXO_NOME_ARQUIVO_IMAGEM_ANEXO_CONTEXTO_FAB_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_montar_rels_anexo_regeneracao_tutorial_com_disco_projeto_em_branco_transcribrothers import (
    montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers,
)

_BYTES_PNG_MINIMO_TRANSCRIBROTHERS = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def test_pool_rels_projeto_em_branco_inclui_fab_ctx_extra_no_disco(tmp_path: Path) -> None:
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    nome = f"{PREFIXO_NOME_ARQUIVO_IMAGEM_ANEXO_CONTEXTO_FAB_PROJETO_EM_BRANCO_TRANSCRIBROTHERS}_ms_0000000000001.png"
    (assets / nome).write_bytes(_BYTES_PNG_MINIMO_TRANSCRIBROTHERS)
    rel_extra = f"assets/{nome}"

    pool = montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers(
        markdown="# Documento\n\nSem imagens no markdown.",
        rels_snapshot=[],
        assets_dir=assets,
        caminhos_assets_png_contexto_fab_extra=[rel_extra],
        eh_projeto_em_branco=True,
    )

    caminhos = [rel for _, rel in pool]
    assert rel_extra in caminhos


def test_post_fab_anexo_imagem_projeto_em_branco_grava_png_com_prefixo() -> None:
    with TestClient(app) as client:
        r = client.post("/api/jobs/projeto-em-branco")
        assert r.status_code == 200, r.text
        job_id = r.json()["id"]
        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / job_id
        try:
            up = client.post(
                f"/api/jobs/{job_id}/fab-anexos-contexto-imagem",
                files={"imagem": ("anexo-teste.png", _BYTES_PNG_MINIMO_TRANSCRIBROTHERS, "image/png")},
            )
            assert up.status_code == 200, up.text
            body = up.json()
            assert body["caminho_relativo"].startswith("assets/")
            assert PREFIXO_NOME_ARQUIVO_IMAGEM_ANEXO_CONTEXTO_FAB_PROJETO_EM_BRANCO_TRANSCRIBROTHERS in body[
                "nome_arquivo"
            ]
            assert (work / "assets_exportados_para_markdown" / body["nome_arquivo"]).is_file()
        finally:
            sf = app.state.session_factory
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, job_id))
            if work.is_dir():
                shutil.rmtree(work, ignore_errors=True)


def test_post_fab_anexo_imagem_rejeita_job_que_nao_e_projeto_em_branco() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / jid
        try:
            asyncio.run(_inserir_job_upload_local_transcribrothers(sf, jid))
            up = client.post(
                f"/api/jobs/{jid}/fab-anexos-contexto-imagem",
                files={"imagem": ("x.png", _BYTES_PNG_MINIMO_TRANSCRIBROTHERS, "image/png")},
            )
            assert up.status_code == 400
            assert "projeto em branco" in (up.json().get("detail") or "").lower()
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(sf, jid))
            if work.is_dir():
                shutil.rmtree(work, ignore_errors=True)


async def _inserir_job_upload_local_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: test.mp4",
                file_id="-",
                error_message=None,
                result_markdown="# t",
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
