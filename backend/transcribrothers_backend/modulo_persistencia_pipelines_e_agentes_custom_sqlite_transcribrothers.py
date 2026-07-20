"""CRUD SQLite para pipelines e agentes custom (duplicar do catálogo sistema, editar, excluir)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    AgenteCustomTranscribrothers,
    PipelineCustomTranscribrothers,
    novo_id_custom_transcribrothers,
)
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    AgenteCatalogoDocumentacaoTranscribrothers,
    PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS,
    PipelineCatalogoDocumentacaoTranscribrothers,
    PromptCatalogoPassoPipelineTranscribrothers,
    mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers,
    normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers,
    obter_agente_catalogo_sistema_por_id_transcribrothers,
    obter_pipeline_catalogo_sistema_por_id_transcribrothers,
)


def _prompts_catalogo_para_json(
    prompts: list[PromptCatalogoPassoPipelineTranscribrothers],
) -> list[dict[str, Any]]:
    return [p.model_dump() for p in prompts]


def _agente_catalogo_para_row_custom_transcribrothers(
    agente: AgenteCatalogoDocumentacaoTranscribrothers,
    *,
    novo_id: str,
    handler_chave: str,
    copiado_de: str,
) -> AgenteCustomTranscribrothers:
    agora = datetime.now(timezone.utc)
    return AgenteCustomTranscribrothers(
        id=novo_id,
        handler_chave=handler_chave,
        copiado_de=copiado_de,
        rotulo=agente.rotulo,
        descricao=agente.descricao,
        prompts_json=_prompts_catalogo_para_json(agente.prompts),
        modelo_litellm=None,
        created_at=agora,
        updated_at=agora,
    )


async def obter_agente_custom_por_id_transcribrothers(
    session: AsyncSession,
    agente_id: str,
) -> AgenteCustomTranscribrothers | None:
    res = await session.execute(
        select(AgenteCustomTranscribrothers).where(AgenteCustomTranscribrothers.id == agente_id)
    )
    return res.scalar_one_or_none()


async def obter_pipeline_custom_por_id_transcribrothers(
    session: AsyncSession,
    pipeline_id: str,
) -> PipelineCustomTranscribrothers | None:
    res = await session.execute(
        select(PipelineCustomTranscribrothers).where(PipelineCustomTranscribrothers.id == pipeline_id)
    )
    return res.scalar_one_or_none()


async def listar_agentes_custom_transcribrothers(
    session: AsyncSession,
) -> list[AgenteCustomTranscribrothers]:
    res = await session.execute(select(AgenteCustomTranscribrothers))
    return list(res.scalars().all())


async def listar_pipelines_custom_transcribrothers(
    session: AsyncSession,
) -> list[PipelineCustomTranscribrothers]:
    res = await session.execute(
        select(PipelineCustomTranscribrothers).order_by(
            PipelineCustomTranscribrothers.ordem_exibicao.asc(),
            PipelineCustomTranscribrothers.created_at.asc(),
        )
    )
    return list(res.scalars().all())


async def proxima_ordem_exibicao_pipeline_custom_transcribrothers(session: AsyncSession) -> int:
    res = await session.execute(select(func.max(PipelineCustomTranscribrothers.ordem_exibicao)))
    max_ordem = res.scalar_one_or_none()
    if max_ordem is None:
        return 0
    return int(max_ordem) + 1


async def obter_agente_custom_biblioteca_por_handler_chave_transcribrothers(
    session: AsyncSession,
    handler_chave: str,
) -> AgenteCustomTranscribrothers | None:
    """Agente custom mais antigo com o handler (âncora da biblioteca compartilhada)."""
    chave = (handler_chave or "").strip()
    if not chave:
        return None
    res = await session.execute(
        select(AgenteCustomTranscribrothers)
        .where(AgenteCustomTranscribrothers.handler_chave == chave)
        .order_by(AgenteCustomTranscribrothers.created_at.asc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def obter_ou_criar_agente_custom_biblioteca_por_fonte_transcribrothers(
    session: AsyncSession,
    fonte_id: str,
) -> AgenteCustomTranscribrothers:
    """
    Biblioteca compartilhada: se fonte é custom, referencia; se sistema, reutiliza
    o custom mais antigo com o mesmo handler_chave ou cria um (sem sufixo cópia).
    """
    fonte_norm = (fonte_id or "").strip()
    if not fonte_norm:
        raise ValueError("fonte_id é obrigatório.")

    agente_custom = await obter_agente_custom_por_id_transcribrothers(session, fonte_norm)
    if agente_custom is not None:
        return agente_custom

    agente_sistema = obter_agente_catalogo_sistema_por_id_transcribrothers(fonte_norm)
    if agente_sistema is None:
        raise ValueError(f"Agente fonte não encontrado: {fonte_norm}")

    existente = await obter_agente_custom_biblioteca_por_handler_chave_transcribrothers(
        session, fonte_norm
    )
    if existente is not None:
        return existente

    row = _agente_catalogo_para_row_custom_transcribrothers(
        agente_sistema,
        novo_id=novo_id_custom_transcribrothers(),
        handler_chave=fonte_norm,
        copiado_de=fonte_norm,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return row


async def duplicar_agente_catalogo_para_custom_transcribrothers(
    session: AsyncSession,
    fonte_id: str,
) -> AgenteCustomTranscribrothers:
    """Cria variante explícita (sempre nova row com sufixo cópia)."""
    agente_sistema = obter_agente_catalogo_sistema_por_id_transcribrothers(fonte_id)
    if agente_sistema is None:
        agente_custom = await obter_agente_custom_por_id_transcribrothers(session, fonte_id)
        if agente_custom is None:
            raise ValueError(f"Agente fonte não encontrado: {fonte_id}")
        agora = datetime.now(timezone.utc)
        novo = AgenteCustomTranscribrothers(
            id=novo_id_custom_transcribrothers(),
            handler_chave=agente_custom.handler_chave,
            copiado_de=agente_custom.copiado_de,
            rotulo=f"{agente_custom.rotulo} (cópia)",
            descricao=agente_custom.descricao,
            prompts_json=list(agente_custom.prompts_json or []),
            modelo_litellm=agente_custom.modelo_litellm,
            created_at=agora,
            updated_at=agora,
        )
        session.add(novo)
        await session.commit()
        await session.refresh(novo)
        return novo

    novo_id = novo_id_custom_transcribrothers()
    row = _agente_catalogo_para_row_custom_transcribrothers(
        agente_sistema,
        novo_id=novo_id,
        handler_chave=fonte_id,
        copiado_de=fonte_id,
    )
    row.rotulo = f"{agente_sistema.rotulo} (cópia)"
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


def obter_mapa_agentes_catalogo_sistema_para_pipeline_transcribrothers(
    pipeline: PipelineCatalogoDocumentacaoTranscribrothers,
) -> dict[str, AgenteCatalogoDocumentacaoTranscribrothers]:
    from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
        obter_mapa_agentes_catalogo_sistema_transcribrothers,
    )

    todos = obter_mapa_agentes_catalogo_sistema_transcribrothers()
    return {p.agente_id: todos[p.agente_id] for p in pipeline.passos if p.agente_id in todos}


async def duplicar_pipeline_catalogo_para_custom_transcribrothers(
    session: AsyncSession,
    fonte_id: str,
) -> PipelineCustomTranscribrothers:
    pipeline_sistema = obter_pipeline_catalogo_sistema_por_id_transcribrothers(fonte_id)
    if pipeline_sistema is not None:
        copiado_de_raiz = fonte_id
        id_map: dict[str, str] = {}
        for passo in pipeline_sistema.passos:
            agente_id_sistema = passo.agente_id
            if agente_id_sistema in id_map:
                continue
            agente_row = await obter_ou_criar_agente_custom_biblioteca_por_fonte_transcribrothers(
                session, agente_id_sistema
            )
            id_map[agente_id_sistema] = agente_row.id

        passos_json = [
            {
                "id": passo.id,
                "agente_id": id_map[passo.agente_id],
                "rotulo": passo.rotulo,
                "descricao": passo.descricao,
            }
            for passo in pipeline_sistema.passos
        ]
        agora = datetime.now(timezone.utc)
        novo_pipeline_id = novo_id_custom_transcribrothers()
        ordem = await proxima_ordem_exibicao_pipeline_custom_transcribrothers(session)
        pipeline_row = PipelineCustomTranscribrothers(
            id=novo_pipeline_id,
            copiado_de=copiado_de_raiz,
            titulo=f"{pipeline_sistema.titulo} (cópia)",
            descricao=pipeline_sistema.descricao,
            passos_json=passos_json,
            ordem_exibicao=ordem,
            entradas_aceitas_json=list(pipeline_sistema.entradas_aceitas),
            created_at=agora,
            updated_at=agora,
        )
        session.add(pipeline_row)
        await session.commit()
        await session.refresh(pipeline_row)
        return pipeline_row

    pipeline_custom = await obter_pipeline_custom_por_id_transcribrothers(session, fonte_id)
    if pipeline_custom is None:
        raise ValueError(f"Pipeline fonte não encontrada: {fonte_id}")

    copiado_de_raiz = str(pipeline_custom.copiado_de or "")
    passos_fonte = list(pipeline_custom.passos_json or [])
    for passo in passos_fonte:
        aid = str(passo.get("agente_id") or "")
        if not aid:
            continue
        agente_custom = await obter_agente_custom_por_id_transcribrothers(session, aid)
        if agente_custom is None:
            raise ValueError(f"Agente custom referenciado não encontrado: {aid}")

    passos_json = [
        {
            "id": str(p.get("id") or ""),
            "agente_id": str(p.get("agente_id") or ""),
            "rotulo": str(p.get("rotulo") or ""),
            "descricao": str(p.get("descricao") or ""),
        }
        for p in passos_fonte
    ]
    agora = datetime.now(timezone.utc)
    novo_pipeline_id = novo_id_custom_transcribrothers()
    ordem = await proxima_ordem_exibicao_pipeline_custom_transcribrothers(session)
    entradas_herdadas = normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
        pipeline_custom.entradas_aceitas_json,
        padrao=["video"],
    )
    if not pipeline_custom.entradas_aceitas_json:
        molde = obter_pipeline_catalogo_sistema_por_id_transcribrothers(copiado_de_raiz)
        if molde is not None:
            entradas_herdadas = list(molde.entradas_aceitas)
    pipeline_row = PipelineCustomTranscribrothers(
        id=novo_pipeline_id,
        copiado_de=copiado_de_raiz,
        titulo=f"{pipeline_custom.titulo} (cópia)",
        descricao=pipeline_custom.descricao,
        passos_json=passos_json,
        ordem_exibicao=ordem,
        entradas_aceitas_json=entradas_herdadas,
        created_at=agora,
        updated_at=agora,
    )
    session.add(pipeline_row)
    await session.commit()
    await session.refresh(pipeline_row)
    return pipeline_row


async def criar_pipeline_custom_a_partir_de_molde_transcribrothers(
    session: AsyncSession,
    fonte_id: str,
    *,
    titulo: str | None = None,
    descricao: str | None = None,
) -> PipelineCustomTranscribrothers:
    fonte_norm = fonte_id.strip()
    if not pipeline_custom_e_executavel_upload_transcribrothers(fonte_norm):
        raise ValueError(
            "fonte_id deve ser um molde executável inicial "
            f"(tutorial, notas, bug ou só transcrição): {fonte_norm!r}."
        )
    row = await duplicar_pipeline_catalogo_para_custom_transcribrothers(session, fonte_norm)
    titulo_norm = (titulo or "").strip()
    descricao_norm = descricao if descricao is not None else None
    if titulo_norm or descricao_norm is not None:
        return await atualizar_pipeline_custom_transcribrothers(
            session,
            row.id,
            titulo=titulo_norm or None,
            descricao=descricao_norm,
        )
    return row


async def reordenar_pipelines_custom_transcribrothers(
    session: AsyncSession,
    pipeline_ids_ordenados: list[str],
) -> None:
    existentes = await listar_pipelines_custom_transcribrothers(session)
    ids_existentes = {p.id for p in existentes}
    ids_solicitados = [i.strip() for i in pipeline_ids_ordenados if i.strip()]
    if set(ids_solicitados) != ids_existentes:
        raise ValueError(
            "pipeline_ids_ordenados deve listar exatamente todas as pipelines custom, sem faltantes nem extras."
        )
    if len(ids_solicitados) != len(set(ids_solicitados)):
        raise ValueError("pipeline_ids_ordenados contém IDs duplicados.")
    mapa = {p.id: p for p in existentes}
    agora = datetime.now(timezone.utc)
    for indice, pipeline_id in enumerate(ids_solicitados):
        row = mapa[pipeline_id]
        row.ordem_exibicao = indice
        row.updated_at = agora
    await session.commit()


async def atualizar_agente_custom_transcribrothers(
    session: AsyncSession,
    agente_id: str,
    *,
    rotulo: str | None = None,
    descricao: str | None = None,
    prompts_json: list[dict[str, Any]] | None = None,
    modelo_litellm: str | None = ...,  # type: ignore[assignment]
) -> AgenteCustomTranscribrothers:
    row = await obter_agente_custom_por_id_transcribrothers(session, agente_id)
    if row is None:
        raise ValueError(f"Agente custom não encontrado: {agente_id}")
    if rotulo is not None:
        row.rotulo = rotulo.strip()
    if descricao is not None:
        row.descricao = descricao
    if prompts_json is not None:
        row.prompts_json = prompts_json
    if modelo_litellm is not ...:
        row.modelo_litellm = (modelo_litellm or "").strip() or None
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    return row


async def atualizar_pipeline_custom_transcribrothers(
    session: AsyncSession,
    pipeline_id: str,
    *,
    titulo: str | None = None,
    descricao: str | None = None,
    entradas_aceitas: list[str] | None = None,
) -> PipelineCustomTranscribrothers:
    row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_id)
    if row is None:
        raise ValueError(f"Pipeline custom não encontrada: {pipeline_id}")
    if titulo is not None:
        row.titulo = titulo.strip()
    if descricao is not None:
        row.descricao = descricao
    if entradas_aceitas is not None:
        normalizadas = normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
            entradas_aceitas, padrao=[]
        )
        if not normalizadas:
            raise ValueError("entradas_aceitas deve incluir ao menos video ou audio.")
        # Pipelines derivadas de moldes só-vídeo (tutorial/notas/bug) não podem aceitar áudio nesta fatia.
        destino = mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(
            str(row.copiado_de or "")
        )
        if destino in {"gerar_tutorial", "notas_proposta_funcionalidade", "reproducao_bug"}:
            if "audio" in normalizadas:
                raise ValueError(
                    "Esta pipeline (tutorial, notas ou bug) só aceita entrada de vídeo nesta versão."
                )
            normalizadas = ["video"]
        row.entradas_aceitas_json = normalizadas
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    return row


async def agente_custom_referenciado_por_pipeline_transcribrothers(
    session: AsyncSession,
    agente_id: str,
) -> bool:
    pipelines = await listar_pipelines_custom_transcribrothers(session)
    for p in pipelines:
        for passo in p.passos_json or []:
            if str(passo.get("agente_id") or "") == agente_id:
                return True
    return False


async def excluir_agente_custom_transcribrothers(session: AsyncSession, agente_id: str) -> None:
    if await agente_custom_referenciado_por_pipeline_transcribrothers(session, agente_id):
        raise ValueError("Agente ainda referenciado por uma pipeline custom.")
    await session.execute(delete(AgenteCustomTranscribrothers).where(AgenteCustomTranscribrothers.id == agente_id))
    await session.commit()


async def excluir_pipeline_custom_transcribrothers(session: AsyncSession, pipeline_id: str) -> None:
    row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_id)
    if row is None:
        raise ValueError(f"Pipeline custom não encontrada: {pipeline_id}")
    agente_ids = {str(p.get("agente_id") or "") for p in (row.passos_json or [])}
    await session.execute(
        delete(PipelineCustomTranscribrothers).where(PipelineCustomTranscribrothers.id == pipeline_id)
    )
    await session.commit()
    for aid in agente_ids:
        if aid and not await agente_custom_referenciado_por_pipeline_transcribrothers(session, aid):
            await session.execute(
                delete(AgenteCustomTranscribrothers).where(AgenteCustomTranscribrothers.id == aid)
            )
    await session.commit()


async def carregar_agentes_custom_da_pipeline_transcribrothers(
    session: AsyncSession,
    pipeline_row: PipelineCustomTranscribrothers,
) -> list[AgenteCustomTranscribrothers]:
    ids = [str(p.get("agente_id") or "") for p in (pipeline_row.passos_json or [])]
    ids_unicos = list(dict.fromkeys(i for i in ids if i))
    resultado: list[AgenteCustomTranscribrothers] = []
    for aid in ids_unicos:
        row = await obter_agente_custom_por_id_transcribrothers(session, aid)
        if row is not None:
            resultado.append(row)
    return resultado


def pipeline_custom_e_executavel_upload_transcribrothers(copiado_de: str) -> bool:
    return copiado_de in PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS
