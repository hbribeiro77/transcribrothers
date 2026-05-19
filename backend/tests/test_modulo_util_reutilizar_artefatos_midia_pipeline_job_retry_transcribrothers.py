"""Testes de reutilização de vídeo/áudio no retry do pipeline."""

from pathlib import Path

from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers,
    deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers,
    deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers,
    steps_json_job_para_reexecucao_pipeline_transcribrothers,
)


def test_steps_json_remove_apenas_erros(tmp_path: Path) -> None:
    s = steps_json_job_para_reexecucao_pipeline_transcribrothers(
        {"audio_ok": True, "error_traceback": "x", "pipeline_fase": "failed"}
    )
    assert s["audio_ok"] is True
    assert "error_traceback" not in s
    assert s["pipeline_fase"] == "failed"


def test_reutiliza_wav_quando_arquivo_e_flag_existem(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    wav.write_bytes(b"\x00" * 2048)
    assert (
        deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(
            wav,
            {"audio_ok": True},
        )
        is True
    )


def test_nao_reutiliza_wav_sem_flag_audio_ok(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    wav.write_bytes(b"\x00" * 2048)
    assert (
        deve_reutilizar_audio_wav_extraido_do_video_pipeline_retry_transcribrothers(wav, {})
        is False
    )


def test_reutiliza_mp3_inline_quando_config_coincide(tmp_path: Path) -> None:
    mp3 = tmp_path / "a.mp3"
    mp3.write_bytes(b"\x00" * 512)
    steps = {
        "transcricao_multimodal_audio_codificado_ok": True,
        "transcricao_multimodal_formato_audio_inline": "mp3",
        "transcricao_multimodal_audio_bitrate_kbps": 96,
        "transcricao_multimodal_audio_mono": True,
    }
    assert (
        deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers(
            mp3,
            formato_audio_inline="mp3",
            audio_bitrate_kbps=96,
            audio_mono=True,
            steps=steps,
        )
        is True
    )


def test_nao_reutiliza_mp3_se_bitrate_mudou(tmp_path: Path) -> None:
    mp3 = tmp_path / "a.mp3"
    mp3.write_bytes(b"\x00" * 512)
    steps = {
        "transcricao_multimodal_audio_codificado_ok": True,
        "transcricao_multimodal_formato_audio_inline": "mp3",
        "transcricao_multimodal_audio_bitrate_kbps": 96,
        "transcricao_multimodal_audio_mono": True,
    }
    assert (
        deve_reutilizar_audio_inline_codificado_transcricao_multimodal_pipeline_retry_transcribrothers(
            mp3,
            formato_audio_inline="mp3",
            audio_bitrate_kbps=128,
            audio_mono=True,
            steps=steps,
        )
        is False
    )


def test_reutiliza_video_drive_com_download_ok(tmp_path: Path) -> None:
    vid = tmp_path / "v.mp4"
    vid.write_bytes(b"\x00" * 2048)
    assert (
        deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers(
            vid,
            {"download_ok": True},
        )
        is True
    )
