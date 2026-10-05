"""Persistência SQLite do provedor TTS (LiteLLM / ElevenLabs)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import Base
from transcribrothers_backend.modulo_persistencia_runtime_config_provedor_tts_narracao_sqlite_transcribrothers import (
    apagar_override_provedor_tts_narracao_runtime_sqlite_transcribrothers,
    gravar_preferencias_provedor_tts_narracao_runtime_sqlite_transcribrothers,
    resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers,
)
from transcribrothers_backend.modulo_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers import (
    MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
    PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
    PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
)


@pytest.fixture
async def session_sqlite_memoria_transcribrothers():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_provedor_padrao_e_litellm_sem_override(
    session_sqlite_memoria_transcribrothers: AsyncSession,
) -> None:
    prefs, definido = await resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(
        session_sqlite_memoria_transcribrothers
    )
    assert definido is False
    assert prefs.provedor == PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS
    assert prefs.modelo_elevenlabs == MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    assert prefs.voz_elevenlabs == ""


@pytest.mark.asyncio
async def test_gravar_elevenlabs_e_apagar_volta_ao_litellm(
    session_sqlite_memoria_transcribrothers: AsyncSession,
) -> None:
    gravado = await gravar_preferencias_provedor_tts_narracao_runtime_sqlite_transcribrothers(
        session_sqlite_memoria_transcribrothers,
        provedor="elevenlabs",
        modelo_elevenlabs="eleven_v4",
        voz_elevenlabs="voz-abc",
    )
    assert gravado.provedor == PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS
    assert gravado.voz_elevenlabs == "voz-abc"
    lido, definido = await resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(
        session_sqlite_memoria_transcribrothers
    )
    assert definido is True
    assert lido.provedor == PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS
    assert lido.voz_elevenlabs == "voz-abc"
    await apagar_override_provedor_tts_narracao_runtime_sqlite_transcribrothers(
        session_sqlite_memoria_transcribrothers
    )
    de_novo, definido2 = await resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(
        session_sqlite_memoria_transcribrothers
    )
    assert definido2 is False
    assert de_novo.provedor == PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS
