"""Decide se vídeo/áudio já no disco do job podem ser reutilizados em retry (evita ffmpeg desnecessário)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_TAMANHO_MINIMO_VIDEO_ENTRADA_BYTES = 1024
_TAMANHO_MINIMO_AUDIO_WAV_BYTES = 1024
_TAMANHO_MINIMO_AUDIO_INLINE_MULTIMODAL_BYTES = 256

_CHAVES_ERRO_PIPELINE_STEPS = frozenset(
    {"error_traceback", "error_type", "error_repr"},
)


def steps_json_job_para_reexecucao_pipeline_transcribrothers(
    steps_json: dict[str, Any] | None,
) -> dict[str, Any]:
    """Carrega steps anteriores do job, removendo apenas campos de erro da última falha."""
    base = dict(steps_json or {})
    for k in _CHAVES_ERRO_PIPELINE_STEPS:
        base.pop(k, None)
    return base


def caminho_midia_existe_e_tem_tamanho_minimo_transcribrothers(
    caminho: Path,
    *,
    min_bytes: int,
) -> bool:
    try:
        return caminho.is_file() and caminho.stat().st_size >= int(min_bytes)
    except OSError:
        return False


def deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers(
    caminho_video: Path,
    steps: dict[str, Any],
) -> bool:
    if not caminho_midia_existe_e_tem_tamanho_minimo_transcribrothers(
        caminho_video,
        min_bytes=_TAMANHO_MINIMO_VIDEO_ENTRADA_BYTES,
    ):
        return False
    return bool(steps.get("download_ok") or steps.get("upload_ok"))


def deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(
    caminho_audio_wav: Path,
    steps: dict[str, Any],
) -> bool:
    if not caminho_midia_existe_e_tem_tamanho_minimo_transcribrothers(
        caminho_audio_wav,
        min_bytes=_TAMANHO_MINIMO_AUDIO_WAV_BYTES,
    ):
        return False
    return bool(steps.get("audio_ok"))


def deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers(
    caminho_audio_inline: Path,
    *,
    formato_audio_inline: str,
    audio_bitrate_kbps: int,
    audio_mono: bool,
    steps: dict[str, Any],
) -> bool:
    if not caminho_midia_existe_e_tem_tamanho_minimo_transcribrothers(
        caminho_audio_inline,
        min_bytes=_TAMANHO_MINIMO_AUDIO_INLINE_MULTIMODAL_BYTES,
    ):
        return False
    if not steps.get("transcricao_multimodal_audio_codificado_ok"):
        return False
    if str(steps.get("transcricao_multimodal_formato_audio_inline") or "").strip().lower() != str(
        formato_audio_inline or ""
    ).strip().lower():
        return False
    if int(steps.get("transcricao_multimodal_audio_bitrate_kbps") or 0) != int(audio_bitrate_kbps):
        return False
    if bool(steps.get("transcricao_multimodal_audio_mono")) != bool(audio_mono):
        return False
    return True
