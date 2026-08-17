"""Preparar video_entrada unificado a partir de lista de clips."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    ResultadoConcatenacaoVideosEntradaTranscribrothers,
)
from transcribrothers_backend.modulo_preparar_video_entrada_unificado_a_partir_lista_clips_job_transcribrothers import (
    preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers,
)


@pytest.mark.asyncio
async def test_preparar_unifica_e_arquiva_clips(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    a = tmp_path / "a.webm"
    b = tmp_path / "b.webm"
    a.write_bytes(b"AAA")
    b.write_bytes(b"BBB")

    async def _fake_lista(*, caminhos_videos, caminho_saida):
        assert len(caminhos_videos) == 2
        caminho_saida.write_bytes(b"UNIDO")
        return ResultadoConcatenacaoVideosEntradaTranscribrothers(
            caminho_saida=caminho_saida,
            modo="stream_copy",
        )

    with patch(
        "transcribrothers_backend.modulo_preparar_video_entrada_unificado_a_partir_lista_clips_job_transcribrothers.concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers",
        new=AsyncMock(side_effect=_fake_lista),
    ), patch(
        "transcribrothers_backend.modulo_preparar_video_entrada_unificado_a_partir_lista_clips_job_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        new=AsyncMock(return_value=33.0),
    ):
        meta = await preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers(
            work=work,
            caminhos_clips_ordenados=[a, b],
            nomes_originais_ordenados=["parte1.webm", "parte2.webm"],
        )

    final = work / "video_entrada_arquivo_local.webm"
    assert final.is_file()
    assert final.read_bytes() == b"UNIDO"
    assert meta["modo_concat_video_entrada"] == "stream_copy"
    assert meta["duracao_video_segundos"] == 33.0
    assert len(meta["clips_arquivados"]) == 2
    assert (work / "clips_entrada_originais").is_dir()
