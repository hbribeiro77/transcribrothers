"""Testes do backfill de snapshot para jobs legados de reprodução de bug."""

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_util_garantir_snapshot_regeneracao_reproducao_bug_job_legado_transcribrothers import (
    montar_rels_snapshot_a_partir_de_pngs_assets_reproducao_bug_transcribrothers,
)


def test_montar_rels_a_partir_de_pngs_com_offset_ms_no_nome(tmp_path: Path) -> None:
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir()
    (assets / "screenshot_reproducao_bug_recbrothers_frame_no_offset_ms_0000003000_indice_0001.png").write_bytes(
        b"x"
    )
    (assets / "screenshot_reproducao_bug_recbrothers_frame_no_offset_ms_0000001000_indice_0000.png").write_bytes(
        b"x"
    )
    rels = montar_rels_snapshot_a_partir_de_pngs_assets_reproducao_bug_transcribrothers(assets)
    assert rels == [
        (1.0, "assets/screenshot_reproducao_bug_recbrothers_frame_no_offset_ms_0000001000_indice_0000.png"),
        (3.0, "assets/screenshot_reproducao_bug_recbrothers_frame_no_offset_ms_0000003000_indice_0001.png"),
    ]


def test_get_job_backfill_snapshot_reproducao_bug_legado() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
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
        assert r_st.status_code == 200, r_st.text
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
        assert r_job.status_code == 200, r_job.text
        job_id = r_job.json()["id"]
        data_dir = Path(app.state.data_dir)
        work = data_dir / "jobs" / job_id
        assets = work / "assets_exportados_para_markdown"
        assets.mkdir(parents=True, exist_ok=True)
        nome_png = (
            "screenshot_reproducao_bug_recbrothers_frame_no_offset_ms_0000001000_indice_0000.png"
        )
        (assets / nome_png).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
        md = f"# Bug\n\n![](assets/{nome_png})\n"

        async def _simular_job_legado_concluido() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                steps = dict(row.steps_json or {})
                steps.pop("regeneracao_tutorial_snapshot", None)
                row.steps_json = steps
                row.status = "completed"
                row.result_markdown = md
                await session.commit()

        asyncio.run(_simular_job_legado_concluido())

        r_get = client.get(f"/api/jobs/{job_id}")
        assert r_get.status_code == 200, r_get.text
        body = r_get.json()
        snap = body["steps_json"].get("regeneracao_tutorial_snapshot")
        assert isinstance(snap, dict)
        assert snap.get("caminhos_frames_rel_job") == [[1.0, f"assets/{nome_png}"]]
        assert body["steps_json"].get("regeneracao_tutorial_snapshot_backfill_reproducao_bug_em")
