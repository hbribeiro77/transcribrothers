from __future__ import annotations

import asyncio
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
    gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
    planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_captura_frames_png_tutorial_sob_demanda_transcribrothers import (
    capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers,
    extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers,
    limite_maximo_capturas_frames_tutorial_transcribrothers,
    resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers,
)
from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    cancelamento_pipeline_foi_solicitado_para_job_transcribrothers,
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_pipeline_transcrever_audio_wav_janelas_multimodal_ou_whisper_transcribrothers import (
    transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    resolver_modelo_agente_pipeline_custom_transcribrothers,
    resolver_prompt_agente_pipeline_custom_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_download_google_drive_publico_arquivo_por_id import (
    ErroDownloadGoogleDrive,
    baixar_arquivo_google_drive_publico_por_id_para_caminho,
    max_bytes_da_config,
)
from transcribrothers_backend.modulo_metadados_google_drive_publico_arquivo_por_id import (
    extensao_sugerida_para_video_a_partir_do_mime,
    obter_metadados_google_drive_publico_por_id,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    amostrar_indices_por_limite_por_minuto,
    extrair_audio_wav_de_video_para_caminho,
    reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_handlers_pipeline_custom_habilitados_job_steps_transcribrothers import (
    handler_pipeline_custom_habilitado_no_job_transcribrothers,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers,
    deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers,
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)


class PipelineCanceladoPeloUsuarioTranscribrothers(Exception):
    """Fluxo interrompido após POST /api/jobs/{id}/cancel."""


def _levantar_se_cancelamento_pipeline_solicitado(job_id: str) -> None:
    if cancelamento_pipeline_foi_solicitado_para_job_transcribrothers(job_id):
        limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
        raise PipelineCanceladoPeloUsuarioTranscribrothers()


def _instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(
    steps: dict[str, Any],
) -> str | None:
    raw = steps.get("tutorial_litellm_instrucao_prefixo_custom")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def _resolver_instrucao_prefixo_gerador_tutorial_markdown_de_steps_transcribrothers(
    steps: dict[str, Any],
    *,
    usar_visao: bool,
) -> str | None:
    """Prefixo do user message: UI do job > prompt custom do agente gerador > padrão interno."""
    ui = _instrucao_litellm_prefixo_custom_de_steps_para_geracao_tutorial_transcribrothers(steps)
    if ui:
        return ui
    if not steps.get("pipeline_custom_agentes"):
        return None
    chave = "instrucao_tutorial_com_imagens" if usar_visao else "instrucao_tutorial_sem_imagens"
    default = (
        INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS
        if usar_visao
        else INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS
    )
    return resolver_prompt_agente_pipeline_custom_transcribrothers(
        "gerador_tutorial_markdown",
        chave,
        steps,
        default,
    )


def _montar_snapshot_regeneracao_tutorial_transcribrothers(
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
) -> dict[str, Any]:
    return {
        "texto_completo": transcricao_corta.texto_completo,
        "idioma": transcricao_corta.idioma_detectado,
        "segmentos": [asdict(s) for s in transcricao_corta.segmentos],
        "caminhos_frames_rel_job": [[t, rel] for t, rel in rels],
    }


def _snapshot_dict_para_transcricao_e_rels(
    snap: dict[str, Any],
) -> tuple[ResultadoTranscricaoComSegmentos, list[tuple[float, str]]]:
    segmentos_raw = snap.get("segmentos") or []
    segmentos: list[SegmentoTranscricaoComTempo] = []
    for s in segmentos_raw:
        if not isinstance(s, dict):
            continue
        segmentos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=float(s.get("inicio_segundos", 0.0)),
                fim_segundos=float(s.get("fim_segundos", 0.0)),
                texto=str(s.get("texto") or ""),
            )
        )
    rels: list[tuple[float, str]] = []
    for pair in snap.get("caminhos_frames_rel_job") or []:
        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
            rels.append((float(pair[0]), str(pair[1])))
    texto = str(snap.get("texto_completo") or "")
    idioma = snap.get("idioma")
    idioma_s = str(idioma) if idioma is not None else None
    return (
        ResultadoTranscricaoComSegmentos(
            texto_completo=texto,
            segmentos=segmentos,
            idioma_detectado=idioma_s,
        ),
        rels,
    )


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


