"""Preferências SQLite: verificação e correção automática de redundância na edição por seção."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_DESATIVADA = (
    "verificacao_redundancia_secao_markdown_desativada"
)
CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_HABILITADA = (
    "verificacao_redundancia_secao_correcao_automatica_habilitada"
)
CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_INCLUIR_ATENCAO = (
    "verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao"
)

PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_HABILITADA = True
PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_INCLUIR_CLASSIFICACAO_ATENCAO = False


@dataclass(frozen=True)
class PreferenciasEfetivasRuntimeRedundanciaSecaoMarkdownTranscribrothers:
    verificacao_desativada: bool
    correcao_automatica_habilitada: bool
    correcao_automatica_incluir_classificacao_atencao: bool
    preferencia_sqlite_verificacao_definida: bool
    preferencia_sqlite_correcao_habilitada_definida: bool
    preferencia_sqlite_correcao_incluir_atencao_definida: bool


def _parsear_string_bool_transcribrothers(s: str) -> bool | None:
    v = (s or "").strip().lower()
    if v in ("1", "true", "yes", "on", "sim"):
        return True
    if v in ("0", "false", "no", "off", "nao", "não"):
        return False
    return None


async def _obter_bool_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    chave: str,
) -> bool | None:
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
    if row is None or not (row.valor or "").strip():
        return None
    return _parsear_string_bool_transcribrothers(row.valor)


async def obter_override_verificacao_redundancia_secao_desativada_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> bool | None:
    return await _obter_bool_runtime_sqlite_transcribrothers(
        session,
        CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_DESATIVADA,
    )


async def resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers(
    session: AsyncSession,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> PreferenciasEfetivasRuntimeRedundanciaSecaoMarkdownTranscribrothers:
    ov_verif = await obter_override_verificacao_redundancia_secao_desativada_do_sqlite_transcribrothers(
        session
    )
    ov_corr_hab = await _obter_bool_runtime_sqlite_transcribrothers(
        session,
        CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_HABILITADA,
    )
    ov_corr_atencao = await _obter_bool_runtime_sqlite_transcribrothers(
        session,
        CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_INCLUIR_ATENCAO,
    )
    if ov_verif is None:
        verificacao_desativada = bool(configuracao.verificacao_redundancia_secao_markdown_desativada)
    else:
        verificacao_desativada = bool(ov_verif)
    correcao_hab = (
        bool(ov_corr_hab)
        if ov_corr_hab is not None
        else PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_HABILITADA
    )
    correcao_atencao = (
        bool(ov_corr_atencao)
        if ov_corr_atencao is not None
        else PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_INCLUIR_CLASSIFICACAO_ATENCAO
    )
    return PreferenciasEfetivasRuntimeRedundanciaSecaoMarkdownTranscribrothers(
        verificacao_desativada=verificacao_desativada,
        correcao_automatica_habilitada=correcao_hab,
        correcao_automatica_incluir_classificacao_atencao=correcao_atencao,
        preferencia_sqlite_verificacao_definida=ov_verif is not None,
        preferencia_sqlite_correcao_habilitada_definida=ov_corr_hab is not None,
        preferencia_sqlite_correcao_incluir_atencao_definida=ov_corr_atencao is not None,
    )


async def verificacao_redundancia_secao_markdown_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
    session: AsyncSession,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> tuple[bool, bool]:
    prefs = await resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers(
        session,
        configuracao,
    )
    return prefs.verificacao_desativada, prefs.preferencia_sqlite_verificacao_definida


async def _gravar_bool_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    chave: str,
    valor: bool,
) -> None:
    agora = datetime.now(timezone.utc)
    valor_str = "true" if bool(valor) else "false"
    row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
    if row is None:
        session.add(
            RegistroRuntimeConfigValorTranscribrothers(
                chave=chave,
                valor=valor_str,
                updated_at=agora,
            )
        )
    else:
        row.valor = valor_str
        row.updated_at = agora


async def gravar_preferencias_runtime_redundancia_secao_markdown_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    verificacao_desativada: bool,
    correcao_automatica_habilitada: bool,
    correcao_automatica_incluir_classificacao_atencao: bool,
) -> None:
    await _gravar_bool_runtime_sqlite_transcribrothers(
        session,
        chave=CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_DESATIVADA,
        valor=bool(verificacao_desativada),
    )
    await _gravar_bool_runtime_sqlite_transcribrothers(
        session,
        chave=CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_HABILITADA,
        valor=bool(correcao_automatica_habilitada),
    )
    await _gravar_bool_runtime_sqlite_transcribrothers(
        session,
        chave=CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_INCLUIR_ATENCAO,
        valor=bool(correcao_automatica_incluir_classificacao_atencao),
    )
    await session.commit()


async def gravar_verificacao_redundancia_secao_markdown_desativada_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    desativada: bool,
) -> None:
    """Compatibilidade: grava só a flag de verificação (demais preferências intactas)."""
    await _gravar_bool_runtime_sqlite_transcribrothers(
        session,
        chave=CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_DESATIVADA,
        valor=bool(desativada),
    )
    await session.commit()


_CHAVES_RUNTIME_REDUNDANCIA_SECAO_MARKDOWN = (
    CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_DESATIVADA,
    CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_HABILITADA,
    CHAVE_RUNTIME_VERIFICACAO_REDUNDANCIA_SECAO_CORRECAO_AUTOMATICA_INCLUIR_ATENCAO,
)


async def apagar_override_verificacao_redundancia_secao_markdown_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave.in_(
                _CHAVES_RUNTIME_REDUNDANCIA_SECAO_MARKDOWN
            )
        )
    )
    await session.commit()
