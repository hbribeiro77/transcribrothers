"""Pipeline assíncrono A+B: âncoras ?t= (ou STT) → TTS por cue → retarget/concat MP4 + VTT na timeline TTS."""

from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers,
)
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
    CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS,
    aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
    resolver_modelo_tts_para_narracao_documento_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
    converter_alinhamento_stt_em_cues_com_janelas_video_transcribrothers,
    converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers,
    markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers,
    montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers,
)
from transcribrothers_backend.modulo_util_filtrar_trechos_narraveis_para_tts_transcribrothers import (
    texto_e_narravel_para_tts_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_LIMPANDO_LEGENDAS_IA,
    aplicar_textos_limpos_nas_cues_janela_transcribrothers,
    limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_validar_cues_janelas_video_antes_narracao_tts_transcribrothers import (
    validar_cues_janelas_video_antes_narracao_tts_transcribrothers,
)
from transcribrothers_backend.modulo_util_registrar_tempos_etapas_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS,
    fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers,
    iniciar_etapa_pela_fase_pipeline_video_narrado_transcribrothers,
)
from transcribrothers_backend.modulo_util_resolver_markdown_escopo_pipeline_video_narrado_transcribrothers import (
    resolver_markdown_para_pipeline_video_narrado_transcribrothers,
)
from transcribrothers_backend.modulo_diretriz_conteudo_legendas_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS,
    normalizar_diretriz_conteudo_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    normalizar_paralelismo_tts_cues_experimental_transcribrothers,
    normalizar_perfil_tts_narracao_transcribrothers,
    normalizar_ritmo_tts_narracao_transcribrothers,
    normalizar_temperatura_tts_narracao_transcribrothers,
)

CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS = "pipeline_video_narrado_documento"

FASE_VIDEO_NARRADO_AGENDADO = "video_narrado_agendado"
FASE_VIDEO_NARRADO_ALINHANDO_LEGENDAS = "video_narrado_alinhando_legendas"
FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS = "video_narrado_validando_legendas"
FASE_VIDEO_NARRADO_GERANDO_TTS = "video_narrado_gerando_tts"
FASE_VIDEO_NARRADO_MUX_FFMPEG = "video_narrado_mux_ffmpeg"
FASE_VIDEO_NARRADO_CONCLUIDO = "video_narrado_concluido"
FASE_VIDEO_NARRADO_FALHOU = "video_narrado_falhou"
FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT = (
    "video_narrado_aguardando_resolucao_tts_timeout"
)

_NOME_SUBPASTA_WAVS_POR_CUE = "wavs_narracao_por_cue"


def _filtrar_cues_narraveis_mantendo_janelas_video_transcribrothers(
    resultado: ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
) -> tuple[ResultadoCuesNarracaoComJanelasVideoTranscribrothers, list[str]]:
    cues_ok: list[CueNarracaoComJanelaVideoTranscribrothers] = []
    descartados: list[str] = []
    for cue in resultado.cues:
        if texto_e_narravel_para_tts_transcribrothers(cue.texto):
            cues_ok.append(cue)
        else:
            t = (cue.texto or "").strip()
            if t:
                descartados.append(t)
    casadas = sum(1 for c in cues_ok if c.casado)
    filtrado = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=cues_ok,
        modo=resultado.modo,
        quantidade_ancoras_markdown=resultado.quantidade_ancoras_markdown,
        quantidade_casadas=casadas,
        quantidade_interpoladas=len(cues_ok) - casadas,
    )
    return filtrado, descartados


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def _diretorio_assets_do_job(data_dir: Path, job_id: str) -> Path:
    return _diretorio_trabalho_job(data_dir, job_id) / "assets_exportados_para_markdown"


def _localizar_arquivo_video_entrada_no_diretorio_job(work: Path) -> Path | None:
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in sorted(work.glob(pattern)):
            if p.is_file():
                return p
    return None


def _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
    steps: dict[str, Any],
    fase: str,
    *,
    reiniciar_tempos: bool = False,
) -> None:
    if reiniciar_tempos:
        steps.pop(CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS, None)
    steps["pipeline_fase"] = fase
    iniciar_etapa_pela_fase_pipeline_video_narrado_transcribrothers(steps, fase=fase)