async def _atualizar_job(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    status: StatusJobTranscribrothers | None = None,
    error: str | None = None,
    limpar_mensagem_erro: bool = False,
    markdown: str | None = None,
    steps: dict[str, Any] | None = None,
) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            return
        if status is not None:
            row.status = status.value
        if limpar_mensagem_erro:
            row.error_message = None
        elif error is not None:
            row.error_message = error
        if markdown is not None:
            row.result_markdown = markdown
        if steps is not None:
            row.steps_json = steps
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()


async def _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
    markdown_tutorial: str,
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> None:
    """Grava `steps_json.verificacao_sustentacao_tutorial` e fases de progresso; não altera o Markdown."""
    from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
        SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS,
        blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers,
        executar_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers,
    )

    if not handler_pipeline_custom_habilitado_no_job_transcribrothers(
        steps, "auditor_sustentacao_tutorial"
    ):
        steps["verificacao_sustentacao_tutorial"] = (
            blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(
                motivo="omitida_pipeline_custom_sem_passo"
            )
        )
        steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_concluida"
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
        motivo = (
            "desativada_definicao_persistente_interface"
            if sqlite_definido
            else "desativada_por_configuracao_ambiente"
        )
        steps["verificacao_sustentacao_tutorial"] = (
            blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(motivo=motivo)
        )
        return

    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        job_steps_indicam_projeto_em_branco_transcribrothers,
    )

    if job_steps_indicam_projeto_em_branco_transcribrothers(steps):
        steps["verificacao_sustentacao_tutorial"] = (
            blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(
                motivo="projeto_em_branco_sem_transcricao"
            )
        )
        steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_concluida"
        await _atualizar_job(session_factory, job_id, steps=dict(steps))
        return

    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_litellm"
    await _atualizar_job(session_factory, job_id, steps=dict(steps))

    def _levantar_cancelamento_verificacao_transcribrothers() -> None:
        _levantar_se_cancelamento_pipeline_solicitado(job_id)

    ver = await executar_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers(
        configuracao=configuracao,
        markdown_tutorial=markdown_tutorial,
        transcricao_corta=transcricao_corta,
        rels=rels,
        modelo_litellm=resolver_modelo_agente_pipeline_custom_transcribrothers(
            "auditor_sustentacao_tutorial", steps, modelo_litellm, configuracao
        ),
        api_key_litellm=api_key_litellm,
        api_base_litellm=api_base_litellm,
        http_verify_litellm=http_verify_litellm,
        levantar_se_cancelado=_levantar_cancelamento_verificacao_transcribrothers,
        steps_para_log_decisoes_ia=steps,
        system_prompt_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
            "auditor_sustentacao_tutorial",
            "system_verificacao_sustentacao_tutorial",
            steps,
            SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS,
        ),
    )
    steps["verificacao_sustentacao_tutorial"] = ver
    steps["pipeline_fase"] = "verificacao_sustentacao_tutorial_concluida"
    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    await _atualizar_job(session_factory, job_id, steps=dict(steps))


async def _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
    markdown_tutorial: str,
    assets_dir: Path,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
) -> str:
    from transcribrothers_backend.modulo_verificacao_imagens_duplicadas_tutorial_markdown_litellm_visao_lotes_transcribrothers import (
        SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS,
        blob_verificacao_imagens_duplicadas_omitida_transcribrothers,
        executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_no_markdown_transcribrothers,
    )

    if not handler_pipeline_custom_habilitado_no_job_transcribrothers(
        steps, "verificacao_imagens_duplicadas"
    ):
        steps["verificacao_imagens_duplicadas_tutorial"] = (
            blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
                motivo="omitida_pipeline_custom_sem_passo"
            )
        )
        steps["pipeline_fase"] = "verificacao_imagens_duplicadas_tutorial_concluida"
        await _atualizar_job(session_factory, job_id, steps=dict(steps))
        return markdown_tutorial

    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    steps["pipeline_fase"] = "verificacao_imagens_duplicadas_tutorial_litellm_visao"
    await _atualizar_job(session_factory, job_id, steps=dict(steps))

    md_atualizado, blob = await executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_no_markdown_transcribrothers(
        configuracao=configuracao,
        markdown_tutorial=markdown_tutorial,
        diretorio_assets_absoluto=assets_dir,
        modelo_litellm=resolver_modelo_agente_pipeline_custom_transcribrothers(
            "verificacao_imagens_duplicadas", steps, modelo_litellm, configuracao
        ),
        api_key_litellm=api_key_litellm,
        api_base_litellm=api_base_litellm,
        http_verify_litellm=http_verify_litellm,
        levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
        steps_para_log_decisoes_ia=steps,
        system_prompt_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
            "verificacao_imagens_duplicadas",
            "system_verificacao_imagens_duplicadas",
            steps,
            SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS,
        ),
    )
    steps["verificacao_imagens_duplicadas_tutorial"] = blob
    steps["pipeline_fase"] = "verificacao_imagens_duplicadas_tutorial_concluida"
    _levantar_se_cancelamento_pipeline_solicitado(job_id)
    await _atualizar_job(session_factory, job_id, steps=dict(steps))
    return md_atualizado


