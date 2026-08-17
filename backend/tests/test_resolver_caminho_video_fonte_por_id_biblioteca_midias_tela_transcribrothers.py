"""Resolve Path de vídeo por id_fonte_video (entrada vs biblioteca)."""

from __future__ import annotations

from pathlib import Path

import pytest

from transcribrothers_backend.modulo_persistencia_biblioteca_midias_tela_job_transcribrothers import (
    ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
    alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers,
    confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers,
    resolver_caminho_video_fonte_por_id_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
    caminho_video_efetivo_do_segmento_retarget_transcribrothers,
)


def test_resolver_caminho_fonte_entrada_e_biblioteca(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    entrada = work / "video_entrada_arquivo_local.mp4"
    entrada.write_bytes(b"ENT")

    assert (
        resolver_caminho_video_fonte_por_id_no_work_transcribrothers(
            work=work,
            id_fonte_video="",
            caminho_video_entrada=entrada,
        )
        == entrada
    )
    assert (
        resolver_caminho_video_fonte_por_id_no_work_transcribrothers(
            work=work,
            id_fonte_video=ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
            caminho_video_entrada=entrada,
        )
        == entrada
    )

    item, destino = alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers(
        work=work,
        nome_original="extra.mp4",
        extensao_com_ponto=".mp4",
    )
    destino.write_bytes(b"BROLL")
    confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers(
        work=work, item=item, tamanho_bytes=5
    )
    assert (
        resolver_caminho_video_fonte_por_id_no_work_transcribrothers(
            work=work,
            id_fonte_video=item.id,
            caminho_video_entrada=entrada,
        )
        == destino
    )


def test_caminho_video_efetivo_do_segmento_usa_fonte(tmp_path: Path) -> None:
    padrao = tmp_path / "entrada.mp4"
    padrao.write_bytes(b"A")
    fonte = tmp_path / "broll.mp4"
    fonte.write_bytes(b"B")
    wav = tmp_path / "a.wav"
    wav.write_bytes(b"W")
    seg = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav,
        inicio_video_segundos=0,
        fim_video_segundos=1,
        caminho_video_fonte=fonte,
    )
    assert caminho_video_efetivo_do_segmento_retarget_transcribrothers(padrao, seg) == fonte
    seg2 = SegmentoVideoNarradoRetargetTranscribrothers(
        caminho_wav=wav,
        inicio_video_segundos=0,
        fim_video_segundos=1,
    )
    assert caminho_video_efetivo_do_segmento_retarget_transcribrothers(padrao, seg2) == padrao
