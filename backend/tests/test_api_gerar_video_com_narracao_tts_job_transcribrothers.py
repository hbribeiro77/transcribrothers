"""POST /api/jobs/{id}/gerar-video-com-narracao-tts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
)


def test_gerar_video_com_narracao_job_sem_video_retorna_400() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]
        r = client.post(f"/api/jobs/{job_id}/gerar-video-com-narracao-tts")
    assert r.status_code == 400
    assert "vídeo" in r.text.lower() or "video" in r.text.lower()


def test_gerar_video_com_narracao_sucesso_com_mock(tmp_path: Path) -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        # Injeta vídeo + wav de narração no diretório do job (via patch dos localizadores)
        work = Path("data") / "jobs" / job_id
        # data dir vem da config — descobrir pelo GET não é trivial; mockamos as funções de caminho
        saida_fake = tmp_path / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
        saida_fake.write_bytes(b"mp4")

        video_fake = tmp_path / "video_entrada_arquivo_local.mp4"
        video_fake.write_bytes(b"vid")
        wav_fake = tmp_path / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        wav_fake.write_bytes(b"RIFF")

        with patch(
            "transcribrothers_backend.main._localizar_arquivo_video_entrada_no_diretorio_job",
            return_value=video_fake,
        ), patch(
            "transcribrothers_backend.main._diretorio_assets_png_exportados_markdown_do_job",
            return_value=tmp_path,
        ), patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            return_value=tmp_path,
        ), patch(
            "transcribrothers_backend.main.substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers",
            new_callable=AsyncMock,
            return_value=saida_fake,
        ):
            r = client.post(f"/api/jobs/{job_id}/gerar-video-com-narracao-tts")

        assert r.status_code == 200, r.text
        d = r.json()
        assert d["ok"] is True
        assert d["nome_arquivo"] == NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
        assert "video-com-narracao-tts" in d["url_download"]

        job = client.get(f"/api/jobs/{job_id}").json()
        assert job["steps_json"].get("video_com_narracao_tts", {}).get("nome_arquivo") == (
            NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
        )
