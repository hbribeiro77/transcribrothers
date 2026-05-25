"""Índice da pasta wiki: bullet com link para subpágina após exportação."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers,
    _indice_pasta_ja_contem_link_subpagina_wiki_transcribrothers,
    _montar_linha_markdown_link_lista_indice_pasta_wiki_transcribrothers,
    criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers,
    montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers,
    montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers,
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


def test_montar_linha_markdown_link_lista() -> None:
    linha = _montar_linha_markdown_link_lista_indice_pasta_wiki_transcribrothers(
        "Edital de vacância",
        "https://gitlab.exemplo/def/-/wikis/workshop/edital",
    )
    assert linha == "* [Edital de vacância](https://gitlab.exemplo/def/-/wikis/workshop/edital)"


def test_adicionar_link_no_indice_vazio() -> None:
    novo, incluiu = _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers(
        "",
        titulo_link="Novo doc",
        url_subpagina="https://x/wikis/workshop/novo-doc",
        slug_filho="novo-doc",
    )
    assert incluiu is True
    assert novo.strip().startswith("* [Novo doc]")


def test_adicionar_link_preserva_conteudo_existente() -> None:
    base = "* [Antigo](https://x/antigo)\n"
    novo, incluiu = _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers(
        base,
        titulo_link="Novo",
        url_subpagina="https://x/wikis/workshop/novo",
        slug_filho="novo",
    )
    assert incluiu is True
    assert "[Antigo]" in novo
    assert "[Novo](https://x/wikis/workshop/novo)" in novo


def test_nao_duplica_link_pela_url() -> None:
    url = "https://gitlab.exemplo/def/-/wikis/workshop/meu-doc"
    base = f"* [Meu doc]({url})\n"
    assert _indice_pasta_ja_contem_link_subpagina_wiki_transcribrothers(
        base, url_subpagina=url, slug_filho="meu-doc"
    )
    _, incluiu = _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers(
        base,
        titulo_link="Meu doc",
        url_subpagina=url,
        slug_filho="meu-doc",
    )
    assert incluiu is False


def _resposta_json(status: int, payload: dict) -> httpx.Response:
    req = httpx.Request("GET", "https://gitlab.exemplo.defensoria/api/v4/projects/x/wikis/y")
    return httpx.Response(status, json=payload, request=req)


@pytest.mark.asyncio
async def test_apos_criar_subpagina_atualiza_indice_com_put() -> None:
    cfg = _cfg()
    slug = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, "Novo tutorial")
    slug_enc = slug.replace("/", "%2F")
    web = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
        cfg, "novo-tutorial", prefixo_pasta="workshop"
    )

    async def _get(url: str, **_k):
        if slug_enc in url:
            return _resposta_json(404, {"message": "404"})
        return _resposta_json(
            200,
            {"slug": "workshop", "title": "workshop", "content": "# Workshop\n"},
        )

    puts: list[str] = []

    async def _put(url: str, **_k):
        puts.append(url)
        return _resposta_json(200, {"slug": "workshop" if slug_enc not in url else slug})

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.put = AsyncMock(side_effect=_put)
    mock_client.post = AsyncMock(return_value=_resposta_json(201, {"slug": slug}))

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        body = await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
            cfg,
            titulo="Novo tutorial",
            conteudo_markdown="# Novo tutorial\n",
            slug_completo=slug,
        )

    assert body["link_adicionado_no_indice_pasta"] is True
    assert len(puts) == 1
    put_data = mock_client.put.await_args.kwargs["data"]
    assert web in put_data["content"]
    assert "* [Novo tutorial]" in put_data["content"]
