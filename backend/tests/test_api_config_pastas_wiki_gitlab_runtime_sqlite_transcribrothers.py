"""Pastas wiki GitLab: runtime SQLite + API config."""

from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    normalizar_prefixo_pasta_wiki_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_pastas_wiki_gitlab_sqlite_transcribrothers import (
    pasta_wiki_esta_na_lista_permitida_transcribrothers,
)


def test_normalizar_e_lista_permitida_pastas_wiki_transcribrothers() -> None:
    assert normalizar_prefixo_pasta_wiki_gitlab_transcribrothers("Workshop") == "workshop"
    assert pasta_wiki_esta_na_lista_permitida_transcribrothers("workshop", ["workshop", "treinamentos"])
    assert not pasta_wiki_esta_na_lista_permitida_transcribrothers("outra", ["workshop"])


def test_config_publica_inclui_pastas_wiki_default_env_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.get("/api/config/transcribrothers")
        assert r.status_code == 200, r.text
        d = r.json()
        assert isinstance(d.get("gitlab_wiki_pastas_disponiveis"), list)
        assert len(d["gitlab_wiki_pastas_disponiveis"]) >= 1
        assert d["gitlab_wiki_slug_prefixo_pasta"] in d["gitlab_wiki_pastas_disponiveis"]


def test_patch_e_delete_pastas_wiki_runtime_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.patch(
            "/api/config/transcribrothers/gitlab-wiki-pastas-runtime",
            json={"pastas": ["workshop", "treinamentos"], "pasta_padrao": "treinamentos"},
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["gitlab_wiki_pastas_preferencia_sqlite_definida"] is True
        assert d["gitlab_wiki_pastas_disponiveis"] == ["workshop", "treinamentos"]
        assert d["gitlab_wiki_slug_prefixo_pasta"] == "treinamentos"

        r_bad = client.patch(
            "/api/config/transcribrothers/gitlab-wiki-pastas-runtime",
            json={"pastas": ["workshop"], "pasta_padrao": "inexistente"},
        )
        assert r_bad.status_code == 400

        r_del = client.delete("/api/config/transcribrothers/gitlab-wiki-pastas-runtime")
        assert r_del.status_code == 200, r_del.text
        assert r_del.json()["gitlab_wiki_pastas_preferencia_sqlite_definida"] is False


def test_preview_wiki_rejeita_pasta_fora_da_lista_transcribrothers() -> None:
    from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
        ConfiguracaoAmbienteTranscribrothers,
    )

    cfg = ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo.defensoria",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=True,
        gitlab_wiki_project_path="portal-da-defensoria/documentacao",
        gitlab_wiki_slug_prefixo_pasta="workshop",
    )
    with patch("transcribrothers_backend.main.obter_configuracao", return_value=cfg):
        with TestClient(app) as client:
            client.patch(
                "/api/config/transcribrothers/gitlab-wiki-pastas-runtime",
                json={"pastas": ["workshop"], "pasta_padrao": "workshop"},
            )
            r = client.get(
                "/api/gitlab/wikis/preview-create-page-url",
                params={
                    "title": "Doc teste",
                    "job_id": "job-fake",
                    "prefixo_pasta_wiki": "pasta-proibida",
                },
            )
            assert r.status_code == 400, r.text
            client.delete("/api/config/transcribrothers/gitlab-wiki-pastas-runtime")
