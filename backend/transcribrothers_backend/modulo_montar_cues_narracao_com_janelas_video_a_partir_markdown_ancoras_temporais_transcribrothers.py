"""Monta cues de narração com janelas de vídeo a partir de âncoras `?t=` no Markdown (estratégia B)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
    ResultadoAlinhamentoLegendasTranscribrothers,
)
from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)

_RE_ANCORA_TEMPORAL_T_SEGUNDOS = re.compile(r"\?t=(\d+(?:\.\d+)?)", re.IGNORECASE)
_HOLD_PADRAO_APOS_ULTIMA_ANCORA_SEGUNDOS = 4.0
_JANELA_MINIMA_VIDEO_SEGUNDOS = 0.45
_QUANTIDADE_MINIMA_ANCORAS_PARA_USAR_MARKDOWN = 1


@dataclass(frozen=True)
class CueNarracaoComJanelaVideoTranscribrothers:
    texto: str
    inicio_video_segundos: float
    fim_video_segundos: float
    origem_ancora: str  # "markdown_t" | "stt"
    casado: bool
    sem_narracao: bool = False
    # Voz Gemini TTS desta cue; vazio = herda o padrão do job/app.
    voz_tts: str = ""
    # Pronúncia para TTS; vazio = narrar o mesmo texto da legenda (`texto`).
    texto_tts: str = ""
    # Fonte de tela: ""/"entrada" = video_entrada; senão id da biblioteca_midias_tela.
    id_fonte_video: str = ""


@dataclass(frozen=True)
class ResultadoCuesNarracaoComJanelasVideoTranscribrothers:
    cues: list[CueNarracaoComJanelaVideoTranscribrothers]
    modo: str  # "markdown_ancoras" | "stt"
    quantidade_ancoras_markdown: int
    quantidade_casadas: int
    quantidade_interpoladas: int

    @property
    def percentual_casado(self) -> float:
        total = len(self.cues)
        if total == 0:
            return 0.0
        return 100.0 * self.quantidade_casadas / total


def listar_timestamps_ancoras_t_segundos_no_markdown_transcribrothers(markdown: str) -> list[float]:
    saida: list[float] = []
    for m in _RE_ANCORA_TEMPORAL_T_SEGUNDOS.finditer(markdown or ""):
        try:
            saida.append(float(m.group(1)))
        except ValueError:
            continue
    return saida


def markdown_tem_ancoras_temporais_suficientes_para_janelas_video_transcribrothers(
    markdown: str,
) -> bool:
    return (
        len(listar_timestamps_ancoras_t_segundos_no_markdown_transcribrothers(markdown))
        >= _QUANTIDADE_MINIMA_ANCORAS_PARA_USAR_MARKDOWN
    )


def _clamp_janela_video_transcribrothers(
    inicio: float,
    fim: float,
    *,
    duracao_video_segundos: float,
) -> tuple[float, float]:
    dur = max(0.0, float(duracao_video_segundos))
    a = max(0.0, min(float(inicio), dur))
    b = max(0.0, min(float(fim), dur))
    if b < a:
        a, b = b, a
    if (b - a) < _JANELA_MINIMA_VIDEO_SEGUNDOS:
        b = min(dur, a + _JANELA_MINIMA_VIDEO_SEGUNDOS)
        if (b - a) < _JANELA_MINIMA_VIDEO_SEGUNDOS and a > 0:
            a = max(0.0, b - _JANELA_MINIMA_VIDEO_SEGUNDOS)
    return a, b


def _partir_janela_entre_frases_transcribrothers(
    inicio: float,
    fim: float,
    quantidade: int,
) -> list[tuple[float, float]]:
    if quantidade <= 0:
        return []
    if quantidade == 1:
        return [(inicio, fim)]
    span = max(fim - inicio, _JANELA_MINIMA_VIDEO_SEGUNDOS)
    passo = span / quantidade
    out: list[tuple[float, float]] = []
    for i in range(quantidade):
        a = inicio + i * passo
        b = inicio + (i + 1) * passo if i < quantidade - 1 else fim
        if b <= a:
            b = a + _JANELA_MINIMA_VIDEO_SEGUNDOS
        out.append((a, b))
    return out


def montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
    markdown: str,
    *,
    duracao_video_segundos: float,
) -> ResultadoCuesNarracaoComJanelasVideoTranscribrothers:
    """
    Estratégia B: texto antes de cada `?t=` fica associado àquela âncora;
    a janela de tela vai da âncora atual até a próxima (ou hold após a última).
    """
    md = markdown or ""
    matches = list(_RE_ANCORA_TEMPORAL_T_SEGUNDOS.finditer(md))
    if not matches:
        return ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
            cues=[],
            modo="markdown_ancoras",
            quantidade_ancoras_markdown=0,
            quantidade_casadas=0,
            quantidade_interpoladas=0,
        )

    dur = max(0.0, float(duracao_video_segundos))
    cues: list[CueNarracaoComJanelaVideoTranscribrothers] = []

    for i, m in enumerate(matches):
        t_ancora = float(m.group(1))
        inicio_char = 0 if i == 0 else matches[i - 1].end()
        trecho_md = md[inicio_char : m.start()]
        texto_plano = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(
            trecho_md
        )
        frases = partir_texto_plano_em_frases_para_legendas_transcribrothers(texto_plano)
        if not frases:
            continue

        if i + 1 < len(matches):
            t_fim = float(matches[i + 1].group(1))
        else:
            t_fim = min(dur, t_ancora + _HOLD_PADRAO_APOS_ULTIMA_ANCORA_SEGUNDOS)
        ini_v, fim_v = _clamp_janela_video_transcribrothers(
            t_ancora,
            t_fim,
            duracao_video_segundos=dur,
        )
        janelas = _partir_janela_entre_frases_transcribrothers(ini_v, fim_v, len(frases))
        for frase, (a, b) in zip(frases, janelas, strict=True):
            aa, bb = _clamp_janela_video_transcribrothers(a, b, duracao_video_segundos=dur)
            cues.append(
                CueNarracaoComJanelaVideoTranscribrothers(
                    texto=frase,
                    inicio_video_segundos=aa,
                    fim_video_segundos=bb,
                    origem_ancora="markdown_t",
                    casado=True,
                )
            )

    trecho_apos = md[matches[-1].end() :]
    texto_apos = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(
        trecho_apos
    )
    frases_apos = partir_texto_plano_em_frases_para_legendas_transcribrothers(texto_apos)
    if frases_apos:
        t_last = float(matches[-1].group(1))
        ini_v, fim_v = _clamp_janela_video_transcribrothers(
            t_last,
            min(dur, t_last + _HOLD_PADRAO_APOS_ULTIMA_ANCORA_SEGUNDOS),
            duracao_video_segundos=dur,
        )
        for frase, (a, b) in zip(
            frases_apos,
            _partir_janela_entre_frases_transcribrothers(ini_v, fim_v, len(frases_apos)),
            strict=True,
        ):
            aa, bb = _clamp_janela_video_transcribrothers(a, b, duracao_video_segundos=dur)
            cues.append(
                CueNarracaoComJanelaVideoTranscribrothers(
                    texto=frase,
                    inicio_video_segundos=aa,
                    fim_video_segundos=bb,
                    origem_ancora="markdown_t",
                    casado=True,
                )
            )

    casadas = sum(1 for c in cues if c.casado)
    return ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=cues,
        modo="markdown_ancoras",
        quantidade_ancoras_markdown=len(matches),
        quantidade_casadas=casadas,
        quantidade_interpoladas=len(cues) - casadas,
    )


def converter_alinhamento_stt_em_cues_com_janelas_video_transcribrothers(
    alinhamento: ResultadoAlinhamentoLegendasTranscribrothers,
) -> ResultadoCuesNarracaoComJanelasVideoTranscribrothers:
    """Fallback: janelas = tempos das cues alinhadas ao STT."""
    cues = [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=c.texto,
            inicio_video_segundos=float(c.inicio_segundos),
            fim_video_segundos=float(c.fim_segundos),
            origem_ancora="stt",
            casado=bool(c.casado),
        )
        for c in alinhamento.cues
    ]
    return ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
        cues=cues,
        modo="stt",
        quantidade_ancoras_markdown=0,
        quantidade_casadas=alinhamento.quantidade_casadas,
        quantidade_interpoladas=alinhamento.quantidade_interpoladas,
    )


def converter_cues_janela_video_em_cues_legenda_vtt_timeline_video_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
) -> list[CueLegendaAlinhadaTranscribrothers]:
    """VTT preliminar na timeline do vídeo-fonte (útil para depuração)."""
    return [
        CueLegendaAlinhadaTranscribrothers(
            texto=c.texto,
            inicio_segundos=c.inicio_video_segundos,
            fim_segundos=c.fim_video_segundos,
            casado=c.casado,
        )
        for c in cues
    ]


def converter_cues_janela_video_em_cues_legenda_vtt_timeline_narracao_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    duracoes_audio_por_cue_segundos: list[float],
) -> list[CueLegendaAlinhadaTranscribrothers]:
    """VTT na timeline da narração (soma das durações reais dos WAVs) — estratégia C."""
    if len(duracoes_audio_por_cue_segundos) != len(cues):
        raise ValueError(
            "Quantidade de durações de áudio não bate com a quantidade de cues "
            f"({len(duracoes_audio_por_cue_segundos)} != {len(cues)})."
        )
    out: list[CueLegendaAlinhadaTranscribrothers] = []
    t = 0.0
    for cue, dur in zip(cues, duracoes_audio_por_cue_segundos, strict=True):
        d = max(0.05, float(dur))
        out.append(
            CueLegendaAlinhadaTranscribrothers(
                texto=cue.texto,
                inicio_segundos=t,
                fim_segundos=t + d,
                casado=cue.casado,
            )
        )
        t += d
    return out
