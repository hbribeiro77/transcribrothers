"""Testes da API de regeneração de Markdown de reprodução de bug."""

import asyncio
import json
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.constante_texto_instrucao_regeneracao_reproducao_bug_sem_video_transcribrothers import (
    TEXTO_INSTRUCAO_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers import (
    montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers,
)


def test_montar_prefixo_inclui_bloco_sem_video_quando_solicitado() -> None:
    prefixo = montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers(
        documento_autonomo_sem_video=True,
        instrucoes_revisao_humana="Deixe os passos mais curtos.",
    )
    assert TEXTO_INSTRUCAO_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS in prefixo
    assert "Deixe os passos mais curtos." in prefixo


def test_regenerate_reproducao_bug_job_inexistente_retorna_404() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
    ):
        r = client.post("/api/jobs/job-inexistente-regen-bug/regenerate-reproducao-bug", json={})
        assert r.status_code == 404


def test_regenerate_reproducao_bug_destino_errado_retorna_400() -> None:
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
        r = client.post(f"/api/jobs/{job_id}/regenerate-reproducao-bug", json={})
        assert r.status_code == 400
        assert "reproducao_bug" in r.json()["detail"].lower() or "reprodução" in r.json()["detail"].lower()


def test_regenerate_reproducao_bug_sem_snapshot_retorna_400() -> None:
    job_id = novo_id_job()
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
    ):
        try:
            asyncio.run(_inserir_job_reproducao_bug_sem_snapshot_transcribrothers(app.state.session_factory, job_id))
            r = client.post(f"/api/jobs/{job_id}/regenerate-reproducao-bug", json={})
            assert r.status_code == 400
            assert "snapshot" in r.json()["detail"].lower()
        finally:
            asyncio.run(_remover_job_se_existir_transcribrothers(app.state.session_factory, job_id))


def test_regenerate_reproducao_bug_com_snapshot_agenda_task() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.agendar_regeneracao_markdown_reproducao_bug_em_task_assincrona",
        ) as mock_agendar,
    ):
        conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
        cliques_payload = json.dumps(
            {"cliques": [{"tRelativoMs": 1000, "url": "https://exemplo.test/"}]},
        ).encode("utf-8")
        r_st = client.post(
            "/api/staging/upload",
            data={"modo_recbrothers": "demonstracao_bug"},
            files={
                "video": ("bug.webm", conteudo, "video/webm"),
                "cliques_json": ("cliques.json", cliques_payload, "application/json"),
            },
        )
        staging_id = r_st.json()["staging_id"]
        with (
            patch(
                "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
                return_value=True,
            ),
            patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
        ):
            r_job = client.post(
                "/api/jobs/upload",
                data={
                    "staging_id": staging_id,
                    "destino_apos_transcricao": "reproducao_bug",
                },
            )
        job_id = r_job.json()["id"]
        snap = {
            "texto_completo": "fala",
            "idioma": "pt",
            "segmentos": [],
            "caminhos_frames_rel_job": [[1.0, "assets/frame.png"]],
        }
        async def _gravar_snapshot() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                steps = dict(row.steps_json or {})
                steps["regeneracao_tutorial_snapshot"] = snap
                row.steps_json = steps
                row.status = "completed"
                await session.commit()

        asyncio.run(_gravar_snapshot())

        r = client.post(
            f"/api/jobs/{job_id}/regenerate-reproducao-bug",
            json={"documento_autonomo_sem_video": True, "instrucoes_revisao_humana": "teste"},
        )
        assert r.status_code == 200, r.text
        mock_agendar.assert_called_once()
        kwargs = mock_agendar.call_args.kwargs
        assert kwargs["job_id"] == job_id
        assert kwargs["documento_autonomo_sem_video"] is True


async def _inserir_job_reproducao_bug_sem_snapshot_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: bug.webm",
                file_id="-",
                error_message=None,
                result_markdown=None,
                steps_json={"destino_apos_transcricao": "reproducao_bug"},
            )
        )
        await session.commit()


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()
