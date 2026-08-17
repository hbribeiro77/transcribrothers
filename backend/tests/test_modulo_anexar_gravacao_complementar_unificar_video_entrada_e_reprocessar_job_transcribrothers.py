"""Unificar vídeo de entrada com gravação complementar (ffmpeg mockado)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers import (
    NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS,
    NOME_VIDEO_ENTRADA_UNIFICADO_LOCAL_TRANSCRIBROTHERS,
    aplicar_metadados_unificacao_nos_steps_json_transcribrothers,
    invalidar_artefatos_derivados_apos_troca_video_entrada_transcribrothers,
    unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    ResultadoConcatenacaoVideosEntradaTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS,
)


def test_invalidar_artefatos_remove_wav_snapshot_e_cache(tmp_path: Path) -> None:
    (tmp_path / "audio_extraido_para_transcricao.wav").write_bytes(b"WAV")
    (tmp_path / "audio_extraido_para_transcricao_multimodal_inline.m4a").write_bytes(b"M4A")
    (tmp_path / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).write_text(
        "{}", encoding="utf-8"
    )
    (tmp_path / "tutorial_gerado_transcribrothers.md").write_text("# t", encoding="utf-8")
    cache = tmp_path / "frames_png_capturados_para_tutorial"
    cache.mkdir()
    (cache / "f.png").write_bytes(b"PNG")

    invalidar_artefatos_derivados_apos_troca_video_entrada_transcribrothers(tmp_path)

    assert not (tmp_path / "audio_extraido_para_transcricao.wav").exists()
    assert not (tmp_path / "audio_extraido_para_transcricao_multimodal_inline.m4a").exists()
    assert not (tmp_path / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).exists()
    assert not (tmp_path / "tutorial_gerado_transcribrothers.md").exists()
    assert not cache.exists()


def test_aplicar_metadados_limpa_chaves_e_registra_historico() -> None:
    steps = {
        "destino_apos_transcricao": "gerar_tutorial",
        "audio_ok": True,
        "regeneracao_tutorial_snapshot": {"x": 1},
        "transcricao_snapshot_finalizada_em_disco": True,
        "error_traceback": "boom",
    }
    meta = {
        "saved_as": NOME_VIDEO_ENTRADA_UNIFICADO_LOCAL_TRANSCRIBROTHERS,
        "bytes_written": 99,
        "duracao_video_segundos": 12.5,
        "clip_arquivado_antes": "001_antes.mp4",
        "clip_arquivado_complementar": "002_comp.webm",
        "nome_original_complementar": "parte2.webm",
        "unificado_em_utc": "20260804T120000Z",
        "modo_concat_video_entrada": "stream_copy",
    }
    out = aplicar_metadados_unificacao_nos_steps_json_transcribrothers(steps, meta)
    assert out["destino_apos_transcricao"] == "gerar_tutorial"
    assert "audio_ok" not in out
    assert "regeneracao_tutorial_snapshot" not in out
    assert "error_traceback" not in out
    assert out["bytes_written"] == 99
    assert out["duracao_video_segundos"] == 12.5
    assert out["ultimo_modo_concat_video_entrada"] == "stream_copy"
    assert len(out["gravacoes_complementares_unificadas"]) == 1
    assert out["gravacoes_complementares_unificadas"][0]["modo_concat_video_entrada"] == "stream_copy"
    assert out["pipeline_fase"].startswith("anexar_gravacao_complementar")


@pytest.mark.asyncio
async def test_unificar_arquiva_clips_e_substitui_video_entrada(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    atual = work / "video_entrada_arquivo_local.webm"
    atual.write_bytes(b"VIDEO1")
    complementar = tmp_path / "comp.webm"
    complementar.write_bytes(b"VIDEO2")
    (work / "audio_extraido_para_transcricao.wav").write_bytes(b"WAV")
    (work / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).write_text(
        "{}", encoding="utf-8"
    )

    async def _fake_concat(*, caminho_video_a, caminho_video_b, caminho_saida):
        assert caminho_video_a.is_file()
        assert caminho_video_b.is_file()
        caminho_saida.write_bytes(b"UNIFICADO")
        return ResultadoConcatenacaoVideosEntradaTranscribrothers(
            caminho_saida=caminho_saida,
            modo="stream_copy",
        )

    with patch(
        "transcribrothers_backend.modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers.concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers",
        new=AsyncMock(side_effect=_fake_concat),
    ), patch(
        "transcribrothers_backend.modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        new=AsyncMock(return_value=42.0),
    ):
        meta = await unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers(
            work=work,
            caminho_video_complementar=complementar,
            nome_original_complementar="reuniao_parte2.webm",
        )

    final = work / "video_entrada_arquivo_local.webm"
    assert final.is_file()
    assert final.read_bytes() == b"UNIFICADO"
    assert meta["saved_as"] == "video_entrada_arquivo_local.webm"
    assert not (work / NOME_VIDEO_ENTRADA_UNIFICADO_LOCAL_TRANSCRIBROTHERS).exists()
    pasta = work / NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS
    assert pasta.is_dir()
    arquivados = sorted(p.name for p in pasta.iterdir() if p.is_file())
    assert len(arquivados) == 2
    assert any("antes_unificar" in n for n in arquivados)
    assert any("complementar" in n and "reuniao_parte2" in n for n in arquivados)
    assert not (work / "audio_extraido_para_transcricao.wav").exists()
    assert not (work / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).exists()
    assert meta["bytes_written"] == len(b"UNIFICADO")
    assert meta["duracao_video_segundos"] == 42.0
    assert meta["modo_concat_video_entrada"] == "stream_copy"
