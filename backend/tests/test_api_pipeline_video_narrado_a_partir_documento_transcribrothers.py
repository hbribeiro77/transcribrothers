"""POST /api/jobs/{id}/pipeline-video-narrado-a-partir-documento."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    FASE_VIDEO_NARRADO_AGENDADO,
)


def test_pipeline_video_narrado_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/00000000-0000-0000-0000-000000000000/pipeline-video-narrado-a-partir-documento",
            json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
        )
    assert r.status_code == 404


def test_pipeline_video_narrado_sem_markdown_retorna_400() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        async def _limpar_md() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.result_markdown = ""
                row.status = "completed"
                await session.commit()

        asyncio.run(_limpar_md())
        r = client.post(
            f"/api/jobs/{job_id}/pipeline-video-narrado-a-partir-documento",
            json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
        )
    assert r.status_code == 400
    assert "markdown" in r.json()["detail"].lower()


def test_pipeline_video_narrado_sem_snapshot_retorna_400(tmp_path: Path) -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        async def _marcar_ok() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                row.result_markdown = "# Tutorial\n\nTexto narrável."
                await session.commit()

        asyncio.run(_marcar_ok())

        video_fake = tmp_path / "video_entrada_arquivo_local.mp4"
        video_fake.write_bytes(b"vid")

        with (
            patch(
                "transcribrothers_backend.main._diretorio_trabalho_job",
                return_value=tmp_path,
            ),
            patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ),
        ):
            r = client.post(
                f"/api/jobs/{job_id}/pipeline-video-narrado-a-partir-documento",
                json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
            )
    assert r.status_code == 400
    assert "snapshot" in r.json()["detail"].lower() or "transcri" in r.json()["detail"].lower()


def test_pipeline_video_narrado_agenda_task_e_grava_fase(tmp_path: Path) -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        async def _marcar_ok() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                row.result_markdown = "# Tutorial\n\nOlá mundo."
                await session.commit()

        asyncio.run(_marcar_ok())

        video_fake = tmp_path / "video_entrada_arquivo_local.mp4"
        video_fake.write_bytes(b"vid")
        snap_path = tmp_path / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS
        snap_path.write_text(
            json.dumps(
                {
                    "versao": 1,
                    "texto_completo": "Olá mundo.",
                    "idioma_detectado": "pt",
                    "segmentos": [
                        {"inicio_segundos": 0.0, "fim_segundos": 2.0, "texto": "Olá mundo."},
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with (
            patch(
                "transcribrothers_backend.main._diretorio_trabalho_job",
                return_value=tmp_path,
            ),
            patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ),
            patch(
                "transcribrothers_backend.main.resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers",
                return_value="openai/gpt-4o-mini",
            ),
            patch(
                "transcribrothers_backend.main.agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona",
            ) as mock_agendar,
        ):
            r = client.post(
                f"/api/jobs/{job_id}/pipeline-video-narrado-a-partir-documento",
                json={
                    "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                    "litellm_model_chat": "openai/gpt-4o-mini",
                },
            )

        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "generating_tutorial"
        assert body["steps_json"]["pipeline_fase"] == FASE_VIDEO_NARRADO_AGENDADO
        assert body["steps_json"]["pipeline_video_narrado_modelo_chat_limpeza"] == "openai/gpt-4o-mini"
        assert body["steps_json"]["pipeline_video_narrado_perfil_tts"] == "padrao"
        assert body["steps_json"]["pipeline_video_narrado_paralelismo_tts_experimental"] == 3
        assert body["steps_json"]["pipeline_video_narrado_temperatura_tts"] == 0.4
        assert body["steps_json"]["pipeline_video_narrado_ritmo_tts"] == "normal"
        assert body["steps_json"]["pipeline_video_narrado_diretriz_conteudo_legendas"] == "conservador"
        mock_agendar.assert_called_once()
        assert mock_agendar.call_args.kwargs["job_id"] == job_id
        assert mock_agendar.call_args.kwargs["modelo_tts"] == "gemini/gemini-2.5-flash-preview-tts"
        assert mock_agendar.call_args.kwargs["modelo_chat_limpeza"] == "openai/gpt-4o-mini"
        assert mock_agendar.call_args.kwargs["perfil_tts"] == "padrao"
        assert mock_agendar.call_args.kwargs["paralelismo_tts_experimental"] == 3
        assert mock_agendar.call_args.kwargs["temperatura_tts"] == 0.4
        assert mock_agendar.call_args.kwargs["ritmo_tts"] == "normal"
        assert mock_agendar.call_args.kwargs["diretriz_conteudo_legendas"] == "conservador"


def test_pipeline_video_narrado_aceita_perfil_tts_experimental(tmp_path: Path) -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200, criado.text
        job_id = criado.json()["id"]

        async def _marcar_ok() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                row.result_markdown = "# Tutorial\n\nOlá mundo."
                await session.commit()

        asyncio.run(_marcar_ok())

        video_fake = tmp_path / "video_entrada_arquivo_local.mp4"
        video_fake.write_bytes(b"vid")
        snap_path = tmp_path / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS
        snap_path.write_text(
            json.dumps(
                {
                    "versao": 1,
                    "texto_completo": "Olá mundo.",
                    "idioma_detectado": "pt",
                    "segmentos": [
                        {"inicio_segundos": 0.0, "fim_segundos": 2.0, "texto": "Olá mundo."},
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with (
            patch(
                "transcribrothers_backend.main._diretorio_trabalho_job",
                return_value=tmp_path,
            ),
            patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ),
            patch(
                "transcribrothers_backend.main.resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers",
                return_value="openai/gpt-4o-mini",
            ),
            patch(
                "transcribrothers_backend.main.agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona",
            ) as mock_agendar,
        ):
            r = client.post(
                f"/api/jobs/{job_id}/pipeline-video-narrado-a-partir-documento",
                json={
                    "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                    "litellm_model_chat": "openai/gpt-4o-mini",
                    "perfil_tts": "experimental_voz",
                    "temperatura_tts": 0.7,
                    "ritmo_tts": "rapido",
                    "diretriz_conteudo_legendas": "mais_falavel",
                },
            )

        assert r.status_code == 200, r.text
        body = r.json()
        assert body["steps_json"]["pipeline_video_narrado_perfil_tts"] == "experimental_voz"
        assert body["steps_json"]["pipeline_video_narrado_paralelismo_tts_experimental"] == 3
        assert body["steps_json"]["pipeline_video_narrado_temperatura_tts"] == 0.7
        assert body["steps_json"]["pipeline_video_narrado_ritmo_tts"] == "rapido"
        assert body["steps_json"]["pipeline_video_narrado_diretriz_conteudo_legendas"] == "mais_falavel"
        assert mock_agendar.call_args.kwargs["perfil_tts"] == "experimental_voz"
        assert mock_agendar.call_args.kwargs["paralelismo_tts_experimental"] == 3
        assert mock_agendar.call_args.kwargs["temperatura_tts"] == 0.7
        assert mock_agendar.call_args.kwargs["ritmo_tts"] == "rapido"
        assert mock_agendar.call_args.kwargs["diretriz_conteudo_legendas"] == "mais_falavel"
