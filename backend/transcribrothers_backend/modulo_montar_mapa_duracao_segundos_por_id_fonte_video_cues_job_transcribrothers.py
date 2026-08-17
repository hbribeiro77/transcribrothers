"""Monta mapa id_fonte_video → duração (ffprobe) para validar janelas por origem."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_biblioteca_midias_tela_job_transcribrothers import (
    ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
    ErroBibliotecaMidiasTelaTranscribrothers,
    normalizar_id_fonte_video_transcribrothers,
    resolver_caminho_video_fonte_por_id_no_work_transcribrothers,
)


async def montar_mapa_duracao_segundos_por_id_fonte_video_das_cues_job_transcribrothers(
    *,
    work: Path,
    cues_ou_ids_fonte: Sequence[Any],
    caminho_video_entrada: Path,
    duracao_video_entrada_segundos: float,
) -> dict[str, float]:
    """
    Para cada id de origem distinto nas cues, resolve o Path e obtém a duração.
    `cues_ou_ids_fonte` aceita objetos com `id_fonte_video` ou strings.
    """
    ids: set[str] = set()
    for item in cues_ou_ids_fonte:
        if isinstance(item, str):
            ids.add(normalizar_id_fonte_video_transcribrothers(item))
        else:
            ids.add(
                normalizar_id_fonte_video_transcribrothers(
                    str(getattr(item, "id_fonte_video", "") or "")
                )
            )
    if not ids:
        ids.add(ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS)

    mapa: dict[str, float] = {
        ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS: float(duracao_video_entrada_segundos),
    }
    for id_fonte in sorted(ids):
        if id_fonte == ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS:
            continue
        try:
            caminho = resolver_caminho_video_fonte_por_id_no_work_transcribrothers(
                work=work,
                id_fonte_video=id_fonte,
                caminho_video_entrada=caminho_video_entrada,
            )
        except ErroBibliotecaMidiasTelaTranscribrothers:
            continue
        if not caminho.is_file():
            continue
        dur = await obter_duracao_video_segundos_via_ffprobe(caminho)
        if dur > 0:
            mapa[id_fonte] = float(dur)
    return mapa
