"""Persistência SQLite: provedor TTS da narração (LiteLLM ou ElevenLabs)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers import (
    MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
    PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
    PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
    normalizar_modelo_tts_elevenlabs_transcribrothers,
    normalizar_provedor_tts_narracao_transcribrothers,
)

CHAVE_RUNTIME_PROVEDOR_TTS_NARRACAO = "provedor_tts_narracao"
CHAVE_RUNTIME_MODELO_TTS_ELEVENLABS = "modelo_tts_elevenlabs"
CHAVE_RUNTIME_VOZ_TTS_ELEVENLABS = "voz_tts_elevenlabs"


@dataclass(frozen=True)
class PreferenciasProvedorTtsNarracaoTranscribrothers:
    provedor: str
    modelo_elevenlabs: str
    voz_elevenlabs: str


def preferencias_provedor_tts_narracao_padrao_transcribrothers() -> (
    PreferenciasProvedorTtsNarracaoTranscribrothers
):
    return PreferenciasProvedorTtsNarracaoTranscribrothers(
        provedor=PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
        modelo_elevenlabs=MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
        voz_elevenlabs="",
    )


def _normalizar_voz_elevenlabs_transcribrothers(valor: object) -> str:
    return str(valor or "").strip()


async def _ler_valor_runtime(session: AsyncSession, chave: str) -> str:
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
    if row is None:
        return ""
    return str(row.valor or "").strip()


async def _gravar_valor_runtime(session: AsyncSession, chave: str, valor: str) -> None:
    agora = datetime.now(timezone.utc)
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
    if row is None:
        session.add(
            RegistroRuntimeConfigValorTranscribrothers(
                chave=chave,
                valor=valor,
                updated_at=agora,
            )
        )
        return
    row.valor = valor
    row.updated_at = agora


async def resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(
    session: AsyncSession,
) -> tuple[PreferenciasProvedorTtsNarracaoTranscribrothers, bool]:
    raw_provedor = await _ler_valor_runtime(session, CHAVE_RUNTIME_PROVEDOR_TTS_NARRACAO)
    raw_modelo = await _ler_valor_runtime(session, CHAVE_RUNTIME_MODELO_TTS_ELEVENLABS)
    raw_voz = await _ler_valor_runtime(session, CHAVE_RUNTIME_VOZ_TTS_ELEVENLABS)
    if not raw_provedor and not raw_modelo and not raw_voz:
        return preferencias_provedor_tts_narracao_padrao_transcribrothers(), False
    try:
        provedor = normalizar_provedor_tts_narracao_transcribrothers(raw_provedor)
        modelo = normalizar_modelo_tts_elevenlabs_transcribrothers(raw_modelo)
    except ValueError:
        return preferencias_provedor_tts_narracao_padrao_transcribrothers(), False
    return (
        PreferenciasProvedorTtsNarracaoTranscribrothers(
            provedor=provedor,
            modelo_elevenlabs=modelo,
            voz_elevenlabs=_normalizar_voz_elevenlabs_transcribrothers(raw_voz),
        ),
        True,
    )


async def gravar_preferencias_provedor_tts_narracao_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    provedor: str,
    modelo_elevenlabs: str | None = None,
    voz_elevenlabs: str | None = None,
) -> PreferenciasProvedorTtsNarracaoTranscribrothers:
    atual, _ = await resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(session)
    prefs = PreferenciasProvedorTtsNarracaoTranscribrothers(
        provedor=normalizar_provedor_tts_narracao_transcribrothers(provedor),
        modelo_elevenlabs=normalizar_modelo_tts_elevenlabs_transcribrothers(
            modelo_elevenlabs if modelo_elevenlabs is not None else atual.modelo_elevenlabs
        ),
        voz_elevenlabs=_normalizar_voz_elevenlabs_transcribrothers(
            voz_elevenlabs if voz_elevenlabs is not None else atual.voz_elevenlabs
        ),
    )
    if prefs.provedor == PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS and not prefs.voz_elevenlabs:
        # Permite gravar o provedor antes de escolher a voz; a síntese exige voice_id depois.
        pass
    await _gravar_valor_runtime(session, CHAVE_RUNTIME_PROVEDOR_TTS_NARRACAO, prefs.provedor)
    await _gravar_valor_runtime(session, CHAVE_RUNTIME_MODELO_TTS_ELEVENLABS, prefs.modelo_elevenlabs)
    await _gravar_valor_runtime(session, CHAVE_RUNTIME_VOZ_TTS_ELEVENLABS, prefs.voz_elevenlabs)
    await session.commit()
    return prefs


async def apagar_override_provedor_tts_narracao_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave.in_(
                [
                    CHAVE_RUNTIME_PROVEDOR_TTS_NARRACAO,
                    CHAVE_RUNTIME_MODELO_TTS_ELEVENLABS,
                    CHAVE_RUNTIME_VOZ_TTS_ELEVENLABS,
                ]
            )
        )
    )
    await session.commit()


async def carregar_provedor_tts_narracao_do_session_factory_transcribrothers(
    session_factory: object,
) -> PreferenciasProvedorTtsNarracaoTranscribrothers:
    async with session_factory() as session:  # type: ignore[misc]
        prefs, _ = await resolver_preferencias_provedor_tts_narracao_efetivas_transcribrothers(session)
    return prefs
