"""Pipeline de job com destino `notas_proposta_funcionalidade` (reunião de discovery/refinement)."""

from __future__ import annotations

import traceback
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_notas_proposta_funcionalidade_markdown_transcribrothers import (
    gerar_markdown_notas_proposta_funcionalidade_com_litellm_transcribrothers,
    gerar_rascunho_notas_proposta_funcionalidade_com_litellm_transcribrothers,
)
from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_rascunho_sem_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_com_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
    planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    extrair_audio_wav_de_video_para_caminho,
)
from transcribrothers_backend.modulo_ffprobe_video_tem_faixa_audio_transcribrothers import (
    video_tem_faixa_audio_via_ffprobe_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers,
    extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers,
    limite_maximo_capturas_frames_tutorial_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    gravar_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    PipelineCanceladoPeloUsuarioTranscribrothers,
    _atualizar_job,
    _diretorio_trabalho_job,
    _levantar_se_cancelamento_pipeline_solicitado,
    _montar_snapshot_regeneracao_tutorial_transcribrothers,
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers,
)
from transcribrothers_backend.modulo_util_handlers_pipeline_custom_habilitados_job_steps_transcribrothers import (
    handler_pipeline_custom_habilitado_no_job_transcribrothers,
)
from transcribrothers_backend.modulo_util_retomar_transcricao_e_rascunho_pipeline_retry_transcribrothers import (
    tentar_carregar_rascunho_notas_proposta_para_retry_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_transcrever_audio_wav_janelas_multimodal_ou_whisper_transcribrothers import (
    transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    resolver_modelo_agente_pipeline_custom_transcribrothers,
    resolver_prompt_agente_pipeline_custom_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS,
    executar_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
    blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers,
)


async def _executar_verificacao_sustentacao_notas_proposta_apos_geracao_markdown_se_ativa_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
    markdown_notas: str,
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> None:
    if not handler_pipeline_custom_habilitado_no_job_transcribrothers(
        steps, "auditor_sustentacao_notas"
    ):
        steps["verificacao_sustentacao_notas_proposta"] = (
            blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(
                motivo="omitida_pipeline_custom_sem_passo"
            )
        )
        steps["pipeline_fase"] = "verificacao_sustentacao_notas_proposta_concluida"
        await _atualizar_job(session_factory, job_id, steps=dict(steps))
        return

    async with session_factory() as session:
        from transcribrothers_backend.modulo_persistencia_runtime_config_verificacao_sustentacao_tutorial_sqlite_transcribrothers import (
            verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers,
        )

        desativada_efetiva, sqlite_definido = (
            await verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
                session,
                configuracao,
            )
        )

    if desativada_efetiva:
        motivo = "desativada_definicao_persistente_interface" if sqlite_definido else "desativada_por_configuracao_ambiente"
        steps["verificacao_sustentacao_notas_proposta"] = blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(
            motivo=motivo,
        )
        return

    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    steps["pipeline_fase"] = "verificacao_sustentacao_notas_proposta_litellm"
    await _atualizar_job(session_factory, job_id, steps=dict(steps))

    ver = await executar_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers(
        configuracao=configuracao,
        markdown_notas=markdown_notas,
        transcricao_corta=transcricao_corta,
        rels=rels,
        modelo_litellm=resolver_modelo_agente_pipeline_custom_transcribrothers(
            "auditor_sustentacao_notas", steps, modelo_litellm, configuracao
        ),
        api_key_litellm=api_key_litellm,
        api_base_litellm=api_base_litellm,
        http_verify_litellm=http_verify_litellm,
        levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
        steps_para_log_decisoes_ia=steps,
        system_prompt_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
            "auditor_sustentacao_notas",
            "system_verificacao_sustentacao_notas",
            steps,
            SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS,
        ),
    )
    steps["verificacao_sustentacao_notas_proposta"] = ver
    steps["pipeline_fase"] = "verificacao_sustentacao_notas_proposta_concluida"
    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    await _atualizar_job(session_factory, job_id, steps=dict(steps))


