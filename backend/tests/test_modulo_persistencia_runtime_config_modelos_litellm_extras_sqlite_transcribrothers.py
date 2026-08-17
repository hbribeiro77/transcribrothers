"""Persistência SQLite de modelos LiteLLM extras (allowlist runtime)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import Base
from transcribrothers_backend.modulo_persistencia_runtime_config_modelos_litellm_extras_sqlite_transcribrothers import (
    adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers,
    definir_cache_modelos_litellm_extras_runtime_transcribrothers,
    obter_modelos_litellm_extras_em_cache_transcribrothers,
    obter_modelos_litellm_extras_do_sqlite_transcribrothers,
)


@pytest.fixture
async def session_sqlite_memoria_transcribrothers():
    definir_cache_modelos_litellm_extras_runtime_transcribrothers([])
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
    definir_cache_modelos_litellm_extras_runtime_transcribrothers([])


@pytest.mark.asyncio
async def test_adicionar_modelo_extra_grava_sqlite_e_atualiza_cache_transcribrothers(
    session_sqlite_memoria_transcribrothers: AsyncSession,
) -> None:
    lista = await adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers(
        session_sqlite_memoria_transcribrothers,
        modelo="azure_ai/claude-opus-4-8",
    )
    assert lista == ["azure_ai/claude-opus-4-8"]
    assert obter_modelos_litellm_extras_em_cache_transcribrothers() == ["azure_ai/claude-opus-4-8"]

    lista2 = await adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers(
        session_sqlite_memoria_transcribrothers,
        modelo="azure_ai/claude-opus-4-8",
    )
    assert lista2 == ["azure_ai/claude-opus-4-8"]

    lidos = await obter_modelos_litellm_extras_do_sqlite_transcribrothers(
        session_sqlite_memoria_transcribrothers
    )
    assert lidos == ["azure_ai/claude-opus-4-8"]
