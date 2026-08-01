"""Remonta o MP4 narrado após edição das janelas de vídeo (reutiliza WAVs; sem novo TTS)."""

from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers import (
    cues_janela_do_manifest_ou_erro_transcribrothers,
    obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers,
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
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    obter_duracao_wav_pcm16_mono_segundos_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
    converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_CONCLUIDO,
    FASE_VIDEO_NARRADO_FALHOU,
    FASE_VIDEO_NARRADO_MUX_FFMPEG,
    _localizar_arquivo_video_entrada_no_diretorio_job,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_validar_cues_janelas_video_antes_narracao_tts_transcribrothers import (
    validar_cues_janelas_video_antes_narracao_tts_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)

FASE_VIDEO_NARRADO_REMUX_JANELAS_EDITADAS = "video_narrado_remux_janelas_editadas"


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def _diretorio_assets_do_job(data_dir: Path, job_id: str) -> Path:
    return _diretorio_trabalho_job(data_dir, job_id) / "assets_exportados_para_markdown"


async def _atualizar_steps(
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


def validar_pre_requisitos_remux_janelas_editadas_transcribrothers(*, work: Path) -> None:
    try:
        cues = cues_janela_do_manifest_ou_erro_transcribrothers(work)
    except ValueError as e:
        raise ValueError(str(e)) from e
    if not cues:
        raise ValueError("Manifesto de janelas vazio.")
    video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if video is None or not video.is_file():
        raise ValueError("Vídeo de entrada não encontrado para remux.")
    for i in range(len(cues)):
        if obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, i) is None:
            raise ValueError(
                f"Falta o áudio da cue {i + 1}. Gere a narração antes de aplicar os tempos."
            )


async def executar_remux_video_narrado_apos_edicao_janelas_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
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

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_REMUX_JANELAS_EDITADAS
        await _atualizar_steps(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
        )

        cues = cues_janela_do_manifest_ou_erro_transcribrothers(work)
        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        assert video is not None
        duracao_video = await obter_duracao_video_segundos_via_ffprobe(video)
        resultado = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
            cues=cues,
            modo="janelas_editadas_ui",
            quantidade_ancoras_markdown=0,
            quantidade_casadas=sum(1 for c in cues if c.casado),
            quantidade_interpoladas=sum(1 for c in cues if not c.casado),
        )
        validacao = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
            resultado,
            duracao_video_segundos=duracao_video,
        )
        if not validacao.ok:
            raise RuntimeError(validacao.motivo_rejeicao or "Janelas inválidas para remux.")

        caminhos_wav: list[Path] = []
        duracoes: list[float] = []
        for i in range(len(cues)):
            caminho = obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, i)
            if caminho is None:
                raise RuntimeError(f"WAV da cue {i + 1} não encontrado.")
            caminhos_wav.append(caminho)
            duracoes.append(obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho))

        cues_vtt = converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
            list(cues),
            duracoes,
        )
        caminho_vtt = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
            diretorio_assets=assets,
            cues=cues_vtt,
        )
        url_vtt = f"/api/jobs/{job_id}/assets/{caminho_vtt.name}"
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": caminho_vtt.name,
            "url_asset": url_vtt,
            "quantidade_cues": len(cues),
            "timeline": "narracao_tts",
            "janelas_editadas_em": datetime.now(timezone.utc).isoformat(),
        }

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_MUX_FFMPEG
        steps["video_narrado_mux_segmento_indice"] = 0
        steps["video_narrado_mux_segmento_total"] = len(cues)
        await _atualizar_steps(session_factory, job_id, steps=steps)

        async def _progresso_mux(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps(session_factory, job_id, steps=steps)

        segmentos = [
            SegmentoVideoNarradoRetargetTranscribrothers(
                caminho_wav=wav,
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
            )
            for cue, wav in zip(cues, caminhos_wav, strict=True)
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
        )
        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_mp4.name,
            "url_download": url_mp4,
            "modo_montagem": "segmentos_retarget_audio",
            "quantidade_segmentos": len(segmentos),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "remux_janelas_editadas": True,
        }
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS) or {}),
            "ok": True,
            "mensagem": (
                f"Vídeo remontado com janelas de tela editadas ({len(cues)} cue(s); "
                "áudio TTS reutilizado)."
            ),
            "remux_janelas_editadas": True,
            "quantidade_cues": len(cues),
            "nome_arquivo_vtt": caminho_vtt.name,
            "url_asset_vtt": url_vtt,
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
            origem="remux",
        )
        if versao_snap:
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS][
                "versao_video_narrado_id"
            ] = versao_snap
        await _atualizar_steps(
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
            "remux_janelas_editadas": True,
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro,
        )


def agendar_remux_video_narrado_apos_edicao_janelas_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> None:
    asyncio.create_task(
        executar_remux_video_narrado_apos_edicao_janelas_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
        )
    )
