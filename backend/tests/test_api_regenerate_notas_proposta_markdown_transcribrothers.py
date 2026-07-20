"""Testes da API de regeneração de Markdown de notas de proposta."""

import asyncio
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)


def test_regenerate_notas_proposta_job_inexistente_retorna_404() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
    ):
        r = client.post("/api/jobs/job-inexistente-regen-notas/regenerate-notas-proposta", json={})
        assert r.status_code == 404


def test_regenerate_notas_proposta_destino_errado_retorna_400() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
    ):
        r_up = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "gerar_tutorial"},
            files={"video": ("v.webm", b"\x00" * 128, "video/webm")},
        )
        assert r_up.status_code == 200, r_up.text
        job_id = r_up.json()["id"]
        r = client.post(f"/api/jobs/{job_id}/regenerate-notas-proposta", json={})
        assert r.status_code == 400
        assert "notas" in r.json()["detail"].lower()


def test_regenerate_notas_proposta_sem_snapshot_retorna_400() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
    ):
        r_up = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
            files={"video": ("reuniao.webm", b"\x1a\x45\xdf\xa3" + b"\x00" * 64, "video/webm")},
        )
        assert r_up.status_code == 200, r_up.text
        job_id = r_up.json()["id"]
        r = client.post(f"/api/jobs/{job_id}/regenerate-notas-proposta", json={})
        assert r.status_code == 400
        assert "snapshot" in r.json()["detail"].lower()


def test_regenerate_notas_proposta_com_snapshot_agenda_task() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.agendar_regeneracao_markdown_notas_proposta_funcionalidade_em_task_assincrona",
        ) as mock_agendar,
    ):
        with (
            patch(
                "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
                return_value=True,
            ),
            patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
        ):
            r_job = client.post(
                "/api/jobs/upload",
                data={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
                files={"video": ("reuniao.webm", b"\x1a\x45\xdf\xa3" + b"\x00" * 64, "video/webm")},
            )
        assert r_job.status_code == 200, r_job.text
        job_id = r_job.json()["id"]
        snap = {
            "texto_completo": "Discussão sobre feature X.",
            "idioma": "pt",
            "segmentos": [],
            "caminhos_frames_rel_job": [],
        }

        async def _gravar_snapshot() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                steps = dict(row.steps_json or {})
                steps["regeneracao_tutorial_snapshot"] = snap
                row.steps_json = steps
                row.status = "completed"
                row.result_markdown = "# Notas\n\n## Contexto"
                await session.commit()

        asyncio.run(_gravar_snapshot())

        r = client.post(
            f"/api/jobs/{job_id}/regenerate-notas-proposta",
            json={"documento_autonomo_sem_video": True, "instrucoes_revisao_humana": "Detalhe pendências."},
        )
        assert r.status_code == 200, r.text
        mock_agendar.assert_called_once()
        kwargs = mock_agendar.call_args.kwargs
        assert kwargs["job_id"] == job_id
        assert kwargs["documento_autonomo_sem_video"] is True
