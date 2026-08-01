"""Validação de cues com janelas de vídeo (âncoras Markdown ou STT) antes do TTS/mux A+B."""

from __future__ import annotations

from dataclasses import dataclass

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
)
from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
    ResultadoAlinhamentoLegendasTranscribrothers,
)
from transcribrothers_backend.modulo_validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers import (
    validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers,
)

_MARGEM_DURACAO_SEGUNDOS = 0.5


@dataclass(frozen=True)
class ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers:
    ok: bool
    motivo_rejeicao: str | None = None


def validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
    resultado: ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
    *,
    duracao_video_segundos: float,
) -> ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers:
    """
    Modo markdown_ancoras: exige cues e janelas dentro da duração do vídeo.
    Modo stt: reutiliza a validação clássica (% casado / interpolação).
    """
    cues = list(resultado.cues)
    if not cues:
        return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao="Nenhuma cue de narração foi gerada a partir do documento.",
        )

    if duracao_video_segundos <= 0:
        return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
            ok=False,
            motivo_rejeicao="Duração do vídeo inválida para validar as janelas de tela.",
        )

    teto = float(duracao_video_segundos) + _MARGEM_DURACAO_SEGUNDOS
    for i, cue in enumerate(cues, start=1):
        if not getattr(cue, "sem_narracao", False) and not (cue.texto or "").strip():
            return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
                ok=False,
                motivo_rejeicao=f"Cue {i} está sem texto narrável.",
            )
        if cue.inicio_video_segundos < -0.01:
            return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
                ok=False,
                motivo_rejeicao=f"Cue {i} tem início de janela negativo.",
            )
        if cue.fim_video_segundos > teto:
            return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
                ok=False,
                motivo_rejeicao=(
                    f"Cue {i} ultrapassa a duração do vídeo "
                    f"({cue.fim_video_segundos:.1f}s > {duracao_video_segundos:.1f}s)."
                ),
            )
        if cue.fim_video_segundos + 1e-6 < cue.inicio_video_segundos:
            return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
                ok=False,
                motivo_rejeicao=f"Cue {i} tem janela de vídeo invertida.",
            )

    if resultado.modo == "markdown_ancoras":
        if resultado.quantidade_ancoras_markdown < 1:
            return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
                ok=False,
                motivo_rejeicao="Documento sem âncoras temporais (?t=) utilizáveis.",
            )
        return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
            ok=True,
            motivo_rejeicao=None,
        )

    # Fallback STT: mesmas regras do validador clássico.
    alinhamento = ResultadoAlinhamentoLegendasTranscribrothers(
        cues=[
            CueLegendaAlinhadaTranscribrothers(
                texto=c.texto,
                inicio_segundos=c.inicio_video_segundos,
                fim_segundos=c.fim_video_segundos,
                casado=c.casado,
            )
            for c in cues
        ],
        quantidade_casadas=resultado.quantidade_casadas,
        quantidade_interpoladas=resultado.quantidade_interpoladas,
    )
    classico = validar_cues_legendas_contra_duracao_video_antes_narracao_tts_transcribrothers(
        alinhamento,
        duracao_video_segundos=duracao_video_segundos,
    )
    return ResultadoValidacaoCuesJanelasVideoAntesNarracaoTranscribrothers(
        ok=classico.ok,
        motivo_rejeicao=classico.motivo_rejeicao,
    )
