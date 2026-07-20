"""Logs de diagnóstico para upload de vídeo e criação de job (terminal do uvicorn)."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile

_LOGGER_NOME = "transcribrothers.upload_job"
_INTERVALO_LOG_PROGRESSO_BYTES = 50 * 1024 * 1024  # 50 MiB


def obter_logger_upload_video_job_pipeline_transcribrothers() -> logging.Logger:
    return logging.getLogger(_LOGGER_NOME)


def configurar_logging_upload_video_job_pipeline_transcribrothers() -> None:
    """Garante nível INFO no logger do upload (idempotente com outros handlers)."""
    logger = obter_logger_upload_video_job_pipeline_transcribrothers()
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def _formatar_mebibytes(bytes_total: int) -> str:
    return f"{bytes_total / (1024 * 1024):.1f} MiB"


def log_inicio_upload_video_job_transcribrothers(
    *,
    job_id: str,
    destino_apos_transcricao: str,
    nome_arquivo: str,
    max_video_bytes: int,
    data_dir: Path,
    via_staging: bool,
) -> None:
    obter_logger_upload_video_job_pipeline_transcribrothers().info(
        "upload iniciado job_id=%s destino=%s arquivo=%r limite=%s (%s) data_dir=%s staging=%s",
        job_id,
        destino_apos_transcricao,
        nome_arquivo,
        max_video_bytes,
        _formatar_mebibytes(max_video_bytes),
        data_dir,
        via_staging,
    )


def log_fim_gravacao_video_upload_job_transcribrothers(
    *,
    job_id: str,
    destino_video: Path,
    bytes_gravados: int,
    duracao_ffprobe_segundos: float,
) -> None:
    obter_logger_upload_video_job_pipeline_transcribrothers().info(
        "upload gravado job_id=%s caminho=%s bytes=%s (%s) duracao_ffprobe_s=%.3f",
        job_id,
        destino_video,
        bytes_gravados,
        _formatar_mebibytes(bytes_gravados),
        duracao_ffprobe_segundos,
    )


def log_job_upload_registrado_e_pipeline_agendado_transcribrothers(*, job_id: str) -> None:
    obter_logger_upload_video_job_pipeline_transcribrothers().info(
        "upload concluído job_id=%s — registro SQLite OK, pipeline agendado",
        job_id,
    )


def log_erro_upload_video_job_transcribrothers(
    *,
    job_id: str,
    etapa: str,
    exc: BaseException,
) -> None:
    obter_logger_upload_video_job_pipeline_transcribrothers().exception(
        "upload falhou job_id=%s etapa=%s: %s",
        job_id,
        etapa,
        exc,
    )


async def gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
    video: UploadFile,
    destino_video: Path,
    max_video_bytes: int,
    *,
    job_id: str,
) -> int:
    """
    Grava o multipart em disco com limite configurável.
    Emite log de progresso a cada 50 MiB para vídeos longos/grandes.
    """
    logger = obter_logger_upload_video_job_pipeline_transcribrothers()
    chunk_size = 1024 * 1024
    total = 0
    proximo_log_em = _INTERVALO_LOG_PROGRESSO_BYTES
    excedeu_limite = False
    bytes_que_excederiam = 0
    try:
        with destino_video.open("wb") as f:
            while True:
                bloco = await video.read(chunk_size)
                if not bloco:
                    break
                if total + len(bloco) > max_video_bytes:
                    bytes_que_excederiam = total + len(bloco)
                    excedeu_limite = True
                    break
                try:
                    total += len(bloco)
                    f.write(bloco)
                except OSError as e:
                    espaco = shutil.disk_usage(destino_video.parent)
                    logger.error(
                        "upload falha de disco job_id=%s errno=%s livre=%s total=%s caminho=%s",
                        job_id,
                        getattr(e, "errno", None),
                        espaco.free,
                        espaco.total,
                        destino_video,
                    )
                    raise HTTPException(
                        status_code=507,
                        detail=(
                            f"Falha ao gravar o vídeo no servidor ({type(e).__name__}: {e}). "
                            "Verifique espaço em disco em TRANSCRIBROTHERS_DATA_DIR."
                        ),
                    ) from e
                if total >= proximo_log_em:
                    logger.info(
                        "upload progresso job_id=%s bytes=%s (%s) limite=%s (%s)",
                        job_id,
                        total,
                        _formatar_mebibytes(total),
                        max_video_bytes,
                        _formatar_mebibytes(max_video_bytes),
                    )
                    proximo_log_em += _INTERVALO_LOG_PROGRESSO_BYTES
    finally:
        await video.close()

    if excedeu_limite:
        logger.warning(
            "upload excedeu limite job_id=%s bytes_recebidos=%s (%s) limite=%s (%s) — arquivo parcial removido",
            job_id,
            bytes_que_excederiam,
            _formatar_mebibytes(bytes_que_excederiam),
            max_video_bytes,
            _formatar_mebibytes(max_video_bytes),
        )
        destino_video.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=(
                f"Arquivo excede o limite de {max_video_bytes} bytes "
                f"({_formatar_mebibytes(max_video_bytes)}). "
                f"Aumente MAX_VIDEO_BYTES no backend/.env ou use um vídeo menor."
            ),
        )

    return total
