"""Cria job a partir de transcrição importada (snapshot + so_transcricao ou agenda notas)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers,
)
from transcribrothers_backend.modulo_orquestrar_reprocessamento_pos_transcricao_com_novo_destino_job_transcribrothers import (
    preparar_steps_para_reprocessamento_pos_transcricao_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_pipelines_e_agentes_custom_sqlite_transcribrothers import (
    carregar_agentes_custom_da_pipeline_transcribrothers,
    obter_pipeline_custom_por_id_transcribrothers,
    pipeline_custom_e_executavel_upload_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_so_transcricao_midia_entrada_transcribrothers import (
    montar_markdown_resultado_so_transcricao_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_util_parsear_arquivo_ou_texto_transcricao_importada_srt_vtt_txt_transcribrothers import (
    parsear_arquivo_ou_texto_transcricao_importada_transcribrothers,
)

DESTINOS_IMPORTAR_TRANSCRICAO_PRONTA_VALIDOS_TRANSCRIBROTHERS = frozenset(
    {"so_transcricao", "notas_proposta_funcionalidade"}
)


class ErroImportarTranscricaoProntaTranscribrothers(ValueError):
    pass


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


async def resolver_destino_e_snapshot_pipeline_custom_importar_transcricao_transcribrothers(
    session: AsyncSession,
    *,
    destino_solicitado: str,
    pipeline_custom_id: str | None,
) -> tuple[str, dict[str, Any] | None]:
    norm = (pipeline_custom_id or "").strip()
    if not norm:
        if destino_solicitado not in DESTINOS_IMPORTAR_TRANSCRICAO_PRONTA_VALIDOS_TRANSCRIBROTHERS:
            raise ErroImportarTranscricaoProntaTranscribrothers(
                f"destino_apos_transcricao inválido: {destino_solicitado!r}. "
                f"Nesta versão use: {', '.join(sorted(DESTINOS_IMPORTAR_TRANSCRICAO_PRONTA_VALIDOS_TRANSCRIBROTHERS))}."
            )
        return destino_solicitado, None
    pipeline_row = await obter_pipeline_custom_por_id_transcribrothers(session, norm)
    if pipeline_row is None:
        raise ErroImportarTranscricaoProntaTranscribrothers(f"pipeline_custom_id inválido: {norm!r}.")
    copiado_de = str(pipeline_row.copiado_de or "")
    if not pipeline_custom_e_executavel_upload_transcribrothers(copiado_de):
        raise ErroImportarTranscricaoProntaTranscribrothers(
            "Esta pipeline custom não pode ser usada na importação de transcrição."
        )
    destino_mapeado = mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(copiado_de)
    if destino_mapeado != "notas_proposta_funcionalidade":
        raise ErroImportarTranscricaoProntaTranscribrothers(
            "Sem mídia, só é possível importar para «Só transcrição» ou notas de proposta "
            "(use uma custom copiada do molde de notas)."
        )
    agentes_rows = await carregar_agentes_custom_da_pipeline_transcribrothers(session, pipeline_row)
    snapshot = montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers(
        pipeline_row,
        agentes_rows,
    )
    return destino_mapeado, snapshot


def montar_steps_base_transcricao_importada_transcribrothers(
    *,
    transcricao: ResultadoTranscricaoComSegmentos,
    nome_arquivo_origem: str | None,
    modelo_litellm: str | None,
) -> dict[str, Any]:
    steps: dict[str, Any] = {
        "source": OrigemEntradaJobTranscribrothers.transcricao_importada,
        "transcricao_importada": True,
        "transcricao_snapshot_finalizada_em_disco": True,
        "transcricao_segmentos": len(transcricao.segmentos),
        "upload_ok": True,
        "audio_ok": True,
        "pipeline_fase": "so_transcricao_concluida",
        "destino_apos_transcricao": "so_transcricao",
        "pode_gerar_outro_formato": True,
    }
    if nome_arquivo_origem:
        steps["original_filename"] = nome_arquivo_origem
    if modelo_litellm and modelo_litellm.strip():
        steps["litellm_model"] = modelo_litellm.strip()
    if transcricao.idioma_detectado:
        steps["idioma_detectado"] = transcricao.idioma_detectado
    return steps


async def criar_job_a_partir_transcricao_importada_pronta_transcribrothers(
    *,
    data_dir: Path,
    session_factory: async_sessionmaker[AsyncSession],
    texto: str | None,
    nome_arquivo: str | None,
    conteudo_arquivo: bytes | None,
    destino_solicitado: str,
    pipeline_custom_id: str | None = None,
    modelo_litellm: str | None = None,
) -> tuple[JobPipelineTranscribrothers, bool]:
    """
    Retorna (job, deve_agendar_pipeline).
    Se destino for notas, job fica pending com reprocessamento_pos_transcricao_apenas.
    """
    transcricao = parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(
        texto=texto,
        nome_arquivo=nome_arquivo,
        conteudo_arquivo=conteudo_arquivo,
    )
    job_id = novo_id_job()
    work = _diretorio_trabalho_job(data_dir, job_id)
    work.mkdir(parents=True, exist_ok=True)
    (work / "assets_exportados_para_markdown").mkdir(parents=True, exist_ok=True)

    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(work, transcricao)
    md = montar_markdown_resultado_so_transcricao_transcribrothers(
        texto_completo=transcricao.texto_completo,
        segmentos=list(transcricao.segmentos),
    )

    async with session_factory() as session:
        destino_efetivo, snapshot_custom = (
            await resolver_destino_e_snapshot_pipeline_custom_importar_transcricao_transcribrothers(
                session,
                destino_solicitado=destino_solicitado,
                pipeline_custom_id=pipeline_custom_id,
            )
        )
        steps = montar_steps_base_transcricao_importada_transcribrothers(
            transcricao=transcricao,
            nome_arquivo_origem=nome_arquivo,
            modelo_litellm=modelo_litellm,
        )
        deve_agendar = False
        status = StatusJobTranscribrothers.completed
        result_markdown: str | None = md

        if destino_efetivo == "notas_proposta_funcionalidade":
            steps = preparar_steps_para_reprocessamento_pos_transcricao_transcribrothers(
                steps,
                destino_anterior="so_transcricao",
                novo_destino="notas_proposta_funcionalidade",
                snapshot_pipeline_custom=snapshot_custom,
                modelo_litellm=modelo_litellm,
            )
            steps["transcricao_importada"] = True
            steps["transcricao_snapshot_finalizada_em_disco"] = True
            status = StatusJobTranscribrothers.pending
            result_markdown = None
            deve_agendar = True
        else:
            steps["destino_apos_transcricao"] = "so_transcricao"

        row = JobPipelineTranscribrothers(
            id=job_id,
            status=status.value,
            source_kind=OrigemEntradaJobTranscribrothers.transcricao_importada,
            drive_url=(
                f"Transcrição importada: {nome_arquivo}"
                if nome_arquivo
                else "Transcrição importada (texto colado)"
            ),
            file_id="-",
            error_message=None,
            result_markdown=result_markdown,
            steps_json=steps,
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row, deve_agendar
