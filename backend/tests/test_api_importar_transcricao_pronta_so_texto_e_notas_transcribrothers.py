"""POST /api/jobs/importar-transcricao — snapshot sem STT; notas via reprocessamento."""

from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)


def test_importar_texto_destino_so_transcricao_completed_com_snapshot_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/importar-transcricao",
            data={
                "destino_apos_transcricao": "so_transcricao",
                "texto": "Fala importada de teste para o job.",
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "completed"
        assert body["steps_json"]["transcricao_importada"] is True
        assert body["steps_json"]["destino_apos_transcricao"] == "so_transcricao"
        assert body["steps_json"]["pode_gerar_outro_formato"] is True
        assert "Fala importada" in (body.get("result_markdown") or "")
        data_dir: Path = app.state.data_dir
        work = data_dir / "jobs" / body["id"]
        snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work)
        assert snap is not None
        assert "Fala importada" in snap.texto_completo


def test_importar_srt_destino_notas_agenda_pipeline_transcribrothers() -> None:
    srt = """1
00:00:00,000 --> 00:00:01,000
Descoberta da feature X
"""
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona") as agendar,
    ):
        r = client.post(
            "/api/jobs/importar-transcricao",
            data={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
            files={"arquivo": ("reuniao.srt", srt.encode("utf-8"), "application/x-subrip")},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "pending"
        assert body["steps_json"]["destino_apos_transcricao"] == "notas_proposta_funcionalidade"
        assert body["steps_json"]["reprocessamento_pos_transcricao_apenas"] is True
        assert body["steps_json"]["transcricao_importada"] is True
        agendar.assert_called_once()


def test_importar_destino_tutorial_retorna_400_transcribrothers() -> None:
    with (
        TestClient(app) as client,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
    ):
        r = client.post(
            "/api/jobs/importar-transcricao",
            data={
                "destino_apos_transcricao": "gerar_tutorial",
                "texto": "texto qualquer",
            },
        )
        assert r.status_code == 400


def test_gerar_outro_formato_notas_em_job_importado_sem_midia_transcribrothers() -> None:
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
        criado = client.post(
            "/api/jobs/importar-transcricao",
            data={
                "destino_apos_transcricao": "so_transcricao",
                "texto": "Base para gerar notas depois.",
            },
        )
        assert criado.status_code == 200, criado.text
        job_id = criado.json()["id"]
        r = client.post(
            f"/api/jobs/{job_id}/gerar-outro-formato",
            json={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["steps_json"]["destino_apos_transcricao"] == "notas_proposta_funcionalidade"


def test_gerar_outro_formato_tutorial_em_job_importado_retorna_400_transcribrothers() -> None:
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
        criado = client.post(
            "/api/jobs/importar-transcricao",
            data={"destino_apos_transcricao": "so_transcricao", "texto": "Só texto."},
        )
        job_id = criado.json()["id"]
        r = client.post(
            f"/api/jobs/{job_id}/gerar-outro-formato",
            json={"destino_apos_transcricao": "gerar_tutorial"},
        )
        assert r.status_code == 400
        detail = r.json()["detail"].lower()
        assert "notas" in detail or "vídeo" in detail or "video" in detail