async def executar_pipeline_job_transcricao_tutorial_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    video: Path | None = None
    audio = work / "audio_extraido_para_transcricao.wav"
    frames_dir = work / "frames_png_capturados_para_tutorial"
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
            file_id = job.file_id
            api_key = configuracao.google_drive_api_key
            source_kind = job.source_kind or OrigemEntradaJobTranscribrothers.drive
            job_steps = dict(job.steps_json or {})
            steps = steps_json_job_para_reexecucao_pipeline_transcribrothers(job_steps)
            modelo_litellm = (job_steps.get("litellm_model") or configuracao.litellm_model or "").strip()
            api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(
                configuracao
            )
            overrides_tm = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(
                session
            )

        configuracao_exec_transcricao_mm = aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
            configuracao,
            overrides_tm,
        )

        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
            configuracao
        )

        def _resumo_httpx_verify_para_steps_json(v: bool | str) -> str:
            if v is True:
                return "true"
            if v is False:
                return "false"
            return f"ca_bundle_file:{Path(v).name}"

        steps["litellm_httpx_verify_diagnostico"] = _resumo_httpx_verify_para_steps_json(
            http_verify_litellm
        )
        steps["litellm_http_verify_ssl_configurado_bool"] = bool(configuracao.litellm_http_verify_ssl)
        steps["litellm_ssl_ca_bundle_configurado_bool"] = bool(
            (configuracao.litellm_ssl_ca_bundle or "").strip()
        )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "metadados_job_carregados"

        destino_pipeline = str(job_steps.get("destino_apos_transcricao") or "gerar_tutorial").strip()
        if destino_pipeline == "so_transcricao":
            from transcribrothers_backend.modulo_pipeline_job_so_transcricao_midia_entrada_transcribrothers import (
                executar_pipeline_job_so_transcricao_em_background,
            )

            await executar_pipeline_job_so_transcricao_em_background(
                job_id=job_id,
                session_factory=session_factory,
                configuracao=configuracao,
            )
            return

        if destino_pipeline == "reproducao_bug":
            from transcribrothers_backend.modulo_pipeline_job_reproducao_bug_recbrothers_transcribrothers import (
                executar_pipeline_job_reproducao_bug_recbrothers_em_background,
            )

            await executar_pipeline_job_reproducao_bug_recbrothers_em_background(
                job_id=job_id,
                session_factory=session_factory,
                configuracao=configuracao,
            )
            return

        if destino_pipeline == "notas_proposta_funcionalidade":
            from transcribrothers_backend.modulo_pipeline_job_notas_proposta_funcionalidade_transcribrothers import (
                executar_pipeline_job_notas_proposta_funcionalidade_em_background,
            )

            await executar_pipeline_job_notas_proposta_funcionalidade_em_background(
                job_id=job_id,
                session_factory=session_factory,
                configuracao=configuracao,
            )
            return

        await marcar(StatusJobTranscribrothers.downloading)
        work.mkdir(parents=True, exist_ok=True)

        if source_kind == OrigemEntradaJobTranscribrothers.upload_local:
            candidatos = sorted(work.glob("video_entrada_arquivo_local.*"))
            video = next((p for p in candidatos if p.is_file()), None)
            if video is None:
                raise FileNotFoundError(
                    "Vídeo enviado não encontrado no diretório do job (esperado video_entrada_arquivo_local.*)."
                )
            steps["source"] = OrigemEntradaJobTranscribrothers.upload_local
            steps["upload_ok"] = True
            steps["video_filename"] = video.name
        else:
            try:
                meta = await obter_metadados_google_drive_publico_por_id(
                    file_id=file_id, api_key=api_key
                )
                ext = extensao_sugerida_para_video_a_partir_do_mime(
                    str(meta.get("mimeType") or "")
                )
                video = work / f"video_entrada_google_drive.{ext}"
                steps["drive_mime_type"] = meta.get("mimeType")
                steps["drive_name"] = meta.get("name")
            except Exception:  # noqa: BLE001
                video = work / "video_entrada_google_drive.mp4"
            if deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers(video, steps):
                steps["source"] = OrigemEntradaJobTranscribrothers.drive
                steps["download_ok"] = True
                steps["video_entrada_reutilizado_retry"] = True
                steps["video_filename"] = video.name
                steps["pipeline_fase"] = "video_entrada_reutilizado_sem_redownload"
            else:
                await baixar_arquivo_google_drive_publico_por_id_para_caminho(
                    file_id=file_id,
                    api_key=api_key,
                    destino=video,
                    max_bytes=max_bytes_da_config(configuracao),
                )
                steps["source"] = OrigemEntradaJobTranscribrothers.drive
                steps["download_ok"] = True
                steps.pop("video_entrada_reutilizado_retry", None)
                steps["video_filename"] = video.name

        assert video is not None

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        reprocessamento_pos_transcricao_apenas = bool(steps.get("reprocessamento_pos_transcricao_apenas"))
        if reprocessamento_pos_transcricao_apenas:
            from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
                carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers,
            )

            transcricao = carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers(
                work, steps
            )
            steps["audio_ok"] = True
            await _atualizar_job(session_factory, job_id, steps=steps)
        else:
            await marcar(StatusJobTranscribrothers.extracting_audio)
            if deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(audio, steps):
                steps["pipeline_fase"] = "audio_wav_reutilizado_sem_reextrair"
                steps["audio_ok"] = True
                steps["audio_wav_reutilizado_retry"] = True
            else:
                steps["pipeline_fase"] = "ffmpeg_extrair_audio"
                steps.pop("audio_wav_reutilizado_retry", None)
                await extrair_audio_wav_de_video_para_caminho(
                    caminho_video=video,
                    caminho_audio_wav=audio,
                    forcar_mono=bool(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_mono),
                )
                steps["audio_ok"] = True

            _levantar_se_cancelamento_pipeline_solicitado(job_id)

            await marcar(StatusJobTranscribrothers.transcribing)

            async def ao_persistir_steps_transcricao_transcribrothers(st: dict[str, Any]) -> None:
                await _atualizar_job(session_factory, job_id, steps=st)

            transcricao = await transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers(
                work=work,
                audio=audio,
                configuracao=configuracao,
                configuracao_exec_transcricao_mm=configuracao_exec_transcricao_mm,
                http_verify_litellm=http_verify_litellm,
                steps=steps,
                ao_persistir_steps=ao_persistir_steps_transcricao_transcribrothers,
                levantar_se_cancelado=lambda: _levantar_se_cancelamento_pipeline_solicitado(job_id),
                pipeline_fase_inicial="transcrevendo_audio",
            )

        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        dur = await obter_duracao_video_segundos_via_ffprobe(video)
        if dur > 0:
            steps["duracao_video_segundos"] = round(float(dur), 3)
        prefixo = "screenshot_tutorial_transcribrothers"
        largura_png = (
            int(configuracao.tutorial_frame_max_width_px)
            if configuracao.tutorial_frame_max_width_px > 0
            else None
        )
        captura_sob_demanda = bool(configuracao.tutorial_captura_frames_sob_demanda)
        steps["tutorial_captura_frames_sob_demanda"] = captura_sob_demanda
        rels: list[tuple[float, str]] = []
        md_rascunho: str | None = None

        if captura_sob_demanda:
            _levantar_se_cancelamento_pipeline_solicitado(job_id)
            await marcar(StatusJobTranscribrothers.generating_tutorial)
            steps["pipeline_fase"] = "gerando_rascunho_tutorial_sem_imagens"
            steps["geracao_tutorial_litellm_total_imagens"] = 0
            md_rascunho = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
                transcricao=transcricao,
                caminhos_frames_rel_job=[],
                modelo=resolver_modelo_agente_pipeline_custom_transcribrothers(
                    "rascunho_tutorial_sob_demanda", steps, modelo_litellm, configuracao
                ),
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                enviar_screenshots_png_como_imagens_multimodais=False,
                httpx_timeout_connect_segundos=float(
                    configuracao.litellm_http_timeout_connect_segundos
                ),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                instrucao_prefixo_litellm_custom=resolver_prompt_agente_pipeline_custom_transcribrothers(
                    "rascunho_tutorial_sob_demanda",
                    "instrucao_rascunho_sem_imagens",
                    steps,
                    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
                ),
                steps_para_log_decisoes_ia=steps,
                log_etapa_geracao_tutorial="geracao_rascunho_tutorial_sem_imagens",
            )
            steps["tutorial_rascunho_sem_imagens_ok"] = True

            margem_links = float(
                configuracao_exec_transcricao_mm.tutorial_margem_minima_segundos_entre_links_temporais_captura
            )
            candidatos_captura = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
                md_rascunho,
                duracao_video_segundos=dur,
                margem_minima_segundos_entre_links_temporais=margem_links,
            )
            steps["frames_candidatos_rascunho_total"] = len(candidatos_captura)
            max_capturas_teto = limite_maximo_capturas_frames_tutorial_transcribrothers(
                dur if dur > 0 else 1.0,
                max_frames_per_minute=configuracao_exec_transcricao_mm.max_frames_per_minute,
                tutorial_max_frames_total=configuracao_exec_transcricao_mm.tutorial_max_frames_total,
            )
            timestamps_pre_planejados: list[float] | None = None
            if candidatos_captura:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "planejando_instantes_captura_frames_tutorial"
                await _atualizar_job(session_factory, job_id, steps=steps)
                escolhidos, meta_planej = (
                    await planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers(
                        markdown_rascunho_tutorial=md_rascunho,
                        candidatos_segundos=candidatos_captura,
                        transcricao=transcricao,
                        duracao_video_segundos=dur,
                        margem_minima_segundos_entre_links=margem_links,
                        max_capturas_apos_limites=max_capturas_teto,
                        modelo_litellm=resolver_modelo_agente_pipeline_custom_transcribrothers(
                            "plano_capturas_tutorial", steps, modelo_litellm, configuracao
                        ),
                        api_key=api_key_litellm,
                        api_base=api_base_litellm,
                        httpx_verify=http_verify_litellm,
                        configuracao=configuracao_exec_transcricao_mm,
                        steps_para_log_decisoes_ia=steps,
                        system_prompt_override=resolver_prompt_agente_pipeline_custom_transcribrothers(
                            "plano_capturas_tutorial",
                            "system_planejamento_instantes_tutorial",
                            steps,
                            SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
                        ),
                    )
                )
                steps["planejamento_instantes_captura_frames"] = meta_planej
                timestamps_pre_planejados = escolhidos

            timestamps_captura = resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
                markdown_rascunho_tutorial=md_rascunho,
                transcricao=transcricao,
                duracao_video_segundos=dur,
                max_frames_per_minute=configuracao_exec_transcricao_mm.max_frames_per_minute,
                tutorial_max_frames_total=configuracao_exec_transcricao_mm.tutorial_max_frames_total,
                margem_minima_segundos_entre_links_temporais=margem_links,
                timestamps_pre_planejados=timestamps_pre_planejados,
            )
            steps["frames_planejados_captura_sob_demanda"] = len(timestamps_captura)

            async def _progresso_captura_sob_demanda(indice: int, total: int, t_seg: float) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "capturando_frame_png_sob_demanda"
                steps["captura_frame_indice"] = indice
                steps["captura_frames_total"] = total
                steps["captura_frame_timestamp_segundos"] = round(float(t_seg), 2)
                await _atualizar_job(session_factory, job_id, steps=steps)

            await marcar(StatusJobTranscribrothers.capturing_frames)
            steps["pipeline_fase"] = "capturando_frames_png_sob_demanda"
            rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
                caminho_video=video,
                timestamps_segundos=timestamps_captura,
                duracao_video_segundos=dur,
                frames_dir=frames_dir,
                assets_dir=assets_dir,
                prefixo_nome_arquivo=prefixo,
                largura_maxima_saida_pixeis=largura_png,
                ao_atualizar_progresso_captura=_progresso_captura_sob_demanda,
            )
        else:
            await marcar(StatusJobTranscribrothers.capturing_frames)
            steps["pipeline_fase"] = "capturando_frames_png"
            n_seg = len(transcricao.segmentos)
            indices_segmentos = list(range(n_seg)) if n_seg else []
            if not indices_segmentos and dur > 0:
                indices_segmentos = [0]
                transcricao = ResultadoTranscricaoComSegmentos(
                    texto_completo=transcricao.texto_completo or "Sem fala detectada.",
                    segmentos=[
                        SegmentoTranscricaoComTempo(
                            inicio_segundos=0.0,
                            fim_segundos=max(1.0, dur),
                            texto="Conteúdo visual (sem segmentos de fala).",
                        )
                    ],
                    idioma_detectado=transcricao.idioma_detectado,
                )
                n_seg = 1
                indices_segmentos = [0]
            indices_segmentos = amostrar_indices_por_limite_por_minuto(
                n_itens=n_seg,
                max_por_minuto=configuracao.max_frames_per_minute,
                duracao_video_segundos=dur
                if dur > 0
                else max(
                    1.0,
                    transcricao.segmentos[-1].fim_segundos if transcricao.segmentos else 1.0,
                ),
            )
            indices_segmentos = reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers(
                indices_segmentos,
                configuracao.tutorial_max_frames_total,
            )
            timestamps_legado = [
                max(0.0, (transcricao.segmentos[i].inicio_segundos + transcricao.segmentos[i].fim_segundos) / 2.0)
                for i in indices_segmentos
                if i < len(transcricao.segmentos)
            ]

            async def _progresso_captura_legado(indice: int, total: int, t_seg: float) -> None:
                _levantar_se_cancelamento_pipeline_solicitado(job_id)
                steps["pipeline_fase"] = "capturando_frame_png_individual"
                steps["captura_frame_indice"] = indice
                steps["captura_frames_total"] = total
                steps["captura_frame_timestamp_segundos"] = round(float(t_seg), 2)
                await _atualizar_job(session_factory, job_id, steps=steps)

            rels = await capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
                caminho_video=video,
                timestamps_segundos=timestamps_legado,
                duracao_video_segundos=dur,
                frames_dir=frames_dir,
                assets_dir=assets_dir,
                prefixo_nome_arquivo=prefixo,
                largura_maxima_saida_pixeis=largura_png,
                ao_atualizar_progresso_captura=_progresso_captura_legado,
            )

        steps["frames_capturados"] = len(rels)
        _levantar_se_cancelamento_pipeline_solicitado(job_id)

        transcricao_para_tutorial = transcricao
        steps["regeneracao_tutorial_snapshot"] = _montar_snapshot_regeneracao_tutorial_transcribrothers(
            transcricao_para_tutorial,
            rels,
        )
        steps["pipeline_fase"] = "gerando_tutorial_http_chat_completions"
        steps["geracao_tutorial_litellm_total_imagens"] = 0
        await marcar(StatusJobTranscribrothers.generating_tutorial)

        instrucao_final = _resolver_instrucao_prefixo_gerador_tutorial_markdown_de_steps_transcribrothers(
            steps,
            usar_visao=False,
        )
        instrucoes_revisao_final: str | None = None
        if captura_sob_demanda and md_rascunho:
            instrucoes_revisao_final = resolver_prompt_agente_pipeline_custom_transcribrothers(
                "gerador_tutorial_markdown",
                "instrucao_incorporar_frames_sob_demanda",
                steps,
                INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
            )

        md = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
            transcricao=transcricao_para_tutorial,
            caminhos_frames_rel_job=rels,
            modelo=resolver_modelo_agente_pipeline_custom_transcribrothers(
                "gerador_tutorial_markdown", steps, modelo_litellm, configuracao
            ),
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            enviar_screenshots_png_como_imagens_multimodais=False,
            bloco_markdown_tutorial_atual_para_contexto_em_revisao=md_rascunho
            if captura_sob_demanda
            else None,
            instrucoes_revisao_humana=instrucoes_revisao_final,
            httpx_timeout_connect_segundos=float(
                configuracao.litellm_http_timeout_connect_segundos
            ),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            instrucao_prefixo_litellm_custom=instrucao_final,
            steps_para_log_decisoes_ia=steps,
        )
        md = await _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            assets_dir=assets_dir,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        await _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            transcricao_corta=transcricao_para_tutorial,
            rels=rels,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        caminho_md = work / "tutorial_gerado_transcribrothers.md"
        caminho_md.write_text(md, encoding="utf-8")
        steps["tutorial_ok"] = True

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.completed,
            markdown=md,
            steps=steps,
        )
        from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
            ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        )
        from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
            inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers,
        )

        await inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers(
            session_factory,
            job_id=job_id,
            conteudo_markdown=md,
            origem=ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        )
        from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
            finalizar_reprocessamento_pos_transcricao_nos_steps_transcribrothers,
        )

        finalizar_reprocessamento_pos_transcricao_nos_steps_transcribrothers(steps)
        await _atualizar_job(session_factory, job_id, steps=steps)
    except PipelineCanceladoPeloUsuarioTranscribrothers:
        steps["pipeline_fase"] = "cancelado_pelo_usuario"
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.cancelled,
            error="Cancelado pelo usuário.",
            steps=steps,
        )
    except ErroDownloadGoogleDrive as e:
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=str(e),
            steps=steps,
        )
    except ErroFfmpegTranscribrothers as e:
        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.failed,
            error=str(e),
            steps=steps,
        )
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        msg_curta = str(e).strip() or repr(e)
        steps_com_diagnostico = {
            **steps,
            "error_traceback": tb[:32000],
            "error_type": type(e).__name__,
            "error_repr": repr(e),
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


async def executar_regeneracao_apenas_tutorial_markdown_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    revisao_profunda_multifase: bool = False,
) -> None:
    """Reexecuta só o LLM do tutorial usando snapshot + PNGs já gerados no disco."""
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
            snap = job_steps.get("regeneracao_tutorial_snapshot")
            steps = {**job_steps}

        if not isinstance(snap, dict):
            raise RuntimeError(
                "Snapshot de regeneração ausente: só é possível após captura de telas no pipeline completo."
            )

        transcricao_corta, rels = _snapshot_dict_para_transcricao_e_rels(snap)
        from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
            job_steps_indicam_projeto_em_branco_transcribrothers,
        )

        eh_projeto_em_branco = job_steps_indicam_projeto_em_branco_transcribrothers(steps)
        if not rels and not eh_projeto_em_branco:
            raise RuntimeError("Snapshot sem referências a frames (assets).")

        assets_dir = work / "assets_exportados_para_markdown"
        if not eh_projeto_em_branco:
            for _t, rel in rels:
                nome = rel.split("/")[-1]
                if not nome or not (assets_dir / nome).is_file():
                    raise RuntimeError(
                        f"Imagem do tutorial não encontrada no servidor (esperado em assets): {nome}"
                    )

        api_key_litellm, api_base_litellm = resolver_api_key_e_api_base_para_chamada_litellm(
            configuracao
        )
        http_verify_litellm = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
            configuracao
        )

        steps["pipeline_identificador"] = IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS
        steps["pipeline_fase"] = "regenerando_somente_tutorial_litellm"
        steps["regeneracao_apenas_markdown"] = True
        steps["regeneracao_instrucoes_usadas"] = bool((instrucoes_revisao_humana or "").strip())
        steps["revisao_profunda_multifase_agendada"] = bool(revisao_profunda_multifase)

        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
            FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps.pop("regeneracao_tutorial_aplicada_em", None)

        md_atual = (job.result_markdown or "").strip()
        caminhos_ctx_fab = steps.get("regeneracao_fab_contexto_caminhos_assets_png")
        extras_ctx: list[str] = []
        if isinstance(caminhos_ctx_fab, list):
            extras_ctx = [str(x) for x in caminhos_ctx_fab if isinstance(x, str)]
        from transcribrothers_backend.modulo_util_montar_rels_anexo_regeneracao_tutorial_com_disco_projeto_em_branco_transcribrothers import (
            montar_rels_png_anexo_regeneracao_com_pool_disco_projeto_em_branco_transcribrothers,
        )

        rels_anexo_regeneracao = montar_rels_png_anexo_regeneracao_com_pool_disco_projeto_em_branco_transcribrothers(
            markdown=md_atual,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            rels_snapshot=rels,
            assets_dir=assets_dir,
            caminhos_assets_png_contexto_fab_extra=extras_ctx,
            eh_projeto_em_branco=eh_projeto_em_branco,
        )
        textos_ctx_fab = steps.get("regeneracao_fab_contexto_textos")
        textos_anexos: list[str] = []
        if isinstance(textos_ctx_fab, list):
            textos_anexos = [str(x) for x in textos_ctx_fab if isinstance(x, str) and str(x).strip()]
        usar_visao_regeneracao = bool(rels_anexo_regeneracao)
        steps["geracao_tutorial_litellm_total_imagens"] = (
            len(rels_anexo_regeneracao) if usar_visao_regeneracao else 0
        )

        await _atualizar_job(
            session_factory,
            job_id,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
            steps=steps,
        )

        if revisao_profunda_multifase:
            from transcribrothers_backend.modulo_pipeline_regeneracao_tutorial_revisao_profunda_multifase_litellm_transcribrothers import (
                gerar_markdown_tutorial_via_revisao_profunda_multifase_litellm_transcribrothers,
            )

            md = await gerar_markdown_tutorial_via_revisao_profunda_multifase_litellm_transcribrothers(
                job_id=job_id,
                session_factory=session_factory,
                configuracao=configuracao,
                steps_mutavel=steps,
                transcricao_corta=transcricao_corta,
                rels=rels,
                assets_dir=assets_dir,
                md_atual_inicial=md_atual,
                rels_anexo_regeneracao=rels_anexo_regeneracao,
                usar_visao_regeneracao=usar_visao_regeneracao,
                instrucoes_revisao_humana=instrucoes_revisao_humana,
                modelo_litellm=modelo_litellm.strip(),
                api_key_litellm=api_key_litellm,
                api_base_litellm=api_base_litellm,
                http_verify_litellm=http_verify_litellm,
            )
        else:
            md = await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
                transcricao=transcricao_corta,
                caminhos_frames_rel_job=rels,
                modelo=modelo_litellm.strip(),
                api_key=api_key_litellm,
                api_base=api_base_litellm,
                httpx_verify=http_verify_litellm,
                instrucoes_revisao_humana=instrucoes_revisao_humana,
                httpx_timeout_connect_segundos=float(
                    configuracao.litellm_http_timeout_connect_segundos
                ),
                httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
                diretorio_assets_absoluto=assets_dir if usar_visao_regeneracao else None,
                enviar_screenshots_png_como_imagens_multimodais=usar_visao_regeneracao,
                markdown_para_decidir_quais_pngs_anexar=None,
                rels_png_anexo_ja_resolvidos=rels_anexo_regeneracao if usar_visao_regeneracao else None,
                bloco_markdown_tutorial_atual_para_contexto_em_revisao=md_atual if md_atual else None,
                instrucao_prefixo_litellm_custom=_resolver_instrucao_prefixo_gerador_tutorial_markdown_de_steps_transcribrothers(
                    steps,
                    usar_visao=usar_visao_regeneracao,
                ),
                modo_regeneracao_projeto_em_branco_sem_video=eh_projeto_em_branco,
                textos_contexto_anexos_fab=textos_anexos,
                steps_para_log_decisoes_ia=steps,
                log_etapa_geracao_tutorial="regeneracao_tutorial_markdown",
            )
        from transcribrothers_backend.modulo_util_remover_referencias_imagens_assets_inexistentes_markdown_tutorial_transcribrothers import (
            remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers,
        )

        md, _linhas_img_fantasma = remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers(
            md or "",
            assets_dir,
        )
        if _linhas_img_fantasma > 0:
            steps["regeneracao_linhas_imagem_assets_inexistentes_removidas"] = int(_linhas_img_fantasma)
        md = await _executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            assets_dir=assets_dir,
            modelo_litellm=modelo_litellm.strip(),
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
        await _executar_verificacao_sustentacao_tutorial_apos_geracao_markdown_se_ativa_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            steps=steps,
            markdown_tutorial=md,
            transcricao_corta=transcricao_corta,
            rels=rels,
            modelo_litellm=modelo_litellm.strip(),
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
        )
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
            "revisao_profunda_multifase": bool(revisao_profunda_multifase),
        }
        ver_sust = steps.get("verificacao_sustentacao_tutorial")
        if isinstance(ver_sust, dict):
            preview_blob["verificacao_sustentacao_tutorial"] = ver_sust

        steps[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS] = (
            preview_blob
        )
        steps["pipeline_fase"] = FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS
        steps["revisao_profunda_multifase"] = bool(revisao_profunda_multifase)

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
            "error_repr": repr(e),
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


def agendar_regeneracao_apenas_tutorial_markdown_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    instrucoes_revisao_humana: str | None,
    modelo_litellm: str,
    revisao_profunda_multifase: bool = False,
) -> None:
    asyncio.create_task(
        executar_regeneracao_apenas_tutorial_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            instrucoes_revisao_humana=instrucoes_revisao_humana,
            modelo_litellm=modelo_litellm,
            revisao_profunda_multifase=revisao_profunda_multifase,
        )
    )


def agendar_pipeline_job_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    asyncio.create_task(
        executar_pipeline_job_transcricao_tutorial_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
        )
    )
