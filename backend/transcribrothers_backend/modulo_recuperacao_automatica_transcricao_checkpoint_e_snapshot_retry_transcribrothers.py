"""Recuperação automática: snapshot final, checkpoint multimodal completo ou retomada parcial."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
    caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers,
    carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers,
    dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
    normalizar_backend_transcricao_audio_configurado,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers import (
    listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers,
    mesclar_resultados_transcricao_com_offset_temporal_segundos_transcribrothers,
)


def resolver_caminho_audio_fonte_transcricao_multimodal_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
    caminho_audio_wav: Path,
    *,
    formato_audio_inline: str,
) -> Path:
    fmt = str(formato_audio_inline or "wav").strip().lower()
    if fmt == "mp3":
        return diretorio_trabalho_job / "audio_extraido_para_transcricao_multimodal_inline.mp3"
    if fmt == "opus":
        return diretorio_trabalho_job / "audio_extraido_para_transcricao_multimodal_inline.opus"
    if fmt == "aac":
        return diretorio_trabalho_job / "audio_extraido_para_transcricao_multimodal_inline.m4a"
    return caminho_audio_wav


def carregar_checkpoint_multimodal_bruto_do_work_se_existir_transcribrothers(
    diretorio_trabalho_job: Path,
) -> dict[str, Any] | None:
    path = caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers(
        diretorio_trabalho_job
    )
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def contar_janelas_concluidas_no_checkpoint_multimodal_bruto_transcribrothers(
    raw: dict[str, Any],
) -> tuple[int, int]:
    """Retorna (concluídas, total_esperado) a partir do JSON bruto do checkpoint."""
    total = int(raw.get("total_janelas") or 0)
    jc = raw.get("janelas_concluidas")
    if not isinstance(jc, dict):
        return 0, total
    return len(jc), total


def mesclar_mapa_janelas_checkpoint_em_resultado_transcricao_transcribrothers(
    mapa_janelas: dict[int, ResultadoTranscricaoComSegmentos],
    *,
    janela_segundos: float,
    duracao_audio_segundos: float,
) -> ResultadoTranscricaoComSegmentos:
    janelas_temporais = listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers(
        float(duracao_audio_segundos),
        float(janela_segundos),
    )
    parciais: list[tuple[float, ResultadoTranscricaoComSegmentos]] = []
    for indice in sorted(mapa_janelas.keys()):
        if 0 <= indice < len(janelas_temporais):
            offset = float(janelas_temporais[indice][0])
        else:
            offset = float(indice) * float(janela_segundos)
        parciais.append((offset, mapa_janelas[indice]))
    return mesclar_resultados_transcricao_com_offset_temporal_segundos_transcribrothers(parciais)


def tentar_mesclar_transcricao_de_checkpoint_multimodal_bruto_se_todas_janelas_concluidas_transcribrothers(
    raw: dict[str, Any],
    *,
    duracao_audio_ffprobe: float,
) -> ResultadoTranscricaoComSegmentos | None:
    concluidas, total = contar_janelas_concluidas_no_checkpoint_multimodal_bruto_transcribrothers(raw)
    if total <= 0 or concluidas < total:
        return None
    janela_seg = float(raw.get("janela_segundos") or 30.0)
    jc = raw.get("janelas_concluidas")
    if not isinstance(jc, dict):
        return None
    mapa: dict[int, ResultadoTranscricaoComSegmentos] = {}
    for chave, valor in jc.items():
        try:
            indice = int(chave)
        except (TypeError, ValueError):
            continue
        if not isinstance(valor, dict):
            continue
        mapa[indice] = dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers(valor)
    if len(mapa) < total:
        return None
    return mesclar_mapa_janelas_checkpoint_em_resultado_transcricao_transcribrothers(
        mapa,
        janela_segundos=janela_seg,
        duracao_audio_segundos=float(duracao_audio_ffprobe),
    )


async def tentar_recuperar_transcricao_automatica_antes_de_reexecutar_pipeline_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    caminho_audio_wav: Path,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    configuracao_exec_transcricao_mm: ConfiguracaoAmbienteTranscribrothers,
    steps: dict[str, Any],
) -> tuple[ResultadoTranscricaoComSegmentos | None, dict[str, Any]]:
    """
    Ordem: snapshot em disco → checkpoint multimodal com todas as janelas → None (caller transcreve/retoma parcial).

    Retorna (transcrição ou None, metadados para steps_json).
    """
    meta: dict[str, Any] = {}

    snapshot = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
    if snapshot is not None:
        meta["transcricao_recuperacao_automatica"] = "snapshot_finalizada_em_disco"
        meta["transcricao_reutilizada_snapshot_retry"] = True
        return snapshot, meta

    backend_tr = normalizar_backend_transcricao_audio_configurado(configuracao)
    if backend_tr != TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO:
        return None, meta

    fmt_mm = str(
        configuracao_exec_transcricao_mm.transcricao_multimodal_formato_audio_inline or "wav"
    ).strip().lower()
    if fmt_mm not in ("wav", "mp3", "opus", "aac"):
        fmt_mm = "wav"
    mono_mm = bool(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_mono)
    br_mm = int(configuracao_exec_transcricao_mm.transcricao_multimodal_audio_bitrate_kbps)
    janela_seg = float(configuracao_exec_transcricao_mm.transcricao_multimodal_janela_segundos)
    modelo_tr = resolver_modelo_para_transcricao_litellm_multimodal_audio(configuracao) or ""

    audio_fonte = resolver_caminho_audio_fonte_transcricao_multimodal_no_work_transcribrothers(
        diretorio_trabalho_job,
        caminho_audio_wav,
        formato_audio_inline=fmt_mm,
    )
    if not audio_fonte.is_file():
        audio_fonte = caminho_audio_wav
    if not audio_fonte.is_file():
        return None, meta

    dur_audio = await obter_duracao_video_segundos_via_ffprobe(audio_fonte)
    if dur_audio <= 0:
        dur_audio = float(steps.get("duracao_video_segundos") or 0.0)

    janelas_mm = listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers(
        float(dur_audio) if dur_audio > 0 else 1.0,
        float(janela_seg),
    )
    total_janelas = len(janelas_mm)

    carregado_ck = carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers(
        diretorio_trabalho_job,
        caminho_audio_fonte=audio_fonte,
        janela_segundos=float(janela_seg),
        formato_audio_inline=str(fmt_mm),
        audio_bitrate_kbps=int(br_mm),
        audio_mono=bool(mono_mm),
        modelo_transcricao=str(modelo_tr).strip(),
        duracao_audio_ffprobe_atual=float(dur_audio),
        total_janelas_esperado=int(total_janelas),
    )
    if carregado_ck is not None:
        mapa_janelas, _regs = carregado_ck
        if len(mapa_janelas) >= total_janelas:
            resultado = mesclar_mapa_janelas_checkpoint_em_resultado_transcricao_transcribrothers(
                mapa_janelas,
                janela_segundos=float(janela_seg),
                duracao_audio_segundos=float(dur_audio) if dur_audio > 0 else 1.0,
            )
            gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(
                diretorio_trabalho_job,
                resultado,
            )
            meta["transcricao_recuperacao_automatica"] = "checkpoint_multimodal_completo_validado"
            meta["transcricao_reutilizada_checkpoint_completo_retry"] = True
            meta["transcricao_multimodal_checkpoint_trechos_salvos"] = len(mapa_janelas)
            return resultado, meta

    raw = carregar_checkpoint_multimodal_bruto_do_work_se_existir_transcribrothers(diretorio_trabalho_job)
    if raw is not None:
        if int(raw.get("versao", 0)) == CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS:
            concluidas, total_ck = contar_janelas_concluidas_no_checkpoint_multimodal_bruto_transcribrothers(raw)
            if total_ck > 0 and concluidas >= total_ck:
                resultado_bruto = (
                    tentar_mesclar_transcricao_de_checkpoint_multimodal_bruto_se_todas_janelas_concluidas_transcribrothers(
                        raw,
                        duracao_audio_ffprobe=float(dur_audio) if dur_audio > 0 else 1.0,
                    )
                )
                if resultado_bruto is not None:
                    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(
                        diretorio_trabalho_job,
                        resultado_bruto,
                    )
                    meta["transcricao_recuperacao_automatica"] = "checkpoint_multimodal_completo_bruto"
                    meta["transcricao_reutilizada_checkpoint_completo_retry"] = True
                    return resultado_bruto, meta

            if 0 < concluidas < total_ck:
                meta["transcricao_recuperacao_automatica"] = "checkpoint_multimodal_parcial"
                meta["transcricao_multimodal_retomada_trechos"] = concluidas
                meta["transcricao_multimodal_mensagem_retomada"] = (
                    f"Recuperação automática: retomando transcrição com {concluidas} de {total_ck} "
                    "trecho(s) já salvos no checkpoint."
                )

    return None, meta
