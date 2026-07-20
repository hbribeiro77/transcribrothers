"""Mescla catálogo estático do sistema com pipelines/agentes custom do SQLite."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    AgenteCustomTranscribrothers,
    PipelineCustomTranscribrothers,
)
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    AgenteCatalogoDocumentacaoTranscribrothers,
    PassoCatalogoPipelineTranscribrothers,
    PipelineCatalogoDocumentacaoTranscribrothers,
    PromptCatalogoPassoPipelineTranscribrothers,
    RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
    montar_resposta_catalogo_pipelines_disponiveis_documentacao_transcribrothers,
    normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers,
    obter_pipeline_catalogo_sistema_por_id_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_pipelines_e_agentes_custom_sqlite_transcribrothers import (
    listar_agentes_custom_transcribrothers,
    listar_pipelines_custom_transcribrothers,
    pipeline_custom_e_executavel_upload_transcribrothers,
)


def _agente_custom_row_para_catalogo_transcribrothers(
    row: AgenteCustomTranscribrothers,
    pipelines_ids: list[str],
) -> AgenteCatalogoDocumentacaoTranscribrothers:
    prompts_raw = row.prompts_json or []
    prompts: list[PromptCatalogoPassoPipelineTranscribrothers] = []
    for p in prompts_raw:
        if not isinstance(p, dict):
            continue
        try:
            prompts.append(PromptCatalogoPassoPipelineTranscribrothers.model_validate(p))
        except Exception:  # noqa: BLE001
            continue
    return AgenteCatalogoDocumentacaoTranscribrothers(
        id=row.id,
        rotulo=row.rotulo,
        descricao=row.descricao,
        handler_chave=row.handler_chave,
        origem="usuario",
        editavel=True,
        copiado_de=row.copiado_de,
        modelo_litellm=row.modelo_litellm,
        prompts=prompts,
        pipelines_ids=pipelines_ids,
    )


def _pipeline_custom_row_para_catalogo_transcribrothers(
    row: PipelineCustomTranscribrothers,
) -> PipelineCatalogoDocumentacaoTranscribrothers:
    passos: list[PassoCatalogoPipelineTranscribrothers] = []
    for p in row.passos_json or []:
        if not isinstance(p, dict):
            continue
        passos.append(
            PassoCatalogoPipelineTranscribrothers(
                id=str(p.get("id") or ""),
                agente_id=str(p.get("agente_id") or ""),
                rotulo=str(p.get("rotulo") or ""),
                descricao=str(p.get("descricao") or ""),
            )
        )
    padrao_entradas = ["video"]
    molde = obter_pipeline_catalogo_sistema_por_id_transcribrothers(str(row.copiado_de or ""))
    if molde is not None:
        padrao_entradas = list(molde.entradas_aceitas)
    entradas = normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
        row.entradas_aceitas_json,
        padrao=padrao_entradas,  # type: ignore[arg-type]
    )
    return PipelineCatalogoDocumentacaoTranscribrothers(
        id=row.id,
        titulo=row.titulo,
        descricao=row.descricao,
        origem="usuario",
        editavel=True,
        executavel=pipeline_custom_e_executavel_upload_transcribrothers(str(row.copiado_de or "")),
        copiado_de=row.copiado_de,
        ordem=int(row.ordem_exibicao),
        entradas_aceitas=entradas,
        passos=passos,
    )


async def montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(
    session: AsyncSession,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    base = montar_resposta_catalogo_pipelines_disponiveis_documentacao_transcribrothers()
    custom_pipelines_rows = await listar_pipelines_custom_transcribrothers(session)
    custom_agentes_rows = await listar_agentes_custom_transcribrothers(session)

    uso_agente_em_pipeline: dict[str, list[str]] = {}
    pipelines_custom_catalogo: list[PipelineCatalogoDocumentacaoTranscribrothers] = []
    for row in custom_pipelines_rows:
        cat = _pipeline_custom_row_para_catalogo_transcribrothers(row)
        pipelines_custom_catalogo.append(cat)
        for passo in cat.passos:
            uso_agente_em_pipeline.setdefault(passo.agente_id, [])
            if cat.id not in uso_agente_em_pipeline[passo.agente_id]:
                uso_agente_em_pipeline[passo.agente_id].append(cat.id)

    agentes_custom_catalogo = [
        _agente_custom_row_para_catalogo_transcribrothers(
            row,
            uso_agente_em_pipeline.get(row.id, []),
        )
        for row in custom_agentes_rows
    ]

    return RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers(
        pipeline_identificador=base.pipeline_identificador,
        agentes=list(base.agentes) + agentes_custom_catalogo,
        pipelines=list(base.pipelines) + pipelines_custom_catalogo,
    )