async def executar_pipeline_job_notas_proposta_funcionalidade_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    audio = work / "audio_extraido_para_transcricao.wav"
    frames_dir = work / "frames_png_capturados_notas_proposta"
    assets_dir = work / "assets_exportados_para_markdown"
    steps: dict[str, Any] = {}

    async def marcar(s: StatusJobTranscribrothers, extra: dict[str, Any] | None = None) -> None:
        nonlocal steps
        if extra:
            steps = {**steps, **extra}
        await _atualizar_job(session_factory, job_id, status=s, steps=steps)

    try:
        async with session_factory() as session:
            res = await session.execute(
                select(JobPipelineTranscribrothers).where(JobPipelineTranscribrothers.id == job_id)
            )
            job = res.scalar_one()
            job_steps = dict(job.steps_json or {})
            steps = steps_json_job_para_reexecucao_pipeline_transcribrothers(job_steps)
            modelo_litellm = (job_steps.get("litellm_model") or configuracao.litellm_model or "").strip()
            api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
            overrides_tm = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(session)

        configuracao_exec = aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
            configuracao,
            overrides_tm,
        )
        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)

        steps["destino_apos_transcricao"] = "notas_proposta_funcionalidade"
        steps["pipeline_fase"] = "notas_proposta_inicio"
        steps["tutorial_captura_frames_sob_demanda"] = True
        steps["upload_ok"] = True
        await marcar(StatusJobTranscribrothers.downloading)

        from transcribrothers_backend.modulo_util_obter_wav_para_transcricao_a_partir_entrada_midia_job_transcribrothers import (
            localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers,
        )

        entrada_midia, tipo_entrada_midia = localizar_arquivo_entrada_midia_no_diretorio_job_transcribrothers(
            work
        )
        reprocessamento_pos_transcricao_apenas = bool(steps.get("reprocessamento_pos_transcricao_apenas"))
        sem_midia_importada = entrada_midia is None and (
            reprocessamento_pos_transcricao_apenas or bool(steps.get("transcricao_importada"))
        )
        if entrada_midia is None and not sem_midia_importada:
            raise FileNotFoundError(
                "Mídia de entrada do job não encontrada (vídeo ou áudio)."
            )
        if tipo_entrada_midia:
            steps["tipo_entrada_midia"] = tipo_entrada_midia
        video = entrada_midia if tipo_entrada_midia == "video" else None

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        if sem_midia_importada:
            tem_audio = False
            steps["entrada_somente_transcricao_importada"] = True
            steps["video_tem_faixa_audio_ffprobe"] = False
        elif video is not None:
            tem_audio = await video_tem_faixa_audio_via_ffprobe_transcribrothers(video)
            steps["video_tem_faixa_audio_ffprobe"] = tem_audio
        else:
            tem_audio = True
            steps["video_tem_faixa_audio_ffprobe"] = True
            steps["entrada_somente_audio"] = True
        transcricao = ResultadoTranscricaoComSegmentos(
            texto_completo="",
            segmentos=[],
            idioma_detectado=None,
        )

        if reprocessamento_pos_transcricao_apenas:
            from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
                carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers,
            )

            transcricao = carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers(
                work, steps
            )
            steps["audio_ok"] = True
            await _atualizar_job(session_factory, job_id, steps=steps)
        elif tem_audio:
            await marcar(StatusJobTranscribrothers.extracting_audio)
            if deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(audio, steps):
                steps["pipeline_fase"] = "audio_wav_reutilizado_sem_reextrair"
                steps["audio_ok"] = True
                steps["audio_wav_reutilizado_retry"] = True
            else:
                steps["pipeline_fase"] = "ffmpeg_extrair_audio"
                steps.pop("audio_wav_reutilizado_retry", None)
                try:
                    await extrair_audio_wav_de_video_para_caminho(
                        caminho_video=video,
                        caminho_audio_wav=audio,
                        forcar_mono=bool(configuracao_exec.transcricao_multimodal_audio_mono),
                    )
                except ErroFfmpegTranscribrothers as e:
                    steps["audio_extracao_falhou"] = str(e)
                    tem_audio = False
                else:
                    steps["audio_ok"] = True

            if tem_audio and steps.get("audio_ok"):
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                await marcar(StatusJobTranscribrothers.transcribing)

                async def ao_persistir_steps_transcricao_transcribrothers(st: dict[str, Any]) -> None:
                    await _atualizar_job(
                        session_factory,
                        job_id,
                        status=StatusJobTranscribrothers.transcribing,
                        steps=st,
                    )

                transcricao = await transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers(
                    work=work,
                    audio=audio,
                    configuracao=configuracao,
                    configuracao_exec_transcricao_mm=configuracao_exec,
                    http_verify_litellm=http_verify_litellm,
                    steps=steps,
                    ao_persistir_steps=ao_persistir_steps_transcricao_transcribrothers,
                    levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
                    pipeline_fase_inicial="transcrevendo_audio_opcional",
                )
        else:
            steps["pipeline_fase"] = "sem_faixa_audio_pulando_transcricao"

        _levantar_se_cancelamento_pipeline_solicitado(job_id)
        dur = 0.0
        if entrada_midia is not None:
            dur = await obter_duracao_video_segundos_via_ffprobe(entrada_midia)
            if dur > 0:
                steps["duracao_video_segundos"] = round(float(dur), 3)

        await marcar(StatusJobTranscribrothers.generating_tutorial)
        md_rascunho_salvo = tentar_carregar_rascunho_notas_proposta_para_retry_pipeline_transcribrothers(
            work,
            steps,
        )
        if md_rascunho_salvo is not None:
            md_rascunho = md_rascunho_salvo
            steps["pipeline_fase"] = "rascunho_notas_reutilizado_sem_regenerar_litellm"
            steps["rascunho_notas_reutilizado_retry"] = True
        else:
            steps["pipeline_fase"] = "gerando_rascunho_notas_proposta"
            md_rascunho = await gerar_rascunho_notas_proposta_funcionalidade_com_litellm_transcribrothers(
                transcricao=transcricao,
                modelo=resolver_modelo_agente_pipeline_custom_transcribrothers(
                    "rascunho_notas_proposta", steps, modelo_litellm, configuracao
                ),
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                steps_para_log_decisoes_ia=steps,
                instrucao_prefixo_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
                    "rascunho_notas_proposta",
                    "instrucao_rascunho_notas_sem_imagens",
                    steps,
                    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
                ),
            )
            gravar_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(work, md_rascunho)
            steps["notas_proposta_rascunho_sem_imagens_ok"] = True

        margem_links = float(
            configuracao_exec.tutorial_margem_minima_segundos_entre_links_temporais_captura
        )
        candidatos_captura = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
            md_rascunho,
            duracao_video_segundos=dur,
            margem_minima_segundos_entre_links_temporais=margem_links,
        )
        steps["frames_candidatos_rascunho_total"] = len(candidatos_captura)
        max_capturas_teto = limite_maximo_capturas_frames_tutorial_transcribrothers(
            dur if dur > 0 else 1.0,
            max_frames_per_minute=configuracao_exec.max_frames_per_minute,
            tutorial_max_frames_total=configuracao_exec.tutorial_max_frames_total,
        )
        timestamps_pre_planejados: list[float] | None = None
        if candidatos_captura:
            _levantar_se_cancelamento_pipeline_solicitado(job_id)
            steps["pipeline_fase"] = "planejando_instantes_captura_notas_proposta"
            await _atualizar_job(session_factory, job_id, steps=steps)
            escolhidos, meta_planej = await planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers(
                markdown_rascunho_tutorial=md_rascunho,
                candidatos_segundos=candidatos_captura,
                transcricao=transcricao,
                duracao_video_segundos=dur,
                margem_minima_segundos_entre_links=margem_links,
                max_capturas_apos_limites=max_capturas_teto,
                modelo_litellm=resolver_modelo_agente_pipeline_custom_transcribrothers(
                    "plano_capturas_notas", steps, modelo_litellm, configuracao
                ),
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                configuracao=configuracao_exec,
                steps_para_log_decisoes_ia=steps,
                modo_notas_proposta_funcionalidade=True,
                system_prompt_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
                    "plano_capturas_notas",
                    "system_planejamento_instantes_notas",
                    steps,
                    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
                ),
            )
            steps["planejamento_instantes_captura_notas_proposta"] = meta_planej
            timestamps_pre_planejados = escolhidos

        timestamps_captura = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
            markdown_rascunho_tutorial=md_rascunho,
            transcricao=transcricao,
            duracao_video_segundos=dur,
            max_frames_per_minute=configuracao_exec.max_frames_per_minute,
            tutorial_max_frames_total=configuracao_exec.tutorial_max_frames_total,
            margem_minima_segundos_entre_links_temporais=margem_links,
            timestamps_pre_planejados=timestamps_pre_planejados,
        )
        steps["frames_planejados_captura_notas_proposta"] = len(timestamps_captura)

        rels: list[tuple[float, str]] = []
        if timestamps_captura and video is not None:
            await marcar(StatusJobTranscribrothers.capturing_frames)
            steps["pipeline_fase"] = "capturando_frames_notas_proposta"
            largura_png = (
                int(configuracao.tutorial_frame_max_width_px)
                if configuracao.tutorial_frame_max_width_px > 0
                else None
            )
            rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
                caminho_video=video,
                timestamps_segundos=timestamps_captura,
                duracao_video_segundos=dur,
                frames_dir=frames_dir,
                assets_dir=assets_dir,
                prefixo_nome_arquivo="screenshot_notas_proposta_funcionalidade",
                largura_maxima_saida_pixeis=largura_png,
            )
        elif timestamps_captura and video is None:
            steps["capturas_omitidas_entrada_somente_audio"] = True
            if sem_midia_importada:
                steps["capturas_omitidas_transcricao_importada"] = True
                steps["pipeline_fase"] = "capturas_omitidas_transcricao_importada"
            else:
                steps["pipeline_fase"] = "capturas_omitidas_somente_audio"
        steps["notas_proposta_frames_capturados"] = len(rels)

        _levantar_se_cancelamento_pipeline_solicitado(job_id)
        steps["pipeline_fase"] = "gerando_markdown_notas_proposta_litellm"
        md = await gerar_markdown_notas_proposta_funcionalidade_com_litellm_transcribrothers(
            transcricao=transcricao,
            caminhos_frames_rel_job=rels,
            modelo=resolver_modelo_agente_pipeline_custom_transcribrothers(
                "gerador_notas_proposta", steps, modelo_litellm, configuracao
            ),
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            diretorio_assets_absoluto=assets_dir,
            steps_para_log_decisoes_ia=steps,
            markdown_rascunho_para_contexto=md_rascunho,
            instrucao_prefixo_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
                "gerador_notas_proposta",
                "instrucao_notas_com_imagens",
                steps,
                TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
            ),
        )

        steps["regeneracao_tutorial_snapshot"] = _montar_snapshot_regeneracao_tutorial_transcribrothers(
            transcricao,
            rels,
        )

        await _executar_verificacao_sustentacao_notas_proposta_apos_geracao_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_notas=md,
            transcricao_corta=transcricao,
            rels=rels,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )

        steps["pipeline_fase"] = "notas_proposta_concluida"
        era_reprocessamento_pos_transcricao = bool(steps.get("reprocessamento_pos_transcricao_apenas"))
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            markdown=md,
            steps=steps,
        )
        if era_reprocessamento_pos_transcricao:
            from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
                ORIGEM_HISTORICO_NOTAS_PIPELINE_INICIAL_TRANSCRIBROTHERS,
            )
            from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
                inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers,
            )
            from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
                finalizar_reprocessamento_pos_transcricao_nos_steps_transcribrothers,
            )

            await inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers(
                session_factory,
                job_id=job_id,
                conteudo_markdown=md,
                origem=ORIGEM_HISTORICO_NOTAS_PIPELINE_INICIAL_TRANSCRIBROTHERS,
            )
            finalizar_reprocessamento_pos_transcricao_nos_steps_transcribrothers(steps)
            await _atualizar_job(session_factory, job_id, steps=steps)
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
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
        if len(texto_erro_ui) > 65000:
            texto_erro_ui = texto_erro_ui[:65000] + "\n...[truncado]"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro_ui,
            steps=steps_com_diagnostico,
        )
