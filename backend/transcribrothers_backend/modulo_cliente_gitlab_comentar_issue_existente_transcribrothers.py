"""Cliente HTTP para comentar em uma issue existente do GitLab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, unquote, urlparse

import httpx

from transcribrothers_backend.modulo_cliente_gitlab_criar_issue_portal_defensoria_gateway_transcribrothers import (
    gitlab_criar_issue_configurado_no_ambiente_transcribrothers,
    resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

LIMITE_CARACTERES_CORPO_NOTA_ISSUE_GITLAB_TRANSCRIBROTHERS = 1_000_000


@dataclass(frozen=True)
class DestinoIssueGitlabTranscribrothers:
    project_path: str
    issue_iid: int
    issue_url: str


def _origem_url_gitlab_transcribrothers(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL de issue GitLab inválida.")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def extrair_destino_issue_gitlab_a_partir_url_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    issue_url: str,
) -> DestinoIssueGitlabTranscribrothers:
    """Valida a URL informada e extrai projeto + IID da issue."""
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")

    origem_configurada = _origem_url_gitlab_transcribrothers(base)
    parsed = urlparse((issue_url or "").strip())
    origem_informada = _origem_url_gitlab_transcribrothers(issue_url)
    if origem_informada != origem_configurada:
        raise ValueError("A URL informada não pertence ao GitLab configurado no servidor.")

    partes = [unquote(p) for p in parsed.path.split("/") if p]
    try:
        marcador = partes.index("-")
    except ValueError as exc:
        raise ValueError("URL de issue GitLab inválida: use o formato /grupo/projeto/-/issues/123.") from exc

    if marcador < 1 or len(partes) <= marcador + 2 or partes[marcador + 1] != "issues":
        raise ValueError("URL de issue GitLab inválida: use o formato /grupo/projeto/-/issues/123.")

    iid_texto = partes[marcador + 2].strip()
    if not iid_texto.isdigit():
        raise ValueError("O IID da issue deve ser um número.")
    issue_iid = int(iid_texto)
    project_path = "/".join(partes[:marcador]).strip("/")
    if not project_path:
        raise ValueError("URL de issue GitLab inválida: projeto não identificado.")

    issue_url_limpa = f"{origem_configurada}/{project_path}/-/issues/{issue_iid}"
    return DestinoIssueGitlabTranscribrothers(
        project_path=project_path,
        issue_iid=issue_iid,
        issue_url=issue_url_limpa,
    )


def montar_url_api_comentar_issue_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    destino: DestinoIssueGitlabTranscribrothers,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_enc = quote(destino.project_path, safe="")
    return f"{base}/api/v4/projects/{project_enc}/issues/{destino.issue_iid}/notes"


def montar_url_api_issue_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    destino: DestinoIssueGitlabTranscribrothers,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_enc = quote(destino.project_path, safe="")
    return f"{base}/api/v4/projects/{project_enc}/issues/{destino.issue_iid}"


def montar_descricao_issue_gitlab_com_markdown_anexado_transcribrothers(
    descricao_atual: str | None,
    markdown_documento: str,
) -> str:
    documento = (markdown_documento or "").strip()
    if not documento:
        raise ValueError("Markdown do documento vazio.")
    prefixo = (descricao_atual or "").strip()
    bloco = f"---\n\n{documento}"
    if prefixo:
        return f"{prefixo}\n\n{bloco}"
    return bloco


async def comentar_issue_gitlab_existente_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    issue_url: str,
    corpo_markdown: str,
    timeout_segundos: float = 60.0,
) -> dict[str, Any]:
    """POST /api/v4/projects/{path}/issues/{iid}/notes."""
    if not gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg):
        raise ValueError(
            "GitLab não configurado: defina GITLAB_BASE_URL e GITLAB_TOKEN no servidor (ex.: env.local na raiz)."
        )
    corpo = (corpo_markdown or "").strip()
    if not corpo:
        raise ValueError("Corpo do comentário vazio.")
    if len(corpo) > LIMITE_CARACTERES_CORPO_NOTA_ISSUE_GITLAB_TRANSCRIBROTHERS:
        raise ValueError("Corpo do comentário excede o limite de 1.000.000 caracteres do GitLab.")

    destino = extrair_destino_issue_gitlab_a_partir_url_transcribrothers(cfg, issue_url)
    token = (cfg.gitlab_token or "").strip()
    url = montar_url_api_comentar_issue_gitlab_transcribrothers(cfg, destino)
    headers = {
        "PRIVATE-TOKEN": token,
        "Content-Type": "application/json",
    }
    payload = {"body": corpo}
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)

    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        resp = await client.post(url, headers=headers, json=payload)

    if resp.status_code >= 400:
        detalhe = resp.text.strip()
        if len(detalhe) > 800:
            detalhe = f"{detalhe[:800]}…"
        raise RuntimeError(
            f"GitLab recusou a criação do comentário (HTTP {resp.status_code}). {detalhe or 'sem corpo'}"
        )

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao criar comentário na issue.")
    data.setdefault("project_path", destino.project_path)
    data.setdefault("issue_iid", destino.issue_iid)
    data.setdefault("issue_url", destino.issue_url)
    return data


async def adicionar_markdown_na_descricao_issue_gitlab_existente_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    issue_url: str,
    markdown_documento: str,
    timeout_segundos: float = 60.0,
) -> dict[str, Any]:
    """GET da issue atual e PUT preservando a descrição existente com Markdown anexado ao final."""
    if not gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg):
        raise ValueError(
            "GitLab não configurado: defina GITLAB_BASE_URL e GITLAB_TOKEN no servidor (ex.: env.local na raiz)."
        )
    destino = extrair_destino_issue_gitlab_a_partir_url_transcribrothers(cfg, issue_url)
    token = (cfg.gitlab_token or "").strip()
    url = montar_url_api_issue_gitlab_transcribrothers(cfg, destino)
    headers = {
        "PRIVATE-TOKEN": token,
        "Content-Type": "application/json",
    }
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)

    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        resp_get = await client.get(url, headers=headers)
        if resp_get.status_code >= 400:
            detalhe = resp_get.text.strip()
            if len(detalhe) > 800:
                detalhe = f"{detalhe[:800]}…"
            raise RuntimeError(
                f"GitLab recusou a consulta da issue (HTTP {resp_get.status_code}). {detalhe or 'sem corpo'}"
            )
        issue_atual = resp_get.json()
        if not isinstance(issue_atual, dict):
            raise RuntimeError("Resposta inesperada do GitLab ao consultar issue.")
        nova_descricao = montar_descricao_issue_gitlab_com_markdown_anexado_transcribrothers(
            str(issue_atual.get("description") or ""),
            markdown_documento,
        )
        resp_put = await client.put(url, headers=headers, json={"description": nova_descricao})

    if resp_put.status_code >= 400:
        detalhe = resp_put.text.strip()
        if len(detalhe) > 800:
            detalhe = f"{detalhe[:800]}…"
        raise RuntimeError(
            f"GitLab recusou a atualização da descrição da issue (HTTP {resp_put.status_code}). {detalhe or 'sem corpo'}"
        )

    data = resp_put.json()
    if not isinstance(data, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao atualizar descrição da issue.")
    data.setdefault("project_path", destino.project_path)
    data.setdefault("issue_iid", destino.issue_iid)
    data.setdefault("issue_url", destino.issue_url)
    return data
