"""Alinha frases do Markdown aos segmentos STT (similaridade + interpolação)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    SegmentoTranscricaoComTempo,
)

_LIMIAR_SIMILARIDADE_CASADO = 0.45
_JANELA_SEGMENTOS_BUSCA = 8
_DURACAO_MINIMA_CUE_SEGUNDOS = 0.8


@dataclass(frozen=True)
class CueLegendaAlinhadaTranscribrothers:
    texto: str
    inicio_segundos: float
    fim_segundos: float
    casado: bool


@dataclass(frozen=True)
class ResultadoAlinhamentoLegendasTranscribrothers:
    cues: list[CueLegendaAlinhadaTranscribrothers]
    quantidade_casadas: int
    quantidade_interpoladas: int

    @property
    def percentual_casado(self) -> float:
        total = len(self.cues)
        if total == 0:
            return 0.0
        return 100.0 * self.quantidade_casadas / total


def _normalizar_para_match_transcribrothers(texto: str) -> str:
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    return re.sub(r"\s+", " ", t).strip()


def _similaridade_texto_transcribrothers(a: str, b: str) -> float:
    na = _normalizar_para_match_transcribrothers(a)
    nb = _normalizar_para_match_transcribrothers(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def _filtrar_segmentos_dentro_da_duracao_video_transcribrothers(
    segmentos: list[SegmentoTranscricaoComTempo],
    duracao_video_segundos: float | None,
) -> list[SegmentoTranscricaoComTempo]:
    if duracao_video_segundos is None or duracao_video_segundos <= 0:
        return list(segmentos)
    teto = float(duracao_video_segundos)
    out: list[SegmentoTranscricaoComTempo] = []
    for seg in segmentos:
        if float(seg.inicio_segundos) >= teto:
            continue
        fim = min(float(seg.fim_segundos), teto)
        ini = float(seg.inicio_segundos)
        if fim <= ini:
            fim = min(teto, ini + _DURACAO_MINIMA_CUE_SEGUNDOS)
        out.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=ini,
                fim_segundos=fim,
                texto=seg.texto,
            )
        )
    return out


def _clamp_cues_a_duracao_video_transcribrothers(
    cues: list[CueLegendaAlinhadaTranscribrothers],
    duracao_video_segundos: float | None,
) -> list[CueLegendaAlinhadaTranscribrothers]:
    if duracao_video_segundos is None or duracao_video_segundos <= 0:
        return cues
    teto = float(duracao_video_segundos)
    out: list[CueLegendaAlinhadaTranscribrothers] = []
    for cue in cues:
        ini = max(0.0, float(cue.inicio_segundos))
        if ini >= teto:
            continue
        fim = min(float(cue.fim_segundos), teto)
        if fim <= ini:
            fim = min(teto, ini + _DURACAO_MINIMA_CUE_SEGUNDOS)
        if fim <= ini:
            continue
        out.append(
            CueLegendaAlinhadaTranscribrothers(
                texto=cue.texto,
                inicio_segundos=ini,
                fim_segundos=fim,
                casado=cue.casado,
            )
        )
    # Ordem não decrescente sem ultrapassar o teto
    for i in range(1, len(out)):
        if out[i].inicio_segundos < out[i - 1].fim_segundos:
            novo_ini = out[i - 1].fim_segundos
            if novo_ini >= teto:
                out = out[:i]
                break
            novo_fim = min(teto, max(novo_ini + _DURACAO_MINIMA_CUE_SEGUNDOS, out[i].fim_segundos))
            if novo_fim <= novo_ini:
                out = out[:i]
                break
            out[i] = CueLegendaAlinhadaTranscribrothers(
                texto=out[i].texto,
                inicio_segundos=novo_ini,
                fim_segundos=novo_fim,
                casado=out[i].casado,
            )
    return out


def alinhar_frases_aos_segmentos_transcricao_para_cues_legendas_transcribrothers(
    frases: list[str],
    segmentos: list[SegmentoTranscricaoComTempo],
    *,
    limiar_similaridade: float = _LIMIAR_SIMILARIDADE_CASADO,
    duracao_video_segundos: float | None = None,
) -> ResultadoAlinhamentoLegendasTranscribrothers:
    """
    Para cada frase, busca o melhor segmento numa janela sequencial.
    Frases sem match bom ficam com tempos interpolados entre vizinhos.
    Quando `duracao_video_segundos` é informada, segmentos e cues respeitam esse teto.
    """
    frases_norm = [f.strip() for f in frases if (f or "").strip()]
    if not frases_norm:
        return ResultadoAlinhamentoLegendasTranscribrothers([], 0, 0)

    segmentos_uteis = _filtrar_segmentos_dentro_da_duracao_video_transcribrothers(
        segmentos,
        duracao_video_segundos,
    )
    teto_interp = (
        float(duracao_video_segundos)
        if duracao_video_segundos is not None and duracao_video_segundos > 0
        else None
    )

    if not segmentos_uteis:
        # Sem STT útil: espaça cues em 3s a partir de 0 (com teto se houver)
        cues = []
        for i, f in enumerate(frases_norm):
            ini = float(i * 3)
            fim = float(i * 3 + 2.5)
            if teto_interp is not None and ini >= teto_interp:
                break
            if teto_interp is not None:
                fim = min(fim, teto_interp)
            if fim <= ini:
                break
            cues.append(
                CueLegendaAlinhadaTranscribrothers(
                    texto=f,
                    inicio_segundos=ini,
                    fim_segundos=fim,
                    casado=False,
                )
            )
        cues = _clamp_cues_a_duracao_video_transcribrothers(cues, duracao_video_segundos)
        return ResultadoAlinhamentoLegendasTranscribrothers(cues, 0, len(cues))

    cursor = 0
    preliminares: list[tuple[str, float | None, float | None, bool]] = []
    for frase in frases_norm:
        fim_janela = min(len(segmentos_uteis), cursor + _JANELA_SEGMENTOS_BUSCA)
        melhor_idx = -1
        melhor_score = 0.0
        for idx in range(cursor, fim_janela):
            score = _similaridade_texto_transcribrothers(frase, segmentos_uteis[idx].texto)
            if score > melhor_score:
                melhor_score = score
                melhor_idx = idx
        if melhor_idx >= 0 and melhor_score >= limiar_similaridade:
            seg = segmentos_uteis[melhor_idx]
            preliminares.append((frase, float(seg.inicio_segundos), float(seg.fim_segundos), True))
            cursor = melhor_idx + 1
        else:
            preliminares.append((frase, None, None, False))

    # Interpolação de gaps
    cues: list[CueLegendaAlinhadaTranscribrothers] = []
    n = len(preliminares)
    fim_fallback = teto_interp if teto_interp is not None else float(segmentos_uteis[-1].fim_segundos)
    for i, (texto, ini, fim, casado) in enumerate(preliminares):
        if casado and ini is not None and fim is not None:
            if fim <= ini:
                fim = ini + 1.5
            cues.append(
                CueLegendaAlinhadaTranscribrothers(
                    texto=texto,
                    inicio_segundos=ini,
                    fim_segundos=fim,
                    casado=True,
                )
            )
            continue

        ini_ant = 0.0
        for j in range(i - 1, -1, -1):
            if preliminares[j][1] is not None:
                ini_ant = float(preliminares[j][2] or preliminares[j][1] or 0.0)
                break
        fim_prox = None
        for j in range(i + 1, n):
            if preliminares[j][1] is not None:
                fim_prox = float(preliminares[j][1] or 0.0)
                break
        if fim_prox is None:
            fim_prox = max(ini_ant + 2.5, fim_fallback)
        if teto_interp is not None:
            fim_prox = min(fim_prox, teto_interp)

        gap_count = 1
        k = i + 1
        while k < n and preliminares[k][1] is None:
            gap_count += 1
            k += 1
        pos = 0
        j = i - 1
        while j >= 0 and preliminares[j][1] is None:
            pos += 1
            j -= 1
        dur_total = max(0.5, fim_prox - ini_ant)
        slice_dur = dur_total / gap_count
        inicio = ini_ant + pos * slice_dur
        fim_cue = inicio + slice_dur
        if fim_cue <= inicio:
            fim_cue = inicio + 1.2
        cues.append(
            CueLegendaAlinhadaTranscribrothers(
                texto=texto,
                inicio_segundos=inicio,
                fim_segundos=fim_cue,
                casado=False,
            )
        )

    # Garante ordem não decrescente e duração mínima (antes do clamp final)
    for i in range(1, len(cues)):
        if cues[i].inicio_segundos < cues[i - 1].fim_segundos:
            novo_ini = cues[i - 1].fim_segundos
            novo_fim = max(novo_ini + _DURACAO_MINIMA_CUE_SEGUNDOS, cues[i].fim_segundos)
            cues[i] = CueLegendaAlinhadaTranscribrothers(
                texto=cues[i].texto,
                inicio_segundos=novo_ini,
                fim_segundos=novo_fim,
                casado=cues[i].casado,
            )

    cues = _clamp_cues_a_duracao_video_transcribrothers(cues, duracao_video_segundos)
    casadas = sum(1 for c in cues if c.casado)
    return ResultadoAlinhamentoLegendasTranscribrothers(
        cues=cues,
        quantidade_casadas=casadas,
        quantidade_interpoladas=len(cues) - casadas,
    )
