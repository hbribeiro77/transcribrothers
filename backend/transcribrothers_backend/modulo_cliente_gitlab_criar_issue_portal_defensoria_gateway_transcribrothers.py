"""Cliente HTTP para criar issues no GitLab (portal-defensoria-gateway + label squad::bravo)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def gitlab_criar_issue_configurado_no_ambiente_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    return bool((cfg.gitlab_base_url or "").strip() and (cfg.gitlab_token or "").strip())


def resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    if cfg.gitlab_tls_insecure_dev:
        return False
    return True


def normalizar_titulo_issue_gitlab_transcribrothers(titulo: str, *, max_caracteres: int = 255) -> str:
    t = (titulo or "").strip()
    if not t:
        raise ValueError("Título da issue vazio.")
    if len(t) > max_caracteres:
        return f"{t[: max_caracteres - 1].rstrip()}…"
    return t


def montar_url_api_criar_issue_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_path = (cfg.gitlab_create_issue_project_path or "").strip()
    if not project_path:
        raise ValueError("GITLAB_CREATE_ISSUE_PROJECT_PATH vazio.")
    project_enc = quote(project_path, safe="")
    return f"{base}/api/v4/projects/{project_enc}/issues"


async def criar_issue_gitlab_portal_defensoria_gateway_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    titulo: str,
    descricao_markdown: str,
    timeout_segundos: float = 60.0,
) -> dict[str, Any]:
    """
    POST /api/v4/projects/{path}/issues com labels padrão (squad::bravo).

    Retorna o JSON da issue (campos `iid`, `web_url`, etc.).
    """
    if not gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg):
        raise ValueError(
            "GitLab não configurado: defina GITLAB_BASE_URL e GITLAB_TOKEN no servidor (ex.: env.local na raiz)."
        )
    token = (cfg.gitlab_token or "").strip()
    titulo_norm = normalizar_titulo_issue_gitlab_transcribrothers(titulo)
    descricao = (descricao_markdown or "").strip()
    if not descricao:
        raise ValueError("Descrição da issue vazia.")

    labels = (cfg.gitlab_create_issue_default_labels or "squad::bravo").strip() or "squad::bravo"
    url = montar_url_api_criar_issue_gitlab_projeto_transcribrothers(cfg)
    payload = {
        "title": titulo_norm,
        "description": descricao,
        "labels": labels,
    }
    headers = {
        "PRIVATE-TOKEN": token,
        "Content-Type": "application/json",
    }
    verify = resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers(cfg)

    async with httpx.AsyncClient(timeout=timeout_segundos, verify=verify) as client:
        resp = await client.post(url, headers=headers, json=payload)

    if resp.status_code >= 400:
        detalhe = resp.text.strip()
        if len(detalhe) > 800:
            detalhe = f"{detalhe[:800]}…"
        raise RuntimeError(
            f"GitLab recusou a criação da issue (HTTP {resp.status_code}). {detalhe or 'sem corpo'}"
        )

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao criar issue.")
    return data
