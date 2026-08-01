"""API de versões do vídeo narrado (listar / servir / tornar-atual / apagar)."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
    criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def _criar_job_com_work(tmp_path: Path) -> tuple[str, Path, Path]:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

    work = tmp_path / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    work.mkdir(parents=True)
    assets.mkdir(parents=True)
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"MP4-API" + b"x" * 200)
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
        "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOi\n",
        encoding="utf-8",
    )
    (assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS).write_bytes(b"RIFF" + b"\0" * 100)

    async def _status() -> None:
        async with app.state.session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            assert row is not None
            row.status = "completed"
            await session.commit()

    asyncio.run(_status())
    return job_id, work, assets


def test_api_listar_tornar_atual_e_apagar_versoes_video_narrado(tmp_path: Path) -> None:
    job_id, work, assets = _criar_job_com_work(tmp_path)
    with (
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._gerar_thumbnail_jpg_do_mp4_transcribrothers",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._obter_duracao_video_segundos_via_ffprobe_sync",
            return_value=9.0,
        ),
        patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            side_effect=lambda _data_dir, jid: tmp_path / "jobs" / jid,
        ),
        patch(
            "transcribrothers_backend.main._diretorio_assets_png_exportados_markdown_do_job",
            side_effect=lambda _data_dir, jid: tmp_path / "jobs" / jid / "assets_exportados_para_markdown",
        ),
    ):
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="pipeline_completo",
        )
        (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"MP4-API2" + b"y" * 200)
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="edicoes_modal",
        )

        with TestClient(app) as client:
            lista = client.get(f"/api/jobs/{job_id}/videos-narrados")
            assert lista.status_code == 200
            corpo = lista.json()
            assert corpo["versao_atual_id"] == "v0002"
            assert len(corpo["versoes"]) == 2

            mp4 = client.get(
                f"/api/jobs/{job_id}/videos-narrados/v0001/arquivo/{NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS}"
            )
            assert mp4.status_code == 200
            assert mp4.content.startswith(b"MP4-API")

            tornar = client.post(f"/api/jobs/{job_id}/videos-narrados/v0001/tornar-atual")
            assert tornar.status_code == 200
            steps = tornar.json()["steps_json"]
            assert steps["video_com_narracao_tts"]["restaurado_de_versao"] == "v0001"
            assert (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).read_bytes().startswith(
                b"MP4-API"
            )

            ok_del_atual = client.delete(f"/api/jobs/{job_id}/videos-narrados/v0001")
            assert ok_del_atual.status_code == 200
            corpo_del = ok_del_atual.json()
            assert corpo_del["versao_atual_id"] == "v0002"
            assert [v["id"] for v in corpo_del["versoes"]] == ["v0002"]
            assert "job" in corpo_del

            ok_del_ultima = client.delete(f"/api/jobs/{job_id}/videos-narrados/v0002")
            assert ok_del_ultima.status_code == 200
            assert ok_del_ultima.json()["versao_atual_id"] is None
            assert ok_del_ultima.json()["versoes"] == []
            assert "video_com_narracao_tts" not in (ok_del_ultima.json()["job"].get("steps_json") or {})
            assert not (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).exists()
