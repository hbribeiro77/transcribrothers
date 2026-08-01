"""Persistência em SQLite: voz Gemini TTS da narração."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    PreferenciasVozTtsNarracaoTranscribrothers,
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
    montar_preferencias_voz_tts_narracao_transcribrothers,
    preferencias_voz_tts_narracao_padrao_transcribrothers,
)

CHAVE_RUNTIME_VOZ_TTS_NARRACAO = "voz_tts_narracao_gemini"


async def resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(
    session: AsyncSession,
) -> tuple[PreferenciasVozTtsNarracaoTranscribrothers, bool]:
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, CHAVE_RUNTIME_VOZ_TTS_NARRACAO)
    if row is None or not (row.valor or "").strip():
        return preferencias_voz_tts_narracao_padrao_transcribrothers(), False
    try:
        prefs = montar_preferencias_voz_tts_narracao_transcribrothers(voz=row.valor)
    except ValueError:
        return preferencias_voz_tts_narracao_padrao_transcribrothers(), False
    return prefs, True


async def gravar_preferencias_voz_tts_narracao_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    voz: str,
) -> PreferenciasVozTtsNarracaoTranscribrothers:
    prefs = montar_preferencias_voz_tts_narracao_transcribrothers(voz=voz)
    agora = datetime.now(timezone.utc)
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, CHAVE_RUNTIME_VOZ_TTS_NARRACAO)
    if row is None:
        session.add(
            RegistroRuntimeConfigValorTranscribrothers(
                chave=CHAVE_RUNTIME_VOZ_TTS_NARRACAO,
                valor=prefs.voz,
                updated_at=agora,
            )
        )
    else:
        row.valor = prefs.voz
        row.updated_at = agora
    await session.commit()
    return prefs


async def apagar_override_voz_tts_narracao_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave == CHAVE_RUNTIME_VOZ_TTS_NARRACAO
        )
    )
    await session.commit()


async def carregar_voz_tts_narracao_do_session_factory_transcribrothers(
    session_factory: object,
) -> str:
    async with session_factory() as session:  # type: ignore[misc]
        prefs, _ = await resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(session)
    return prefs.voz or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
