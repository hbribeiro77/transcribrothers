"""Gera e grava arquivo WebVTT a partir de cues alinhadas."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
)

NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS = "legendas_documento_alinhadas.vtt"
CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS = "legendas_documento_alinhadas"


def _formatar_timestamp_vtt_transcribrothers(segundos: float) -> str:
    total_ms = max(0, int(round(float(segundos) * 1000)))
    horas = total_ms // 3_600_000
    resto = total_ms % 3_600_000
    minutos = resto // 60_000
    resto %= 60_000
    segs = resto // 1000
    ms = resto % 1000
    return f"{horas:02d}:{minutos:02d}:{segs:02d}.{ms:03d}"


def gerar_conteudo_vtt_a_partir_cues_legendas_transcribrothers(
    cues: list[CueLegendaAlinhadaTranscribrothers],
) -> str:
    linhas = ["WEBVTT", ""]
    for i, cue in enumerate(cues, start=1):
        inicio = _formatar_timestamp_vtt_transcribrothers(cue.inicio_segundos)
        fim = _formatar_timestamp_vtt_transcribrothers(cue.fim_segundos)
        texto = (cue.texto or "").replace("\n", " ").strip()
        linhas.append(str(i))
        linhas.append(f"{inicio} --> {fim}")
        linhas.append(texto)
        linhas.append("")
    return "\n".join(linhas).rstrip() + "\n"


def gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
    *,
    diretorio_assets: Path,
    cues: list[CueLegendaAlinhadaTranscribrothers],
    nome_arquivo: str = NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
) -> Path:
    diretorio_assets.mkdir(parents=True, exist_ok=True)
    path = diretorio_assets / nome_arquivo
    path.write_text(
        gerar_conteudo_vtt_a_partir_cues_legendas_transcribrothers(cues),
        encoding="utf-8",
        newline="\n",
    )
    return path
