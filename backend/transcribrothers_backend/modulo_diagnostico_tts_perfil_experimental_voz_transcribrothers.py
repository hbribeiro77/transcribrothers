"""Diagnóstico TTS só do perfil experimental_voz — não usar no motor sagrado (padrão)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
)

CHAVE_STEPS_JSON_DIAGNOSTICO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS = (
    "video_narrado_tts_diagnostico_experimental"
)
CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS = (
    "video_narrado_tts_cues_pendentes_timeout"
)
FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS = (
    "video_narrado_aguardando_resolucao_tts_timeout"
)

# Read timeout do experimental (padrão sagrado continua 180s no outro módulo).
# Com notas do diretor enxutas, títulos ~26–30s na probe; 30s ficava no fio da navalha.
TTS_TIMEOUT_READ_EXPERIMENTAL_VOZ_SEGUNDOS = 90.0

_MAX_TENTATIVAS_LOG = 200
_MAX_PULADAS_LOG = 80
_MAX_ERRO_CHARS = 280
_MAX_PREVIEW_CHARS = 120


@dataclass
class TentativaTtsExperimentalVozTranscribrothers:
    indice_cue: int
    tentativa: int
    latencia_ms: int
    resultado: str
    http_status: int | None = None
    erro_curto: str = ""
    texto_preview: str = ""
    voz: str = ""
    chars_content: int = 0

    def para_json(self) -> dict[str, Any]:
        return {
            "indice_cue": self.indice_cue,
            "tentativa": self.tentativa,
            "latencia_ms": self.latencia_ms,
            "resultado": self.resultado,
            "http_status": self.http_status,
            "erro_curto": self.erro_curto,
            "texto_preview": self.texto_preview,
            "voz": self.voz,
            "chars_content": self.chars_content,
        }


@dataclass
class CuePuladaTtsExperimentalVozTranscribrothers:
    indice_cue: int
    texto_preview: str
    motivo: str
    tentativas: int
    ultimo_erro: str
    latencia_ms_ultima: int

    def para_json(self) -> dict[str, Any]:
        return {
            "indice_cue": self.indice_cue,
            "texto_preview": self.texto_preview,
            "motivo": self.motivo,
            "tentativas": self.tentativas,
            "ultimo_erro": self.ultimo_erro,
            "latencia_ms_ultima": self.latencia_ms_ultima,
        }


@dataclass
class FalhaFatalTtsExperimentalVozTranscribrothers:
    indice_cue: int
    texto_preview: str
    motivo: str
    tentativa: int
    erro_curto: str
    latencia_ms: int

    def para_json(self) -> dict[str, Any]:
        return {
            "indice_cue": self.indice_cue,
            "texto_preview": self.texto_preview,
            "motivo": self.motivo,
            "tentativa": self.tentativa,
            "erro_curto": self.erro_curto,
            "latencia_ms": self.latencia_ms,
        }


@dataclass
class DiagnosticoTtsPerfilExperimentalVozTranscribrothers:
    perfil_tts: str = PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS
    timeout_read_segundos: float = TTS_TIMEOUT_READ_EXPERIMENTAL_VOZ_SEGUNDOS
    quantidade_cues_total: int = 0
    quantidade_cues_ok: int = 0
    quantidade_cues_puladas: int = 0
    quantidade_timeouts: int = 0
    tentativas: list[TentativaTtsExperimentalVozTranscribrothers] = field(
        default_factory=list
    )
    cues_puladas: list[CuePuladaTtsExperimentalVozTranscribrothers] = field(
        default_factory=list
    )
    falha: FalhaFatalTtsExperimentalVozTranscribrothers | None = None

    def registrar_tentativa(
        self,
        tentativa: TentativaTtsExperimentalVozTranscribrothers,
    ) -> None:
        if len(self.tentativas) < _MAX_TENTATIVAS_LOG:
            self.tentativas.append(tentativa)
        if tentativa.resultado == "timeout":
            self.quantidade_timeouts += 1

    def registrar_pulada(self, pulada: CuePuladaTtsExperimentalVozTranscribrothers) -> None:
        if len(self.cues_puladas) < _MAX_PULADAS_LOG:
            self.cues_puladas.append(pulada)
        self.quantidade_cues_puladas = len(self.cues_puladas)

    def registrar_falha(self, falha: FalhaFatalTtsExperimentalVozTranscribrothers) -> None:
        self.falha = falha

    def marcar_cue_ok(self) -> None:
        self.quantidade_cues_ok += 1

    def latencias_ok_ms(self) -> list[int]:
        return [t.latencia_ms for t in self.tentativas if t.resultado == "ok"]

    def montar_resumo_texto_para_copiar_transcribrothers(self) -> str:
        lats = sorted(self.latencias_ok_ms())
        p50 = lats[len(lats) // 2] if lats else None
        pmax = lats[-1] if lats else None
        linhas = [
            "DIAGNOSTICO TTS EXPERIMENTAL",
            f"perfil={self.perfil_tts} timeout_read={self.timeout_read_segundos:.0f}s",
            (
                f"cues_total={self.quantidade_cues_total} ok={self.quantidade_cues_ok} "
                f"puladas={self.quantidade_cues_puladas} timeouts={self.quantidade_timeouts}"
            ),
        ]
        if p50 is not None and pmax is not None:
            linhas.append(f"latencia_ok_ms p50={p50} max={pmax}")
        if self.cues_puladas:
            linhas.append("PULADAS:")
            for p in self.cues_puladas:
                linhas.append(
                    f"  cue[{p.indice_cue}] motivo={p.motivo} tentativas={p.tentativas} "
                    f"lat_ultima={p.latencia_ms_ultima}ms «{p.texto_preview}» "
                    f"erro={p.ultimo_erro}"
                )
        if self.falha is not None:
            f = self.falha
            linhas.append("FALHA_FATAL:")
            linhas.append(
                f"  cue[{f.indice_cue}] motivo={f.motivo} tentativa={f.tentativa} "
                f"lat={f.latencia_ms}ms «{f.texto_preview}» erro={f.erro_curto}"
            )
        return "\n".join(linhas)

    def para_steps_json(self) -> dict[str, Any]:
        return {
            "perfil_tts": self.perfil_tts,
            "timeout_read_segundos": self.timeout_read_segundos,
            "quantidade_cues_total": self.quantidade_cues_total,
            "quantidade_cues_ok": self.quantidade_cues_ok,
            "quantidade_cues_puladas": self.quantidade_cues_puladas,
            "quantidade_timeouts": self.quantidade_timeouts,
            "latencia_ok_ms_p50": (
                (sorted(self.latencias_ok_ms())[len(self.latencias_ok_ms()) // 2])
                if self.latencias_ok_ms()
                else None
            ),
            "latencia_ok_ms_max": (
                max(self.latencias_ok_ms()) if self.latencias_ok_ms() else None
            ),
            "tentativas": [t.para_json() for t in self.tentativas],
            "cues_puladas": [p.para_json() for p in self.cues_puladas],
            "falha": self.falha.para_json() if self.falha is not None else None,
            "resumo_texto": self.montar_resumo_texto_para_copiar_transcribrothers(),
        }


def preview_texto_diagnostico_tts_experimental_transcribrothers(texto: str) -> str:
    t = " ".join((texto or "").replace("\r\n", "\n").replace("\r", "\n").split())
    if len(t) <= _MAX_PREVIEW_CHARS:
        return t
    return t[: _MAX_PREVIEW_CHARS - 1] + "…"


def erro_curto_diagnostico_tts_experimental_transcribrothers(exc: BaseException) -> str:
    msg = str(exc or "").replace("\n", " ").strip()
    if len(msg) <= _MAX_ERRO_CHARS:
        return msg
    return msg[: _MAX_ERRO_CHARS - 1] + "…"


def classificar_resultado_erro_tts_experimental_transcribrothers(
    exc: BaseException,
) -> str:
    import httpx

    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    msg = str(exc).lower()
    if "sem choices" in msg or "choices" in msg and "vazia" in msg:
        return "choices_vazio"
    if "áudio tts vazio" in msg or "audio tts vazio" in msg:
        return "audio_vazio"
    if "http 429" in msg:
        return "http_429"
    if "http 5" in msg:
        return "http_5xx"
    if "http 4" in msg:
        return "http_4xx"
    return "erro"


def agora_monotonic_ms_transcribrothers() -> float:
    return time.perf_counter() * 1000.0


def aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers(
    steps: dict[str, Any],
    diagnostico: dict[str, Any] | None,
) -> None:
    """Grava o bloco de diagnóstico no steps_json (só quando há payload)."""
    if diagnostico is None:
        return
    steps[CHAVE_STEPS_JSON_DIAGNOSTICO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS] = diagnostico


def ultima_tentativa_da_cue_diagnostico_tts_experimental_transcribrothers(
    diagnostico: DiagnosticoTtsPerfilExperimentalVozTranscribrothers,
    indice_cue: int,
) -> TentativaTtsExperimentalVozTranscribrothers | None:
    for tentativa in reversed(diagnostico.tentativas):
        if tentativa.indice_cue == indice_cue:
            return tentativa
    return None
