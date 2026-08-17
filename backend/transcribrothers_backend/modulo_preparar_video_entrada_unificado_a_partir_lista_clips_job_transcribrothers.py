"""Arquiva clips de entrada, unifica em um video_entrada e devolve metadados para steps_json."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers import (
    NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_ffmpeg_concatenar_lista_videos_entrada_em_cadeia_transcribrothers import (
    concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)

_RE_NOME_SEGURO = re.compile(r"[^a-zA-Z0-9._-]+")


class ErroPrepararVideoEntradaMultiploTranscribrothers(ValueError):
    pass


def _sanitizar_trecho_nome_arquivo(nome: str, *, max_len: int = 80) -> str:
    base = Path(nome or "parte").name
    limpo = _RE_NOME_SEGURO.sub("_", base).strip("._") or "parte"
    return limpo[:max_len]


async def preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers(
    *,
    work: Path,
    caminhos_clips_ordenados: list[Path],
    nomes_originais_ordenados: list[str],
) -> dict[str, Any]:
    """
    Copia clips para `clips_entrada_originais/`, concatena na ordem e grava
    `video_entrada_arquivo_local.{ext}` (ext do resultado da unificação).
    """
    if len(caminhos_clips_ordenados) < 2:
        raise ErroPrepararVideoEntradaMultiploTranscribrothers(
            "Unificação no upload exige ao menos dois vídeos."
        )
    if len(caminhos_clips_ordenados) != len(nomes_originais_ordenados):
        raise ErroPrepararVideoEntradaMultiploTranscribrothers(
            "Lista de caminhos e nomes originais com tamanhos diferentes."
        )
    for p in caminhos_clips_ordenados:
        if not p.is_file():
            raise ErroPrepararVideoEntradaMultiploTranscribrothers(f"Clip ausente: {p.name}")

    pasta_clips = work / NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS
    pasta_clips.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    arquivados: list[str] = []
    caminhos_para_concat: list[Path] = []

    for i, (origem, nome_orig) in enumerate(
        zip(caminhos_clips_ordenados, nomes_originais_ordenados, strict=True),
        start=1,
    ):
        nome_limpo = _sanitizar_trecho_nome_arquivo(nome_orig)
        ext = origem.suffix.lower() or Path(nome_orig).suffix.lower() or ".mp4"
        destino_arq = pasta_clips / f"{i:03d}_parte_{stamp}_{nome_limpo}"
        if destino_arq.suffix.lower() != ext:
            destino_arq = destino_arq.with_suffix(ext)
        if origem.resolve() != destino_arq.resolve():
            shutil.copy2(origem, destino_arq)
        arquivados.append(destino_arq.name)
        caminhos_para_concat.append(destino_arq)

    ext_tmp = caminhos_para_concat[0].suffix.lower() or ".mp4"
    saida_tmp = work / f".video_entrada_unificado_upload_{stamp}{ext_tmp}"
    saida_final: Path | None = None
    modo_concat = "reencode"
    try:
        resultado = await concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers(
            caminhos_videos=caminhos_para_concat,
            caminho_saida=saida_tmp,
        )
        modo_concat = resultado.modo
        gerado = resultado.caminho_saida
        destino = work / f"video_entrada_arquivo_local{gerado.suffix.lower()}"
        if destino.resolve() != gerado.resolve():
            if destino.exists():
                destino.unlink()
            gerado.replace(destino)
            saida_final = destino
        else:
            saida_final = gerado
    finally:
        for p in work.glob(f".video_entrada_unificado_upload_{stamp}*"):
            if saida_final is not None and p.resolve() == saida_final.resolve():
                continue
            if p.is_file():
                p.unlink(missing_ok=True)

    if saida_final is None or not saida_final.is_file():
        raise ErroPrepararVideoEntradaMultiploTranscribrothers(
            "Falha ao gerar o vídeo unificado a partir dos clips enviados."
        )

    # Remove entradas soltas que não sejam o unificado (uploads temporários na raiz do work)
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in work.glob(pattern):
            if p.resolve() != saida_final.resolve():
                p.unlink(missing_ok=True)
    for p in work.glob(".upload_parte_video_*"):
        if p.is_file():
            p.unlink(missing_ok=True)

    dur = await obter_duracao_video_segundos_via_ffprobe(saida_final)
    return {
        "saved_as": saida_final.name,
        "bytes_written": int(saida_final.stat().st_size),
        "duracao_video_segundos": round(float(dur), 3) if dur > 0 else None,
        "caminho_video_entrada": saida_final,
        "modo_concat_video_entrada": modo_concat,
        "clips_arquivados": arquivados,
        "nomes_originais": [Path(n).name for n in nomes_originais_ordenados],
        "unificado_em_utc": stamp,
    }
