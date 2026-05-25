from __future__ import annotations

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
from transcribrothers_backend.modulo_cliente_litellm_regeneracao_secao_markdown_tutorial_transcribrothers import (
    regenerar_markdown_secao_tutorial_com_litellm_transcribrothers,
    regenerar_markdown_zona_escopo_secao_tutorial_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
    ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    mesclar_corpo_regiao_editada_no_markdown_completo_tutorial_transcribrothers,
    mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers,
    preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers,
    secao_sintetica_para_verificacao_redundancia_prefacio_markdown_transcribrothers,
    validar_corpo_secao_apos_edicao_escopada_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    PipelineCanceladoPeloUsuarioTranscribrothers,
    _atualizar_job,
    _diretorio_trabalho_job,
    _snapshot_dict_para_transcricao_e_rels,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers,
)

CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = (
    "regeneracao_secao_markdown_preview"
)


def _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id: str) -> None:
    if cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id):
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        raise PipelineCanceladoPeloUsuarioTranscribrothers()


async def executar_regeneracao_secao_markdown_tutorial_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    titulo_secao_heading: str | None,
    indice_secao: int | None,
    instrucoes_revisor: str,
    modelo_litellm: str,
    modo_escopo_edicao: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers = "trecho_local",
    trecho_ancora: str | None = None,
    interpretar_escopo_automaticamente: bool = False,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    steps: dict[str, Any] = {}
    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            job_steps = dict(job.steps_json or {})
            steps = {**job_steps}
            snap = job_steps.get("regeneracao_tutorial_snapshot")
            md_atual = (job.result_markdown or "").strip()

        if not md_atual:
            raise RuntimeError("Tutorial vazio: não há Markdown para editar por seção.")
        if not isinstance(snap, dict):
            raise RuntimeError("Snapshot de regeneração indisponível para este job.")

        api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
        http_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)

        interpretacao_escopo_blob: dict[str, Any] | None = None
        modo_efetivo = modo_escopo_edicao
        trecho_efetivo = (trecho_ancora or "").strip() or None
        instrucoes_efetivas = (instrucoes_revisor or "").strip()
        titulo_efetivo = titulo_secao_heading
        indice_efetivo = indice_secao

        from transcribrothers_backend.modulo_resolver_escopo_edicao_secao_markdown_validacao_e_refinamento_litellm_transcribrothers import (
            resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers,
        )

        steps["pipeline_fase"] = (
            "interpretando_escopo_pedido_edicao_secao_markdown_litellm"
            if interpretar_escopo_automaticamente
            else "validando_escopo_edicao_secao_markdown"
        )
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            steps=steps,
        )
        _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)

        async def _atualizar_fase_escopo(fase: str) -> None:
            steps["pipeline_fase"] = fase
            await _atualizar_job(
                session_factory,
                job_id,
                status=StatusJobTranscribrothers.generating_tutorial,
                steps=steps,
            )

        escopo_resolvido = await resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers(
            pedido_usuario=instrucoes_efetivas,
            markdown_tutorial=md_atual,
            configuracao=configuracao,
            modelo_litellm=modelo_litellm.strip(),
            api_key_litellm=api_key,
            api_base_litellm=api_base,
            http_verify_litellm=http_verify,
            interpretar_escopo_automaticamente=interpretar_escopo_automaticamente,
            modo_escopo_edicao=modo_efetivo,
            trecho_ancora=trecho_efetivo,
            titulo_secao_heading=titulo_efetivo,
            indice_secao=indice_efetivo,
            on_atualizar_fase_pipeline=_atualizar_fase_escopo,
            steps_para_log_decisoes_ia=steps,
        )

        interpretacao_escopo_blob = escopo_resolvido.interpretacao_blob
        steps["interpretacao_escopo_edicao_secao_markdown"] = interpretacao_escopo_blob
        steps["escopo_edicao_secao_resolvido"] = {
            "confirmado": True,
            "modo_escopo_edicao": escopo_resolvido.modo_escopo_edicao,
            "regiao_rotulo": escopo_resolvido.preparacao.regiao.rotulo_regiao,
            "explicacao_curta": interpretacao_escopo_blob.get("explicacao_curta", ""),
            "confianca": interpretacao_escopo_blob.get("confianca", "media"),
        }
        steps["pipeline_fase"] = "escopo_edicao_secao_confirmado"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            steps=steps,
        )
        _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)

        modo_efetivo = escopo_resolvido.modo_escopo_edicao
        trecho_efetivo = escopo_resolvido.trecho_ancora
        instrucoes_efetivas = escopo_resolvido.instrucoes_revisor
        titulo_efetivo = escopo_resolvido.titulo_secao_heading
        indice_efetivo = escopo_resolvido.indice_secao
        prep = escopo_resolvido.preparacao
        regiao = prep.regiao
        secao = regiao.secao
        corpo_secao = prep.corpo_regiao
        fatia_escopo = prep.fatia
        linha_heading_ctx = regiao.rotulo_regiao
        transcricao_corta, rels = _snapshot_dict_para_transcricao_e_rels(snap)
        from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
            job_steps_indicam_projeto_em_branco_transcribrothers,
        )
        from transcribrothers_backend.modulo_util_montar_rels_anexo_regeneracao_tutorial_com_disco_projeto_em_branco_transcribrothers import (
            montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers,
        )

        eh_projeto_em_branco = job_steps_indicam_projeto_em_branco_transcribrothers(steps)
        assets_dir = work / "assets_exportados_para_markdown"
        if eh_projeto_em_branco and assets_dir.is_dir():
            caminhos_ctx_fab = steps.get("regeneracao_fab_contexto_caminhos_assets_png")
            extras_ctx: list[str] = []
            if isinstance(caminhos_ctx_fab, list):
                extras_ctx = [str(x) for x in caminhos_ctx_fab if isinstance(x, str)]
            rels = montar_pool_rels_completos_disponiveis_regeneracao_tutorial_transcribrothers(
                markdown=md_atual,
                rels_snapshot=rels,
                assets_dir=assets_dir,
                caminhos_assets_png_contexto_fab_extra=extras_ctx,
                eh_projeto_em_branco=True,
            )
            textos_ctx_fab = steps.get("regeneracao_fab_contexto_textos")
            if isinstance(textos_ctx_fab, list):
                partes_txt = [str(x).strip() for x in textos_ctx_fab if isinstance(x, str) and str(x).strip()]
                if partes_txt:
                    instrucoes_efetivas = (
                        (instrucoes_efetivas or "").strip()
                        + "\n\n---\nContexto adicional anexado neste pedido:\n\n"
                        + "\n\n---\n".join(partes_txt)
                    )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "regenerando_secao_markdown_litellm"
        steps["regeneracao_secao_heading"] = regiao.rotulo_regiao
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
            steps=steps,
        )

        _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)

        titulos_outras_secoes = [
            s.linha_heading
            for s in listar_secoes_markdown_nivel2_tutorial_transcribrothers(md_atual)
            if regiao.eh_prefacio or secao is None or s.indice != secao.indice
        ]

        zona_editavel_depois: str | None = None
        if modo_efetivo == "secao_inteira":
            if secao is None:
                raise RuntimeError("Seção «##» não resolvida para regeneração da seção inteira.")
            secao_nova = await regenerar_markdown_secao_tutorial_com_litellm_transcribrothers(
                markdown_secao_atual=corpo_secao,
                markdown_tutorial_completo=md_atual,
                linha_heading_secao=secao.linha_heading,
                instrucoes_revisor=instrucoes_efetivas,
                transcricao=transcricao_corta,
                rels_completos_snapshot=rels,
                diretorio_assets_absoluto=assets_dir if assets_dir.is_dir() else None,
                titulos_outras_secoes_markdown_nivel2=titulos_outras_secoes,
                modelo=modelo_litellm.strip(),
                api_key=api_key,
                api_base=api_base,
                httpx_verify=http_verify,
                httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                steps_para_log_decisoes_ia=steps,
            )
        else:
            zona_nova = await regenerar_markdown_zona_escopo_secao_tutorial_com_litellm_transcribrothers(
                markdown_secao_completa_para_contexto=corpo_secao,
                markdown_tutorial_completo=md_atual,
                linha_heading_secao=linha_heading_ctx,
                fatia=fatia_escopo,
                modo_escopo=modo_efetivo,
                instrucoes_revisor=instrucoes_efetivas,
                transcricao=transcricao_corta,
                rels_completos_snapshot=rels,
                diretorio_assets_absoluto=assets_dir if assets_dir.is_dir() else None,
                titulos_outras_secoes_markdown_nivel2=titulos_outras_secoes,
                modelo=modelo_litellm.strip(),
                api_key=api_key,
                api_base=api_base,
                httpx_verify=http_verify,
                httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                steps_para_log_decisoes_ia=steps,
            )
            corpo_mesclado = mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers(
                fatia_escopo,
                zona_nova,
                linha_heading_secao=None if regiao.eh_prefacio else (secao.linha_heading if secao else None),
            )
            if not regiao.eh_prefacio and secao is not None:
                validar_corpo_secao_apos_edicao_escopada_transcribrothers(corpo_mesclado, secao)
            zona_editavel_depois = zona_nova.strip()
            secao_nova = corpo_mesclado.strip()

        _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)

        from transcribrothers_backend.modulo_util_sanitizar_referencias_assets_png_markdown_contra_catalogo_frames_transcribrothers import (
            sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers,
        )

        secao_nova, ajustes_assets_png = sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers(
            secao_nova,
            rels,
        )

        if regiao.eh_prefacio:
            md_proposto = mesclar_corpo_regiao_editada_no_markdown_completo_tutorial_transcribrothers(
                md_atual,
                regiao,
                secao_nova,
            )
        else:
            if secao is None:
                raise RuntimeError("Seção «##» não resolvida para mesclar no tutorial.")
            md_proposto = validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers(
                md_atual, secao, secao_nova
            )

        secao_verificacao_redundancia = (
            secao_sintetica_para_verificacao_redundancia_prefacio_markdown_transcribrothers(regiao.fim_caractere)
            if regiao.eh_prefacio
            else secao
        )

        preview_blob: dict[str, Any] = {
            "titulo_secao_heading": regiao.rotulo_regiao,
            "indice_secao": secao.indice if secao is not None else -1,
            "regiao_prefacio_introducao": regiao.eh_prefacio,
            "secao_markdown_antes": corpo_secao,
            "secao_markdown_depois": secao_nova.strip(),
            "markdown_completo_proposto": md_proposto,
            "instrucoes_usadas": instrucoes_efetivas,
            "instrucoes_pedido_original": (instrucoes_revisor or "").strip(),
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "modo_escopo_edicao": modo_efetivo,
            "interpretacao_escopo_pedido": interpretacao_escopo_blob,
            "trecho_ancora_informado": (trecho_ancora or "").strip() or None,
            "trecho_ancora_resolvido": fatia_escopo.trecho_ancora_resolvido or None,
            "zona_editavel_antes": fatia_escopo.zona_editavel if modo_efetivo != "secao_inteira" else None,
            "zona_editavel_depois": zona_editavel_depois,
        }
        if ajustes_assets_png:
            preview_blob["assets_png_caminhos_corrigidos_automaticamente"] = ajustes_assets_png

        _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)

        from transcribrothers_backend.modulo_persistencia_runtime_config_verificacao_redundancia_secao_markdown_sqlite_transcribrothers import (
            resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers,
        )
        from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
            blob_verificacao_redundancia_secao_omitida_por_configuracao_transcribrothers,
            executar_verificacao_redundancia_secao_markdown_litellm_transcribrothers,
        )

        async with session_factory() as session:
            prefs_redundancia = (
                await resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers(
                    session,
                    configuracao,
                )
            )

        desativada_redundancia = prefs_redundancia.verificacao_desativada

        if desativada_redundancia:
            preview_blob["verificacao_redundancia_outras_secoes"] = (
                blob_verificacao_redundancia_secao_omitida_por_configuracao_transcribrothers()
            )
        else:
            steps["pipeline_fase"] = "verificacao_redundancia_secao_markdown_litellm"
            await _atualizar_job(
                session_factory,
                job_id,
                status=StatusJobTranscribrothers.generating_tutorial,
                steps=steps,
            )
            _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)
            if secao_verificacao_redundancia is None:
                raise RuntimeError("Região para verificação de redundância não resolvida.")
            ver_blob = await executar_verificacao_redundancia_secao_markdown_litellm_transcribrothers(
                configuracao=configuracao,
                markdown_completo_atual=md_atual,
                secao_em_edicao=secao_verificacao_redundancia,
                secao_markdown_proposta=secao_nova.strip(),
                instrucoes_revisor=instrucoes_efetivas,
                modelo_litellm=modelo_litellm.strip(),
                api_key_litellm=api_key,
                api_base_litellm=api_base,
                http_verify_litellm=http_verify,
                steps_para_log_decisoes_ia=steps,
            )
            steps["pipeline_fase"] = "verificacao_redundancia_secao_markdown_concluida"

            from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
                corrigir_secao_markdown_apos_verificacao_redundancia_litellm_transcribrothers,
                deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers,
                montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers,
            )
            from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
                _serializar_segmentos,
            )

            if (
                not regiao.eh_prefacio
                and secao is not None
                and deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
                    ver_blob,
                    correcao_automatica_habilitada=prefs_redundancia.correcao_automatica_habilitada,
                    correcao_automatica_incluir_classificacao_atencao=(
                        prefs_redundancia.correcao_automatica_incluir_classificacao_atencao
                    ),
                )
            ):
                preview_blob["verificacao_redundancia_outras_secoes_antes_correcao_automatica"] = ver_blob
                steps["pipeline_fase"] = "corrigindo_redundancia_secao_markdown_litellm"
                await _atualizar_job(
                    session_factory,
                    job_id,
                    status=StatusJobTranscribrothers.generating_tutorial,
                    steps=steps,
                )
                _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)
                max_por = max(
                    800, int(configuracao.verificacao_redundancia_secao_max_chars_corpo_outra_secao)
                )
                max_n = max(1, min(24, int(configuracao.verificacao_redundancia_secao_max_outras_secoes)))
                outras_payload, _ = montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers(
                    md_atual,
                    secao_verificacao_redundancia,
                    max_chars_por_secao=max_por,
                    max_secoes=max_n,
                )
                transcricao_ctx = {
                    "texto_completo_resumo": transcricao_corta.texto_completo[:6000],
                    "segmentos": _serializar_segmentos(transcricao_corta.segmentos[:40]),
                }
                secao_corrigida = await corrigir_secao_markdown_apos_verificacao_redundancia_litellm_transcribrothers(
                    configuracao=configuracao,
                    linha_heading_secao=secao.linha_heading,
                    secao_markdown_proposta=secao_nova.strip(),
                    verificacao_redundancia_blob=ver_blob,
                    outras_secoes_payload=outras_payload,
                    instrucoes_revisor=instrucoes_efetivas,
                    transcricao_resumo_json=transcricao_ctx,
                    modelo_litellm=modelo_litellm.strip(),
                    api_key_litellm=api_key,
                    api_base_litellm=api_base,
                    http_verify_litellm=http_verify,
                    steps_para_log_decisoes_ia=steps,
                )
                secao_nova = secao_corrigida
                md_proposto = validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers(
                    md_atual, secao, secao_nova
                )
                preview_blob["secao_markdown_depois_antes_correcao_automatica"] = preview_blob[
                    "secao_markdown_depois"
                ]
                preview_blob["secao_markdown_depois"] = secao_nova.strip()
                preview_blob["markdown_completo_proposto"] = md_proposto
                preview_blob["correcao_redundancia_automatica_aplicada"] = True
                preview_blob["correcao_redundancia_automatica_classificacao_disparo"] = ver_blob.get(
                    "classificacao_global"
                )
                steps["pipeline_fase"] = "verificacao_redundancia_secao_apos_correcao_automatica_litellm"
                await _atualizar_job(
                    session_factory,
                    job_id,
                    status=StatusJobTranscribrothers.generating_tutorial,
                    steps=steps,
                )
                _levantar_se_cancelamento_regeneracao_secao_transcribrothers(job_id)
                ver_pos = await executar_verificacao_redundancia_secao_markdown_litellm_transcribrothers(
                    configuracao=configuracao,
                    markdown_completo_atual=md_atual,
                    secao_em_edicao=secao,
                    secao_markdown_proposta=secao_nova.strip(),
                    instrucoes_revisor=instrucoes_efetivas,
                    modelo_litellm=modelo_litellm.strip(),
                    api_key_litellm=api_key,
                    api_base_litellm=api_base,
                    http_verify_litellm=http_verify,
                    steps_para_log_decisoes_ia=steps,
                )
                ver_pos["apos_correcao_automatica"] = True
                preview_blob["verificacao_redundancia_outras_secoes"] = ver_pos
                steps["pipeline_fase"] = "correcao_redundancia_secao_markdown_concluida"
            else:
                preview_blob["verificacao_redundancia_outras_secoes"] = ver_blob

        steps[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS] = preview_blob
        steps["pipeline_fase"] = "regeneracao_secao_markdown_preview_pronta"
        steps.pop("regeneracao_secao_heading", None)

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
            steps=steps,
        )
    except PipelineCanceladoPeloUsuarioTranscribrothers:
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
        texto_erro_ui = f"{type(e).__name__}: {msg_curta}\n\n--- traceback ---\n{tb}"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui[:65000],
            steps=steps_com_diagnostico,
        )


def agendar_regeneracao_secao_markdown_tutorial_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    titulo_secao_heading: str | None,
    indice_secao: int | None,
    instrucoes_revisor: str,
    modelo_litellm: str,
    modo_escopo_edicao: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers = "trecho_local",
    trecho_ancora: str | None = None,
    interpretar_escopo_automaticamente: bool = False,
) -> None:
    import asyncio

    asyncio.create_task(
        executar_regeneracao_secao_markdown_tutorial_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            titulo_secao_heading=titulo_secao_heading,
            indice_secao=indice_secao,
            instrucoes_revisor=instrucoes_revisor,
            modelo_litellm=modelo_litellm,
            modo_escopo_edicao=modo_escopo_edicao,
            trecho_ancora=trecho_ancora,
            interpretar_escopo_automaticamente=interpretar_escopo_automaticamente,
        )
    )
