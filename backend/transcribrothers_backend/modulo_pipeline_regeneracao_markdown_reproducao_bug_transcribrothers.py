"""Regeneração do Markdown de reprodução de bug (FAB) via LiteLLM."""

from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers import (
    gerar_markdown_reproducao_bug_recbrothers_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
    CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
    FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_reproducao_bug_recbrothers_transcribrothers import (
    _carregar_cliques_reproducao_bug_do_job_opcional,
    _montar_pseudo_cliques_a_partir_de_rels_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    PipelineCanceladoPeloUsuarioTranscribrothers,
    _atualizar_job,
    _diretorio_trabalho_job,
    _snapshot_dict_para_transcricao_e_rels,
)
from transcribrothers_backend.modulo_util_job_steps_indicam_reproducao_bug_transcribrothers import (
    job_steps_indicam_reproducao_bug_transcribrothers,
)
from transcribrothers_backend.modulo_util_remover_referencias_imagens_assets_inexistentes_markdown_tutorial_transcribrothers import (
    remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)


async def executar_regeneracao_markdown_reproducao_bug_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    documento_autonomo_sem_video: bool = False,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    steps: dict[str, Any] = {}
    md_atual = ""
    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            job_steps = dict(job.steps_json or {})
            steps = {**job_steps}
            md_atual = (job.result_markdown or "").strip()

        if not job_steps_indicam_reproducao_bug_transcribrothers(steps):
            raise RuntimeError("Este job não é de reprodução de bug (destino_apos_transcricao).")

        snap = steps.get("regeneracao_tutorial_snapshot")
        if not isinstance(snap, dict):
            raise RuntimeError(
                "Snapshot de regeneração ausente. Conclua o pipeline de reprodução de bug antes de regenerar."
            )

        transcricao, rels = _snapshot_dict_para_transcricao_e_rels(snap)
        if not rels:
            raise RuntimeError("Snapshot sem frames (assets) para reprodução de bug.")

        cliques = _carregar_cliques_reproducao_bug_do_job_opcional(work)
        sem_json_cliques = bool(steps.get("reproducao_bug_sem_json_cliques")) or not cliques
        if sem_json_cliques:
            cliques = _montar_pseudo_cliques_a_partir_de_rels_transcribrothers(rels)
        assets_dir = work / "assets_exportados_para_markdown"
        for _t, rel in rels:
            nome = rel.split("/")[-1]
            if not nome or not (assets_dir / nome).is_file():
                raise RuntimeError(
                    f"Imagem do roteiro não encontrada no servidor (esperado em assets): {nome}"
                )

        api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(
            configuracao
        )
        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
            configuracao
        )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "regenerando_markdown_reproducao_bug_litellm"
        steps["regeneracao_apenas_markdown"] = True
        steps["regeneracao_reproducao_bug"] = True
        steps["regeneracao_instrucoes_usadas"] = bool((instrucoes_revisao_humana or "").strip())
        steps["regeneracao_reproducao_bug_documento_autonomo_sem_video"] = bool(documento_autonomo_sem_video)
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps.pop("regeneracao_tutorial_aplicada_em", None)

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
            steps=steps,
        )

        md = await gerar_markdown_reproducao_bug_recbrothers_com_litellm_transcribrothers(
            cliques=cliques,
            transcricao=transcricao,
            caminhos_frames_rel_job=rels,
            modelo=modelo_litellm.strip(),
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            diretorio_assets_absoluto=assets_dir,
            steps_para_log_decisoes_ia=steps,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            markdown_atual_para_contexto=md_atual if md_atual else None,
            documento_autonomo_sem_video=documento_autonomo_sem_video,
            sem_json_cliques_recbrothers=sem_json_cliques,
            log_etapa_geracao_tutorial="regeneracao_reproducao_bug_markdown",
        )

        md, _linhas_removidas = remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers(
            md or "",
            assets_dir,
        )
        if _linhas_removidas > 0:
            steps["regeneracao_linhas_imagem_assets_inexistentes_removidas"] = int(_linhas_removidas)

        md_proposto = (md or "").strip()
        if not md_proposto:
            raise RuntimeError("Regeneração devolveu Markdown vazio.")

        preview_blob: dict[str, Any] = {
            "markdown_antes": md_atual,
            "markdown_depois": md_proposto,
            "markdown_completo_proposto": md_proposto,
            "instrucoes_usadas": (instrucoes_revisao_humana or "").strip(),
            "instrucoes_pedido_original": (instrucoes_revisao_humana or "").strip(),
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "reproducao_bug": True,
            "documento_autonomo_sem_video": bool(documento_autonomo_sem_video),
        }
        steps[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS] = (
            preview_blob
        )
        steps["pipeline_fase"] = FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
            steps=steps,
        )
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        steps["pipeline_fase"] = "cancelado_pelo_usuario"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.cancelled,
            error="Cancelado pelo usuário.",
            steps=steps,
        )
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        msg_curta = str(e).strip() or repr(e)
        steps_com_diagnostico = {
            **steps,
            "error_traceback": tb[:32000],
            "error_type": type(e).__name__,
        }
        texto_erro_ui = (
            f"{type(e).__name__}: {msg_curta}\n\n"
            f"--- traceback (servidor; copie para o suporte) ---\n{tb}"
        )
        if len(texto_erro_ui) > 65000:
            texto_erro_ui = texto_erro_ui[:65000] + "\n...[truncado]"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui,
            steps=steps_com_diagnostico,
        )


def agendar_regeneracao_markdown_reproducao_bug_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    documento_autonomo_sem_video: bool = False,
) -> None:
    asyncio.create_task(
        executar_regeneracao_markdown_reproducao_bug_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            modelo_litellm=modelo_litellm,
            documento_autonomo_sem_video=documento_autonomo_sem_video,
        )
    )
