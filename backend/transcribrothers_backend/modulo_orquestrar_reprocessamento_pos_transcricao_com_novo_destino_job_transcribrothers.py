"""Orquestra 'gerar outro formato' em job concluído — reprocessa pós-transcrição sem retranscrever."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers,
)
from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
    ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_NOTAS_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_REPRODUCAO_BUG_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
    inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_pipelines_e_agentes_custom_sqlite_transcribrothers import (
    carregar_agentes_custom_da_pipeline_transcribrothers,
    obter_pipeline_custom_por_id_transcribrothers,
    pipeline_custom_e_executavel_upload_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
    snapshot_transcricao_disponivel_no_work_transcribrothers,
)

DESTINOS_GERAR_OUTRO_FORMATO_VALIDOS_TRANSCRIBROTHERS = frozenset(
    {"gerar_tutorial", "notas_proposta_funcionalidade", "reproducao_bug"},
)

_CHAVES_STEPS_REMOVER_AO_TROCAR_DESTINO_POS_TRANSCRICAO_TRANSCRIBROTHERS = frozenset(
    {
        "regeneracao_tutorial_snapshot",
        "tutorial_rascunho_sem_imagens_ok",
        "rascunho_notas_reutilizado_retry",
        "notas_proposta_rascunho_sem_imagens_ok",
        "regeneracao_apenas_markdown",
        "regeneracao_reproducao_bug",
        "regeneracao_notas_proposta",
        "verificacao_sustentacao_tutorial",
        "verificacao_sustentacao_notas_proposta",
        "verificacao_imagens_duplicadas_tutorial",
        "frames_capturados",
        "frames_candidatos_rascunho_total",
        "captura_frame_indice",
        "captura_frames_total",
        "captura_frame_timestamp_segundos",
        "geracao_tutorial_litellm_total_imagens",
        "pipeline_custom_id",
        "pipeline_custom_copiado_de",
        "pipeline_custom_titulo",
        "pipeline_custom_descricao",
        "pipeline_custom_passos",
        "pipeline_custom_agentes",
    }
)


class ErroGerarOutroFormatoJobTranscribrothers(ValueError):
    """Erro de validação para POST /api/jobs/{id}/gerar-outro-formato."""


def _origem_backup_por_destino_transcribrothers(destino: str) -> str:
    if destino == "notas_proposta_funcionalidade":
        return ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_NOTAS_TRANSCRIBROTHERS
    if destino == "reproducao_bug":
        return ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_REPRODUCAO_BUG_TRANSCRIBROTHERS
    return ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_TUTORIAL_TRANSCRIBROTHERS


def job_possui_video_entrada_no_work_transcribrothers(work: Path) -> bool:
    return any(p.is_file() for p in work.glob("video_entrada_arquivo_local.*"))


def job_possui_audio_entrada_no_work_transcribrothers(work: Path) -> bool:
    return any(p.is_file() for p in work.glob("audio_entrada_arquivo_local.*"))


def job_pode_gerar_outro_formato_pos_transcricao_transcribrothers(
    *,
    job: JobPipelineTranscribrothers,
    work: Path,
) -> bool:
    if job.status != StatusJobTranscribrothers.completed.value:
        return False
    steps = job.steps_json or {}
    if steps.get("destino_apos_transcricao") == "projeto_em_branco":
        return False
    # Com snapshot: elegível (sem mídia só notas — validado em validar_job_pode_gerar_outro_formato).
    return snapshot_transcricao_disponivel_no_work_transcribrothers(work)


def validar_job_pode_gerar_outro_formato_transcribrothers(
    *,
    job: JobPipelineTranscribrothers,
    work: Path,
    novo_destino: str,
) -> None:
    if job.status != StatusJobTranscribrothers.completed.value:
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Só é possível gerar outro formato em jobs concluídos (status completed)."
        )
    steps = dict(job.steps_json or {})
    destino_atual = str(steps.get("destino_apos_transcricao") or "").strip()
    if destino_atual == "projeto_em_branco":
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Projetos em branco não possuem transcrição para reutilizar."
        )
    if novo_destino not in DESTINOS_GERAR_OUTRO_FORMATO_VALIDOS_TRANSCRIBROTHERS:
        raise ErroGerarOutroFormatoJobTranscribrothers(
            f"destino_apos_transcricao inválido: {novo_destino!r}. "
            f"Valores aceitos: {', '.join(sorted(DESTINOS_GERAR_OUTRO_FORMATO_VALIDOS_TRANSCRIBROTHERS))}."
        )
    tem_video = job_possui_video_entrada_no_work_transcribrothers(work)
    tem_audio = job_possui_audio_entrada_no_work_transcribrothers(work)
    tipo = str(steps.get("tipo_entrada_midia") or "").strip()
    sem_midia = not tem_video and not tem_audio
    if not snapshot_transcricao_disponivel_no_work_transcribrothers(work):
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Transcrição finalizada não encontrada neste job. "
            "Só é possível gerar outro formato após uma transcrição concluída com sucesso."
        )
    if sem_midia and novo_destino != "notas_proposta_funcionalidade":
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Jobs sem vídeo/áudio (ex.: transcrição importada) só podem gerar notas de proposta "
            "nesta versão (tutorial e bug exigem vídeo)."
        )
    if (tipo == "audio" or (tem_audio and not tem_video)) and novo_destino != "notas_proposta_funcionalidade":
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Jobs iniciados só com áudio só podem gerar notas de proposta nesta versão "
            "(tutorial e bug exigem vídeo)."
        )
    if not tem_video and novo_destino in {"gerar_tutorial", "reproducao_bug"}:
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Vídeo do job não encontrado; tutorial e reprodução de bug exigem vídeo."
        )


async def resolver_snapshot_pipeline_custom_para_gerar_outro_formato_transcribrothers(
    session: AsyncSession,
    pipeline_custom_id: str | None,
    destino_solicitado: str,
) -> tuple[str, dict[str, Any] | None]:
    """Retorna (destino_efetivo, snapshot_pipeline_custom ou None)."""
    norm = (pipeline_custom_id or "").strip()
    if not norm:
        return destino_solicitado, None
    pipeline_row = await obter_pipeline_custom_por_id_transcribrothers(session, norm)
    if pipeline_row is None:
        raise ErroGerarOutroFormatoJobTranscribrothers(f"pipeline_custom_id inválido: {norm!r}.")
    copiado_de = str(pipeline_row.copiado_de or "")
    if not pipeline_custom_e_executavel_upload_transcribrothers(copiado_de):
        raise ErroGerarOutroFormatoJobTranscribrothers(
            "Esta pipeline custom não pode ser usada aqui (fluxo 2). "
            "Escolha uma cópia de tutorial, notas ou bug."
        )
    destino_mapeado = mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(copiado_de)
    if not destino_mapeado:
        raise ErroGerarOutroFormatoJobTranscribrothers(
            f"Pipeline custom sem destino mapeado: {copiado_de!r}."
        )
    agentes_rows = await carregar_agentes_custom_da_pipeline_transcribrothers(session, pipeline_row)
    snapshot = montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers(
        pipeline_row,
        agentes_rows,
    )
    return destino_mapeado, snapshot


def preparar_steps_para_reprocessamento_pos_transcricao_transcribrothers(
    steps: dict[str, Any],
    *,
    destino_anterior: str,
    novo_destino: str,
    snapshot_pipeline_custom: dict[str, Any] | None,
    modelo_litellm: str | None = None,
) -> dict[str, Any]:
    out = dict(steps)
    for chave in _CHAVES_STEPS_REMOVER_AO_TROCAR_DESTINO_POS_TRANSCRICAO_TRANSCRIBROTHERS:
        out.pop(chave, None)
    for chave in list(out.keys()):
        if chave.startswith("verificacao_") and chave.endswith("_concluida"):
            out.pop(chave, None)
        if chave.endswith("_concluida") and chave.startswith(("notas_proposta_", "reproducao_bug_", "regeneracao_")):
            out.pop(chave, None)
    out["reprocessamento_pos_transcricao_apenas"] = True
    out["reprocessamento_destino_anterior"] = destino_anterior
    out["reprocessamento_iniciado_em"] = datetime.now(timezone.utc).isoformat()
    out["destino_apos_transcricao"] = novo_destino
    out["pipeline_fase"] = "reprocessamento_pos_transcricao_agendado"
    if modelo_litellm:
        out["litellm_model"] = modelo_litellm.strip()
    if snapshot_pipeline_custom:
        out.update(snapshot_pipeline_custom)
    else:
        out.pop("pipeline_custom_id", None)
        out.pop("pipeline_custom_copiado_de", None)
        out.pop("pipeline_custom_titulo", None)
        out.pop("pipeline_custom_descricao", None)
        out.pop("pipeline_custom_passos", None)
        out.pop("pipeline_custom_agentes", None)
    return out


async def gravar_backup_markdown_antes_trocar_destino_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    job_id: str,
    markdown: str | None,
    destino_anterior: str,
) -> None:
    texto = (markdown or "").strip()
    if not texto:
        return
    origem = _origem_backup_por_destino_transcribrothers(destino_anterior)
    await inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers(
        session_factory,
        job_id=job_id,
        conteudo_markdown=texto,
        origem=origem,
    )


async def aplicar_gerar_outro_formato_no_job_transcribrothers(
    session: AsyncSession,
    *,
    job: JobPipelineTranscribrothers,
    novo_destino: str,
    snapshot_pipeline_custom: dict[str, Any] | None,
    modelo_litellm: str | None,
    session_factory: async_sessionmaker[AsyncSession],
) -> JobPipelineTranscribrothers:
    steps_antigos = dict(job.steps_json or {})
    destino_anterior = str(steps_antigos.get("destino_apos_transcricao") or "gerar_tutorial").strip()
    await gravar_backup_markdown_antes_trocar_destino_transcribrothers(
        session_factory,
        job_id=job.id,
        markdown=job.result_markdown,
        destino_anterior=destino_anterior,
    )
    job.steps_json = preparar_steps_para_reprocessamento_pos_transcricao_transcribrothers(
        steps_antigos,
        destino_anterior=destino_anterior,
        novo_destino=novo_destino,
        snapshot_pipeline_custom=snapshot_pipeline_custom,
        modelo_litellm=modelo_litellm,
    )
    job.status = StatusJobTranscribrothers.pending.value
    job.result_markdown = None
    job.error_message = None
    await session.commit()
    await session.refresh(job)
    return job
