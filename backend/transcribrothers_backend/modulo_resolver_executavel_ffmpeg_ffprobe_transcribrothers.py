"""Resolve caminhos de ffmpeg/ffprobe (PATH ou variáveis de ambiente)."""

from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
    obter_configuracao,
)


def _caminho_executavel_configurado_existe(caminho_bruto: str) -> str | None:
    bruto = (caminho_bruto or "").strip()
    if not bruto:
        return None
    p = Path(bruto)
    if p.is_file():
        return str(p.resolve())
    return None


def resolver_caminho_ffprobe_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers | None = None,
) -> str | None:
    configuracao = cfg or obter_configuracao()
    direto = _caminho_executavel_configurado_existe(configuracao.ffprobe_path)
    if direto:
        return direto
    pasta = (configuracao.ffmpeg_bin_dir or "").strip()
    if pasta:
        for nome in ("ffprobe.exe", "ffprobe"):
            candidato = Path(pasta) / nome
            if candidato.is_file():
                return str(candidato.resolve())
    return shutil.which("ffprobe")


def resolver_caminho_ffmpeg_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers | None = None,
) -> str | None:
    configuracao = cfg or obter_configuracao()
    direto = _caminho_executavel_configurado_existe(configuracao.ffmpeg_path)
    if direto:
        return direto
    pasta = (configuracao.ffmpeg_bin_dir or "").strip()
    if pasta:
        for nome in ("ffmpeg.exe", "ffmpeg"):
            candidato = Path(pasta) / nome
            if candidato.is_file():
                return str(candidato.resolve())
    return shutil.which("ffmpeg")


def ffprobe_disponivel_transcribrothers(cfg: ConfiguracaoAmbienteTranscribrothers | None = None) -> bool:
    return resolver_caminho_ffprobe_transcribrothers(cfg) is not None


def ffmpeg_disponivel_transcribrothers(cfg: ConfiguracaoAmbienteTranscribrothers | None = None) -> bool:
    return resolver_caminho_ffmpeg_transcribrothers(cfg) is not None


@lru_cache(maxsize=1)
def obter_diagnostico_ffmpeg_ffprobe_transcribrothers() -> dict[str, str | bool]:
    cfg = obter_configuracao()
    caminho_ffprobe = resolver_caminho_ffprobe_transcribrothers(cfg)
    caminho_ffmpeg = resolver_caminho_ffmpeg_transcribrothers(cfg)
    versao_ffprobe = ""
    if caminho_ffprobe:
        try:
            proc = subprocess.run(
                [caminho_ffprobe, "-version"],
                capture_output=True,
                check=False,
                timeout=8,
            )
            linha = (proc.stdout or b"").decode(errors="replace").splitlines()
            versao_ffprobe = linha[0].strip() if linha else ""
        except (OSError, subprocess.TimeoutExpired):
            versao_ffprobe = ""
    return {
        "ffprobe_disponivel": bool(caminho_ffprobe),
        "ffprobe_caminho_resolvido": caminho_ffprobe or "",
        "ffprobe_versao_linha": versao_ffprobe,
        "ffmpeg_disponivel": bool(caminho_ffmpeg),
        "ffmpeg_caminho_resolvido": caminho_ffmpeg or "",
    }
