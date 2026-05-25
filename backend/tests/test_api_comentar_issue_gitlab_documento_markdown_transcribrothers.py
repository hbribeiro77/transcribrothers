"""Testes de POST /api/gitlab/issues/comment-in-existing-issue."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def _cfg_gitlab_mock() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.defpub.local",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=True,
    )


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


def test_comment_in_existing_issue_sem_gitlab_configurado_retorna_503() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(gitlab_base_url="", gitlab_token="")
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/issues/comment-in-existing-issue",
                json={
                    "issue_url": "https://gitlab.defpub.local/grupo/projeto/-/issues/1",
                    "description": "# Corpo\n\nTexto.",
                    "incluir_imagens_png_markdown": False,
                },
            )

    assert r.status_code == 503
    assert "GitLab" in (r.json().get("detail") or "")


def test_comment_in_existing_issue_rejeita_url_de_outro_gitlab() -> None:
    cfg = _cfg_gitlab_mock()
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            r = client.post(
                "/api/gitlab/issues/comment-in-existing-issue",
                json={
                    "issue_url": "https://gitlab.externo.local/grupo/projeto/-/issues/1",
                    "description": "# Corpo",
                    "incluir_imagens_png_markdown": False,
                },
            )

    assert r.status_code == 400
    assert "GitLab configurado" in (r.json().get("detail") or "")


def test_comment_in_existing_issue_sucesso_retorna_note_url() -> None:
    cfg = _cfg_gitlab_mock()

    async def _fake_comentar(*_a, **_k):
        return {"id": 321}

    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with patch(
            "transcribrothers_backend.main.comentar_issue_gitlab_existente_transcribrothers",
            new_callable=AsyncMock,
            side_effect=_fake_comentar,
        ) as comentar_mock:
            with TestClient(app) as client:
                r = client.post(
                    "/api/gitlab/issues/comment-in-existing-issue",
                    json={
                        "issue_url": "https://gitlab.defpub.local/grupo/projeto/-/issues/44",
                        "description": "# Documento\n\nConteúdo.",
                        "incluir_imagens_png_markdown": False,
                    },
                )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["note_id"] == 321
    assert body["note_url"] == "https://gitlab.defpub.local/grupo/projeto/-/issues/44#note_321"
    assert body["issue_url"] == "https://gitlab.defpub.local/grupo/projeto/-/issues/44"
    assert body["project"] == "grupo/projeto"
    assert body["issue_iid"] == 44
    assert comentar_mock.await_args.kwargs["corpo_markdown"] == "# Documento\n\nConteúdo."


def test_comment_in_existing_issue_rejeita_markdown_acima_limite_antes_de_postar() -> None:
    cfg = _cfg_gitlab_mock()
    markdown_grande = "a" * 1_000_001
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with patch(
            "transcribrothers_backend.main.comentar_issue_gitlab_existente_transcribrothers",
            new_callable=AsyncMock,
        ) as comentar_mock:
            with TestClient(app) as client:
                r = client.post(
                    "/api/gitlab/issues/comment-in-existing-issue",
                    json={
                        "issue_url": "https://gitlab.defpub.local/grupo/projeto/-/issues/44",
                        "description": markdown_grande,
                        "incluir_imagens_png_markdown": False,
                    },
                )

    assert r.status_code == 400
    assert "1.000.000" in (r.json().get("detail") or "")
    comentar_mock.assert_not_awaited()


def test_comment_in_existing_issue_com_job_id_prepara_imagens_no_projeto_extraido() -> None:
    cfg = _cfg_gitlab_mock()
    job = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    chamadas_preparar: list[dict[str, object]] = []

    async def _fake_preparar(*_args, **kwargs):
        chamadas_preparar.append(dict(kwargs))
        return "# Documento\n\n![tela](/uploads/abc/foto.png)", 1, 0

    async def _fake_comentar(*_a, **_k):
        return {
            "id": 654,
            "url": "https://gitlab.defpub.local/grupo/projeto/-/issues/55#note_654",
        }

    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with patch(
            "transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers.preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers",
            new_callable=AsyncMock,
            side_effect=_fake_preparar,
        ):
            with patch(
                "transcribrothers_backend.main.comentar_issue_gitlab_existente_transcribrothers",
                new_callable=AsyncMock,
                side_effect=_fake_comentar,
            ) as comentar_mock:
                with TestClient(app) as client:
                    client.app.state.session_factory = _session_factory_com_job_markdown(
                        "# Documento\n\n![tela](assets/foto.png)",
                    )
                    r = client.post(
                        "/api/gitlab/issues/comment-in-existing-issue",
                        json={
                            "issue_url": "https://gitlab.defpub.local/grupo/projeto/-/issues/55",
                            "job_id": job,
                            "incluir_imagens_png_markdown": True,
                        },
                    )

    assert r.status_code == 200
    body = r.json()
    assert body["imagens_png_enviadas_gitlab"] == 1
    assert body["imagens_png_ignoradas_gitlab"] == 0
    assert chamadas_preparar[0]["project_path_gitlab"] == "grupo/projeto"
    assert comentar_mock.await_args.kwargs["corpo_markdown"] == "# Documento\n\n![tela](/uploads/abc/foto.png)"
