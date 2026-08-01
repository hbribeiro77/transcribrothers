"""Validação determinística de cues de legenda antes de gastar TTS/mux."""

from __future__ import annotations

from dataclasses import dataclass

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
    ResultadoAlinhamentoLegendasTranscribrothers,
)

_MARGEM_DURACAO_SEGUNDOS = 0.5
_MAX_CUES_INTERPOLADAS_CONSECUTIVAS = 6
_PERCENTUAL_CASADO_MINIMO = 25.0
_PERCENTUAL_CASADO_COM_MINIMO_ABSOLUTO = 15.0
_QUANTIDADE_CASADAS_MINIMA_ALTERNATIVA = 3


@dataclass(frozen=True)
class ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers:
    ok: bool
    motivo_rejeicao: str | None = None


def _maior_sequencia_interpolada_consecutiva_transcribrothers(
    cues: list[CueLegendaAlinhadaTranscribrothers],
) -> int:
    melhor = 0
    atual = 0
    for cue in cues:
        if not cue.casado:
            atual += 1
            melhor = max(melhor, atual)
        else:
            atual = 0
    return melhor


def validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
    alinhamento: ResultadoAlinhamentoLegendasTranscribrothers,
    *,
    duracao_video_segundos: float,
) -> ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers:
    """
    Fail-fast antes do TTS: cues vazias, além da duração do vídeo,
    % casado insuficiente ou longa sequência só interpolada.
    """
    cues = list(alinhamento.cues)
    if not cues:
        return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao="Nenhuma cue de legenda foi gerada a partir do documento.",
        )

    if duracao_video_segundos <= 0:
        return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao="Duração do vídeo inválida para validar as legendas.",
        )

    max_fim = max(float(c.fim_segundos) for c in cues)
    teto = float(duracao_video_segundos) + _MARGEM_DURACAO_SEGUNDOS
    if max_fim > teto:
        return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao=(
                f"Legendas ultrapassam a duração do vídeo "
                f"({max_fim:.1f}s > {duracao_video_segundos:.1f}s). "
                "Provável desalinhamento ou timestamps inventados."
            ),
        )

    pct = float(alinhamento.percentual_casado)
    casadas = int(alinhamento.quantidade_casadas)
    casamento_ok = pct >= _PERCENTUAL_CASADO_MINIMO or (
        casadas >= _QUANTIDADE_CASADAS_MINIMA_ALTERNATIVA
        and pct >= _PERCENTUAL_CASADO_COM_MINIMO_ABSOLUTO
    )
    if not casamento_ok:
        return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao=(
                f"Poucas legendas casaram com a transcrição "
                f"({pct:.0f}% casado, {casadas} cue(s) casada(s)). "
                "Revise o documento ou a transcrição antes de narrar."
            ),
        )

    seq_interp = _maior_sequencia_interpolada_consecutiva_transcribrothers(cues)
    if seq_interp > _MAX_CUES_INTERPOLADAS_CONSECUTIVAS:
        return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao=(
                f"Há {seq_interp} cues interpoladas consecutivas "
                f"(limite {_MAX_CUES_INTERPOLADAS_CONSECUTIVAS}). "
                "Isso indica chute em massa nos tempos."
            ),
        )

    return ResultadoValidacaoCuesLegendasAntesNarracaoTranscribrothers(ok=True, motivo_rejeicao=None)
