"""Atualiza narração/MP4 a partir do VTT editado, regenerando TTS só nas cues alteradas."""

from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_diagnostico_tts_perfil_experimental_voz_transcribrothers import (
    aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
    converter_alinhamento_stt_em_cues_com_janelas_video_transcribrothers,
    converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers,
    markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers,
    montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers,
)
from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    aplicar_textos_vtt_sobre_cues_janela_preservando_tempos_video_transcribrothers,
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    cues_janela_a_partir_manifest_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
    indices_cues_com_texto_diferente_do_manifest_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_AGENDADO,
    FASE_VIDEO_NARRADO_CONCLUIDO,
    FASE_VIDEO_NARRADO_FALHOU,
    FASE_VIDEO_NARRADO_GERANDO_TTS,
    FASE_VIDEO_NARRADO_MUX_FFMPEG,
    FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS,
    _filtrar_cues_narraveis_mantendo_janelas_video_transcribrothers,
    _localizar_arquivo_video_entrada_no_diretorio_job,
)
from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_util_parsear_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers import (
    parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_validar_cues_janelas_video_antes_narracao_tts_transcribrothers import (
    validar_cues_janelas_video_antes_narracao_tts_transcribrothers,
)

FASE_VIDEO_NARRADO_ATUALIZANDO_LEGENDAS_EDITADAS = "video_narrado_atualizando_legendas_editadas"
_NOME_SUBPASTA_WAVS_POR_CUE = "wavs_narracao_por_cue"


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def _diretorio_assets_do_job(data_dir: Path, job_id: str) -> Path:
    return _diretorio_trabalho_job(data_dir, job_id) / "assets_exportados_para_markdown"


async def _atualizar_steps_job_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    steps: dict[str, Any],
    status: StatusJobTranscribrothers | None = None,
    error: str | None = None,
    limpar_mensagem_erro: bool = False,
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
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()


def _montar_cues_janela_a_partir_markdown_ou_stt_transcribrothers(
    *,
    markdown: str,
    work: Path,
    duracao_video: float,
) -> ResultadoCuesNarracaoComJanelasVideoTranscribrothers:
    usa_ancoras_md = markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers(
        markdown
    )
    if usa_ancoras_md:
        return montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
            markdown,
            duracao_video_segundos=duracao_video,
        )
    snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work)
    if snap is None:
        raise RuntimeError(
            "Snapshot de transcrição não encontrado e o documento não tem âncoras ?t=."
        )
    texto_plano = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(
        markdown
    )
    frases = partir_texto_plano_em_frases_para_legendas_transcribrothers(texto_plano)
    alinhamento = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
        frases,
        list(snap.segmentos),
        duracao_video_segundos=duracao_video,
    )
    return converter_alinhamento_stt_em_cues_com_janelas_video_transcribrothers(alinhamento)


def resolver_cues_janela_e_indices_sujos_para_atualizacao_vtt_transcribrothers(
    *,
    work: Path,
    assets: Path,
    markdown: str,
    duracao_video: float,
) -> tuple[list[CueNarracaoComJanelaVideoTranscribrothers], list[int], str]:
    """
    Devolve (cues com textos do VTT + janelas, índices a regenerar, origem das janelas).
    """
    caminho_vtt = assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    if not caminho_vtt.is_file():
        raise RuntimeError(
            "Arquivo de legendas VTT não encontrado. Gere o vídeo narrado antes de atualizar."
        )
    cues_vtt = parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers(
        caminho_vtt.read_text(encoding="utf-8")
    )
    if not cues_vtt:
        raise RuntimeError("VTT sem cues utilizáveis para atualizar a narração.")
    textos_desejados = [c.texto for c in cues_vtt]

    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if manifest is not None:
        if len(manifest) != len(textos_desejados):
            raise RuntimeError(
                "A quantidade de legendas no VTT não bate com a última narração "
                f"({len(textos_desejados)} vs {len(manifest)}). "
                "Use «Gerar nova narração» para remontar tudo a partir do documento."
            )
        cues_base = cues_janela_a_partir_manifest_transcribrothers(manifest)
        textos_ref = [c.texto for c in cues_base]
        origem = "manifest"
    else:
        resultado = _montar_cues_janela_a_partir_markdown_ou_stt_transcribrothers(
            markdown=markdown,
            work=work,
            duracao_video=duracao_video,
        )
        resultado, _desc = _filtrar_cues_narraveis_mantendo_janelas_video_transcribrothers(resultado)
        if len(resultado.cues) != len(textos_desejados):
            raise RuntimeError(
                "A quantidade de legendas no VTT não bate com as cues do documento "
                f"({len(textos_desejados)} vs {len(resultado.cues)}). "
                "Use «Gerar nova narração» para remontar tudo."
            )
        cues_base = list(resultado.cues)
        textos_ref = [c.texto for c in cues_base]
        origem = "markdown_ou_stt"

    indices_sujos = indices_cues_com_texto_diferente_do_manifest_transcribrothers(
        textos_manifest=textos_ref,
        textos_desejados=textos_desejados,
    )
    cues_finais = aplicar_textos_vtt_sobre_cues_janela_preservando_tempos_video_transcribrothers(
        cues_base,
        textos_desejados,
    )
    return cues_finais, indices_sujos, origem


