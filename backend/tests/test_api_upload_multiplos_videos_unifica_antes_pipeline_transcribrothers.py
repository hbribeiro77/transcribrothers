"""Upload com vários vídeos: unifica antes de agendar o pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_upload_dois_videos_unifica_e_agenda_pipeline(tmp_path: Path) -> None:
    async def _fake_prep(*, work, caminhos_clips_ordenados, nomes_originais_ordenados):
        assert len(caminhos_clips_ordenados) == 2
        assert nomes_originais_ordenados == ["a.webm", "b.webm"]
        final = work / "video_entrada_arquivo_local.webm"
        final.write_bytes(b"UNIDO-UPLOAD")
        return {
            "saved_as": final.name,
            "bytes_written": final.stat().st_size,
            "duracao_video_segundos": 12.0,
            "caminho_video_entrada": final,
            "modo_concat_video_entrada": "stream_copy",
            "clips_arquivados": ["001_a.webm", "002_b.webm"],
            "nomes_originais": ["a.webm", "b.webm"],
            "unificado_em_utc": "20260804T220000Z",
        }

    with (
        patch(
            "transcribrothers_backend.main._diretorio_trabalho_job",
            side_effect=lambda _d, jid: tmp_path / "jobs" / jid,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona") as mock_agendar,
        patch(
            "transcribrothers_backend.main.preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers",
            new=AsyncMock(side_effect=_fake_prep),
        ),
        patch(
            "transcribrothers_backend.main.obter_duracao_video_segundos_via_ffprobe",
            new=AsyncMock(return_value=12.0),
        ),
        TestClient(app) as client,
    ):
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "gerar_tutorial"},
            files=[
                ("videos", ("a.webm", b"\x1a\x45\xdf\xa3" + b"\0" * 32, "video/webm")),
                ("videos", ("b.webm", b"\x1a\x45\xdf\xa3" + b"\0" * 40, "video/webm")),
            ],
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "pending"
    steps = body["steps_json"]
    assert steps["ultimo_modo_concat_video_entrada"] == "stream_copy"
    assert steps["videos_unificados_no_upload"]["nomes_originais"] == ["a.webm", "b.webm"]
    assert "a.webm" in steps["original_filename"]
    mock_agendar.assert_called_once()
