"""Testes de POST /api/gitlab/wikis/create-page-in-project e preview URL."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers,
    montar_slug_filho_pagina_wiki_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
    obter_configuracao,
)


def _cfg_gitlab_wiki_mock() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo.defensoria",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=True,
        gitlab_wiki_project_path="portal-da-defensoria/documentacao",
        gitlab_wiki_slug_prefixo_pasta="workshop",
    )


def _slug_esperado(cfg: ConfiguracaoAmbienteTranscribrothers) -> tuple[str, str]:
    titulo = "Tutorial de teste"
    return (
        montar_slug_filho_pagina_wiki_gitlab_transcribrothers(titulo),
        montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, titulo),
    )


def test_create_wiki_page_sem_gitlab_configurado_retorna_503() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(gitlab_base_url="", gitlab_token="")
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/wikis/create-page-in-project",
                json={
                    "title": "Título",
                    "content": "# Corpo\n\nTexto.",
                    "incluir_imagens_png_markdown": False,
                },
            )
    assert r.status_code == 503
    assert "wiki" in (r.json().get("detail") or "").lower()


def _session_factory_com_job_markdown(markdown: str):
    row = MagicMock()
    row.result_markdown = markdown
    row.steps_json = {}

    @asynccontextmanager
    async def _sf():
        session = AsyncMock()
        session.get = AsyncMock(return_value=row)
        yield session

    return _sf


def test_create_wiki_page_sucesso_retorna_web_url_subpagina() -> None:
    cfg = _cfg_gitlab_wiki_mock()
    slug_filho, slug_api = _slug_esperado(cfg)
    job = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    async def _fake_criar(*_a, **_k):
        return {"slug": slug_api, "slug_filho": slug_filho}

    with patch(
        "transcribrothers_backend.main.obter_configuracao",
        return_value=cfg,
    ):
        with patch(
            "transcribrothers_backend.main.criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers",
            new_callable=AsyncMock,
            side_effect=_fake_criar,
        ):
            with TestClient(app) as client:
                client.app.state.session_factory = _session_factory_com_job_markdown(
                    "# Tutorial\n\nConteúdo **markdown**.",
                )
                r = client.post(
                    "/api/gitlab/wikis/create-page-in-project",
                    json={
                        "title": "Tutorial de teste",
                        "job_id": job,
                        "incluir_imagens_png_markdown": False,
                    },
                )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["slug"] == slug_filho
    assert body["web_url"].endswith(f"/-/wikis/workshop/{slug_filho}")
    assert body["project"] == cfg.gitlab_wiki_project_path


def test_create_wiki_page_sem_job_id_retorna_400() -> None:
    cfg = _cfg_gitlab_wiki_mock()
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/wikis/create-page-in-project",
                json={
                    "title": "Tutorial",
                    "content": "# Corpo",
                    "incluir_imagens_png_markdown": False,
                },
            )
    assert r.status_code == 400
    assert "job_id" in (r.json().get("detail") or "").lower()


def test_create_wiki_page_titulo_vazio_retorna_422() -> None:
    cfg = _cfg_gitlab_wiki_mock()
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/wikis/create-page-in-project",
                json={"title": "   ", "content": "Corpo", "job_id": "x"},
            )
        assert r.status_code == 422

        with TestClient(app) as client:
            client.app.state.session_factory = _session_factory_com_job_markdown("   ")
            r2 = client.post(
                "/api/gitlab/wikis/create-page-in-project",
                json={"title": "Ok", "job_id": "x"},
            )
        assert r2.status_code == 400
        assert "vazio" in (r2.json().get("detail") or "").lower()


def test_preview_create_page_url_retorna_subpagina_workshop() -> None:
    cfg = _cfg_gitlab_wiki_mock()
    job = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    slug_filho, slug_api = _slug_esperado(cfg)

    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with patch(
            "transcribrothers_backend.main.pagina_wiki_gitlab_existe_no_projeto_transcribrothers",
            new_callable=AsyncMock,
            return_value=True,
        ):
            with TestClient(app) as client:
                r = client.get(
                    "/api/gitlab/wikis/preview-create-page-url",
                    params={"title": "Tutorial de teste", "job_id": job},
                )
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == slug_filho
    assert body["prefixo_pasta_wiki"] == "workshop"
    assert body["web_url"].endswith(f"/-/wikis/workshop/{slug_filho}")
    assert body["pagina_destino_ja_existe_no_gitlab"] is True
    assert body["project"] == cfg.gitlab_wiki_project_path


def test_preview_create_page_url_com_pasta_customizada() -> None:
    cfg = _cfg_gitlab_wiki_mock()
    job = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with patch(
            "transcribrothers_backend.main.pagina_wiki_gitlab_existe_no_projeto_transcribrothers",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with TestClient(app) as client:
                r = client.get(
                    "/api/gitlab/wikis/preview-create-page-url",
                    params={
                        "title": "Tutorial de teste",
                        "job_id": job,
                        "prefixo_pasta_wiki": "reviews",
                    },
                )
    assert r.status_code == 200
    body = r.json()
    assert body["prefixo_pasta_wiki"] == "reviews"
    assert "/-/wikis/reviews/" in body["web_url"]
    assert body["web_url_indice_workshop"].endswith("/-/wikis/reviews")


def test_config_publica_indica_gitlab_wiki_habilitado_quando_configurado() -> None:
    cfg = obter_configuracao()
    with TestClient(app) as client:
        r = client.get("/api/config/transcribrothers")
    assert r.status_code == 200
    data = r.json()
    assert "gitlab_criar_wiki_habilitado" in data
    esperado = bool(
        (cfg.gitlab_base_url or "").strip()
        and (cfg.gitlab_token or "").strip()
        and (cfg.gitlab_wiki_project_path or "").strip()
    )
    assert data["gitlab_criar_wiki_habilitado"] is esperado
