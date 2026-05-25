"""Testes de POST /api/gitlab/issues/create-in-project."""

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
    obter_configuracao,
)


def _cfg_gitlab_mock() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo.defensoria",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=True,
    )


def test_create_in_project_sem_gitlab_configurado_retorna_503() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(gitlab_base_url="", gitlab_token="")
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/issues/create-in-project",
                json={
                    "title": "Título",
                    "description": "# Corpo\n\nTexto.",
                    "incluir_imagens_png_markdown": False,
                },
            )
    assert r.status_code == 503
    assert "GitLab" in (r.json().get("detail") or "")


def test_create_in_project_sucesso_retorna_web_url() -> None:
    cfg = _cfg_gitlab_mock()

    async def _fake_criar(*_a, **_k):
        return {"iid": 42, "web_url": "https://gitlab.exemplo/defensoria/-/issues/42"}

    with patch(
        "transcribrothers_backend.main.obter_configuracao",
        return_value=cfg,
    ):
        with patch(
            "transcribrothers_backend.main.criar_issue_gitlab_portal_defensoria_gateway_transcribrothers",
            new_callable=AsyncMock,
            side_effect=_fake_criar,
        ):
            with TestClient(app) as client:
                r = client.post(
                    "/api/gitlab/issues/create-in-project",
                    json={
                        "title": "Tutorial de teste",
                        "description": "# Tutorial\n\nConteúdo **markdown**.",
                        "incluir_imagens_png_markdown": False,
                    },
                )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["iid"] == 42
    assert body["web_url"] == "https://gitlab.exemplo/defensoria/-/issues/42"
    assert body["issue_url"] == body["web_url"]
    assert body["project"] == cfg.gitlab_create_issue_project_path
    assert body["labels"] == "squad::bravo"


def test_create_in_project_titulo_vazio_retorna_422() -> None:
    cfg = _cfg_gitlab_mock()
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/issues/create-in-project",
                json={"title": "   ", "description": "Corpo"},
            )
        assert r.status_code == 422

        with TestClient(app) as client:
            r2 = client.post(
                "/api/gitlab/issues/create-in-project",
                json={"title": "Ok", "description": "   "},
            )
        assert r2.status_code == 422


def test_config_publica_indica_gitlab_habilitado_quando_token_e_url() -> None:
    cfg = obter_configuracao()
    with TestClient(app) as client:
        r = client.get("/api/config/transcribrothers")
    assert r.status_code == 200
    data = r.json()
    assert "gitlab_criar_issue_habilitado" in data
    esperado = bool((cfg.gitlab_base_url or "").strip() and (cfg.gitlab_token or "").strip())
    assert data["gitlab_criar_issue_habilitado"] is esperado
