"""Captura um frame do vídeo do job no instante solicitado e grava PNG em assets."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_constante_chave_steps_json_frames_manuais_capturados_video_tutorial_transcribrothers import (
    CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
    PREFIXO_NOME_ARQUIVO_FRAME_MANUAL_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    capturar_frames_png_do_video_nos_timestamps_segundos,
    limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_util_formatar_timestamp_segundos_para_snippet_markdown_link_temporal_transcribrothers import (
    montar_snippet_markdown_insercao_frame_manual_video_tutorial_transcribrothers,
)


def listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(
    steps_json: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not steps_json:
        return []
    raw = steps_json.get(CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS)
    if not isinstance(raw, list):
        return []
    saida: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            saida.append(dict(item))
    return saida


def proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers(
    steps_json: dict[str, Any] | None,
) -> int:
    return len(listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(steps_json))


def mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers(
    steps_json: dict[str, Any],
    *,
    timestamp_segundos_solicitado: float,
    timestamp_segundos_efetivo: float,
    nome_arquivo: str,
    caminho_relativo: str,
    origem: str | None = None,
) -> dict[str, Any]:
    novo = dict(steps_json)
    lista = listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(novo)
    registro: dict[str, Any] = {
        "timestamp_segundos_solicitado": float(timestamp_segundos_solicitado),
        "timestamp_segundos_efetivo": float(timestamp_segundos_efetivo),
        "nome_arquivo": nome_arquivo,
        "caminho_relativo": caminho_relativo,
        "capturado_em": datetime.now(timezone.utc).isoformat(),
    }
    if origem:
        registro["origem"] = origem
    lista.append(registro)
    novo[CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS] = lista
    return novo


async def capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers(
    *,
    caminho_video: Path,
    diretorio_trabalho_job: Path,
    timestamp_segundos_solicitado: float,
    indice_nome_arquivo: int,
    largura_maxima_saida_pixeis: int | None = None,
) -> tuple[float, str, str, str]:
    """
    Extrai PNG via ffmpeg, copia para `assets_exportados_para_markdown/`.

    Retorna: (timestamp_efetivo, nome_arquivo, caminho_relativo assets/..., snippet_markdown).
    """
    dur = await obter_duracao_video_segundos_via_ffprobe(caminho_video)
    t_efetivo = limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
        float(timestamp_segundos_solicitado),
        dur,
    )
    frames_dir = diretorio_trabalho_job / "frames_manuais_captura_usuario"
    assets_dir = diretorio_trabalho_job / "assets_exportados_para_markdown"
    paths = await capturar_frames_png_do_video_nos_timestamps_segundos(
        caminho_video=caminho_video,
        timestamps_segundos=[t_efetivo],
        diretorio_saida_frames=frames_dir,
        prefixo_nome_arquivo_longo_descritivo=PREFIXO_NOME_ARQUIVO_FRAME_MANUAL_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
        largura_maxima_saida_pixeis=largura_maxima_saida_pixeis,
        deslocamento_indice_nome_arquivo=indice_nome_arquivo,
    )
    if not paths:
        raise RuntimeError("ffmpeg não gerou PNG para o frame manual solicitado.")
    origem = paths[0]
    assets_dir.mkdir(parents=True, exist_ok=True)
    destino = assets_dir / origem.name
    shutil.copy2(origem, destino)
    caminho_relativo = f"assets/{destino.name}"
    snippet = montar_snippet_markdown_insercao_frame_manual_video_tutorial_transcribrothers(
        caminho_relativo_assets=caminho_relativo,
        timestamp_segundos=t_efetivo,
    )
    return t_efetivo, destino.name, caminho_relativo, snippet