def validar_pre_requisitos_atualizar_narracao_a_partir_vtt_editadas_transcribrothers(
    *,
    work: Path,
    assets: Path,
) -> None:
    vtt = assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    if not vtt.is_file():
        raise ValueError(
            "Não há legendas VTT no job. Gere o vídeo narrado antes de atualizar a narração."
        )
    video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if video is None or not video.is_file():
        raise ValueError("Este job não tem vídeo de entrada para remontar o MP4.")
    dir_wavs = work / _NOME_SUBPASTA_WAVS_POR_CUE
    if not dir_wavs.is_dir():
        raise ValueError(
            "Não há áudios por cue da narração anterior. Use «Gerar nova narração» uma vez."
        )


async def executar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_do_job(data_dir, job_id)
    steps: dict[str, Any] = {}
    try:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                return
            steps = dict(row.steps_json or {})
            markdown = (row.result_markdown or "").strip()

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_ATUALIZANDO_LEGENDAS_EDITADAS
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
        )

        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        if video is None or not video.is_file():
            raise RuntimeError("Vídeo de entrada não encontrado.")
        duracao_video = await obter_duracao_video_segundos_via_ffprobe(video)
        if duracao_video <= 0:
            raise RuntimeError("Não foi possível obter a duração do vídeo (ffprobe).")

        cues_finais, indices_sujos, origem_janelas = (
            resolver_cues_janela_e_indices_sujos_para_atualizacao_vtt_transcribrothers(
                work=work,
                assets=assets,
                markdown=markdown,
                duracao_video=duracao_video,
            )
        )

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS
        steps["video_narrado_atualizacao_parcial_origem_janelas"] = origem_janelas
        steps["video_narrado_atualizacao_parcial_cues_sujas"] = len(indices_sujos)
        await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        resultado_cues = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
            cues=cues_finais,
            modo="vtt_editado",
            quantidade_ancoras_markdown=0,
            quantidade_casadas=sum(1 for c in cues_finais if c.casado),
            quantidade_interpoladas=sum(1 for c in cues_finais if not c.casado),
        )
        validacao = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
            resultado_cues,
            duracao_video_segundos=duracao_video,
        )
        if not validacao.ok:
            raise RuntimeError(
                validacao.motivo_rejeicao
                or "Janelas de tela incompatíveis com o vídeo; atualização abortada."
            )

        if not indices_sujos:
            # Nada mudou vs última narração; só garante manifest alinhado ao VTT.
            gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
                work=work,
                cues=cues_finais,
            )
            steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
                **dict(steps.get(CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS) or {}),
                "ok": True,
                "mensagem": (
                    "Nenhuma legenda alterada em relação à última narração; "
                    "áudio e vídeo mantidos."
                ),
                "atualizacao_parcial": True,
                "quantidade_cues_regeneradas": 0,
                "quantidade_cues_reutilizadas": len(cues_finais),
                "concluido_em": datetime.now(timezone.utc).isoformat(),
            }
            await _atualizar_steps_job_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
                status=StatusJobTranscribrothers.completed,
                limpar_mensagem_erro=True,
            )
            return

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_GERANDO_TTS
        steps["video_narrado_tts_cue_indice"] = 0
        steps["video_narrado_tts_cue_total"] = len(cues_finais)
        steps["video_narrado_tts_cue_preview"] = ""
        steps["video_narrado_tts_cue_fase"] = "iniciando"
        steps["video_narrado_tts_pedidos_feitos"] = 0
        steps["video_narrado_tts_cues_puladas"] = 0
        steps["video_narrado_tts_cues_reutilizadas"] = 0
        await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        async def _progresso_tts(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        caminho_wav = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        dir_wavs_cue = work / _NOME_SUBPASTA_WAVS_POR_CUE
        from transcribrothers_backend.modulo_persistencia_runtime_config_voz_tts_narracao_sqlite_transcribrothers import (
            carregar_voz_tts_narracao_do_session_factory_transcribrothers,
        )

        voz_tts = await carregar_voz_tts_narracao_do_session_factory_transcribrothers(
            session_factory
        )
        steps["pipeline_video_narrado_voz_tts"] = voz_tts
        from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
            CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
            CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS,
            CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS,
            PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
            normalizar_perfil_tts_narracao_transcribrothers,
            normalizar_ritmo_tts_narracao_transcribrothers,
            normalizar_temperatura_tts_narracao_transcribrothers,
        )

        perfil_tts_efetivo = normalizar_perfil_tts_narracao_transcribrothers(
            steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS)
            or PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS] = perfil_tts_efetivo
        temperatura_tts_efetiva = normalizar_temperatura_tts_narracao_transcribrothers(
            steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS)
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS] = (
            temperatura_tts_efetiva
        )
        ritmo_tts_efetivo = normalizar_ritmo_tts_narracao_transcribrothers(
            steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS)
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS] = ritmo_tts_efetivo
        resultado_tts = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=[c.texto for c in cues_finais],
            modelo=modelo_tts,
            configuracao=configuracao,
            diretorio_wavs_por_cue=dir_wavs_cue,
            caminho_wav_concatenado=caminho_wav,
            atualizar_progresso=_progresso_tts,
            indices_a_regenerar=set(indices_sujos),
            preservar_indices_da_entrada=True,
            voz=voz_tts,
            perfil_tts=perfil_tts_efetivo,
            temperatura=temperatura_tts_efetiva,
            ritmo=ritmo_tts_efetivo,
        )
        aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers(
            steps,
            resultado_tts.diagnostico_experimental,
        )
        if not resultado_tts.ok:
            raise RuntimeError(resultado_tts.mensagem)
        if len(resultado_tts.caminhos_wav_por_cue) != len(cues_finais):
            raise RuntimeError("Quantidade de WAVs por cue não bate com as legendas.")

        cues_vtt_narracao = converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
            list(cues_finais),
            list(resultado_tts.duracoes_por_cue_segundos),
        )
        caminho_vtt = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
            diretorio_assets=assets,
            cues=cues_vtt_narracao,
        )
        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        url_vtt = f"/api/jobs/{job_id}/assets/{caminho_vtt.name}?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": caminho_vtt.name,
            "url_asset": url_vtt,
            "quantidade_cues": len(cues_finais),
            "timeline": "narracao_tts",
            "atualizado_parcial_em": datetime.now(timezone.utc).isoformat(),
        }

        url_wav = (
            f"/api/jobs/{job_id}/assets/{resultado_tts.nome_arquivo_concatenado}?v={stamp_cache}"
        )
        steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": resultado_tts.nome_arquivo_concatenado,
            "url_asset": url_wav,
            "modelo": resultado_tts.modelo,
            "texto_caracteres": resultado_tts.texto_caracteres,
            "texto_truncado": False,
            "quantidade_chunks": resultado_tts.quantidade_pedidos_tts,
            "quantidade_cues": resultado_tts.quantidade_cues,
            "quantidade_cues_puladas": resultado_tts.quantidade_cues_puladas,
            "quantidade_cues_reutilizadas": resultado_tts.quantidade_cues_reutilizadas,
            "quantidade_cues_regeneradas": len(indices_sujos),
            "indices_cues_regeneradas": list(indices_sujos),
            "previews_cues_puladas": list(resultado_tts.previews_cues_puladas),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "atualizacao_parcial": True,
        }

        indices_regen = set(indices_sujos)
        cues_finais = [
            CueNarracaoComJanelaVideoTranscribrothers(
                texto=c.texto,
                inicio_video_segundos=c.inicio_video_segundos,
                fim_video_segundos=c.fim_video_segundos,
                origem_ancora=c.origem_ancora,
                casado=c.casado,
                sem_narracao=c.sem_narracao,
                voz_tts=voz_tts if i in indices_regen else (c.voz_tts or voz_tts),
                texto_tts=str(getattr(c, "texto_tts", "") or ""),
            )
            for i, c in enumerate(cues_finais)
        ]
        gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
            work=work,
            cues=cues_finais,
        )

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_MUX_FFMPEG
        steps["video_narrado_mux_segmento_indice"] = 0
        steps["video_narrado_mux_segmento_total"] = len(cues_finais)
        steps["video_narrado_mux_fase"] = "iniciando"
        await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        async def _progresso_mux(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        segmentos = [
            SegmentoVideoNarradoRetargetTranscribrothers(
                caminho_wav=caminho_wav_cue,
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
            )
            for cue, caminho_wav_cue in zip(
                cues_finais,
                resultado_tts.caminhos_wav_por_cue,
                strict=True,
            )
        ]
        from transcribrothers_backend.modulo_persistencia_runtime_config_encode_video_narrado_sqlite_transcribrothers import (
            carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers,
        )

        prefs_encode = await carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers(
            session_factory
        )
        steps["video_narrado_mux_encode_resolucao"] = prefs_encode.resolucao
        steps["video_narrado_mux_encode_fps"] = int(prefs_encode.fps)
        caminho_mp4 = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=work,
            atualizar_progresso=_progresso_mux,
            preferencias_encode=prefs_encode,
            # Atualização parcial de legendas/TTS: só reencode segmentos com fingerprint novo.
            forcar_montagem_por_segmentos_com_cache=True,
        )
        url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_mp4.name,
            "url_download": url_mp4,
            "modo_montagem": "segmentos_retarget_audio",
            "quantidade_segmentos": len(segmentos),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "atualizacao_parcial": True,
        }

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": True,
            "mensagem": (
                f"Narração atualizada a partir das legendas: "
                f"{len(indices_sujos)} cue(s) regenerada(s), "
                f"{resultado_tts.quantidade_cues_reutilizadas} reutilizada(s)."
            ),
            "modo_janelas": "vtt_editado",
            "atualizacao_parcial": True,
            "quantidade_cues": len(cues_finais),
            "quantidade_cues_regeneradas": len(indices_sujos),
            "quantidade_cues_reutilizadas": resultado_tts.quantidade_cues_reutilizadas,
            "quantidade_chunks_tts": resultado_tts.quantidade_pedidos_tts,
            "modelo_tts": resultado_tts.modelo,
            "nome_arquivo_vtt": caminho_vtt.name,
            "url_asset_vtt": url_vtt,
            "nome_arquivo_wav": resultado_tts.nome_arquivo_concatenado,
            "url_asset_wav": url_wav,
            "nome_arquivo_mp4": caminho_mp4.name,
            "url_download_mp4": url_mp4,
            "concluido_em": datetime.now(timezone.utc).isoformat(),
        }
        from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
            tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers,
        )

        versao_snap = tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers(
            work=work,
            assets=assets,
            steps=steps,
            origem="atualizar_vtt",
        )
        if versao_snap:
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS][
                "versao_video_narrado_id"
            ] = versao_snap
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
        )
    except Exception as e:
        tb = traceback.format_exc()
        msg_curta = str(e).strip() or type(e).__name__
        if isinstance(e, ErroFfmpegTranscribrothers):
            msg_curta = f"ffmpeg: {msg_curta}"
        texto_erro = (
            f"{type(e).__name__}: {msg_curta}\n\n"
            f"--- traceback (servidor; copie para o suporte) ---\n{tb}"
        )
        if len(texto_erro) > 65000:
            texto_erro = texto_erro[:65000] + "\n...[truncado]"
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_FALHOU
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": False,
            "mensagem": msg_curta,
            "atualizacao_parcial": True,
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro,
        )


def agendar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
) -> None:
    asyncio.create_task(
        executar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            modelo_tts=modelo_tts,
        )
    )


# Reexport constante usada na API
__all__ = [
    "FASE_VIDEO_NARRADO_ATUALIZANDO_LEGENDAS_EDITADAS",
    "FASE_VIDEO_NARRADO_AGENDADO",
    "agendar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_task_assincrona",
    "executar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_background",
    "resolver_cues_janela_e_indices_sujos_para_atualizacao_vtt_transcribrothers",
    "validar_pre_requisitos_atualizar_narracao_a_partir_vtt_editadas_transcribrothers",
]
