"""Persistência SQLite: modelos LiteLLM extras (allowlist além do .env).

O select da UI pode guardar slugs só no navegador; jobs validam no servidor.
Esta tabela runtime permite incluir modelos testados/adicionados na allowlist efetiva.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)

CHAVE_RUNTIME_LITELLM_MODELOS_EXTRAS_JSON = "litellm_modelos_extras_json"

_CACHE_MODELOS_LITELLM_EXTRAS: list[str] = []


def _normalizar_lista_modelos_litellm_extras_transcribrothers(raw: object) -> list[str]:
    if isinstance(raw, str):
        texto = raw.strip()
        if not texto:
            return []
        try:
            data = json.loads(texto)
        except json.JSONDecodeError:
            return []
    elif isinstance(raw, list):
        data = raw
    else:
        return []
    if not isinstance(data, list):
        return []
    out: list[str] = []
    vistos: set[str] = set()
    for item in data:
        if not isinstance(item, str):
            continue
        t = item.strip()
        if not t or t in vistos:
            continue
        vistos.add(t)
        out.append(t)
    return out


def definir_cache_modelos_litellm_extras_runtime_transcribrothers(modelos: list[str]) -> None:
    global _CACHE_MODELOS_LITELLM_EXTRAS
    _CACHE_MODELOS_LITELLM_EXTRAS = _normalizar_lista_modelos_litellm_extras_transcribrothers(modelos)


def obter_modelos_litellm_extras_em_cache_transcribrothers() -> list[str]:
    return list(_CACHE_MODELOS_LITELLM_EXTRAS)


async def obter_modelos_litellm_extras_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> list[str]:
    row = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_LITELLM_MODELOS_EXTRAS_JSON,
    )
    if row is None:
        return []
    return _normalizar_lista_modelos_litellm_extras_transcribrothers(row.valor)


async def sincronizar_cache_modelos_litellm_extras_da_session_transcribrothers(
    session: AsyncSession,
) -> list[str]:
    lista = await obter_modelos_litellm_extras_do_sqlite_transcribrothers(session)
    definir_cache_modelos_litellm_extras_runtime_transcribrothers(lista)
    return lista


async def gravar_modelos_litellm_extras_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    modelos: list[str],
) -> list[str]:
    normalizados = _normalizar_lista_modelos_litellm_extras_transcribrothers(modelos)
    agora = datetime.now(timezone.utc)
    payload = json.dumps(normalizados, ensure_ascii=False)
    row = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_LITELLM_MODELOS_EXTRAS_JSON,
    )
    if row is None:
        session.add(
            RegistroRuntimeConfigValorTranscribrothers(
                chave=CHAVE_RUNTIME_LITELLM_MODELOS_EXTRAS_JSON,
                valor=payload,
                updated_at=agora,
            )
        )
    else:
        row.valor = payload
        row.updated_at = agora
    await session.commit()
    definir_cache_modelos_litellm_extras_runtime_transcribrothers(normalizados)
    return normalizados


async def adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    modelo: str,
) -> list[str]:
    t = (modelo or "").strip()
    if not t:
        raise ValueError("Informe o slug do modelo LiteLLM.")
    atuais = await obter_modelos_litellm_extras_do_sqlite_transcribrothers(session)
    if t not in atuais:
        atuais = [*atuais, t]
    return await gravar_modelos_litellm_extras_runtime_sqlite_transcribrothers(
        session, modelos=atuais
    )
