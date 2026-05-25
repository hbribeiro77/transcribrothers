"""Upload direto de vídeo com destino notas_proposta_funcionalidade."""

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


def test_upload_notas_proposta_funcionalidade_video_local_retorna_200() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 128
    p1, p2, p3 = _patch_credenciais_e_pipeline()
    with TestClient(app) as client, p1, p2, p3:
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
            files={"video": ("reuniao.webm", conteudo, "video/webm")},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["steps_json"]["destino_apos_transcricao"] == "notas_proposta_funcionalidade"


def test_upload_destino_notas_proposta_invalido_rejeitado() -> None:
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 64
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "notas_proposta"},
            files={"video": ("v.webm", conteudo, "video/webm")},
        )
    assert r.status_code == 400
