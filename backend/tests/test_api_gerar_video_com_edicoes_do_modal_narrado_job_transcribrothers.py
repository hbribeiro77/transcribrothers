"""POST /api/jobs/{id}/gerar-video-com-edicoes-do-modal-narrado."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def test_post_gerar_video_edicoes_modal_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/00000000-0000-0000-0000-000000000000/gerar-video-com-edicoes-do-modal-narrado",
            json={
                "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                "cues": [{"inicio_segundos": 0, "fim_segundos": 1, "texto": "oi"}],
            },
        )
    assert r.status_code == 404


def test_post_gerar_video_edicoes_modal_agenda_quando_pronto() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]
        data_dir = Path(app.state.data_dir)
        work = data_dir / "jobs" / job_id
        assets = work / "assets_exportados_para_markdown"
        assets.mkdir(parents=True, exist_ok=True)
        (work / "wavs_narracao_por_cue").mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"fake")
        (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\noi\n",
            encoding="utf-8",
        )
        (work / "manifest_cues_narracao_janelas_video.json").write_text(
            '{"versao":1,"quantidade_cues":1,"cues":[{"texto":"oi","inicio_video_segundos":0,'
            '"fim_video_segundos":1,"origem_ancora":"markdown_t","casado":true}]}\n',
            encoding="utf-8",
        )

        async def _completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_completed())

        with patch(
            "transcribrothers_backend.main.agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona"
        ) as mock_agendar:
            with patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ):
                r = client.post(
                    f"/api/jobs/{job_id}/gerar-video-com-edicoes-do-modal-narrado",
                    json={
                        "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                        "cues": [
                            {
                                "inicio_segundos": 0.5,
                                "fim_segundos": 1.5,
                                "texto": "oi editado",
                                "sem_narracao": False,
                            },
                        ],
                        "janelas": [{"inicio_video_segundos": 0.0, "fim_video_segundos": 1.2}],
                    },
                )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "generating_tutorial"
        mock_agendar.assert_called_once()
        kwargs = mock_agendar.call_args.kwargs
        assert kwargs["cues_brutas"][0]["texto"] == "oi editado"
        assert kwargs["cues_brutas"][0]["sem_narracao"] is False
        assert kwargs["janelas_brutas"][0]["inicio_video_segundos"] == 0.0


def test_post_gerar_video_edicoes_modal_aceita_cue_sem_narracao() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]
        data_dir = Path(app.state.data_dir)
        work = data_dir / "jobs" / job_id
        assets = work / "assets_exportados_para_markdown"
        assets.mkdir(parents=True, exist_ok=True)
        (work / "wavs_narracao_por_cue").mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"fake")
        (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\noi\n",
            encoding="utf-8",
        )
        (work / "manifest_cues_narracao_janelas_video.json").write_text(
            '{"versao":1,"quantidade_cues":1,"cues":[{"texto":"oi","inicio_video_segundos":0,'
            '"fim_video_segundos":2,"origem_ancora":"markdown_t","casado":true}]}\n',
            encoding="utf-8",
        )

        async def _completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_completed())

        with patch(
            "transcribrothers_backend.main.agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona"
        ) as mock_agendar:
            with patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ):
                r = client.post(
                    f"/api/jobs/{job_id}/gerar-video-com-edicoes-do-modal-narrado",
                    json={
                        "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                        "cues": [
                            {
                                "inicio_segundos": 0.0,
                                "fim_segundos": 2.0,
                                "texto": "",
                                "sem_narracao": True,
                            },
                        ],
                        "janelas": [{"inicio_video_segundos": 0.0, "fim_video_segundos": 2.0}],
                    },
                )
        assert r.status_code == 200, r.text
        assert mock_agendar.call_args.kwargs["cues_brutas"][0]["sem_narracao"] is True


def test_post_gerar_video_edicoes_modal_aceita_job_cancelado() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]
        data_dir = Path(app.state.data_dir)
        work = data_dir / "jobs" / job_id
        assets = work / "assets_exportados_para_markdown"
        assets.mkdir(parents=True, exist_ok=True)
        (work / "wavs_narracao_por_cue").mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"fake")
        (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\noi\n",
            encoding="utf-8",
        )
        (work / "manifest_cues_narracao_janelas_video.json").write_text(
            '{"versao":1,"quantidade_cues":1,"cues":[{"texto":"oi","inicio_video_segundos":0,'
            '"fim_video_segundos":1,"origem_ancora":"markdown_t","casado":true}]}\n',
            encoding="utf-8",
        )

        async def _cancelled() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "cancelled"
                row.error_message = "Cancelado pelo usuário."
                row.steps_json = {
                    **dict(row.steps_json or {}),
                    "cancelamento_pipeline_solicitado": True,
                }
                await session.commit()

        asyncio.run(_cancelled())

        with patch(
            "transcribrothers_backend.main.agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona"
        ) as mock_agendar:
            with patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ):
                r = client.post(
                    f"/api/jobs/{job_id}/gerar-video-com-edicoes-do-modal-narrado",
                    json={
                        "litellm_model": "gemini/gemini-2.5-flash-preview-tts",
                        "cues": [
                            {
                                "inicio_segundos": 0.5,
                                "fim_segundos": 1.5,
                                "texto": "oi de novo",
                            },
                        ],
                    },
                )
        assert r.status_code == 200, r.text
        assert mock_agendar.called
        assert r.json()["status"] == "generating_tutorial"
        assert "cancelamento_pipeline_solicitado" not in (r.json().get("steps_json") or {})
