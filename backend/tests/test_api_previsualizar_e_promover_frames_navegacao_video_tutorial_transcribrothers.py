"""API de prévia ‹ ›: não grava asset até promover; não apaga PNG do documento."""

import asyncio
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_previsualizar_e_promover_frames_navegacao_video_tutorial_transcribrothers import (
    NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS,
)

_PNG_MINIMO = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


async def _inserir_job_com_video_e_asset_documento(
    session_factory, job_id: str, data_dir: Path
) -> Path:
    work = data_dir / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "tela.png").write_bytes(_PNG_MINIMO)
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"fake-mp4")
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: test.mp4",
                file_id="-",
                error_message=None,
                result_markdown="![x](assets/tela.png)\n\n[0:31](?t=31.7)",
                steps_json={},
            )
        )
        await session.commit()
    return work


def test_get_e_delete_previa_nao_apagom_asset_do_documento() -> None:
    jid = novo_id_job()
    nome_prev = "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032100_indice_0000.png"
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            work = asyncio.run(_inserir_job_com_video_e_asset_documento(sf, jid, data_dir))
            preview_dir = work / NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS
            preview_dir.mkdir(parents=True)
            (preview_dir / nome_prev).write_bytes(_PNG_MINIMO)
            r_get = client.get(f"/api/jobs/{jid}/previsualizar-frames-video-tutorial/{nome_prev}")
            assert r_get.status_code == 200
            assert r_get.content[:8] == b"\x89PNG\r\n\x1a\n"
            r_del = client.request(
                "DELETE",
                f"/api/jobs/{jid}/previsualizar-frames-video-tutorial",
                json={
                    "nomes_para_apagar": [nome_prev, "tela.png"],
                    "nomes_protegidos": ["tela.png"],
                },
            )
            assert r_del.status_code == 200
            assert not (preview_dir / nome_prev).is_file()
            assert (work / "assets_exportados_para_markdown" / "tela.png").is_file()
        finally:
            asyncio.run(_remover_job(sf, jid))


def test_promover_previa_copia_para_assets_sem_apagar_documento() -> None:
    jid = novo_id_job()
    nome_prev = "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032100_indice_0000.png"
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            work = asyncio.run(_inserir_job_com_video_e_asset_documento(sf, jid, data_dir))
            preview_dir = work / NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS
            preview_dir.mkdir(parents=True)
            (preview_dir / nome_prev).write_bytes(_PNG_MINIMO)
            r = client.post(
                f"/api/jobs/{jid}/promover-frame-previsualizacao-para-assets-video-tutorial",
                json={"nome_arquivo_preview": nome_prev, "timestamp_segundos": 32.1},
            )
            assert r.status_code == 200
            body = r.json()
            assert body["nome_arquivo"].startswith("screenshot_manual_transcribrothers_")
            assert (work / "assets_exportados_para_markdown" / body["nome_arquivo"]).is_file()
            assert (work / "assets_exportados_para_markdown" / "tela.png").is_file()
        finally:
            asyncio.run(_remover_job(sf, jid))


def test_post_previsualizar_nao_grava_em_assets() -> None:
    jid = novo_id_job()
    nome_prev = "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032100_indice_0000.png"

    async def _fake_captura(**_kwargs):
        return [
            {
                "timestamp_segundos_solicitado": 32.1,
                "timestamp_segundos_efetivo": 32.1,
                "nome_arquivo": nome_prev,
            }
        ]

    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            work = asyncio.run(_inserir_job_com_video_e_asset_documento(sf, jid, data_dir))
            with patch(
                "transcribrothers_backend.main.capturar_frames_previsualizacao_navegacao_video_tutorial_transcribrothers",
                side_effect=_fake_captura,
            ):
                r = client.post(
                    f"/api/jobs/{jid}/previsualizar-frames-video-tutorial",
                    json={"timestamps_segundos": [32.1]},
                )
            assert r.status_code == 200
            itens = r.json()["itens"]
            assert itens[0]["nome_arquivo"] == nome_prev
            assert not (work / "assets_exportados_para_markdown" / nome_prev).is_file()
            assert (work / "assets_exportados_para_markdown" / "tela.png").is_file()
        finally:
            asyncio.run(_remover_job(sf, jid))


async def _remover_job(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
