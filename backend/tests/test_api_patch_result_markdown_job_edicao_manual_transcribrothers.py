"""Testes do PATCH manual de result_markdown do job."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_patch_result_markdown_job_inexistente_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.patch(
            "/api/jobs/00000000-0000-4000-8000-000000000001/result-markdown",
            json={"result_markdown": "# oi"},
        )
        assert r.status_code == 404
