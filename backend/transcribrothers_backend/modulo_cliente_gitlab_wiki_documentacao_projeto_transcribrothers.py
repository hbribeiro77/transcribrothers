"""Cliente HTTP para criar/atualizar páginas wiki no GitLab (projeto documentação, pasta workshop/)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any
from urllib.parse import quote

import httpx

from transcribrothers_backend.modulo_cliente_gitlab_criar_issue_portal_defensoria_gateway_transcribrothers import (
    gitlab_criar_issue_configurado_no_ambiente_transcribrothers,
    normalizar_titulo_issue_gitlab_transcribrothers,
    resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    return bool(
        gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg)
        and (cfg.gitlab_wiki_project_path or "").strip()
    )


def _resolver_project_path_wiki_gitlab(cfg: ConfiguracaoAmbienteTranscribrothers) -> str:
    project_path = (cfg.gitlab_wiki_project_path or "").strip()
    if not project_path:
        raise ValueError("GITLAB_WIKI_PROJECT_PATH vazio.")
    return project_path


def _resolver_prefixo_pasta_slug_wiki_gitlab(cfg: ConfiguracaoAmbienteTranscribrothers) -> str:
    prefixo = (cfg.gitlab_wiki_slug_prefixo_pasta or "workshop").strip().strip("/")
    if not prefixo:
        raise ValueError("GITLAB_WIKI_SLUG_PREFIXO_PASTA vazio.")
    return prefixo


def normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(nome_pasta: str) -> str:
    """
    Normaliza o nome do diretório wiki (ex.: workshop, treinamentos).

    Um único segmento: sem barras; ASCII minúsculo e hífens.
    """
    bruto = (nome_pasta or "").strip().strip("/")
    if not bruto:
        raise ValueError("Informe o nome da pasta wiki (ex.: workshop).")
    if "/" in bruto or "\\" in bruto or ".." in bruto:
        raise ValueError(
            "Nome da pasta wiki inválido: use um único diretório (ex.: workshop), sem barras."
        )
    normalizado = slugificar_titulo_pagina_wiki_gitlab_transcribrothers(bruto, max_caracteres=64)
    if not normalizado:
        raise ValueError("Nome da pasta wiki inválido após normalização.")
    return normalizado


def resolver_prefixo_pasta_wiki_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    prefixo_informado: str | None = None,
) -> str:
    """Pasta informada pelo usuário ou default de GITLAB_WIKI_SLUG_PREFIXO_PASTA."""
    if prefixo_informado is not None and str(prefixo_informado).strip():
        return normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(prefixo_informado)
    return _resolver_prefixo_pasta_slug_wiki_gitlab(cfg)


def montar_url_api_wikis_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_enc = quote(_resolver_project_path_wiki_gitlab(cfg), safe="")
    return f"{base}/api/v4/projects/{project_enc}/wikis"


def montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    slug_completo: str,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    project_enc = quote(_resolver_project_path_wiki_gitlab(cfg), safe="")
    slug_enc = quote(slug_completo.strip().strip("/"), safe="")
    return f"{base}/api/v4/projects/{project_enc}/wikis/{slug_enc}"


def montar_url_api_wiki_anexos_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_enc = quote(_resolver_project_path_wiki_gitlab(cfg), safe="")
    return f"{base}/api/v4/projects/{project_enc}/wikis/attachments"


def montar_slug_filho_pagina_wiki_gitlab_transcribrothers(titulo_pagina: str) -> str:
    """Segmento da URL após /-/wikis/workshop/ (só o nome da subpágina, sem prefixo workshop/)."""
    return slugificar_titulo_pagina_wiki_gitlab_transcribrothers(titulo_pagina)


def montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    titulo_pagina: str,
    *,
    prefixo_pasta: str | None = None,
) -> str:
    """Slug na API GitLab: {pasta}/{slug_filho}."""
    prefixo = prefixo_pasta or _resolver_prefixo_pasta_slug_wiki_gitlab(cfg)
    filho = montar_slug_filho_pagina_wiki_gitlab_transcribrothers(titulo_pagina)
    return f"{prefixo}/{filho}"


def montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    slug_filho: str,
    *,
    prefixo_pasta: str | None = None,
) -> str:
    """
    URL humana: {GITLAB_BASE_URL}/{GITLAB_WIKI_PROJECT_PATH}/-/wikis/{pasta}/{slug_filho}.
    """
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    project_path = _resolver_project_path_wiki_gitlab(cfg)
    prefixo = prefixo_pasta or _resolver_prefixo_pasta_slug_wiki_gitlab(cfg)
    bruto = slug_filho.strip().strip("/")
    if "/" in bruto:
        prefixo_resolvido, _, filho = bruto.partition("/")
        if prefixo_resolvido.lower() == prefixo.lower() and filho:
            bruto = filho
    return f"{base}/{project_path}/-/wikis/{prefixo}/{bruto}"


def montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    prefixo_pasta: str | None = None,
) -> str:
    """URL da página índice: …/-/wikis/{pasta} (sem subpágina)."""
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    project_path = _resolver_project_path_wiki_gitlab(cfg)
    prefixo = prefixo_pasta or _resolver_prefixo_pasta_slug_wiki_gitlab(cfg)
    return f"{base}/{project_path}/-/wikis/{prefixo}"


def slugificar_titulo_pagina_wiki_gitlab_transcribrothers(
    titulo: str,
    *,
    max_caracteres: int = 80,
) -> str:
    """Gera segmento de slug estável (ASCII, hífens) a partir do título da página."""
    t = (titulo or "").strip()
    if not t:
        return "pagina"
    normalizado = unicodedata.normalize("NFKD", t)
    ascii_basico = normalizado.encode("ascii", "ignore").decode("ascii")
    minusculo = ascii_basico.lower()
    com_hifens = re.sub(r"[^a-z0-9]+", "-", minusculo)
    limpo = re.sub(r"-+", "-", com_hifens).strip("-")
    if not limpo:
        limpo = "pagina"
    if len(limpo) > max_caracteres:
        limpo = limpo[:max_caracteres].rstrip("-") or "pagina"
    return limpo


def montar_slug_completo_pagina_wiki_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    titulo_pagina: str,
    *,
    sufixo_opcional_slug: str | None = None,
) -> str:
    """Compat: retorna workshop/{slug_filho}. Ignora sufixo_opcional_slug (GitLab não usa sufixo de job)."""
    _ = sufixo_opcional_slug
    return montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, titulo_pagina)


def slug_resposta_gitlab_wiki_corresponde_ao_slug_esperado_transcribrothers(
    slug_resposta: str,
    slug_esperado: str,
) -> bool:
    return slug_resposta.strip().strip("/").lower() == slug_esperado.strip().strip("/").lower()


def slug_resposta_gitlab_wiki_esta_em_subpasta_prefixo_transcribrothers(
    slug_resposta: str,
    prefixo_pasta: str,
) -> bool:
    """True se o slug é subpágina `workshop/…` (não raiz da wiki nem só a página índice workshop)."""
    slug = slug_resposta.strip().strip("/").lower()
    prefixo = prefixo_pasta.strip().strip("/").lower()
    if not slug or not prefixo:
        return False
    if slug == prefixo:
        return False
    return slug.startswith(f"{prefixo}/")


async def pagina_wiki_gitlab_existe_no_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    slug_completo: str,
    *,
    timeout_segundos: float = 30.0,
) -> bool:
    """GET na API — True se a página já existe (sem alterar conteúdo)."""
    token = (cfg.gitlab_token or "").strip()
    if not token:
        return False
    url = montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(cfg, slug_completo)
    headers = {"PRIVATE-TOKEN": token}
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)
    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        resp = await client.get(url, headers=headers)
    return resp.status_code == 200


async def _verificar_pagina_indice_workshop_existe_sem_alterar_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    client: httpx.AsyncClient,
    headers: dict[str, str],
    prefixo_pasta: str,
) -> None:
    """Confirma que a página índice workshop existe; nunca escreve nela."""
    url_pai = montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(cfg, prefixo_pasta)
    resp = await client.get(url_pai, headers=headers)
    if resp.status_code == 200:
        return
    if resp.status_code == 404:
        web_pai = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(cfg)
        raise RuntimeError(
            f"A página índice '{prefixo_pasta}' não existe em {web_pai}. "
            "Crie-a no GitLab antes de exportar subpáginas."
        )
    detalhe = resp.text.strip()
    if len(detalhe) > 400:
        detalhe = f"{detalhe[:400]}…"
    raise RuntimeError(
        f"Não foi possível verificar a página índice '{prefixo_pasta}' (HTTP {resp.status_code}). "
        f"{detalhe or 'sem corpo'}"
    )


def _corpo_formulario_put_atualizar_subpagina_wiki_gitlab_transcribrothers(
    *,
    titulo_exibicao: str,
    conteudo: str,
) -> dict[str, str]:
    """PUT: título legível na wiki; slug vem da URL da requisição."""
    return {
        "title": titulo_exibicao,
        "content": conteudo,
        "format": "markdown",
    }


def _corpo_formulario_post_criar_subpagina_wiki_gitlab_transcribrothers(
    *,
    title_com_caminho_pasta: str,
    conteudo: str,
) -> dict[str, str]:
    """
    POST /wikis — GitLab ignora `slug` no create; o caminho workshop/… vai no `title`.

    Ex.: title=workshop/review-sprint-10-responsavel-… → slug workshop/review-sprint-10-….
    """
    return {
        "title": title_com_caminho_pasta,
        "content": conteudo,
        "format": "markdown",
    }


def _extrair_slug_de_resposta_json_wiki_gitlab_transcribrothers(body: dict[str, Any]) -> str:
    return str(body.get("slug") or "").strip()


def _validar_resposta_wiki_post_criacao_subpagina_workshop_transcribrothers(
    body: dict[str, Any],
    *,
    slug_api_esperado: str,
    slug_filho_esperado: str,
    prefixo_pasta: str,
) -> dict[str, Any]:
    slug_resp = _extrair_slug_de_resposta_json_wiki_gitlab_transcribrothers(body)
    if slug_resposta_gitlab_wiki_esta_em_subpasta_prefixo_transcribrothers(slug_resp, prefixo_pasta):
        body["slug"] = slug_api_esperado.strip().strip("/")
        body["slug_filho"] = slug_filho_esperado.strip().strip("/")
        return body
    raise RuntimeError(
        f"GitLab devolveu slug '{slug_resp or '?'}' fora de '{prefixo_pasta}/'. "
        "A exportação foi cancelada para não alterar outras páginas da wiki."
    )


def _validar_resposta_wiki_put_subpagina_workshop_transcribrothers(
    body: dict[str, Any],
    *,
    slug_api_esperado: str,
    slug_filho_esperado: str,
) -> dict[str, Any]:
    """
    Após PUT em /wikis/workshop%2F{slug}, confia no caminho da URL.

    O JSON de resposta pode trazer slug legível derivado do title (fora de workshop/).
    """
    body["slug"] = slug_api_esperado.strip().strip("/")
    body["slug_filho"] = slug_filho_esperado.strip().strip("/")
    return body


def _gitlab_wiki_resposta_indica_titulo_duplicado_transcribrothers(resp: httpx.Response) -> bool:
    if resp.status_code != 400:
        return False
    texto = resp.text.lower()
    return "duplicate" in texto or "já existe" in texto or "already exists" in texto


def _indice_pasta_ja_contem_link_subpagina_wiki_transcribrothers(
    conteudo: str,
    *,
    url_subpagina: str,
    slug_filho: str,
) -> bool:
    texto = conteudo or ""
    if url_subpagina.strip() and url_subpagina in texto:
        return True
    filho = slug_filho.strip().strip("/")
    if not filho:
        return False
    padroes = (
        f"]({url_subpagina})",
        f"/{filho})",
        f"/{filho}\n",
        f"({filho})",
    )
    return any(p in texto for p in padroes if p)


def _montar_linha_markdown_link_lista_indice_pasta_wiki_transcribrothers(
    titulo_link: str,
    url_subpagina: str,
) -> str:
    titulo = (titulo_link or "Página").strip()
    url = (url_subpagina or "").strip()
    return f"* [{titulo}]({url})"


def _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers(
    conteudo_atual: str,
    *,
    titulo_link: str,
    url_subpagina: str,
    slug_filho: str,
) -> tuple[str, bool]:
    """
    Acrescenta bullet na página índice da pasta. Retorna (conteúdo, True) se incluiu linha nova.
    """
    if _indice_pasta_ja_contem_link_subpagina_wiki_transcribrothers(
        conteudo_atual,
        url_subpagina=url_subpagina,
        slug_filho=slug_filho,
    ):
        return conteudo_atual, False
    linha = _montar_linha_markdown_link_lista_indice_pasta_wiki_transcribrothers(titulo_link, url_subpagina)
    base = (conteudo_atual or "").rstrip()
    if not base:
        return linha + "\n", True
    return f"{base}\n\n{linha}\n", True


async def _adicionar_link_subpagina_no_indice_pasta_wiki_gitlab_transcribrothers(
    client: httpx.AsyncClient,
    cfg: ConfiguracaoAmbienteTranscribrothers,
    headers: dict[str, str],
    *,
    prefixo_pasta: str,
    titulo_link: str,
    web_url_subpagina: str,
    slug_filho: str,
) -> bool:
    """
    Atualiza a página índice da pasta (ex.: workshop) com um item de lista apontando para a subpágina.

    Só acrescenta se o link ainda não estiver no Markdown do índice.
    """
    url_indice = montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(cfg, prefixo_pasta)
    resp_get = await client.get(url_indice, headers=headers)
    if resp_get.status_code != 200:
        web_indice = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(
            cfg, prefixo_pasta=prefixo_pasta
        )
        raise RuntimeError(
            f"Subpágina publicada, mas não foi possível ler o índice '{prefixo_pasta}' em {web_indice} "
            f"(HTTP {resp_get.status_code}) para incluir o link na lista."
        )
    body_get = resp_get.json()
    if not isinstance(body_get, dict):
        raise RuntimeError("Resposta inesperada ao ler página índice da wiki.")
    conteudo_atual = str(body_get.get("content") or "")
    titulo_indice = str(body_get.get("title") or prefixo_pasta).strip() or prefixo_pasta
    novo_conteudo, incluiu = _adicionar_link_subpagina_no_conteudo_indice_pasta_wiki_transcribrothers(
        conteudo_atual,
        titulo_link=titulo_link,
        url_subpagina=web_url_subpagina,
        slug_filho=slug_filho,
    )
    if not incluiu:
        return False
    corpo_put = _corpo_formulario_put_atualizar_subpagina_wiki_gitlab_transcribrothers(
        titulo_exibicao=titulo_indice,
        conteudo=novo_conteudo,
    )
    resp_put = await client.put(url_indice, headers=headers, data=corpo_put)
    if resp_put.status_code >= 400:
        detalhe = resp_put.text.strip()
        if len(detalhe) > 600:
            detalhe = f"{detalhe[:600]}…"
        raise RuntimeError(
            f"Subpágina publicada, mas o índice '{prefixo_pasta}' não pôde ser atualizado com o link "
            f"(HTTP {resp_put.status_code}). {detalhe or 'sem corpo'}"
        )
    return True


async def _finalizar_exportacao_subpagina_com_link_no_indice_pasta_wiki_gitlab_transcribrothers(
    client: httpx.AsyncClient,
    cfg: ConfiguracaoAmbienteTranscribrothers,
    headers: dict[str, str],
    validado: dict[str, Any],
    *,
    prefixo_pai: str,
    titulo_link: str,
    web_destino: str,
    slug_filho: str,
) -> dict[str, Any]:
    validado["link_adicionado_no_indice_pasta"] = await _adicionar_link_subpagina_no_indice_pasta_wiki_gitlab_transcribrothers(
        client,
        cfg,
        headers,
        prefixo_pasta=prefixo_pai,
        titulo_link=titulo_link,
        web_url_subpagina=web_destino,
        slug_filho=slug_filho,
    )
    return validado


async def _put_subpagina_wiki_gitlab_transcribrothers(
    client: httpx.AsyncClient,
    cfg: ConfiguracaoAmbienteTranscribrothers,
    headers: dict[str, str],
    *,
    url_subpagina: str,
    corpo_put: dict[str, str],
    slug_api: str,
    slug_filho: str,
    prefixo_pai: str,
    web_destino: str,
    titulo_link: str,
) -> dict[str, Any]:
    resp_put = await client.put(url_subpagina, headers=headers, data=corpo_put)
    if resp_put.status_code >= 400:
        detalhe = resp_put.text.strip()
        if len(detalhe) > 800:
            detalhe = f"{detalhe[:800]}…"
        raise RuntimeError(
            f"GitLab recusou atualizar a subpágina em {web_destino} (HTTP {resp_put.status_code}). "
            f"A página índice {prefixo_pai} não foi alterada. {detalhe or 'sem corpo'}"
        )
    body = resp_put.json()
    if not isinstance(body, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao atualizar página wiki.")
    validado = _validar_resposta_wiki_put_subpagina_workshop_transcribrothers(
        body,
        slug_api_esperado=slug_api,
        slug_filho_esperado=slug_filho,
    )
    validado["atualizada"] = True
    return await _finalizar_exportacao_subpagina_com_link_no_indice_pasta_wiki_gitlab_transcribrothers(
        client,
        cfg,
        headers,
        validado,
        prefixo_pai=prefixo_pai,
        titulo_link=titulo_link,
        web_destino=web_destino,
        slug_filho=slug_filho,
    )


async def upload_arquivo_png_anexo_wiki_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    conteudo_png: bytes,
    nome_arquivo: str,
    timeout_segundos: float = 120.0,
) -> str:
    """
    POST /wikis/attachments — devolve caminho Markdown relativo (ex.: uploads/…/arquivo.png).
    """
    nome = (nome_arquivo or "").strip().replace("\\", "/").split("/")[-1]
    if not nome or ".." in nome:
        raise ValueError("Nome de arquivo inválido para anexo wiki GitLab.")
    if not nome.lower().endswith(".png"):
        nome = f"{nome}.png" if nome else "imagem.png"

    token = (cfg.gitlab_token or "").strip()
    if not token:
        raise ValueError("GITLAB_TOKEN não configurado no servidor.")

    url = montar_url_api_wiki_anexos_gitlab_projeto_transcribrothers(cfg)
    headers = {"PRIVATE-TOKEN": token}
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)
    files = {"file": (nome, conteudo_png, "image/png")}

    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        resp = await client.post(url, headers=headers, files=files)

    if resp.status_code >= 400:
        detalhe = resp.text.strip()
        if len(detalhe) > 600:
            detalhe = f"{detalhe[:600]}…"
        raise RuntimeError(
            f"GitLab recusou o anexo wiki de '{nome}' (HTTP {resp.status_code}). {detalhe or 'sem corpo'}"
        )

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao enviar anexo wiki.")

    link = data.get("link")
    if isinstance(link, dict):
        markdown_link = str(link.get("markdown") or "").strip()
        m = re.search(r"\]\(([^)]+)\)", markdown_link)
        if m:
            return m.group(1).strip()
        url_link = str(link.get("url") or "").strip()
        if url_link:
            return url_link

    file_path = str(data.get("file_path") or "").strip()
    if file_path:
        return file_path
    raise RuntimeError(f"GitLab não devolveu link de anexo wiki válido para '{nome}'.")


async def criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    titulo: str,
    conteudo_markdown: str,
    slug_completo: str,
    timeout_segundos: float = 60.0,
) -> dict[str, Any]:
    """
    Cria ou atualiza somente a subpágina {pasta}/… indicada pelo slug.

    - A página índice da pasta é lida e, após sucesso na subpágina, recebe um bullet com link.
    - Subpágina inexistente: POST com title={pasta}/{slug_filho}.
    - Subpágina existente: PUT no slug {pasta}/{slug_filho}.
    """
    if not gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(cfg):
        raise ValueError(
            "GitLab wiki não configurado: defina GITLAB_BASE_URL, GITLAB_TOKEN e GITLAB_WIKI_PROJECT_PATH."
        )
    token = (cfg.gitlab_token or "").strip()
    titulo_norm = normalizar_titulo_issue_gitlab_transcribrothers(titulo, max_caracteres=255)
    conteudo = (conteudo_markdown or "").strip()
    if not conteudo:
        raise ValueError("Conteúdo da página wiki vazio.")

    slug_api = slug_completo.strip().strip("/")
    if "/" not in slug_api:
        raise ValueError(
            f"Slug API deve ser workshop/{{slug}} (ex.: workshop/meu-doc). Recebido: '{slug_api}'."
        )
    prefixo_pai, _, slug_filho = slug_api.partition("/")
    if not prefixo_pai or not slug_filho:
        raise ValueError(f"Slug wiki inválido: '{slug_api}'.")

    headers = {"PRIVATE-TOKEN": token}
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)
    url_colecao_wikis = montar_url_api_wikis_gitlab_projeto_transcribrothers(cfg)
    url_subpagina = montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(cfg, slug_api)
    corpo_post = _corpo_formulario_post_criar_subpagina_wiki_gitlab_transcribrothers(
        title_com_caminho_pasta=slug_api,
        conteudo=conteudo,
    )
    corpo_put = _corpo_formulario_put_atualizar_subpagina_wiki_gitlab_transcribrothers(
        titulo_exibicao=titulo_norm,
        conteudo=conteudo,
    )
    web_destino = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
        cfg, slug_filho, prefixo_pasta=prefixo_pai
    )
    web_indice_pasta = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(
        cfg, prefixo_pasta=prefixo_pai
    )

    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        await _verificar_pagina_indice_workshop_existe_sem_alterar_transcribrothers(
            cfg,
            client,
            headers,
            prefixo_pai,
        )

        resp_get = await client.get(url_subpagina, headers=headers)
        if resp_get.status_code == 200:
            return await _put_subpagina_wiki_gitlab_transcribrothers(
                client,
                cfg,
                headers,
                url_subpagina=url_subpagina,
                corpo_put=corpo_put,
                slug_api=slug_api,
                slug_filho=slug_filho,
                prefixo_pai=prefixo_pai,
                web_destino=web_destino,
                titulo_link=titulo_norm,
            )

        if resp_get.status_code == 404:
            resp_post = await client.post(url_colecao_wikis, headers=headers, data=corpo_post)
            if resp_post.status_code >= 400:
                if _gitlab_wiki_resposta_indica_titulo_duplicado_transcribrothers(resp_post):
                    resp_get_apos_dup = await client.get(url_subpagina, headers=headers)
                    if resp_get_apos_dup.status_code == 200:
                        return await _put_subpagina_wiki_gitlab_transcribrothers(
                            client,
                            cfg,
                            headers,
                            url_subpagina=url_subpagina,
                            corpo_put=corpo_put,
                            slug_api=slug_api,
                            slug_filho=slug_filho,
                            prefixo_pai=prefixo_pai,
                            web_destino=web_destino,
                            titulo_link=titulo_norm,
                        )
                    raise RuntimeError(
                        f"Já existe outra página na wiki com o título «{titulo_norm}» (GitLab não permite duplicar). "
                        f"A subpágina desejada é {web_destino}. "
                        "Renomeie ou remova a página antiga com o mesmo título (por exemplo na raiz da wiki) "
                        f"e tente de novo. A página índice {prefixo_pai} em {web_indice_pasta} não foi alterada."
                    )
                detalhe = resp_post.text.strip()
                if len(detalhe) > 800:
                    detalhe = f"{detalhe[:800]}…"
                raise RuntimeError(
                    f"GitLab recusou criar a subpágina em {web_destino} (HTTP {resp_post.status_code}). "
                    f"A página índice {prefixo_pai} em {web_indice_pasta} não foi alterada. "
                    f"{detalhe or 'sem corpo'}"
                )
            body = resp_post.json()
            if not isinstance(body, dict):
                raise RuntimeError("Resposta inesperada do GitLab ao criar página wiki.")
            validado = _validar_resposta_wiki_post_criacao_subpagina_workshop_transcribrothers(
                body,
                slug_api_esperado=slug_api,
                slug_filho_esperado=slug_filho,
                prefixo_pasta=prefixo_pai,
            )
            validado["atualizada"] = False
            return await _finalizar_exportacao_subpagina_com_link_no_indice_pasta_wiki_gitlab_transcribrothers(
                client,
                cfg,
                headers,
                validado,
                prefixo_pai=prefixo_pai,
                titulo_link=titulo_norm,
                web_destino=web_destino,
                slug_filho=slug_filho,
            )

        detalhe = resp_get.text.strip()
        if len(detalhe) > 800:
            detalhe = f"{detalhe[:800]}…"
        raise RuntimeError(
            f"Não foi possível consultar a subpágina em {web_destino} (HTTP {resp_get.status_code}). "
            f"{detalhe or 'sem corpo'}"
        )
