"""Inventário da mídia de origem (entrada + áudio STT) e cache regenerável do job."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_calcular_tamanho_bytes_diretorio_job_pipeline_transcribrothers import (
    calcular_tamanho_bytes_diretorio_recursivo_transcribrothers,
)

NOME_ARQUIVO_AUDIO_EXTRAIDO_TRANSCRICAO_WAV_TRANSCRIBROTHERS = "audio_extraido_para_transcricao.wav"
NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS = (
    "segmentos_video_narrado_retarget",
    "frames_png_capturados_para_tutorial",
    "frames_png_capturados_notas_proposta",
    "frames_png_capturados_reproducao_bug",
)

_RE_NOME_ARQUIVO_SEGURO = re.compile(r"^[a-zA-Z0-9._-]+$")
_PREFIXOS_AUDIO_MULTIMODAL = "audio_extraido_para_transcricao_multimodal_inline."


class ErroMidiaFonteJobTranscribrothers(ValueError):
    """Arquivo de mídia de origem inválido ou não permitido."""


@dataclass(frozen=True)
class ItemMidiaFonteJobTranscribrothers:
    id: str
    rotulo: str
    tipo: str
    nome_arquivo: str
    tamanho_bytes: int

    def para_dict(self, *, job_id: str) -> dict[str, Any]:
        return {
            "id": self.id,
            "rotulo": self.rotulo,
            "tipo": self.tipo,
            "nome_arquivo": self.nome_arquivo,
            "tamanho_bytes": int(self.tamanho_bytes),
            "url_download": (
                f"/api/jobs/{job_id}/midia-fonte/arquivo/{self.nome_arquivo}"
            ),
        }


def localizar_arquivo_video_entrada_no_diretorio_job_transcribrothers(work: Path) -> Path | None:
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in sorted(work.glob(pattern)):
            if p.is_file():
                return p
    return None


def listar_nomes_arquivos_midia_fonte_permitidos_no_work_transcribrothers(work: Path) -> set[str]:
    nomes: set[str] = set()
    video = localizar_arquivo_video_entrada_no_diretorio_job_transcribrothers(work)
    if video is not None:
        nomes.add(video.name)
    wav = work / NOME_ARQUIVO_AUDIO_EXTRAIDO_TRANSCRICAO_WAV_TRANSCRIBROTHERS
    if wav.is_file():
        nomes.add(wav.name)
    for p in sorted(work.glob(f"{_PREFIXOS_AUDIO_MULTIMODAL}*")):
        if p.is_file() and _RE_NOME_ARQUIVO_SEGURO.match(p.name):
            nomes.add(p.name)
    return nomes


def _tamanho_arquivo_ou_zero(caminho: Path) -> int:
    try:
        if caminho.is_file():
            return int(caminho.stat().st_size)
    except OSError:
        return 0
    return 0


def calcular_cache_bytes_regeneravel_job_transcribrothers(work: Path) -> int:
    total = 0
    for nome in NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS:
        total += calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(work / nome)
    return total


def inventariar_midia_fonte_e_cache_do_work_transcribrothers(
    work: Path,
    *,
    job_id: str,
) -> dict[str, Any]:
    itens: list[ItemMidiaFonteJobTranscribrothers] = []
    video = localizar_arquivo_video_entrada_no_diretorio_job_transcribrothers(work)
    if video is not None:
        itens.append(
            ItemMidiaFonteJobTranscribrothers(
                id="video_entrada",
                rotulo="Vídeo de entrada",
                tipo="video",
                nome_arquivo=video.name,
                tamanho_bytes=_tamanho_arquivo_ou_zero(video),
            )
        )
    wav = work / NOME_ARQUIVO_AUDIO_EXTRAIDO_TRANSCRICAO_WAV_TRANSCRIBROTHERS
    if wav.is_file():
        itens.append(
            ItemMidiaFonteJobTranscribrothers(
                id="audio_stt_wav",
                rotulo="Áudio extraído (transcrição)",
                tipo="audio",
                nome_arquivo=wav.name,
                tamanho_bytes=_tamanho_arquivo_ou_zero(wav),
            )
        )
    for p in sorted(work.glob(f"{_PREFIXOS_AUDIO_MULTIMODAL}*")):
        if not p.is_file() or not _RE_NOME_ARQUIVO_SEGURO.match(p.name):
            continue
        itens.append(
            ItemMidiaFonteJobTranscribrothers(
                id=f"audio_stt_multimodal_{p.suffix.lstrip('.') or 'bin'}",
                rotulo="Áudio multimodal (inline)",
                tipo="audio",
                nome_arquivo=p.name,
                tamanho_bytes=_tamanho_arquivo_ou_zero(p),
            )
        )
    cache_bytes = calcular_cache_bytes_regeneravel_job_transcribrothers(work)
    return {
        "itens": [i.para_dict(job_id=job_id) for i in itens],
        "cache_bytes": cache_bytes,
        "pastas_cache": list(NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS),
    }


def resolver_arquivo_midia_fonte_permitido_transcribrothers(work: Path, nome_arquivo: str) -> Path:
    nome = Path(nome_arquivo).name
    if not _RE_NOME_ARQUIVO_SEGURO.match(nome):
        raise ErroMidiaFonteJobTranscribrothers(f"Nome de arquivo inválido: {nome_arquivo!r}.")
    permitidos = listar_nomes_arquivos_midia_fonte_permitidos_no_work_transcribrothers(work)
    if nome not in permitidos:
        raise ErroMidiaFonteJobTranscribrothers(f"Arquivo não permitido: {nome}.")
    caminho = work / nome
    if not caminho.is_file():
        raise ErroMidiaFonteJobTranscribrothers(f"Arquivo não encontrado: {nome}.")
    return caminho


def limpar_cache_regeneravel_job_transcribrothers(work: Path) -> int:
    """Remove pastas de cache regenerável. Retorna cache_bytes restante (deve ser 0)."""
    for nome in NOMES_PASTAS_CACHE_REGENERAVEL_JOB_TRANSCRIBROTHERS:
        pasta = work / nome
        if pasta.is_dir():
            shutil.rmtree(pasta, ignore_errors=True)
    return calcular_cache_bytes_regeneravel_job_transcribrothers(work)
