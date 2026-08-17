"""Resumo de debug: cache de segmentos MP4 do vídeo narrado + último mux nos steps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_calcular_tamanho_bytes_diretorio_job_pipeline_transcribrothers import (
    calcular_tamanho_bytes_diretorio_recursivo_transcribrothers,
)
from transcribrothers_backend.modulo_inventario_midia_fonte_e_cache_job_transcribrothers import (
    NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS,
    calcular_cache_bytes_regeneravel_job_transcribrothers,
)

NOME_PASTA_SEGMENTOS_VIDEO_NARRADO_RETARGET_TRANSCRIBROTHERS = "segmentos_video_narrado_retarget"


def _numero_int_ou_none(valor: Any) -> int | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return int(valor)
    if isinstance(valor, float) and valor == int(valor):
        return int(valor)
    if isinstance(valor, str) and valor.strip().lstrip("-").isdigit():
        return int(valor.strip())
    return None


def extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers(
    steps: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Campos do último (ou em andamento) mux por segmentos, se houver indício nos steps."""
    if not isinstance(steps, dict) or not steps:
        return None
    total = _numero_int_ou_none(steps.get("video_narrado_mux_segmento_total"))
    hits = _numero_int_ou_none(steps.get("video_narrado_mux_segmentos_cache"))
    bloco_video = steps.get("video_com_narracao_tts")
    modo = None
    gerado_em = None
    quantidade_meta = None
    if isinstance(bloco_video, dict):
        modo_raw = bloco_video.get("modo_montagem")
        modo = modo_raw if isinstance(modo_raw, str) else None
        gerado_raw = bloco_video.get("gerado_em")
        gerado_em = gerado_raw if isinstance(gerado_raw, str) else None
        quantidade_meta = _numero_int_ou_none(bloco_video.get("quantidade_segmentos"))
    if total is None:
        total = quantidade_meta
    tem_sinal = (
        total is not None
        or hits is not None
        or modo is not None
        or isinstance(steps.get("video_narrado_mux_fase"), str)
    )
    if not tem_sinal:
        return None
    return {
        "hits_cache": hits,
        "total_segmentos": total,
        "fase_mux": steps.get("video_narrado_mux_fase")
        if isinstance(steps.get("video_narrado_mux_fase"), str)
        else None,
        "paralelismo": _numero_int_ou_none(steps.get("video_narrado_mux_paralelismo")),
        "resolucao": steps.get("video_narrado_mux_encode_resolucao")
        if isinstance(steps.get("video_narrado_mux_encode_resolucao"), str)
        else None,
        "fps": _numero_int_ou_none(steps.get("video_narrado_mux_encode_fps")),
        "modo_montagem": modo,
        "gerado_em": gerado_em,
        "pipeline_fase": steps.get("pipeline_fase")
        if isinstance(steps.get("pipeline_fase"), str)
        else None,
    }


def inventariar_pasta_cache_segmentos_video_narrado_do_work_transcribrothers(
    work: Path,
) -> dict[str, Any]:
    pasta = work / NOME_PASTA_SEGMENTOS_VIDEO_NARRADO_RETARGET_TRANSCRIBROTHERS
    existe = pasta.is_dir()
    quantidade_mp4 = 0
    bytes_pasta = 0
    if existe:
        bytes_pasta = calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(pasta)
        for p in pasta.iterdir():
            if p.is_file() and p.suffix.lower() == ".mp4":
                quantidade_mp4 += 1
    return {
        "nome_pasta": NOME_PASTA_SEGMENTOS_VIDEO_NARRADO_RETARGET_TRANSCRIBROTHERS,
        "pasta_existe": existe,
        "quantidade_mp4": quantidade_mp4,
        "bytes_pasta": int(bytes_pasta),
        "tem_cache_segmentos": existe and quantidade_mp4 > 0,
    }


def extrair_resumo_edicoes_modal_dos_steps_json_transcribrothers(
    steps: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Métricas da última (ou atual) corrida «Gerar vídeo com estas edições»."""
    if not isinstance(steps, dict) or not steps:
        return None
    cues_sujas = _numero_int_ou_none(steps.get("video_narrado_edicoes_modal_cues_sujas"))
    wavs_reusados = _numero_int_ou_none(steps.get("video_narrado_edicoes_modal_wavs_reusados"))
    origem = steps.get("pipeline_origem_corrida")
    origem_str = origem if isinstance(origem, str) else None
    if cues_sujas is None and wavs_reusados is None and origem_str != "edicoes_modal":
        return None
    hits = _numero_int_ou_none(steps.get("video_narrado_mux_segmentos_cache"))
    total = _numero_int_ou_none(steps.get("video_narrado_mux_segmento_total"))
    return {
        "origem_corrida": origem_str,
        "cues_sujas": cues_sujas,
        "wavs_reusados": wavs_reusados,
        "pipeline_fase": steps.get("pipeline_fase")
        if isinstance(steps.get("pipeline_fase"), str)
        else None,
        "mux_hits_cache": hits,
        "mux_total_segmentos": total,
    }


def montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers(
    work: Path,
    *,
    steps: dict[str, Any] | None,
) -> dict[str, Any]:
    pasta_info = inventariar_pasta_cache_segmentos_video_narrado_do_work_transcribrothers(work)
    return {
        "segmentos": pasta_info,
        "cache_bytes_total_regeneravel": calcular_cache_bytes_regeneravel_job_transcribrothers(
            work
        ),
        "pastas_cache_regeneravel": list(NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS),
        "ultimo_mux": extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers(
            steps
        ),
        "edicoes_modal": extrair_resumo_edicoes_modal_dos_steps_json_transcribrothers(steps),
    }
