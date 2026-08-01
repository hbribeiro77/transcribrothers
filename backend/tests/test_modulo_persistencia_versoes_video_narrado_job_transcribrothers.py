"""Testes do versionamento de snapshots do vídeo narrado."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
    apagar_versao_video_narrado_transcribrothers,
    criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers,
    listar_versoes_video_narrado_do_work_transcribrothers,
    tornar_versao_video_narrado_atual_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    nome_subpasta_wavs_narracao_por_cue_transcribrothers,
)


def _preparar_working_set(tmp_path: Path, *, marcador: bytes = b"MP4-V1") -> tuple[Path, Path]:
    work = tmp_path / "work"
    assets = work / "assets_exportados_para_markdown"
    work.mkdir()
    assets.mkdir()
    (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(marcador + b"x" * 200)
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
        "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOi\n",
        encoding="utf-8",
    )
    (assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS).write_bytes(b"RIFF" + b"\0" * 100)
    (work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS).write_text(
        '{"cues":[]}\n',
        encoding="utf-8",
    )
    wavs = work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    wavs.mkdir()
    (wavs / "cue_000.wav").write_bytes(b"wav0")
    return work, assets


def test_criar_snapshot_cria_pasta_e_marca_atual(tmp_path: Path) -> None:
    work, assets = _preparar_working_set(tmp_path)
    with (
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._gerar_thumbnail_jpg_do_mp4_transcribrothers",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._obter_duracao_video_segundos_via_ffprobe_sync",
            return_value=12.5,
        ),
    ):
        r = criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={"pipeline_video_narrado_voz_tts": "Kore"},
            origem="pipeline_completo",
        )
    assert r.meta.id == "v0001"
    assert (r.caminho_pasta / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).is_file()
    assert (r.caminho_pasta / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).is_file()
    assert (r.caminho_pasta / nome_subpasta_wavs_narracao_por_cue_transcribrothers() / "cue_000.wav").is_file()
    atual, versoes = listar_versoes_video_narrado_do_work_transcribrothers(work)
    assert atual == "v0001"
    assert len(versoes) == 1
    assert versoes[0].duracao_segundos == 12.5
    assert versoes[0].voz_tts == "Kore"


def test_tornar_atual_restaura_arquivos(tmp_path: Path) -> None:
    work, assets = _preparar_working_set(tmp_path, marcador=b"MP4-A")
    with (
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._gerar_thumbnail_jpg_do_mp4_transcribrothers",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._obter_duracao_video_segundos_via_ffprobe_sync",
            return_value=1.0,
        ),
    ):
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="pipeline_completo",
        )
        (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"MP4-B" + b"y" * 200)
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="edicoes_modal",
        )

    atual, versoes = listar_versoes_video_narrado_do_work_transcribrothers(work)
    assert atual == "v0002"
    assert len(versoes) == 2

    steps_novo = tornar_versao_video_narrado_atual_transcribrothers(
        work=work,
        assets=assets,
        job_id="job-teste",
        versao_id="v0001",
        steps={
            "pipeline_video_narrado_documento": {
                "ok": True,
                "url_asset_vtt": "/api/jobs/job-teste/assets/antigo.vtt?v=velho",
            },
        },
    )
    mp4 = (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).read_bytes()
    assert mp4.startswith(b"MP4-A")
    assert steps_novo["video_com_narracao_tts"]["url_download"].startswith(
        "/api/jobs/job-teste/video-com-narracao-tts?v="
    )
    url_vtt = steps_novo["legendas_documento_alinhadas"]["url_asset"]
    assert "?v=" in url_vtt
    assert steps_novo["pipeline_video_narrado_documento"]["url_asset_vtt"] == url_vtt
    atual2, _ = listar_versoes_video_narrado_do_work_transcribrothers(work)
    assert atual2 == "v0001"


def test_apagar_versao_atual_promove_outra_ou_limpa(tmp_path: Path) -> None:
    work, assets = _preparar_working_set(tmp_path)
    with (
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._gerar_thumbnail_jpg_do_mp4_transcribrothers",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers._obter_duracao_video_segundos_via_ffprobe_sync",
            return_value=1.0,
        ),
    ):
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="pipeline_completo",
        )
        (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).write_bytes(b"MP4-2" + b"z" * 200)
        criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps={},
            origem="remux",
        )

    # Apagar atual promove a anterior.
    r = apagar_versao_video_narrado_transcribrothers(
        work=work,
        assets=assets,
        job_id="job-teste",
        versao_id="v0002",
        steps={"video_com_narracao_tts": {"url_download": "/x"}},
    )
    assert r.versao_atual_id == "v0001"
    assert r.steps_alterados is True
    assert (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).read_bytes().startswith(b"MP4-V1")
    atual, versoes = listar_versoes_video_narrado_do_work_transcribrothers(work)
    assert atual == "v0001"
    assert [v.id for v in versoes] == ["v0001"]
    assert not (work / "videos_narrados" / "v0002").exists()

    # Apagar a última limpa o working set.
    r2 = apagar_versao_video_narrado_transcribrothers(
        work=work,
        assets=assets,
        job_id="job-teste",
        versao_id="v0001",
        steps=r.steps,
    )
    assert r2.versao_atual_id is None
    assert "video_com_narracao_tts" not in r2.steps
    assert not (work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS).exists()
