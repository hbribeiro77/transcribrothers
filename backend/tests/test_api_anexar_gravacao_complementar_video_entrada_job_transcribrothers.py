"""API: anexar gravação complementar, unificar video_entrada e reprocessar."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS,
)


def test_api_anexar_gravacao_complementar_unifica_e_agenda_pipeline(tmp_path: Path) -> None:
    async def _fake_unificar(*, work, caminho_video_complementar, nome_original_complementar):
        assert caminho_video_complementar.is_file()
        assert nome_original_complementar.endswith(".webm")
        final = work / "video_entrada_arquivo_local.mp4"
        final.write_bytes(b"UNIFICADO-API")
        (work / "audio_extraido_para_transcricao.wav").unlink(missing_ok=True)
        (work / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).unlink(
            missing_ok=True
        )
        return {
            "saved_as": final.name,
            "bytes_written": final.stat().st_size,
            "duracao_video_segundos": 99.0,
            "clip_arquivado_antes": "001_antes.webm",
            "clip_arquivado_complementar": "002_complementar_x.webm",
            "nome_original_complementar": nome_original_complementar,
            "unificado_em_utc": "20260804T153000Z",
        }

    with (
        patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            side_effect=lambda _d, jid: tmp_path / "jobs" / jid,
        ),
        patch(
            "transcribrothers_backend.main.unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers",
            new=AsyncMock(side_effect=_fake_unificar),
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona") as mock_agendar,
        TestClient(app) as client,
    ):
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]
        work = tmp_path / "jobs" / job_id
        work.mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.webm").write_bytes(b"VID1")
        (work / "audio_extraido_para_transcricao.wav").write_bytes(b"WAV")
        (work / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).write_text(
            "{}", encoding="utf-8"
        )

        async def _marcar_completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                row.result_markdown = "# antigo"
                row.steps_json = {
                    **(row.steps_json or {}),
                    "destino_apos_transcricao": "gerar_tutorial",
                    "tipo_entrada_midia": "video",
                    "audio_ok": True,
                    "regeneracao_tutorial_snapshot": {"x": 1},
                }
                await session.commit()

        asyncio.run(_marcar_completed())

        r = client.post(
            f"/api/jobs/{job_id}/anexar-gravacao-complementar-video-entrada",
            files={"video": ("parte2.webm", b"\x1a\x45\xdf\xa3" + b"\0" * 64, "video/webm")},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "pending"
        assert body["result_markdown"] is None
        steps = body["steps_json"]
        assert steps["destino_apos_transcricao"] == "gerar_tutorial"
        assert steps["saved_as"] == "video_entrada_arquivo_local.mp4"
        assert steps["duracao_video_segundos"] == 99.0
        assert "audio_ok" not in steps
        assert "regeneracao_tutorial_snapshot" not in steps
        assert len(steps["gravacoes_complementares_unificadas"]) == 1
        assert (work / "video_entrada_arquivo_local.mp4").read_bytes() == b"UNIFICADO-API"
        mock_agendar.assert_called_once()


def test_api_anexar_gravacao_complementar_rejeita_job_em_execucao(tmp_path: Path) -> None:
    with (
        patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            side_effect=lambda _d, jid: tmp_path / "jobs" / jid,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona") as mock_agendar,
        TestClient(app) as client,
    ):
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]
        work = tmp_path / "jobs" / job_id
        work.mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"VID")

        async def _marcar_transcribing() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "transcribing"
                row.steps_json = {**(row.steps_json or {}), "tipo_entrada_midia": "video"}
                await session.commit()

        asyncio.run(_marcar_transcribing())

        r = client.post(
            f"/api/jobs/{job_id}/anexar-gravacao-complementar-video-entrada",
            files={"video": ("x.mp4", b"x" * 32, "video/mp4")},
        )
        assert r.status_code == 400
        assert "terminou" in r.json()["detail"].lower() or "completed" in r.json()["detail"].lower()
        mock_agendar.assert_not_called()
