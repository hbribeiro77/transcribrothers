"""Upload de arquivos para Markdown no GitLab (POST /projects/:id/uploads)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from transcribrothers_backend.modulo_cliente_gitlab_criar_issue_portal_defensoria_gateway_transcribrothers import (
    resolver_parametro_httpx_verify_ssl_para_chamadas_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def montar_url_api_upload_markdown_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    project_path_gitlab: str | None = None,
) -> str:
    base = (cfg.gitlab_base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("GITLAB_BASE_URL não configurado no servidor.")
    project_path = (project_path_gitlab or cfg.gitlab_create_issue_project_path or "").strip()
    if not project_path:
        raise ValueError("GITLAB_CREATE_ISSUE_PROJECT_PATH vazio.")
    project_enc = quote(project_path, safe="")
    return f"{base}/api/v4/projects/{project_enc}/uploads"


async def upload_arquivo_png_markdown_gitlab_projeto_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    *,
    conteudo_png: bytes,
    nome_arquivo: str,
    project_path_gitlab: str | None = None,
    timeout_segundos: float = 120.0,
) -> str:
    """
    Envia PNG ao projeto GitLab e devolve o caminho Markdown (ex.: `/uploads/secret/arquivo.png`).
    """
    nome = (nome_arquivo or "").strip().replace("\\", "/").split("/")[-1]
    if not nome or ".." in nome:
        raise ValueError("Nome de arquivo inválido para upload GitLab.")
    if not nome.lower().endswith(".png"):
        nome = f"{nome}.png" if nome else "imagem.png"

    token = (cfg.gitlab_token or "").strip()
    if not token:
        raise ValueError("GITLAB_TOKEN não configurado no servidor.")

    url = montar_url_api_upload_markdown_gitlab_projeto_transcribrothers(
        cfg,
        project_path_gitlab=project_path_gitlab,
    )
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
            f"GitLab recusou o upload de '{nome}' (HTTP {resp.status_code}). {detalhe or 'sem corpo'}"
        )

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError("Resposta inesperada do GitLab ao enviar imagem.")
    url_md = str(data.get("url") or "").strip()
    if not url_md.startswith("/uploads/"):
        raise RuntimeError(f"GitLab não devolveu url de upload válida para '{nome}'.")
    return url_md
