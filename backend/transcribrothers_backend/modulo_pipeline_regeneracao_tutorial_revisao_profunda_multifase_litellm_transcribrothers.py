from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import StatusJobTranscribrothers
from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    _serializar_segmentos,
    gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
    ItemTopicoPlanoRevisaoProfundaTranscribrothers,
    montar_schema_json_exemplo_para_prompt_analista_transcribrothers,
    parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    PipelineCanceladoPeloUsuarioTranscribrothers,
    _atualizar_job,
    _instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)


def _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id: str) -> None:
    if cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id):
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        raise PipelineCanceladoPeloUsuarioTranscribrothers()


def _montar_payload_json_transcricao_e_frames_para_revisao_profunda_transcribrothers(
    transcricao: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
) -> dict[str, Any]:
    linhas_frames = [{"t_segundos": t, "arquivo_relativo_markdown": rel} for t, rel in rels]
    return {
        "texto_completo": transcricao.texto_completo,
        "idioma": transcricao.idioma_detectado,
        "segmentos": _serializar_segmentos(transcricao.segmentos),
        "frames": linhas_frames,
    }


def _ordenar_e_limitar_topicos_plano_revisao_profunda_transcribrothers(
    topicos: list[ItemTopicoPlanoRevisaoProfundaTranscribrothers],
    max_n: int,
) -> list[ItemTopicoPlanoRevisaoProfundaTranscribrothers]:
    ordenados = sorted(
        topicos,
        key=lambda t: (t.prioridade, t.id, t.titulo_secao),
    )
    if max_n <= 0:
        return []
    return ordenados[:max_n]


