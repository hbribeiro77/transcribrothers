"""Status/cache da geração em background do MP4 com legendas queimadas."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers import (
    NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend import (
    modulo_tarefa_gerar_video_narrado_com_legendas_queimadas_em_background_transcribrothers as mod_tarefa,
)
from transcribrothers_backend.modulo_tarefa_gerar_video_narrado_com_legendas_queimadas_em_background_transcribrothers import (
    consultar_status_video_narrado_com_legendas_queimadas_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def test_status_pronto_quando_cache_atualizado(tmp_path: Path) -> None:
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"v")
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_bytes(b"t")
    (work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS).write_bytes(
        b"out"
    )
    status = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
        job_id="job-teste",
        diretorio_trabalho_job=work,
        diretorio_assets=assets,
    )
    assert status["status"] == "pronto"
    assert status["url_download"]


def test_status_pendente_quando_falta_saida(tmp_path: Path) -> None:
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"v")
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_bytes(b"t")
    status = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
        job_id="job-teste-2",
        diretorio_trabalho_job=work,
        diretorio_assets=assets,
    )
    assert status["status"] == "pendente"


def test_status_gerando_mesmo_com_arquivo_saida_parcial_enquanto_tarefa_ativa(
    tmp_path: Path,
) -> None:
    """Não marcar pronto pelo mtime enquanto o encode ainda está rodando."""
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"v")
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_bytes(b"t")
    # Arquivo parcial “completo” pelo critério de mtime (bug antigo).
    (work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS).write_bytes(
        b"parcial"
    )
    job_id = "job-gerando-parcial"
    tarefa_fake = MagicMock()
    tarefa_fake.done.return_value = False
    mod_tarefa._tarefas_por_job[job_id] = tarefa_fake
    mod_tarefa._inicio_geracao_por_job[job_id] = 123.0
    try:
        status = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
            job_id=job_id,
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
        )
        assert status["status"] == "gerando"
        assert status.get("url_download") is None
    finally:
        mod_tarefa._tarefas_por_job.pop(job_id, None)
        mod_tarefa._inicio_geracao_por_job.pop(job_id, None)


@pytest.mark.asyncio
async def test_agendar_forcar_nao_devolve_pronto_enquanto_gera(tmp_path: Path) -> None:
    work = tmp_path / "work"
    assets = tmp_path / "assets"
    work.mkdir()
    assets.mkdir()
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"v")
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_bytes(b"t")
    (work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS).write_bytes(
        b"cache-antigo"
    )
    job_id = "job-forcar-gerando"
    barreira = asyncio.Event()

    async def _nunca_termina(**_kwargs: object) -> Path:
        await barreira.wait()
        return work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS

    with patch.object(
        mod_tarefa,
        "obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers",
        new=AsyncMock(side_effect=_nunca_termina),
    ):
        status = mod_tarefa.agendar_geracao_video_narrado_com_legendas_queimadas_transcribrothers(
            job_id=job_id,
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
            forcar_regenerar=True,
        )
        assert status["status"] == "gerando"
        status2 = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
            job_id=job_id,
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
        )
        assert status2["status"] == "gerando"
        tarefa = mod_tarefa._tarefas_por_job.get(job_id)
        assert tarefa is not None
        tarefa.cancel()
        with pytest.raises(asyncio.CancelledError):
            await tarefa
        mod_tarefa._tarefas_por_job.pop(job_id, None)
        mod_tarefa._inicio_geracao_por_job.pop(job_id, None)
        mod_tarefa._erro_por_job.pop(job_id, None)