async def _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
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


async def executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
    modelo_chat_limpeza: str | None = None,
    perfil_tts: str | None = None,
    paralelismo_tts_experimental: int | None = None,
    temperatura_tts: float | None = None,
    ritmo_tts: str | None = None,
    diretriz_conteudo_legendas: str | None = None,
) -> None:
    """A+B: janelas por ?t= (ou STT), TTS por cue, retarget/concat; VTT na timeline da narração."""
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
            markdown = resolver_markdown_para_pipeline_video_narrado_transcribrothers(
                result_markdown=row.result_markdown or "",
                steps=steps,
            )

        perfil_tts_efetivo = normalizar_perfil_tts_narracao_transcribrothers(
            perfil_tts
            if (perfil_tts or "").strip()
            else steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS)
            or PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS] = perfil_tts_efetivo
        paralelismo_tts_efetivo = normalizar_paralelismo_tts_cues_experimental_transcribrothers(
            paralelismo_tts_experimental
            if paralelismo_tts_experimental is not None
            else steps.get(
                CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS
            )
        )
        steps[
            CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS
        ] = paralelismo_tts_efetivo
        temperatura_tts_efetiva = normalizar_temperatura_tts_narracao_transcribrothers(
            temperatura_tts
            if temperatura_tts is not None
            else steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS)
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS] = (
            temperatura_tts_efetiva
        )
        ritmo_tts_efetivo = normalizar_ritmo_tts_narracao_transcribrothers(
            ritmo_tts
            if (ritmo_tts or "").strip()
            else steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS)
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS] = ritmo_tts_efetivo
        diretriz_conteudo_efetiva = normalizar_diretriz_conteudo_legendas_transcribrothers(
            diretriz_conteudo_legendas
            if (diretriz_conteudo_legendas or "").strip()
            else steps.get(
                CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS
            )
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS] = (
            diretriz_conteudo_efetiva
        )

        if not markdown:
            raise RuntimeError("Documento sem Markdown para o pipeline de vídeo narrado.")

        usa_ancoras_md = markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers(
            markdown
        )
        snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work)
        if not usa_ancoras_md and snap is None:
            raise RuntimeError(
                "Snapshot de transcrição não encontrado e o documento não tem âncoras ?t=. "
                "É necessário STT concluído ou timestamps no Markdown."
            )

        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        if video is None or not video.is_file():
            raise RuntimeError("Este job não tem vídeo de entrada para montar o MP4 com narração.")

        duracao_video = await obter_duracao_video_segundos_via_ffprobe(video)
        if duracao_video <= 0:
            raise RuntimeError("Não foi possível obter a duração do vídeo (ffprobe).")

        texto_plano = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(
            markdown
        )
        if not texto_plano.strip():
            raise RuntimeError("Não há texto narrável no documento (Markdown vazio após limpeza).")

        _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
            steps,
            FASE_VIDEO_NARRADO_ALINHANDO_LEGENDAS,
            reiniciar_tempos=True,
        )
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
        )

        if usa_ancoras_md:
            resultado_cues = (
                montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
                    markdown,
                    duracao_video_segundos=duracao_video,
                )
            )
        else:
            assert snap is not None
            frases = partir_texto_plano_em_frases_para_legendas_transcribrothers(texto_plano)
            alinhamento = alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
                frases,
                list(snap.segmentos),
                duracao_video_segundos=duracao_video,
            )
            resultado_cues = converter_alinhamento_stt_em_cues_com_janelas_video_transcribrothers(
                alinhamento
            )

        resultado_cues, trechos_descartados = (
            _filtrar_cues_narraveis_mantendo_janelas_video_transcribrothers(resultado_cues)
        )
        assets.mkdir(parents=True, exist_ok=True)
        # Regeneração completa (FAB / «Gerar nova narração») parte do Markdown.
        # Edições manuais do VTT ficam no fluxo «Atualizar narração» do modal.
        steps["video_narrado_textos_origem_vtt_editado"] = False

        _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
            steps,
            FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS,
        )
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
        )

        validacao = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
            resultado_cues,
            duracao_video_segundos=duracao_video,
        )
        gerado_em_legendas = datetime.now(timezone.utc).isoformat()
        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            "nome_arquivo": NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
            "url_asset": (
                f"/api/jobs/{job_id}/assets/"
                f"{NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS}?v={stamp_cache}"
            ),
            "percentual_casado": round(resultado_cues.percentual_casado, 1),
            "quantidade_casadas": resultado_cues.quantidade_casadas,
            "quantidade_interpoladas": resultado_cues.quantidade_interpoladas,
            "quantidade_cues": len(resultado_cues.cues),
            "quantidade_trechos_descartados": len(trechos_descartados),
            "duracao_video_segundos": round(duracao_video, 3),
            "modo_janelas": resultado_cues.modo,
            "quantidade_ancoras_markdown": resultado_cues.quantidade_ancoras_markdown,
            "validacao_ok": validacao.ok,
            "motivo_rejeicao": validacao.motivo_rejeicao,
            "gerado_em": gerado_em_legendas,
        }
        if not validacao.ok:
            raise RuntimeError(
                validacao.motivo_rejeicao
                or "Janelas de tela incompatíveis com o vídeo; narração abortada."
            )

        # Etapa explícita: preparação IA (limpeza + forma narrável; legenda = TTS).
        if resultado_cues.cues:
            _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
                steps,
                FASE_VIDEO_NARRADO_LIMPANDO_LEGENDAS_IA,
            )
            steps["video_narrado_limpeza_ia_status"] = "iniciando"
            steps["video_narrado_limpeza_ia_resumo"] = (
                f"Enviando {len(resultado_cues.cues)} cue(s) ao modelo de chat para preparar "
                "legendas (limpeza + forma narrável; mesmo texto no TTS)…"
            )
            steps["video_narrado_limpeza_ia_modelo_atual"] = ""
            steps[CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS] = {
                "ok": None,
                "status": "em_andamento",
                "mensagem": steps["video_narrado_limpeza_ia_resumo"],
                "quantidade_cues": len(resultado_cues.cues),
                "quantidade_alteradas": 0,
                "alteracoes": [],
            }
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
            )
            modelo_chat_efetivo = (
                (modelo_chat_limpeza or "").strip()
                or str(steps.get("pipeline_video_narrado_modelo_chat_limpeza") or "").strip()
                or None
            )
            steps["video_narrado_limpeza_ia_modelo_atual"] = modelo_chat_efetivo or ""
            limpeza = await limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers(
                textos=[c.texto for c in resultado_cues.cues],
                configuracao=configuracao,
                modelo_chat=modelo_chat_efetivo,
                diretriz_conteudo=diretriz_conteudo_efetiva,
                steps_para_log=steps,
            )
            alteracoes_json = [
                {"indice": a.indice, "antes": a.antes, "depois": a.depois}
                for a in limpeza.alteracoes
            ]
            steps[CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS] = {
                "ok": limpeza.ok,
                "status": (
                    "falhou_mantidos_originais"
                    if limpeza.usou_fallback_originais
                    else ("concluida_com_alteracoes" if limpeza.quantidade_alteradas else "concluida_sem_alteracoes")
                ),
                "mensagem": limpeza.mensagem,
                "modelo": limpeza.modelo,
                "modelos_tentados": list(limpeza.modelos_tentados),
                "quantidade_cues": len(resultado_cues.cues),
                "quantidade_alteradas": limpeza.quantidade_alteradas,
                "indices_alterados": list(limpeza.indices_alterados),
                "indices_rejeitados_guarda": list(limpeza.indices_rejeitados_guarda),
                "usou_fallback_originais": limpeza.usou_fallback_originais,
                "diretriz_conteudo": diretriz_conteudo_efetiva,
                "alteracoes": alteracoes_json,
            }
            steps["video_narrado_limpeza_ia_status"] = steps[CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS][
                "status"
            ]
            steps["video_narrado_limpeza_ia_resumo"] = limpeza.mensagem
            steps["video_narrado_limpeza_ia_modelo_atual"] = limpeza.modelo
            steps["video_narrado_limpeza_ia_quantidade_alteradas"] = limpeza.quantidade_alteradas
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
            )
            if limpeza.ok and not limpeza.usou_fallback_originais:
                cues_limpas = aplicar_textos_limpos_nas_cues_janela_transcribrothers(
                    list(resultado_cues.cues),
                    limpeza.textos,
                )
                resultado_cues = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
                    cues=cues_limpas,
                    modo=resultado_cues.modo,
                    quantidade_ancoras_markdown=resultado_cues.quantidade_ancoras_markdown,
                    quantidade_casadas=sum(1 for c in cues_limpas if c.casado),
                    quantidade_interpoladas=sum(1 for c in cues_limpas if not c.casado),
                )
                # Após a IA, refiltra: cues que ficaram sem texto narrável não entram no TTS.
                resultado_cues, descartados_pos_limpeza = (
                    _filtrar_cues_narraveis_mantendo_janelas_video_transcribrothers(resultado_cues)
                )
                trechos_descartados.extend(descartados_pos_limpeza)
                steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
                    **steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS],
                    "quantidade_cues": len(resultado_cues.cues),
                    "quantidade_trechos_descartados": len(trechos_descartados),
                    "limpeza_ia_aplicada": True,
                    "quantidade_cues_limpas_ia": limpeza.quantidade_alteradas,
                    "quantidade_cues_descartadas_apos_limpeza_ia": len(descartados_pos_limpeza),
                }
        else:
            steps[CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS] = {
                "ok": True,
                "mensagem": "Nenhuma cue para preparar.",
                "omitida": True,
                "motivo": "sem_cues",
            }

        if not resultado_cues.cues:
            raise RuntimeError(
                "Nenhuma cue narrável restou após a preparação das legendas; narração abortada."
            )

        _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
            steps,
            FASE_VIDEO_NARRADO_GERANDO_TTS,
        )
        steps["video_narrado_tts_cue_indice"] = 0
        steps["video_narrado_tts_cue_total"] = len(resultado_cues.cues)
        steps["video_narrado_tts_cue_preview"] = ""
        steps["video_narrado_tts_cue_fase"] = "iniciando"
        steps["video_narrado_tts_pedidos_feitos"] = 0
        steps["video_narrado_tts_cues_puladas"] = 0
        steps["video_narrado_tts_trechos_descartados"] = len(trechos_descartados)
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
        )

        async def _progresso_tts(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
            )

        caminho_wav = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        dir_wavs_cue = work / _NOME_SUBPASTA_WAVS_POR_CUE
        trechos_cues = [c.texto for c in resultado_cues.cues]
        from transcribrothers_backend.modulo_persistencia_runtime_config_voz_tts_narracao_sqlite_transcribrothers import (
            carregar_voz_tts_narracao_do_session_factory_transcribrothers,
        )

        voz_tts = await carregar_voz_tts_narracao_do_session_factory_transcribrothers(
            session_factory
        )
        steps["pipeline_video_narrado_voz_tts"] = voz_tts
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS] = perfil_tts_efetivo
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS] = (
            temperatura_tts_efetiva
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS] = ritmo_tts_efetivo
        # preservar_indices evita o 2º filtro interno dropar cues e desalinha WAV×janela.
        resultado_tts = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=trechos_cues,
            modelo=modelo_tts,
            configuracao=configuracao,
            diretorio_wavs_por_cue=dir_wavs_cue,
            caminho_wav_concatenado=caminho_wav,
            atualizar_progresso=_progresso_tts,
            preservar_indices_da_entrada=True,
            voz=voz_tts,
            perfil_tts=perfil_tts_efetivo,
            temperatura=temperatura_tts_efetiva,
            ritmo=ritmo_tts_efetivo,
            paralelismo_cues=paralelismo_tts_efetivo,
        )
        aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers(
            steps,
            resultado_tts.diagnostico_experimental,
        )
        if not resultado_tts.ok:
            raise RuntimeError(resultado_tts.mensagem)

        if len(resultado_tts.caminhos_wav_por_cue) != len(resultado_cues.cues):
            raise RuntimeError(
                "Quantidade de WAVs por cue não bate com as cues de janela "
                f"({len(resultado_tts.caminhos_wav_por_cue)} != {len(resultado_cues.cues)})."
            )

        from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
            carimbar_voz_tts_em_todas_as_cues_janela_transcribrothers,
        )

        cues_com_voz = carimbar_voz_tts_em_todas_as_cues_janela_transcribrothers(
            list(resultado_cues.cues),
            voz_tts,
        )
        gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
            work=work,
            cues=cues_com_voz,
        )

        cues_vtt_narracao = converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
            list(resultado_cues.cues),
            list(resultado_tts.duracoes_por_cue_segundos),
        )
        caminho_vtt = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
            diretorio_assets=assets,
            cues=cues_vtt_narracao,
        )
        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        url_vtt = f"/api/jobs/{job_id}/assets/{caminho_vtt.name}?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS],
            "nome_arquivo": caminho_vtt.name,
            "url_asset": url_vtt,
            "timeline": "narracao_tts",
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
            "previews_cues_puladas": list(resultado_tts.previews_cues_puladas),
            "quantidade_trechos_descartados_antes_tts": (
                resultado_tts.quantidade_trechos_descartados_antes_tts + len(trechos_descartados)
            ),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
        }

        pendentes_timeout = list(resultado_tts.cues_pendentes_timeout or ())
        if pendentes_timeout:
            steps[CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS] = (
                pendentes_timeout
            )
            fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(steps)
            steps["pipeline_fase"] = FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
                "ok": False,
                "aguardando_resolucao_tts_timeout": True,
                "mensagem": (
                    f"Narração parcial: {len(pendentes_timeout)} cue(s) com timeout. "
                    "Reenvie manualmente no modal de status para continuar a montagem do vídeo."
                ),
                "quantidade_cues_pendentes_timeout": len(pendentes_timeout),
                "pausado_em": datetime.now(timezone.utc).isoformat(),
            }
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
                status=StatusJobTranscribrothers.completed,
                limpar_mensagem_erro=True,
            )
            return

        steps.pop(CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS, None)
        _definir_fase_pipeline_video_narrado_com_tempo_transcribrothers(
            steps,
            FASE_VIDEO_NARRADO_MUX_FFMPEG,
        )
        steps["video_narrado_mux_segmento_indice"] = 0
        steps["video_narrado_mux_segmento_total"] = len(resultado_cues.cues)
        steps["video_narrado_mux_fase"] = "iniciando"
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
        )

        async def _progresso_mux(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
                session_factory,
                job_id,
                steps=steps,
            )

        segmentos = [
            SegmentoVideoNarradoRetargetTranscribrothers(
                caminho_wav=caminho_wav_cue,
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
            )
            for cue, caminho_wav_cue in zip(
                resultado_cues.cues,
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
            # Aquecer pasta segmentos_video_narrado_retarget para edições do modal.
            forcar_montagem_por_segmentos_com_cache=True,
        )
        url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_mp4.name,
            "url_download": url_mp4,
            "modo_montagem": "segmentos_retarget_audio",
            "quantidade_segmentos": len(segmentos),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
        }

        fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(steps)
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
        rotulo_modo = (
            f"âncoras ?t= ({resultado_cues.quantidade_ancoras_markdown})"
            if resultado_cues.modo == "markdown_ancoras"
            else f"STT ({resultado_cues.percentual_casado:.0f}% casado)"
        )
        extra_msg = ""
        if resultado_tts.quantidade_cues_puladas:
            extra_msg += f" {resultado_tts.quantidade_cues_puladas} cue(s) sem áudio (silêncio)."
        if trechos_descartados:
            extra_msg += f" {len(trechos_descartados)} trecho(s) lixo descartado(s)."
        tempos = steps.get(CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS) or {}
        total_s = tempos.get("total_segundos") if isinstance(tempos, dict) else None
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": True,
            "mensagem": (
                f"Vídeo narrado pronto (A+B): janelas por {rotulo_modo}; "
                f"{resultado_tts.quantidade_cues} cue(s) com retarget à fala; "
                f"textos do Markdown com limpeza IA."
                f"{extra_msg}"
            ),
            "modo_janelas": resultado_cues.modo,
            "percentual_casado": round(resultado_cues.percentual_casado, 1),
            "quantidade_casadas": resultado_cues.quantidade_casadas,
            "quantidade_interpoladas": resultado_cues.quantidade_interpoladas,
            "quantidade_ancoras_markdown": resultado_cues.quantidade_ancoras_markdown,
            "quantidade_cues": len(resultado_cues.cues),
            "quantidade_cues_puladas_tts": resultado_tts.quantidade_cues_puladas,
            "quantidade_trechos_descartados": len(trechos_descartados),
            "quantidade_chunks_tts": resultado_tts.quantidade_pedidos_tts,
            "modelo_tts": resultado_tts.modelo,
            "textos_origem_vtt_editado": False,
            "nome_arquivo_vtt": caminho_vtt.name,
            "url_asset_vtt": url_vtt,
            "nome_arquivo_wav": resultado_tts.nome_arquivo_concatenado,
            "url_asset_wav": url_wav,
            "nome_arquivo_mp4": caminho_mp4.name,
            "url_download_mp4": url_mp4,
            "concluido_em": datetime.now(timezone.utc).isoformat(),
            "duracao_total_pipeline_segundos": total_s,
        }
        from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
            tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers,
        )

        versao_snap = tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers(
            work=work,
            assets=assets,
            steps=steps,
            origem="pipeline_completo",
        )
        if versao_snap:
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS][
                "versao_video_narrado_id"
            ] = versao_snap
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
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
        fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(steps)
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_FALHOU
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": False,
            "mensagem": msg_curta,
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps_e_status_job_pipeline_video_narrado_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro,
        )


def agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
    modelo_chat_limpeza: str | None = None,
    perfil_tts: str | None = None,
    paralelismo_tts_experimental: int | None = None,
    temperatura_tts: float | None = None,
    ritmo_tts: str | None = None,
    diretriz_conteudo_legendas: str | None = None,
) -> None:
    asyncio.create_task(
        executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            modelo_tts=modelo_tts,
            modelo_chat_limpeza=modelo_chat_limpeza,
            perfil_tts=perfil_tts,
            paralelismo_tts_experimental=paralelismo_tts_experimental,
            temperatura_tts=temperatura_tts,
            ritmo_tts=ritmo_tts,
            diretriz_conteudo_legendas=diretriz_conteudo_legendas,
        )
    )


def validar_pre_requisitos_pipeline_video_narrado_no_disco_transcribrothers(
    *,
    work: Path,
    markdown: str,
) -> None:
    """Levanta ValueError com mensagem amigável se faltar pré-requisito de disco/conteúdo."""
    if not (markdown or "").strip():
        raise ValueError("Documento sem Markdown para o pipeline de vídeo narrado.")
    usa_ancoras = markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers(
        markdown
    )
    snap = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(work)
    if not usa_ancoras and snap is None:
        raise ValueError(
            "Snapshot de transcrição não encontrado e o documento não tem âncoras ?t=. "
            "É necessário STT concluído no disco ou timestamps no Markdown."
        )
    video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if video is None or not video.is_file():
        raise ValueError("Este job não tem vídeo de entrada para montar o MP4 com narração.")


# Reexport para testes / API
__all__ = [
    "CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS",
    "FASE_VIDEO_NARRADO_AGENDADO",
    "FASE_VIDEO_NARRADO_ALINHANDO_LEGENDAS",
    "FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS",
    "FASE_VIDEO_NARRADO_LIMPANDO_LEGENDAS_IA",
    "FASE_VIDEO_NARRADO_GERANDO_TTS",
    "FASE_VIDEO_NARRADO_MUX_FFMPEG",
    "FASE_VIDEO_NARRADO_CONCLUIDO",
    "FASE_VIDEO_NARRADO_FALHOU",
    "NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS",
    "NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS",
    "NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS",
    "agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona",
    "executar_pipeline_video_narrado_a_partir_documento_markdown_em_background",
    "resolver_modelo_tts_para_narracao_documento_transcribrothers",
    "validar_pre_requisitos_pipeline_video_narrado_no_disco_transcribrothers",
]
