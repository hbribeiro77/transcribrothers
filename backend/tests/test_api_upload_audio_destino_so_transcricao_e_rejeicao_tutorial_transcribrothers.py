"""Upload de áudio com destino só transcrição; rejeição áudio+tutorial."""

from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def _patch_credenciais_stt_e_pipeline() -> tuple:
    return (
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        ),
        patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"),
    )


def test_upload_wav_destino_so_transcricao_grava_tipo_entrada_audio_transcribrothers() -> None:
    conteudo = b"RIFF" + b"\x00" * 64
    p1, p2 = _patch_credenciais_stt_e_pipeline()
    with TestClient(app) as client, p1, p2:
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "so_transcricao"},
            files={"video": ("fala.wav", conteudo, "audio/wav")},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        steps = body["steps_json"]
        assert steps["destino_apos_transcricao"] == "so_transcricao"
        assert steps["tipo_entrada_midia"] == "audio"
        assert steps["saved_as"] == "audio_entrada_arquivo_local.wav"
        data_dir: Path = app.state.data_dir
        assert (data_dir / "jobs" / body["id"] / "audio_entrada_arquivo_local.wav").is_file()


def test_upload_audio_com_destino_tutorial_retorna_400_transcribrothers() -> None:
    conteudo = b"RIFF" + b"\x00" * 32
    p1, p2 = _patch_credenciais_stt_e_pipeline()
    with (
        TestClient(app) as client,
        p1,
        p2,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        ),
    ):
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "gerar_tutorial"},
            files={"video": ("fala.wav", conteudo, "audio/wav")},
        )
        assert r.status_code == 400
        detail = str(r.json().get("detail", "")).lower()
        assert "só transcrição" in detail or "video" in detail or "vídeo" in detail


def test_upload_so_transcricao_nao_exige_credencial_tutorial_transcribrothers() -> None:
    conteudo = b"RIFF" + b"\x00" * 32
    p1, p2 = _patch_credenciais_stt_e_pipeline()
    with (
        TestClient(app) as client,
        p1,
        p2,
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=False,
        ),
    ):
        r = client.post(
            "/api/jobs/upload",
            data={"destino_apos_transcricao": "so_transcricao"},
            files={"video": ("fala.mp3", conteudo, "audio/mpeg")},
        )
        assert r.status_code == 200, r.text
        assert r.json()["steps_json"]["tipo_entrada_midia"] == "audio"
