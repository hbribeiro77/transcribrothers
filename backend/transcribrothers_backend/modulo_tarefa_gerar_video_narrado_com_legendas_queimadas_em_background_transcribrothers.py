"""Gera MP4 com legendas queimadas em background (não bloqueia o request HTTP)."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, Literal

from transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers import (
    NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS,
    obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers,
    video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)

StatusQueimaLegendasTranscribrothers = Literal["pronto", "gerando", "pendente", "erro"]

_tarefas_por_job: dict[str, asyncio.Task[None]] = {}
_erro_por_job: dict[str, str] = {}
_inicio_geracao_por_job: dict[str, float] = {}
_progresso_percentual_por_job: dict[str, float] = {}


def _caminhos_queima_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    diretorio_assets: Path,
) -> tuple[Path, Path, Path]:
    video = diretorio_trabalho_job / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    vtt = diretorio_assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    saida = (
        diretorio_trabalho_job / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS
    )
    return video, vtt, saida


def consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
    *,
    job_id: str,
    diretorio_trabalho_job: Path,
    diretorio_assets: Path,
) -> dict[str, Any]:
    video, vtt, saida = _caminhos_queima_transcribrothers(
        diretorio_trabalho_job=diretorio_trabalho_job,
        diretorio_assets=diretorio_assets,
    )
    if not video.is_file():
        return {
            "status": "erro",
            "erro": "Vídeo com narração ainda não foi gerado.",
            "url_download": None,
        }
    if not vtt.is_file():
        return {
            "status": "erro",
            "erro": "Legendas VTT ainda não foram geradas.",
            "url_download": None,
        }

    # Tarefa ativa tem prioridade sobre cache/mtime: durante o encode o ficheiro
    # parcial (ou o cache antigo) não deve ser exposto como "pronto".
    tarefa = _tarefas_por_job.get(job_id)
    if tarefa is not None and not tarefa.done():
        inicio = _inicio_geracao_por_job.get(job_id)
        decorrido = (time.time() - inicio) if isinstance(inicio, (int, float)) else None
        return {
            "status": "gerando",
            "erro": None,
            "url_download": None,
            "iniciado_em_epoch": inicio,
            "progresso_percentual": _progresso_percentual_por_job.get(job_id),
            "tempo_decorrido_segundos": round(decorrido, 1) if decorrido is not None else None,
        }

    if video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
        caminho_video_mp4=video,
        caminho_vtt=vtt,
        caminho_saida=saida,
    ):
        _erro_por_job.pop(job_id, None)
        return {
            "status": "pronto",
            "erro": None,
            "url_download": f"/api/jobs/{job_id}/video-com-narracao-tts-com-legendas-queimadas",
            "progresso_percentual": 100.0,
        }

    if job_id in _erro_por_job:
        return {
            "status": "erro",
            "erro": _erro_por_job[job_id],
            "url_download": None,
        }

    return {
        "status": "pendente",
        "erro": None,
        "url_download": None,
    }


async def _executar_geracao_em_background_transcribrothers(
    *,
    job_id: str,
    diretorio_trabalho_job: Path,
    diretorio_assets: Path,
    forcar_regenerar: bool,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> None:
    async def _on_pct(pct: float) -> None:
        _progresso_percentual_por_job[job_id] = float(pct)

    try:
        _progresso_percentual_por_job[job_id] = 0.0
        await obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers(
            diretorio_trabalho_job=diretorio_trabalho_job,
            diretorio_assets=diretorio_assets,
            forcar_regenerar=forcar_regenerar,
            preferencias_encode=preferencias_encode
            or preferencias_encode_video_narrado_padrao_transcribrothers(),
            on_percentual_progresso=_on_pct,
        )
        _progresso_percentual_por_job[job_id] = 100.0
        _erro_por_job.pop(job_id, None)
    except Exception as e:
        _erro_por_job[job_id] = str(e)
    finally:
        _inicio_geracao_por_job.pop(job_id, None)
        # Mantém o último % um pouco para o último poll; limpa ao terminar a tarefa.
        atual = _tarefas_por_job.get(job_id)
        if atual is not None and atual.done():
            _tarefas_por_job.pop(job_id, None)
        _progresso_percentual_por_job.pop(job_id, None)


def agendar_geracao_video_narrado_com_legendas_queimadas_transcribrothers(
    *,
    job_id: str,
    diretorio_trabalho_job: Path,
    diretorio_assets: Path,
    forcar_regenerar: bool = False,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> dict[str, Any]:
    """
    Se o cache já está pronto, devolve pronto.
    Se já há tarefa, devolve gerando.
    Senão agenda asyncio.Task e devolve gerando.
    """
    status = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
        job_id=job_id,
        diretorio_trabalho_job=diretorio_trabalho_job,
        diretorio_assets=diretorio_assets,
    )
    if status["status"] == "pronto" and not forcar_regenerar:
        return status
    if status["status"] == "gerando":
        return status

    video, vtt, _saida = _caminhos_queima_transcribrothers(
        diretorio_trabalho_job=diretorio_trabalho_job,
        diretorio_assets=diretorio_assets,
    )
    if not video.is_file():
        return {
            "status": "erro",
            "erro": "Vídeo com narração ainda não foi gerado.",
            "url_download": None,
        }
    if not vtt.is_file():
        return {
            "status": "erro",
            "erro": "Legendas VTT ainda não foram geradas.",
            "url_download": None,
        }

    _erro_por_job.pop(job_id, None)
    _inicio_geracao_por_job[job_id] = time.time()
    _progresso_percentual_por_job[job_id] = 0.0
    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    tarefa = asyncio.create_task(
        _executar_geracao_em_background_transcribrothers(
            job_id=job_id,
            diretorio_trabalho_job=diretorio_trabalho_job,
            diretorio_assets=diretorio_assets,
            forcar_regenerar=forcar_regenerar,
            preferencias_encode=prefs,
        )
    )
    _tarefas_por_job[job_id] = tarefa
    return {
        "status": "gerando",
        "erro": None,
        "url_download": None,
        "iniciado_em_epoch": _inicio_geracao_por_job.get(job_id),
        "progresso_percentual": 0.0,
        "tempo_decorrido_segundos": 0.0,
    }
