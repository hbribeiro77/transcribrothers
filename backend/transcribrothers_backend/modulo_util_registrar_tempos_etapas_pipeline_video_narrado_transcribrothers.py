"""Registra duração de cada etapa do pipeline de vídeo narrado em `steps_json`."""

from __future__ import annotations

import time
from typing import Any

CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS = "pipeline_tempos_video_narrado"

_MAPA_FASE_PARA_ETAPA_TEMPO_TRANSCRIBROTHERS: dict[str, str] = {
    "video_narrado_alinhando_legendas": "alinhamento_legendas",
    "video_narrado_validando_legendas": "validacao_legendas",
    "video_narrado_limpando_legendas_ia": "limpeza_legendas_ia",
    "video_narrado_gerando_tts": "narracao_tts",
    "video_narrado_mux_ffmpeg": "mux_video",
    "video_narrado_remux_janelas_editadas": "mux_video",
    "video_narrado_gerando_com_edicoes_modal": "narracao_tts",
}


def mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers(fase: str) -> str | None:
    return _MAPA_FASE_PARA_ETAPA_TEMPO_TRANSCRIBROTHERS.get((fase or "").strip())


def _bloco_tempos_mutavel_transcribrothers(steps: dict[str, Any]) -> dict[str, Any]:
    bruto = steps.get(CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS)
    if isinstance(bruto, dict):
        bloco = bruto
    else:
        bloco = {}
        steps[CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS] = bloco
    if not isinstance(bloco.get("etapas"), dict):
        bloco["etapas"] = {}
    return bloco


def fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(
    steps: dict[str, Any],
    *,
    agora_epoch: float | None = None,
) -> None:
    """Fecha a etapa em andamento (se houver) e atualiza `total_segundos`."""
    bloco = _bloco_tempos_mutavel_transcribrothers(steps)
    etapa_atual = bloco.get("etapa_atual")
    if not isinstance(etapa_atual, str) or not etapa_atual.strip():
        _recalcular_total_pipeline_tempos_video_narrado_transcribrothers(bloco)
        return
    agora = float(time.time() if agora_epoch is None else agora_epoch)
    etapas: dict[str, Any] = bloco["etapas"]
    info = etapas.get(etapa_atual)
    if not isinstance(info, dict):
        info = {}
        etapas[etapa_atual] = info
    inicio = info.get("inicio_epoch")
    if isinstance(inicio, (int, float)):
        dur = max(0.0, round(agora - float(inicio), 2))
        info["duracao_segundos"] = dur
        info["fim_epoch"] = agora
    bloco["etapa_atual"] = None
    _recalcular_total_pipeline_tempos_video_narrado_transcribrothers(bloco)


def iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
    steps: dict[str, Any],
    *,
    etapa_id: str,
    agora_epoch: float | None = None,
) -> None:
    """Fecha a etapa atual (se diferente) e inicia a nova."""
    etapa = (etapa_id or "").strip()
    if not etapa:
        return
    bloco = _bloco_tempos_mutavel_transcribrothers(steps)
    agora = float(time.time() if agora_epoch is None else agora_epoch)
    if bloco.get("inicio_epoch") is None:
        bloco["inicio_epoch"] = agora
    atual = bloco.get("etapa_atual")
    if isinstance(atual, str) and atual.strip() and atual != etapa:
        fechar_etapa_atual_pipeline_tempos_video_narrado_transcribrothers(
            steps,
            agora_epoch=agora,
        )
        bloco = _bloco_tempos_mutavel_transcribrothers(steps)
    elif atual == etapa and isinstance(bloco["etapas"].get(etapa), dict):
        # Mesma etapa já em andamento: não reinicia o relógio.
        return
    bloco["etapas"][etapa] = {"inicio_epoch": agora}
    bloco["etapa_atual"] = etapa
    _recalcular_total_pipeline_tempos_video_narrado_transcribrothers(bloco)


def iniciar_etapa_pela_fase_pipeline_video_narrado_transcribrothers(
    steps: dict[str, Any],
    *,
    fase: str,
    agora_epoch: float | None = None,
) -> None:
    etapa = mapear_fase_pipeline_para_id_etapa_tempo_transcribrothers(fase)
    if etapa is None:
        return
    iniciar_etapa_pipeline_tempos_video_narrado_transcribrothers(
        steps,
        etapa_id=etapa,
        agora_epoch=agora_epoch,
    )


def total_segundos_pipeline_tempos_video_narrado_transcribrothers(steps: dict[str, Any]) -> float:
    bloco = steps.get(CHAVE_STEPS_PIPELINE_TEMPOS_VIDEO_NARRADO_TRANSCRIBROTHERS)
    if not isinstance(bloco, dict):
        return 0.0
    total = bloco.get("total_segundos")
    if isinstance(total, (int, float)):
        return float(total)
    return _somar_duracoes_etapas_transcribrothers(bloco)


def _somar_duracoes_etapas_transcribrothers(bloco: dict[str, Any]) -> float:
    etapas = bloco.get("etapas")
    if not isinstance(etapas, dict):
        return 0.0
    soma = 0.0
    for info in etapas.values():
        if not isinstance(info, dict):
            continue
        dur = info.get("duracao_segundos")
        if isinstance(dur, (int, float)):
            soma += float(dur)
    return round(soma, 2)


def _recalcular_total_pipeline_tempos_video_narrado_transcribrothers(bloco: dict[str, Any]) -> None:
    bloco["total_segundos"] = _somar_duracoes_etapas_transcribrothers(bloco)
