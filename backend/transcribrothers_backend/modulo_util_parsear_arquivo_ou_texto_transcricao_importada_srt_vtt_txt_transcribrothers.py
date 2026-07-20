"""Normaliza texto colado ou arquivo .txt/.md/.srt/.vtt em ResultadoTranscricaoComSegmentos."""

from __future__ import annotations

import re
from pathlib import PurePath

from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)

EXTENSOES_TRANSCRICAO_IMPORTADA_PERMITIDAS_TRANSCRIBROTHERS = frozenset(
    {".txt", ".md", ".srt", ".vtt"}
)


class ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(ValueError):
    pass


def _parse_timestamp_srt_para_segundos_transcribrothers(raw: str) -> float:
    # 00:01:02,500 ou 00:01:02.500
    m = re.fullmatch(
        r"(?:(\d{1,2}):)?(\d{1,2}):(\d{1,2})[,.](\d{1,3})",
        (raw or "").strip(),
    )
    if not m:
        raise ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(
            f"Timestamp SRT/VTT inválido: {raw!r}."
        )
    horas = int(m.group(1) or 0)
    minutos = int(m.group(2))
    segundos = int(m.group(3))
    frac = m.group(4).ljust(3, "0")[:3]
    return horas * 3600 + minutos * 60 + segundos + int(frac) / 1000.0


def _parse_timestamp_vtt_para_segundos_transcribrothers(raw: str) -> float:
    return _parse_timestamp_srt_para_segundos_transcribrothers(raw.replace(".", ","))


def parsear_conteudo_srt_para_resultado_transcricao_transcribrothers(
    texto: str,
) -> ResultadoTranscricaoComSegmentos:
    blocos = re.split(r"\n\s*\n", (texto or "").replace("\r\n", "\n").strip())
    segmentos: list[SegmentoTranscricaoComTempo] = []
    for bloco in blocos:
        linhas = [ln.strip() for ln in bloco.split("\n") if ln.strip()]
        if not linhas:
            continue
        # Pula índice numérico opcional
        i = 1 if re.fullmatch(r"\d+", linhas[0]) and len(linhas) >= 2 else 0
        if i >= len(linhas):
            continue
        m = re.match(
            r"^(.+?)\s*-->\s*(.+?)(?:\s+.*)?$",
            linhas[i],
        )
        if not m:
            continue
        inicio = _parse_timestamp_srt_para_segundos_transcribrothers(m.group(1))
        fim = _parse_timestamp_srt_para_segundos_transcribrothers(m.group(2))
        corpo = " ".join(linhas[i + 1 :]).strip()
        if not corpo:
            continue
        segmentos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=inicio,
                fim_segundos=fim,
                texto=corpo,
            )
        )
    if not segmentos:
        raise ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(
            "Arquivo SRT sem falas utilizáveis."
        )
    texto_completo = " ".join(s.texto for s in segmentos).strip()
    return ResultadoTranscricaoComSegmentos(
        texto_completo=texto_completo,
        segmentos=segmentos,
        idioma_detectado=None,
    )


def parsear_conteudo_vtt_para_resultado_transcricao_transcribrothers(
    texto: str,
) -> ResultadoTranscricaoComSegmentos:
    limpo = (texto or "").replace("\r\n", "\n").strip()
    if limpo.upper().startswith("WEBVTT"):
        limpo = limpo.split("\n", 1)[1] if "\n" in limpo else ""
    # Remove NOTE / STYLE blocks simples
    limpo = re.sub(r"(?im)^(NOTE|STYLE)\b.*?(?=\n\n|\Z)", "", limpo, flags=re.DOTALL)
    blocos = re.split(r"\n\s*\n", limpo.strip())
    segmentos: list[SegmentoTranscricaoComTempo] = []
    for bloco in blocos:
        linhas = [ln.rstrip() for ln in bloco.split("\n") if ln.strip()]
        if not linhas:
            continue
        i = 0
        if "-->" not in linhas[0] and len(linhas) >= 2:
            i = 1
        if i >= len(linhas) or "-->" not in linhas[i]:
            continue
        m = re.match(r"^(.+?)\s*-->\s*(.+?)(?:\s+.*)?$", linhas[i].strip())
        if not m:
            continue
        inicio = _parse_timestamp_vtt_para_segundos_transcribrothers(m.group(1))
        fim = _parse_timestamp_vtt_para_segundos_transcribrothers(m.group(2))
        corpo = " ".join(ln.strip() for ln in linhas[i + 1 :]).strip()
        # Remove tags VTT simples
        corpo = re.sub(r"</?[^>]+>", "", corpo).strip()
        if not corpo:
            continue
        segmentos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=inicio,
                fim_segundos=fim,
                texto=corpo,
            )
        )
    if not segmentos:
        raise ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(
            "Arquivo VTT sem falas utilizáveis."
        )
    texto_completo = " ".join(s.texto for s in segmentos).strip()
    return ResultadoTranscricaoComSegmentos(
        texto_completo=texto_completo,
        segmentos=segmentos,
        idioma_detectado=None,
    )


def parsear_texto_puro_para_resultado_transcricao_transcribrothers(
    texto: str,
) -> ResultadoTranscricaoComSegmentos:
    corpo = (texto or "").replace("\r\n", "\n").strip()
    if not corpo:
        raise ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(
            "Informe o texto da transcrição (colar ou enviar arquivo)."
        )
    return ResultadoTranscricaoComSegmentos(
        texto_completo=corpo,
        segmentos=[
            SegmentoTranscricaoComTempo(
                inicio_segundos=0.0,
                fim_segundos=0.0,
                texto=corpo,
            )
        ],
        idioma_detectado=None,
    )


def parsear_arquivo_ou_texto_transcricao_importada_transcribrothers(
    *,
    texto: str | None = None,
    nome_arquivo: str | None = None,
    conteudo_arquivo: str | bytes | None = None,
) -> ResultadoTranscricaoComSegmentos:
    """Prioriza arquivo quando presente; senão usa texto colado."""
    if conteudo_arquivo is not None:
        if isinstance(conteudo_arquivo, bytes):
            try:
                raw = conteudo_arquivo.decode("utf-8")
            except UnicodeDecodeError:
                raw = conteudo_arquivo.decode("utf-8", errors="replace")
        else:
            raw = str(conteudo_arquivo)
        ext = PurePath(nome_arquivo or "").suffix.lower()
        if ext and ext not in EXTENSOES_TRANSCRICAO_IMPORTADA_PERMITIDAS_TRANSCRIBROTHERS:
            raise ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers(
                "Extensão não permitida. Use .txt, .md, .srt ou .vtt."
            )
        if ext == ".srt":
            return parsear_conteudo_srt_para_resultado_transcricao_transcribrothers(raw)
        if ext == ".vtt":
            return parsear_conteudo_vtt_para_resultado_transcricao_transcribrothers(raw)
        return parsear_texto_puro_para_resultado_transcricao_transcribrothers(raw)
    return parsear_texto_puro_para_resultado_transcricao_transcribrothers(texto or "")
