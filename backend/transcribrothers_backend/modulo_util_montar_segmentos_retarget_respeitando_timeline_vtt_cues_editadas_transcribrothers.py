"""Monta segmentos retarget densos: só cues (sem gaps), na ordem da timeline VTT."""

from __future__ import annotations

import shutil
import wave
from dataclasses import dataclass
from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    SegmentoVideoNarradoRetargetTranscribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    obter_duracao_wav_pcm16_mono_segundos_transcribrothers,
)

_SAMPLE_RATE_PADRAO_HZ = 24000
_EPS_GAP_SEGUNDOS = 0.05


@dataclass(frozen=True)
class CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers:
    inicio_vtt_segundos: float
    fim_vtt_segundos: float
    inicio_video_segundos: float
    fim_video_segundos: float
    caminho_wav: Path
    texto: str = ""


@dataclass(frozen=True)
class ResultadoMontagemSegmentosEdicoesModalTranscribrothers:
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers]
    textos_na_ordem: list[str]
    duracoes_audio_na_ordem: list[float]


def _gravar_pcm16_mono_wav_transcribrothers(
    caminho: Path,
    pcm: bytes,
    *,
    sample_rate_hz: int,
) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(sample_rate_hz))
        wf.writeframes(pcm)


def gravar_wav_silencio_pcm16_mono_segundos_transcribrothers(
    caminho: Path,
    segundos: float,
    *,
    sample_rate_hz: int = _SAMPLE_RATE_PADRAO_HZ,
) -> Path:
    n_frames = max(1, int(round(max(_EPS_GAP_SEGUNDOS, float(segundos)) * int(sample_rate_hz))))
    _gravar_pcm16_mono_wav_transcribrothers(
        caminho,
        b"\x00\x00" * n_frames,
        sample_rate_hz=sample_rate_hz,
    )
    return caminho


def ajustar_wav_pcm16_mono_para_duracao_alvo_segundos_transcribrothers(
    *,
    caminho_wav_entrada: Path,
    duracao_alvo_segundos: float,
    caminho_wav_saida: Path,
) -> Path:
    """Corta ou preenche com silêncio para caber no slot VTT."""
    alvo = max(_EPS_GAP_SEGUNDOS, float(duracao_alvo_segundos))
    with wave.open(str(caminho_wav_entrada), "rb") as wf:
        canais = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        rate = wf.getframerate()
        if canais != 1 or sampwidth != 2:
            raise ValueError(
                f"WAV precisa ser PCM16 mono (canais={canais}, sampwidth={sampwidth})."
            )
        frames = wf.readframes(wf.getnframes())

    n_alvo = max(1, int(round(alvo * int(rate))))
    bytes_por_frame = 2
    n_atual = len(frames) // bytes_por_frame
    if n_atual >= n_alvo:
        pcm = frames[: n_alvo * bytes_por_frame]
    else:
        pcm = frames + (b"\x00\x00" * (n_alvo - n_atual))
    _gravar_pcm16_mono_wav_transcribrothers(caminho_wav_saida, pcm, sample_rate_hz=rate)
    return caminho_wav_saida


def montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers(
    *,
    cues: list[CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers],
    diretorio_wavs_preparados: Path,
) -> ResultadoMontagemSegmentosEdicoesModalTranscribrothers:
    """
    Montagem densa (como o play do modal): só as cues, na ordem da timeline VTT,
    sem preencher gaps com silêncio. Cada segmento usa o WAV da cue (duração natural)
    e a janela de tela correspondente.
    """
    if not cues:
        raise ValueError("Nenhuma cue para montar o vídeo narrado.")

    ordenadas = sorted(
        enumerate(cues),
        key=lambda par: (par[1].inicio_vtt_segundos, par[0]),
    )
    diretorio_wavs_preparados.mkdir(parents=True, exist_ok=True)
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers] = []
    textos: list[str] = []
    duracoes: list[float] = []

    for ordem, (indice_original, cue) in enumerate(ordenadas):
        if not cue.caminho_wav.is_file():
            raise FileNotFoundError(f"WAV da cue {indice_original + 1} não encontrado.")
        caminho_copiado = (
            diretorio_wavs_preparados / f"cue_densa_{ordem:04d}_idx_{indice_original:04d}.wav"
        )
        shutil.copy2(cue.caminho_wav, caminho_copiado)
        dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_copiado)
        if dur <= _EPS_GAP_SEGUNDOS:
            raise RuntimeError(f"WAV da cue {indice_original + 1} sem duração útil.")
        segmentos.append(
            SegmentoVideoNarradoRetargetTranscribrothers(
                caminho_wav=caminho_copiado,
                inicio_video_segundos=float(cue.inicio_video_segundos),
                fim_video_segundos=float(cue.fim_video_segundos),
            )
        )
        textos.append((cue.texto or "").strip() or f"Cue {indice_original + 1}")
        duracoes.append(dur)

    return ResultadoMontagemSegmentosEdicoesModalTranscribrothers(
        segmentos=segmentos,
        textos_na_ordem=textos,
        duracoes_audio_na_ordem=duracoes,
    )
