"""Testes do cliente para comentar em issue existente do GitLab."""

import pytest

from transcribrothers_backend.modulo_cliente_gitlab_comentar_issue_existente_transcribrothers import (
    DestinoIssueGitlabTranscribrothers,
    comentar_issue_gitlab_existente_transcribrothers,
    extrair_destino_issue_gitlab_a_partir_url_transcribrothers,
    montar_url_api_comentar_issue_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def _cfg_gitlab() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.defpub.local",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=False,
    )


def test_extrair_destino_issue_gitlab_aceita_issue_do_gitlab_configurado() -> None:
    destino = extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
        _cfg_gitlab(),
        "https://gitlab.defpub.local/portal-da-defensoria/portal-defensoria-gateway/-/issues/3639",
    )

    assert destino.project_path == "portal-da-defensoria/portal-defensoria-gateway"
    assert destino.issue_iid == 3639
    assert (
        destino.issue_url
        == "https://gitlab.defpub.local/portal-da-defensoria/portal-defensoria-gateway/-/issues/3639"
    )


def test_extrair_destino_issue_gitlab_aceita_subgrupos_no_project_path() -> None:
    destino = extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
        _cfg_gitlab(),
        "https://gitlab.defpub.local/grupo/subgrupo/projeto-com-hifen/-/issues/12?tab=discussions#note_99",
    )

    assert destino.project_path == "grupo/subgrupo/projeto-com-hifen"
    assert destino.issue_iid == 12
    assert destino.issue_url == "https://gitlab.defpub.local/grupo/subgrupo/projeto-com-hifen/-/issues/12"


def test_extrair_destino_issue_gitlab_rejeita_host_diferente() -> None:
    with pytest.raises(ValueError, match="GitLab configurado"):
        extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
            _cfg_gitlab(),
            "https://gitlab.externo.local/grupo/projeto/-/issues/3639",
        )


def test_extrair_destino_issue_gitlab_rejeita_url_sem_padrao_de_issue() -> None:
    with pytest.raises(ValueError, match="URL de issue"):
        extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
            _cfg_gitlab(),
            "https://gitlab.defpub.local/grupo/projeto/-/merge_requests/3639",
        )


def test_extrair_destino_issue_gitlab_rejeita_iid_nao_numerico() -> None:
    with pytest.raises(ValueError, match="número"):
        extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
            _cfg_gitlab(),
            "https://gitlab.defpub.local/grupo/projeto/-/issues/abc",
        )


def test_montar_url_api_comentar_issue_gitlab_encode_project_path() -> None:
    url = montar_url_api_comentar_issue_gitlab_transcribrothers(
        _cfg_gitlab(),
        DestinoIssueGitlabTranscribrothers(
            project_path="grupo/subgrupo/projeto",
            issue_iid=77,
            issue_url="https://gitlab.defpub.local/grupo/subgrupo/projeto/-/issues/77",
        ),
    )

    assert (
        url
        == "https://gitlab.defpub.local/api/v4/projects/grupo%2Fsubgrupo%2Fprojeto/issues/77/notes"
    )


@pytest.mark.asyncio
async def test_comentar_issue_gitlab_existente_posta_note_com_body(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[dict[str, object]] = []

    class _RespostaFake:
        status_code = 201
        text = ""

        def json(self) -> dict[str, object]:
            return {
                "id": 456,
                "url": "https://gitlab.defpub.local/grupo/projeto/-/issues/77#note_456",
                "body": "# Documento",
            }

    class _ClienteFake:
        def __init__(self, *, timeout: float, verify: bool) -> None:
            chamadas.append({"timeout": timeout, "verify": verify})

        async def __aenter__(self) -> "_ClienteFake":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def post(self, url: str, *, headers: dict[str, str], json: dict[str, str]) -> _RespostaFake:
            chamadas.append({"url": url, "headers": headers, "json": json})
            return _RespostaFake()

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_cliente_gitlab_comentar_issue_existente_transcribrothers.httpx.AsyncClient",
        _ClienteFake,
    )

    resp = await comentar_issue_gitlab_existente_transcribrothers(
        _cfg_gitlab(),
        issue_url="https://gitlab.defpub.local/grupo/projeto/-/issues/77",
        corpo_markdown="# Documento",
        timeout_segundos=12.0,
    )

    assert chamadas[0] == {"timeout": 12.0, "verify": True}
    assert chamadas[1]["url"] == "https://gitlab.defpub.local/api/v4/projects/grupo%2Fprojeto/issues/77/notes"
    assert chamadas[1]["headers"] == {
        "PRIVATE-TOKEN": "glpat-teste",
        "Content-Type": "application/json",
    }
    assert chamadas[1]["json"] == {"body": "# Documento"}
    assert resp["id"] == 456
    assert resp["project_path"] == "grupo/projeto"
    assert resp["issue_iid"] == 77
    assert resp["issue_url"] == "https://gitlab.defpub.local/grupo/projeto/-/issues/77"
