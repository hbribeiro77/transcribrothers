"""Upload com pipeline_custom_id grava snapshot em steps_json."""

from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def _patch_credenciais_e_pipeline() -> tuple:
    return (
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
    )


def _duplicar_pipeline_tutorial(client: TestClient) -> str:
    r = client.post(
        "/api/pipelines/custom/duplicar",
        json={"fonte_id": "pipeline_inicial_tutorial"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    custom = [p for p in d["pipelines"] if p.get("origem") == "usuario" and p["copiado_de"] == "pipeline_inicial_tutorial"]
    assert custom
    return custom[-1]["id"]


def test_upload_com_pipeline_custom_id_grava_snapshot_agentes_transcribrothers() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 128
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    pipeline_id: str | None = None
    with TestClient(app) as client, p1, p2, p3:
        pipeline_id = _duplicar_pipeline_tutorial(client)
        r = client.post(
            "/api/jobs/upload",
            data={"pipeline_custom_id": pipeline_id},
            files={"video": ("curto.webm", conteudo, "video/webm")},
        )
        assert r.status_code == 200, r.text
        steps = r.json()["steps_json"]
        assert steps["pipeline_custom_id"] == pipeline_id
        assert steps["pipeline_custom_copiado_de"] == "pipeline_inicial_tutorial"
        assert steps["destino_apos_transcricao"] == "gerar_tutorial"
        agentes = steps.get("pipeline_custom_agentes")
        assert isinstance(agentes, dict)
        assert "gerador_tutorial_markdown" in agentes
        assert "prompts" in agentes["gerador_tutorial_markdown"]
        assert steps.get("pipeline_custom_titulo")
        passos = steps.get("pipeline_custom_passos")
        assert isinstance(passos, list)
        assert len(passos) >= 5
        assert all(isinstance(p.get("handler_chave"), str) and p["handler_chave"] for p in passos)

        if pipeline_id:
            client.delete(f"/api/pipelines/custom/{pipeline_id}")


def test_upload_pipeline_custom_id_invalido_retorna_400_transcribrothers() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    with TestClient(app) as client, p1, p2, p3:
        r = client.post(
            "/api/jobs/upload",
            data={"pipeline_custom_id": "00000000-0000-0000-0000-000000000099"},
            files={"video": ("v.webm", conteudo, "video/webm")},
        )
    assert r.status_code == 400


def test_upload_pipeline_custom_fluxo2_retorna_400_transcribrothers() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    pipeline_id: str | None = None
    with TestClient(app) as client, p1, p2, p3:
        dup = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": "regeneracao_markdown"},
        )
        assert dup.status_code == 200
        custom = [
            p for p in dup.json()["pipelines"]
            if p.get("origem") == "usuario" and p["copiado_de"] == "regeneracao_markdown"
        ]
        pipeline_id = custom[-1]["id"]
        r = client.post(
            "/api/jobs/upload",
            data={"pipeline_custom_id": pipeline_id},
            files={"video": ("v.webm", conteudo, "video/webm")},
        )
        assert r.status_code == 400
        client.delete(f"/api/pipelines/custom/{pipeline_id}")
