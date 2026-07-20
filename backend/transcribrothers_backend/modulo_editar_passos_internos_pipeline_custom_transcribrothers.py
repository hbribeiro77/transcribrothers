"""Adicionar, remover e reordenar passos em pipelines custom (Fase 2b do catálogo)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    AgenteCustomTranscribrothers,
    PipelineCustomTranscribrothers,
    novo_id_custom_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_pipelines_e_agentes_custom_sqlite_transcribrothers import (
    agente_custom_referenciado_por_pipeline_transcribrothers,
    obter_agente_custom_por_id_transcribrothers,
    obter_ou_criar_agente_custom_biblioteca_por_fonte_transcribrothers,
    obter_pipeline_custom_por_id_transcribrothers,
)


def _ids_passos_existentes(passos_json: list[dict[str, Any]]) -> set[str]:
    return {str(p.get("id") or "").strip() for p in passos_json if str(p.get("id") or "").strip()}


def _gerar_id_passo_novo_pipeline_custom_transcribrothers(
    handler_chave: str,
    passos_json: list[dict[str, Any]],
) -> str:
    ids = _ids_passos_existentes(passos_json)
    base = (handler_chave or "passo").strip() or "passo"
    if base not in ids:
        return base
    while True:
        candidato = f"passo_{novo_id_custom_transcribrothers()[:8]}"
        if candidato not in ids:
            return candidato


async def _tentar_excluir_agente_custom_orfao_transcribrothers(
    session: AsyncSession,
    agente_id: str,
) -> None:
    aid = agente_id.strip()
    if not aid:
        return
    if await agente_custom_referenciado_por_pipeline_transcribrothers(session, aid):
        return
    await session.execute(delete(AgenteCustomTranscribrothers).where(AgenteCustomTranscribrothers.id == aid))
    await session.commit()


async def reordenar_passos_pipeline_custom_transcribrothers(
    session: AsyncSession,
    pipeline_id: str,
    passo_ids_ordenados: list[str],
) -> PipelineCustomTranscribrothers:
    row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_id)
    if row is None:
        raise ValueError(f"Pipeline custom não encontrada: {pipeline_id}")
    passos = list(row.passos_json or [])
    ids_existentes = [str(p.get("id") or "").strip() for p in passos if str(p.get("id") or "").strip()]
    ids_solicitados = [i.strip() for i in passo_ids_ordenados if i.strip()]
    if set(ids_solicitados) != set(ids_existentes):
        raise ValueError(
            "passo_ids_ordenados deve listar exatamente todos os passos da pipeline, sem faltantes nem extras."
        )
    if len(ids_solicitados) != len(set(ids_solicitados)):
        raise ValueError("passo_ids_ordenados contém IDs duplicados.")
    mapa = {str(p.get("id") or ""): p for p in passos}
    row.passos_json = [mapa[pid] for pid in ids_solicitados]
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    return row


async def adicionar_passo_pipeline_custom_transcribrothers(
    session: AsyncSession,
    pipeline_id: str,
    *,
    agente_fonte_id: str,
    rotulo: str | None = None,
    descricao: str | None = None,
) -> PipelineCustomTranscribrothers:
    row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_id)
    if row is None:
        raise ValueError(f"Pipeline custom não encontrada: {pipeline_id}")
    fonte_norm = agente_fonte_id.strip()
    if not fonte_norm:
        raise ValueError("agente_fonte_id é obrigatório.")
    agente_ref = await obter_ou_criar_agente_custom_biblioteca_por_fonte_transcribrothers(
        session, fonte_norm
    )
    passos = list(row.passos_json or [])
    passo_id = _gerar_id_passo_novo_pipeline_custom_transcribrothers(agente_ref.handler_chave, passos)
    rotulo_passo = (rotulo or "").strip() or agente_ref.rotulo
    descricao_passo = descricao if descricao is not None else agente_ref.descricao
    passos.append(
        {
            "id": passo_id,
            "agente_id": agente_ref.id,
            "rotulo": rotulo_passo,
            "descricao": descricao_passo,
        }
    )
    row.passos_json = passos
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    return row


async def remover_passo_pipeline_custom_transcribrothers(
    session: AsyncSession,
    pipeline_id: str,
    passo_id: str,
) -> PipelineCustomTranscribrothers:
    row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_id)
    if row is None:
        raise ValueError(f"Pipeline custom não encontrada: {pipeline_id}")
    passo_norm = passo_id.strip()
    passos = list(row.passos_json or [])
    if len(passos) <= 1:
        raise ValueError("A pipeline deve manter pelo menos um passo.")
    removido: dict[str, Any] | None = None
    restantes: list[dict[str, Any]] = []
    for p in passos:
        if str(p.get("id") or "") == passo_norm:
            removido = p
        else:
            restantes.append(p)
    if removido is None:
        raise ValueError(f"Passo não encontrado na pipeline: {passo_norm!r}.")
    agente_id = str(removido.get("agente_id") or "")
    row.passos_json = restantes
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    if agente_id:
        agente = await obter_agente_custom_por_id_transcribrothers(session, agente_id)
        if agente is not None:
            await _tentar_excluir_agente_custom_orfao_transcribrothers(session, agente_id)
    return row
