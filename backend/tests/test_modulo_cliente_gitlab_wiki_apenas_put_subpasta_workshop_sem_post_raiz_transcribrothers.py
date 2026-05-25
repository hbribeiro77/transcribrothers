"""Wiki GitLab: POST/PUT em workshop/{slug_filho}; índice recebe bullet com link após sucesso."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers,
    montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def _cfg() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo.defensoria",
        gitlab_token="glpat-teste",
        gitlab_tls_insecure_dev=True,
        gitlab_wiki_project_path="portal-da-defensoria/documentacao",
        gitlab_wiki_slug_prefixo_pasta="workshop",
    )


def _resposta_json(status: int, payload: dict) -> httpx.Response:
    req = httpx.Request("GET", "https://gitlab.exemplo.defensoria/api/v4/projects/x/wikis/y")
    return httpx.Response(status, json=payload, request=req)


def _get_indice_workshop() -> httpx.Response:
    return _resposta_json(
        200,
        {"slug": "workshop", "title": "workshop", "content": "# Workshop\n\nLista de tutoriais.\n"},
    )


def _slug_api(cfg: ConfiguracaoAmbienteTranscribrothers) -> str:
    return montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, "Meu doc")


@pytest.mark.asyncio
async def test_atualiza_subpagina_workshop_existente_sem_post() -> None:
    cfg = _cfg()
    slug = _slug_api(cfg)
    slug_enc = slug.replace("/", "%2F")

    async def _get(url: str, **_k):
        if slug_enc in url:
            return _resposta_json(200, {"slug": slug})
        return _get_indice_workshop()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.put = AsyncMock(
        return_value=_resposta_json(200, {"slug": slug, "title": "Título"}),
    )
    mock_client.post = AsyncMock()

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        body = await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
            cfg,
            titulo="Meu doc",
            conteudo_markdown="# Olá",
            slug_completo=slug,
        )

    assert body["slug"] == slug
    assert body["slug_filho"] == "meu-doc"
    assert body["atualizada"] is True
    assert body.get("link_adicionado_no_indice_pasta") is True
    mock_client.post.assert_not_called()
    assert mock_client.put.await_count == 2


@pytest.mark.asyncio
async def test_subpagina_inexistente_cria_com_post_slug_workshop() -> None:
    cfg = _cfg()
    slug = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, "Novo")
    slug_enc = slug.replace("/", "%2F")

    async def _get(url: str, **_k):
        if slug_enc in url:
            return _resposta_json(404, {"message": "404 Wiki Page Not Found"})
        return _get_indice_workshop()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.put = AsyncMock(return_value=_resposta_json(200, {"slug": "workshop"}))
    mock_client.post = AsyncMock(return_value=_resposta_json(201, {"slug": slug, "title": "Novo"}))

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        body = await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
            cfg,
            titulo="Novo",
            conteudo_markdown="# X",
            slug_completo=slug,
        )

    assert body["slug_filho"] == "novo"
    assert body["atualizada"] is False
    assert body.get("link_adicionado_no_indice_pasta") is True
    assert mock_client.put.await_count == 1
    post_data = mock_client.post.await_args.kwargs["data"]
    assert post_data["title"] == slug
    assert "slug" not in post_data


def test_corpo_post_usa_title_com_caminho_workshop() -> None:
    from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
        _corpo_formulario_post_criar_subpagina_wiki_gitlab_transcribrothers,
    )

    corpo = _corpo_formulario_post_criar_subpagina_wiki_gitlab_transcribrothers(
        title_com_caminho_pasta="workshop/review-sprint-10-responsavel",
        conteudo="# Título humano\n\nCorpo",
    )
    assert corpo["title"] == "workshop/review-sprint-10-responsavel"
    assert "slug" not in corpo


@pytest.mark.asyncio
async def test_post_titulo_duplicado_tenta_put_na_subpagina_workshop() -> None:
    cfg = _cfg()
    slug = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(
        cfg,
        "Review Sprint 10: Responsável indisponível nas tarefas e Melhorias na Triagem",
    )
    slug_enc = slug.replace("/", "%2F")
    chamadas_get = 0

    async def _get(url: str, **_k):
        nonlocal chamadas_get
        chamadas_get += 1
        if slug_enc in url and chamadas_get >= 2:
            return _resposta_json(200, {"slug": slug})
        if slug_enc in url:
            return _resposta_json(404, {"message": "404"})
        return _get_indice_workshop()

    dup_body = {
        "message": {
            "base": [
                "Duplicate page: A page with that title already exists in the file Review-Sprint-10.md",
            ],
        },
    }
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.put = AsyncMock(return_value=_resposta_json(200, {"slug": slug}))
    mock_client.post = AsyncMock(return_value=_resposta_json(400, dup_body))

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        body = await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
            cfg,
            titulo="Review Sprint 10: Responsável indisponível nas tarefas e Melhorias na Triagem",
            conteudo_markdown="# X",
            slug_completo=slug,
        )

    assert body["atualizada"] is True
    assert body.get("link_adicionado_no_indice_pasta") is True
    assert mock_client.put.await_count == 2


@pytest.mark.asyncio
async def test_post_com_slug_na_raiz_falha_sem_tratar_como_sucesso() -> None:
    cfg = _cfg()
    slug = _slug_api(cfg)
    slug_enc = slug.replace("/", "%2F")

    async def _get(url: str, **_k):
        if slug_enc in url:
            return _resposta_json(404, {"message": "404"})
        return _get_indice_workshop()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.post = AsyncMock(
        return_value=_resposta_json(201, {"slug": "Review-Sprint-10-errado", "title": "Novo"}),
    )

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        with pytest.raises(RuntimeError, match="fora de"):
            await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
                cfg,
                titulo="Novo",
                conteudo_markdown="# X",
                slug_completo=slug,
            )