async def gerar_markdown_tutorial_via_revisao_profunda_multifase_litellm_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps_mutavel: dict[str, Any],
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    assets_dir: Path,
    md_atual_inicial: str,
    rels_anexo_regeneracao: list[tuple[float, str]],
    usar_visao_regeneracao: bool,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> str:
    """
    Analista (JSON) → workers sequenciais (Markdown completo) → consolidação com o mesmo gerador multimodal
    usado na regeneração simples.
    """
    max_topicos = int(configuracao.revisao_profunda_max_topicos)
    max_topicos = max(1, min(32, max_topicos))

    steps_mutavel["revisao_profunda_multifase"] = True
    steps_mutavel["revisao_profunda_max_topicos"] = max_topicos

    _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)

    payload_transcricao = _montar_payload_json_transcricao_e_frames_para_revisao_profunda_transcribrothers(
        transcricao_corta,
        rels,
    )
    payload_txt = json.dumps(payload_transcricao, ensure_ascii=False, indent=2)
    schema_exemplo = montar_schema_json_exemplo_para_prompt_analista_transcribrothers()

    steps_mutavel["pipeline_fase"] = "revisao_profunda_analista_litellm"
    steps_mutavel.pop("revisao_profunda_indice", None)
    steps_mutavel.pop("revisao_profunda_total", None)
    await _atualizar_job(session_factory, job_id, steps=dict(steps_mutavel))

    _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)

    user_analista = (
        "Schema JSON esperado (exemplo ilustrativo — siga a forma, não copie o conteúdo):\n"
        f"{schema_exemplo}\n\n"
        "---\n"
        "Transcrição e frames (JSON):\n"
        f"{payload_txt}\n\n"
        "---\n"
        "## Tutorial Markdown actual\n\n"
        f"{md_atual_inicial or '(vazio)'}\n"
    )

    texto_analista = await litellm_chat_completions_texto_simples_transcribrothers(
        modelo=modelo_litellm,
        api_key=api_key_litellm,
        api_base=api_base_litellm,
        httpx_verify=http_verify_litellm,
        mensagens=[
            {"role": "system", "content": SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS},
            {"role": "user", "content": user_analista},
        ],
        temperature=0.2,
        usar_response_format_json_object=bool(
            configuracao.transcricao_litellm_chat_json_object_response_format
        ),
        httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
        httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
        steps_para_log_decisoes_ia=steps_mutavel,
        log_etapa="revisao_profunda_analista_plano",
        log_resumo_pedido="Plano de revisão profunda",
    )

    _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)

    try:
        plano, plano_serial = parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers(texto_analista)
    except ValueError as e:
        trecho = (texto_analista or "")[:4000]
        steps_mutavel["revisao_profunda_analista_resposta_bruta_trunc"] = trecho
        steps_mutavel["pipeline_fase"] = "revisao_profunda_analista_erro_parse"
        await _atualizar_job(session_factory, job_id, steps=dict(steps_mutavel))
        raise ValueError(str(e)) from e

    steps_mutavel["revisao_profunda_plano_json"] = plano_serial
    steps_mutavel["pipeline_fase"] = "revisao_profunda_plano_concluido"
    await _atualizar_job(session_factory, job_id, steps=dict(steps_mutavel))

    topicos_trabalho = _ordenar_e_limitar_topicos_plano_revisao_profunda_transcribrothers(
        list(plano.topicos),
        max_topicos,
    )

    md_corrente = md_atual_inicial
    total = len(topicos_trabalho)
    steps_mutavel["revisao_profunda_total"] = total

    for indice, item in enumerate(topicos_trabalho):
        _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)
        steps_mutavel["pipeline_fase"] = "revisao_profunda_worker_topico"
        steps_mutavel["revisao_profunda_indice"] = indice + 1
        steps_mutavel["revisao_profunda_total"] = total
        await _atualizar_job(session_factory, job_id, steps=dict(steps_mutavel))

        item_json = json.dumps(item.model_dump(), ensure_ascii=False, indent=2)
        user_worker = (
            f"item_plano_json:\n{item_json}\n\n"
            "---\n"
            "transcricao_e_frames_json:\n"
            f"{payload_txt}\n\n"
            "---\n"
            "## Tutorial Markdown completo a editar\n\n"
            f"{md_corrente}\n"
        )
        resposta_worker = await litellm_chat_completions_texto_simples_transcribrothers(
            modelo=modelo_litellm,
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            mensagens=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
                },
                {"role": "user", "content": user_worker},
            ],
            temperature=0.3,
            usar_response_format_json_object=False,
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            steps_para_log_decisoes_ia=steps_mutavel,
            log_etapa="revisao_profunda_worker_topico",
            log_resumo_pedido=f"Tópico {indice + 1}/{total}: {item.titulo_secao}"[:300],
            log_metadados={"topico_id": item.id},
            log_incluir_detalhe_resposta=False,
        )
        if not resposta_worker.strip() or len(resposta_worker.strip()) < 40:
            raise RuntimeError(
                "O modelo do worker devolveu Markdown demasiado curto ou vazio. "
                f"Pré-visualização: {(resposta_worker or '')[:400]!r}"
            )
        md_corrente = resposta_worker.strip()

    _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)

    steps_mutavel["pipeline_fase"] = "revisao_profunda_editor_final"
    steps_mutavel.pop("revisao_profunda_indice", None)
    steps_mutavel["revisao_profunda_total"] = total
    await _atualizar_job(session_factory, job_id, steps=dict(steps_mutavel))

    resumo_plano_compacto = json.dumps(
        [
            {
                "id": t.id,
                "titulo_secao": t.titulo_secao,
                "lacunas": t.lacunas[:6],
                "prioridade": t.prioridade,
            }
            for t in topicos_trabalho
        ],
        ensure_ascii=False,
    )
    partes_instr = [
        INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS,
        "",
        "Plano executado (resumo):",
        resumo_plano_compacto,
    ]
    hum = (instrucoes_revisao_humana or "").strip()
    if hum:
        partes_instr.extend(["", "Instruções adicionais do revisor humano:", hum])
    instrucoes_editor = "\n".join(partes_instr)

    _levantar_se_cancelamento_revisao_profunda_transcribrothers(job_id)

    md_final = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
        transcricao=transcricao_corta,
        caminhos_frames_rel_job=rels,
        modelo=modelo_litellm.strip(),
        api_key=api_key_litellm,
        api_base=api_base_litellm,
        httpx_verify=http_verify_litellm,
        instrucoes_revisao_humana=instrucoes_editor,
        httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
        httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
        diretorio_assets_absoluto=assets_dir if usar_visao_regeneracao else None,
        enviar_screenshots_png_como_imagens_multimodais=usar_visao_regeneracao,
        markdown_para_decidir_quais_pngs_anexar=None,
        rels_png_anexo_ja_resolvidos=rels_anexo_regeneracao if usar_visao_regeneracao else None,
        bloco_markdown_tutorial_atual_para_contexto_em_revisao=md_corrente if md_corrente else None,
        instrucao_prefixo_litellm_custom=_instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(
            steps_mutavel
        ),
        steps_para_log_decisoes_ia=steps_mutavel,
        log_etapa_geracao_tutorial="revisao_profunda_editor_final",
    )

    steps_mutavel.pop("revisao_profunda_indice", None)
    steps_mutavel["revisao_profunda_total"] = total
    return md_final.strip()
