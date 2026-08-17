"""Plano de segmentos retarget denso (só cues, sem gaps) a partir da ordem VTT."""

from __future__ import annotations

import wave
from pathlib import Path

from transcribrothers_backend.modulo_util_montar_segmentos_retarget_respeitando_timeline_vtt_cues_editadas_transcribrothers import (
    CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers,
    ajustar_wav_pcm16_mono_para_duracao_alvo_segundos_transcribrothers,
    montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers,
)


def _gravar_wav_pcm16_mono_segundos(caminho: Path, segundos: float, *, sample_rate: int = 24000) -> None:
    n = max(1, int(round(segundos * sample_rate)))
    with wave.open(str(caminho), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x01\x00" * n)


def _duracao_wav(caminho: Path) -> float:
    with wave.open(str(caminho), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def test_ajustar_wav_preenche_com_silencio_quando_slot_maior(tmp_path: Path) -> None:
    fonte = tmp_path / "cue.wav"
    _gravar_wav_pcm16_mono_segundos(fonte, 1.0)
    saida = tmp_path / "ajustado.wav"
    ajustar_wav_pcm16_mono_para_duracao_alvo_segundos_transcribrothers(
        caminho_wav_entrada=fonte,
        duracao_alvo_segundos=2.5,
        caminho_wav_saida=saida,
    )
    assert abs(_duracao_wav(saida) - 2.5) < 0.03


def test_ajustar_wav_corta_quando_slot_menor(tmp_path: Path) -> None:
    fonte = tmp_path / "cue.wav"
    _gravar_wav_pcm16_mono_segundos(fonte, 2.0)
    saida = tmp_path / "ajustado.wav"
    ajustar_wav_pcm16_mono_para_duracao_alvo_segundos_transcribrothers(
        caminho_wav_entrada=fonte,
        duracao_alvo_segundos=0.8,
        caminho_wav_saida=saida,
    )
    assert abs(_duracao_wav(saida) - 0.8) < 0.03


def test_monta_segmentos_densos_respeita_slot_vtt_nao_a_janela(tmp_path: Path) -> None:
    wav0 = tmp_path / "w0.wav"
    wav1 = tmp_path / "w1.wav"
    _gravar_wav_pcm16_mono_segundos(wav0, 1.2)
    _gravar_wav_pcm16_mono_segundos(wav1, 0.8)
    dir_prep = tmp_path / "prep"
    cues = [
        CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers(
            inicio_vtt_segundos=1.0,
            fim_vtt_segundos=2.0,  # slot 1.0s
            inicio_video_segundos=10.0,
            fim_video_segundos=12.0,  # janela 2s — não deve esticar o segmento
            caminho_wav=wav0,
            texto="primeira",
        ),
        CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers(
            inicio_vtt_segundos=3.5,
            fim_vtt_segundos=4.5,  # slot 1.0s
            inicio_video_segundos=20.0,
            fim_video_segundos=22.0,
            caminho_wav=wav1,
            texto="segunda",
        ),
    ]
    resultado = montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers(
        cues=cues,
        diretorio_wavs_preparados=dir_prep,
    )
    assert len(resultado.segmentos) == 2
    assert abs(_duracao_wav(resultado.segmentos[0].caminho_wav) - 1.0) < 0.03
    assert resultado.segmentos[0].inicio_video_segundos == 10.0
    assert resultado.segmentos[0].fim_video_segundos == 12.0
    assert abs(_duracao_wav(resultado.segmentos[1].caminho_wav) - 1.0) < 0.03
    assert resultado.textos_na_ordem == ["primeira", "segunda"]
    assert abs(resultado.duracoes_audio_na_ordem[0] - 1.0) < 0.03
    assert abs(resultado.duracoes_audio_na_ordem[1] - 1.0) < 0.03


def test_monta_segmentos_estica_wav_quando_slot_vtt_maior_que_fala(tmp_path: Path) -> None:
    wav0 = tmp_path / "w0.wav"
    _gravar_wav_pcm16_mono_segundos(wav0, 1.0)
    dir_prep = tmp_path / "prep"
    cues = [
        CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers(
            inicio_vtt_segundos=0.0,
            fim_vtt_segundos=48.0,
            inicio_video_segundos=0.0,
            fim_video_segundos=48.0,
            caminho_wav=wav0,
            texto="hold longo",
        ),
    ]
    resultado = montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers(
        cues=cues,
        diretorio_wavs_preparados=dir_prep,
    )
    assert abs(resultado.duracoes_audio_na_ordem[0] - 48.0) < 0.05


def test_monta_segmentos_encurta_quando_slot_vtt_menor_que_wav_e_janela(tmp_path: Path) -> None:
    """Ajustar ao áudio: slot 8s, janela ainda 48s, WAV longo → MP4 segue o slot."""
    wav0 = tmp_path / "w0.wav"
    _gravar_wav_pcm16_mono_segundos(wav0, 48.0)
    dir_prep = tmp_path / "prep"
    cues = [
        CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers(
            inicio_vtt_segundos=0.0,
            fim_vtt_segundos=8.0,
            inicio_video_segundos=0.0,
            fim_video_segundos=48.0,
            caminho_wav=wav0,
            texto="encolhida",
        ),
    ]
    resultado = montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers(
        cues=cues,
        diretorio_wavs_preparados=dir_prep,
    )
    assert abs(resultado.duracoes_audio_na_ordem[0] - 8.0) < 0.05
