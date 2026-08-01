"""Testes do inventário de mídia de origem e limpeza de cache."""

from __future__ import annotations

from pathlib import Path

import pytest

from transcribrothers_backend.modulo_inventario_midia_fonte_e_cache_job_transcribrothers import (
    ErroMidiaFonteJobTranscribrothers,
    inventariar_midia_fonte_e_cache_do_work_transcribrothers,
    limpar_cache_regeneravel_job_transcribrothers,
    resolver_arquivo_midia_fonte_permitido_transcribrothers,
)


def test_inventario_lista_video_audio_e_cache(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"v" * 1000)
    (work / "audio_extraido_para_transcricao.wav").write_bytes(b"a" * 500)
    (work / "audio_extraido_para_transcricao_multimodal_inline.m4a").write_bytes(b"m" * 200)
    cache = work / "segmentos_video_narrado_retarget"
    cache.mkdir()
    (cache / "seg.mp4").write_bytes(b"c" * 300)
    frames = work / "frames_png_capturados_para_tutorial"
    frames.mkdir()
    (frames / "f.png").write_bytes(b"p" * 50)

    inv = inventariar_midia_fonte_e_cache_do_work_transcribrothers(work, job_id="j1")
    assert inv["cache_bytes"] == 350
    ids = {i["id"] for i in inv["itens"]}
    assert "video_entrada" in ids
    assert "audio_stt_wav" in ids
    assert any(i["nome_arquivo"].endswith(".m4a") for i in inv["itens"])
    assert inv["itens"][0]["url_download"].startswith("/api/jobs/j1/midia-fonte/arquivo/")


def test_limpar_cache_nao_apaga_origem(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    video = work / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"video")
    wav = work / "audio_extraido_para_transcricao.wav"
    wav.write_bytes(b"wav")
    cache = work / "segmentos_video_narrado_retarget"
    cache.mkdir()
    (cache / "x.bin").write_bytes(b"12345")

    restante = limpar_cache_regeneravel_job_transcribrothers(work)
    assert restante == 0
    assert not cache.exists()
    assert video.is_file()
    assert wav.is_file()


def test_resolver_arquivo_bloqueia_nome_estranho(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"v")
    with pytest.raises(ErroMidiaFonteJobTranscribrothers):
        resolver_arquivo_midia_fonte_permitido_transcribrothers(work, "../secret.txt")
    with pytest.raises(ErroMidiaFonteJobTranscribrothers):
        resolver_arquivo_midia_fonte_permitido_transcribrothers(work, "tutorial_gerado_transcribrothers.md")
