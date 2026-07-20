"""Gravação de upload com limite de bytes e mensagem 413."""

from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from transcribrothers_backend.modulo_log_diagnostico_upload_video_job_pipeline_transcribrothers import (
    gravar_arquivo_upload_video_com_limite_bytes_transcribrothers,
)


@pytest.mark.asyncio
async def test_gravar_upload_rejeita_acima_do_limite_com_413(tmp_path: Path) -> None:
    destino = tmp_path / "video_entrada_arquivo_local.mp4"
    conteudo = b"x" * (1024 * 1024 + 1)
    upload = UploadFile(filename="grande.mp4", file=BytesIO(conteudo))
    with pytest.raises(HTTPException) as exc:
        await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
            upload,
            destino,
            max_video_bytes=1024 * 1024,
            job_id="job-teste-limite",
        )
    assert exc.value.status_code == 413
    assert "MAX_VIDEO_BYTES" in str(exc.value.detail)
    assert not destino.exists()


@pytest.mark.asyncio
async def test_gravar_upload_grava_ate_o_fim_quando_dentro_do_limite(tmp_path: Path) -> None:
    destino = tmp_path / "video_entrada_arquivo_local.webm"
    conteudo = b"\x1a\x45\xdf\xa3" + b"\x00" * 4096
    upload = UploadFile(filename="ok.webm", file=BytesIO(conteudo))
    total = await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
        upload,
        destino,
        max_video_bytes=1024 * 1024,
        job_id="job-teste-ok",
    )
    assert total == len(conteudo)
    assert destino.read_bytes() == conteudo
