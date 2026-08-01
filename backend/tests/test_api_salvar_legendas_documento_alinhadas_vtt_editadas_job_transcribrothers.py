"""PUT /api/jobs/{id}/legendas-documento-alinhadas — edição só do texto das cues."""

from __future__ import annotations

import asyncio
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def _criar_job_completed_com_assets(client: TestClient) -> str:
    criado = client.post("/api/jobs/projeto-em-branco")
    assert criado.status_code == 200
    job_id = criado.json()["id"]

    async def _marcar_completed() -> None:
        async with app.state.session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            assert row is not None
            row.status = "completed"
            row.steps_json = {
                "pipeline_video_narrado_documento": {
                    "ok": True,
                    "nome_arquivo_vtt": NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
                    "url_asset_vtt": f"/api/jobs/{job_id}/assets/{NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS}",
                    "quantidade_cues": 1,
                },
                "legendas_documento_alinhadas": {
                    "nome_arquivo": NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
                    "url_asset": f"/api/jobs/{job_id}/assets/{NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS}",
                    "quantidade_cues": 1,
                    "gerado_em": "2026-01-01T00:00:00+00:00",
                },
            }
            await session.commit()

    asyncio.run(_marcar_completed())
    return job_id


def test_put_legendas_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.put(
            "/api/jobs/00000000-0000-0000-0000-000000000000/legendas-documento-alinhadas",
            json={
                "cues": [
                    {"inicio_segundos": 0.0, "fim_segundos": 1.0, "texto": "oi"},
                ],
            },
        )
    assert r.status_code == 404


def test_put_legendas_cues_vazio_400() -> None:
    with TestClient(app) as client:
        job_id = _criar_job_completed_com_assets(client)
        r = client.put(
            f"/api/jobs/{job_id}/legendas-documento-alinhadas",
            json={"cues": []},
        )
    assert r.status_code == 400
    assert "cue" in r.json()["detail"].lower()


def test_put_legendas_texto_so_espacos_400() -> None:
    with TestClient(app) as client:
        job_id = _criar_job_completed_com_assets(client)
        r = client.put(
            f"/api/jobs/{job_id}/legendas-documento-alinhadas",
            json={
                "cues": [
                    {"inicio_segundos": 0.0, "fim_segundos": 1.0, "texto": "   \n  "},
                ],
            },
        )
    assert r.status_code == 400


def test_put_legendas_fim_antes_inicio_400() -> None:
    with TestClient(app) as client:
        job_id = _criar_job_completed_com_assets(client)
        r = client.put(
            f"/api/jobs/{job_id}/legendas-documento-alinhadas",
            json={
                "cues": [
                    {"inicio_segundos": 2.0, "fim_segundos": 1.0, "texto": "x"},
                ],
            },
        )
    assert r.status_code == 400


def test_put_legendas_grava_vtt_e_atualiza_steps() -> None:
    with TestClient(app) as client:
        job_id = _criar_job_completed_com_assets(client)
        r = client.put(
            f"/api/jobs/{job_id}/legendas-documento-alinhadas",
            json={
                "cues": [
                    {
                        "inicio_segundos": 0.0,
                        "fim_segundos": 1.5,
                        "texto": "  Primeira frase editada  ",
                    },
                    {
                        "inicio_segundos": 1.5,
                        "fim_segundos": 3.0,
                        "texto": "Segunda frase",
                    },
                ],
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        assert body["quantidade_cues"] == 2
        assert body["nome_arquivo"] == NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
        assert body["url_asset"] == (
            f"/api/jobs/{job_id}/assets/{NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS}"
        )

        data_dir = Path(app.state.data_dir)
        vtt_path = (
            data_dir
            / "jobs"
            / job_id
            / "assets_exportados_para_markdown"
            / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
        )
        assert vtt_path.is_file()
        conteudo = vtt_path.read_text(encoding="utf-8")
        assert "WEBVTT" in conteudo
        assert "Primeira frase editada" in conteudo
        assert "Segunda frase" in conteudo
        assert "00:00:00.000 --> 00:00:01.500" in conteudo

        job_get = client.get(f"/api/jobs/{job_id}")
        assert job_get.status_code == 200
        steps = job_get.json()["steps_json"]
        leg = steps["legendas_documento_alinhadas"]
        assert leg["quantidade_cues"] == 2
        assert "editado_em" in leg
        pipe = steps["pipeline_video_narrado_documento"]
        assert pipe["quantidade_cues"] == 2
        assert pipe["url_asset_vtt"] == body["url_asset"]
        assert "legendas_editadas_em" in pipe
