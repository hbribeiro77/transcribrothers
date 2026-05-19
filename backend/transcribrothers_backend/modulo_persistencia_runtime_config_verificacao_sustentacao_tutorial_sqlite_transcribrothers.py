"""Persistência em SQLite: preferência da UI para executar ou omitir o Auditor (verificação sustentação)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

CHAVE_RUNTIME_VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA = (
    "verificacao_sustentacao_tutorial_desativada"
)


def _parsear_string_bool_desativada_verificacao_transcribrothers(s: str) -> bool | None:
    v = (s or "").strip().lower()
    if v in ("1", "true", "yes", "on", "sim"):
        return True
    if v in ("0", "false", "no", "off", "nao", "não"):
        return False
    return None


async def obter_override_verificacao_sustentacao_tutorial_desativada_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> bool | None:
    """
    None = não há preferência gravada na base (usa só o .env).
    True/False = valor persistido (desativada = não executar o Auditor).
    """
    row = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA,
    )
    if row is None or not (row.valor or "").strip():
        return None
    parsed = _parsear_string_bool_desativada_verificacao_transcribrothers(row.valor)
    if parsed is None:
        return None
    return parsed


async def verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
    session: AsyncSession,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> tuple[bool, bool]:
    """
    Devolve (desativada_efetiva, existe_preferencia_sqlite).
    A preferência SQLite tem prioridade sobre o .env quando definida e válida.
    """
    ov = await obter_override_verificacao_sustentacao_tutorial_desativada_do_sqlite_transcribrothers(session)
    if ov is None:
        return bool(configuracao.verificacao_sustentacao_tutorial_desativada), False
    return bool(ov), True


async def gravar_verificacao_sustentacao_tutorial_desativada_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    desativada: bool,
) -> None:
    agora = datetime.now(timezone.utc)
    valor = "true" if bool(desativada) else "false"
    chave = CHAVE_RUNTIME_VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
    if row is None:
        session.add(RegistroRuntimeConfigValorTranscribrothers(chave=chave, valor=valor, updated_at=agora))
    else:
        row.valor = valor
        row.updated_at = agora
    await session.commit()


async def apagar_override_verificacao_sustentacao_tutorial_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave
            == CHAVE_RUNTIME_VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA
        )
    )
    await session.commit()
