"""Persistência SQLite: lista de pastas wiki GitLab permitidas + pasta padrão (exportação)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    normalizar_prefixo_pasta_wiki_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

CHAVE_RUNTIME_GITLAB_WIKI_PASTAS_JSON = "gitlab_wiki_pastas_disponiveis_json"
CHAVE_RUNTIME_GITLAB_WIKI_PASTA_PADRAO = "gitlab_wiki_pasta_padrao"


def _pasta_padrao_do_env_transcribrothers(cfg: ConfiguracaoAmbienteTranscribrothers) -> str:
    try:
        return normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(
            (cfg.gitlab_wiki_slug_prefixo_pasta or "workshop").strip() or "workshop"
        )
    except ValueError:
        return "workshop"


def _parsear_lista_pastas_json_transcribrothers(raw: object) -> list[str] | None:
    if not isinstance(raw, str):
        return None
    texto = raw.strip()
    if not texto:
        return None
    try:
        data = json.loads(texto)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    out: list[str] = []
    vistos: set[str] = set()
    for item in data:
        if not isinstance(item, str):
            continue
        try:
            pasta = normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(item)
        except ValueError:
            continue
        if pasta in vistos:
            continue
        vistos.add(pasta)
        out.append(pasta)
    return out


async def obter_override_pastas_wiki_gitlab_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> tuple[list[str] | None, str | None]:
    """None, None = sem preferência SQLite (usa só o .env)."""
    row_lista = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_GITLAB_WIKI_PASTAS_JSON,
    )
    row_padrao = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_GITLAB_WIKI_PASTA_PADRAO,
    )
    lista = _parsear_lista_pastas_json_transcribrothers(
        row_lista.valor if row_lista is not None else ""
    )
    valor_padrao = row_padrao.valor if row_padrao is not None else ""
    padrao_raw = valor_padrao if isinstance(valor_padrao, str) else ""
    padrao: str | None = None
    if padrao_raw.strip():
        try:
            padrao = normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(padrao_raw)
        except ValueError:
            padrao = None
    if lista is None and padrao is None:
        return None, None
    return lista, padrao


async def resolver_pastas_wiki_gitlab_efetivas_transcribrothers(
    session: AsyncSession,
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> tuple[list[str], str, bool]:
    """
    Devolve (pastas_ordenadas, pasta_padrao, preferencia_sqlite_definida).

    Sem override SQLite: lista = [pasta do .env], padrão = pasta do .env.
    """
    env_padrao = _pasta_padrao_do_env_transcribrothers(cfg)
    lista_ov, padrao_ov = await obter_override_pastas_wiki_gitlab_do_sqlite_transcribrothers(session)
    if lista_ov is None and padrao_ov is None:
        return [env_padrao], env_padrao, False

    pastas = list(lista_ov) if lista_ov is not None and len(lista_ov) > 0 else [env_padrao]
    if padrao_ov and padrao_ov in pastas:
        padrao = padrao_ov
    else:
        padrao = pastas[0]
    return pastas, padrao, True


async def gravar_pastas_wiki_gitlab_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    pastas: list[str],
    pasta_padrao: str | None = None,
) -> tuple[list[str], str]:
    """Normaliza, grava e devolve (pastas, padrao). Exige pelo menos uma pasta."""
    normalizadas: list[str] = []
    vistos: set[str] = set()
    for item in pastas:
        pasta = normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(str(item))
        if pasta in vistos:
            continue
        vistos.add(pasta)
        normalizadas.append(pasta)
    if not normalizadas:
        raise ValueError("Informe ao menos uma pasta wiki (ex.: workshop).")

    if pasta_padrao is not None and str(pasta_padrao).strip():
        padrao = normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(str(pasta_padrao))
        if padrao not in vistos:
            raise ValueError(
                f"Pasta padrão {padrao!r} deve estar na lista de pastas disponíveis."
            )
    else:
        padrao = normalizadas[0]

    agora = datetime.now(timezone.utc)
    valor_lista = json.dumps(normalizadas, ensure_ascii=False)
    for chave, valor in (
        (CHAVE_RUNTIME_GITLAB_WIKI_PASTAS_JSON, valor_lista),
        (CHAVE_RUNTIME_GITLAB_WIKI_PASTA_PADRAO, padrao),
    ):
        row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
        if row is None:
            session.add(
                RegistroRuntimeConfigValorTranscribrothers(
                    chave=chave, valor=valor, updated_at=agora
                )
            )
        else:
            row.valor = valor
            row.updated_at = agora
    await session.commit()
    return normalizadas, padrao


async def apagar_override_pastas_wiki_gitlab_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    from sqlalchemy import delete

    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave.in_(
                [
                    CHAVE_RUNTIME_GITLAB_WIKI_PASTAS_JSON,
                    CHAVE_RUNTIME_GITLAB_WIKI_PASTA_PADRAO,
                ]
            )
        )
    )
    await session.commit()


def pasta_wiki_esta_na_lista_permitida_transcribrothers(
    pasta: str,
    pastas_permitidas: list[str],
) -> bool:
    try:
        norm = normalizar_prefixo_pasta_wiki_gitlab_transcribrothers(pasta)
    except ValueError:
        return False
    return norm in pastas_permitidas


def montar_dict_pastas_wiki_para_config_publica_transcribrothers(
    pastas: list[str],
    pasta_padrao: str,
    *,
    preferencia_sqlite_definida: bool,
) -> dict[str, Any]:
    return {
        "gitlab_wiki_pastas_disponiveis": pastas,
        "gitlab_wiki_slug_prefixo_pasta": pasta_padrao,
        "gitlab_wiki_pastas_preferencia_sqlite_definida": preferencia_sqlite_definida,
    }
