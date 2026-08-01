"""Cue «sem narração»: silêncio com duração da janela de vídeo (não TTS)."""

from __future__ import annotations

from pathlib import Path

import pytest

from transcribrothers_backend.modulo_api_salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers import (
    validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    obter_duracao_wav_pcm16_mono_segundos_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers,
)
from transcribrothers_backend.modulo_util_montar_segmentos_retarget_respeitando_timeline_vtt_cues_editadas_transcribrothers import (
    gravar_wav_silencio_pcm16_mono_segundos_transcribrothers,
)


def test_validar_cue_sem_narracao_aceita_texto_vazio() -> None:
    cues = validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(
        [
            {
                "inicio_segundos": 0.0,
                "fim_segundos": 2.0,
                "texto": "   ",
                "sem_narracao": True,
            }
        ]
    )
    assert len(cues) == 1
    assert cues[0].sem_narracao is True
    assert cues[0].texto  # placeholder para VTT


def test_validar_cue_com_texto_vazio_sem_flag_ainda_rejeita() -> None:
    with pytest.raises(Exception, match="texto vazio"):
        validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(
            [{"inicio_segundos": 0.0, "fim_segundos": 1.0, "texto": "  "}]
        )


def test_silencio_cue_sem_narracao_usa_duracao_da_janela(tmp_path: Path) -> None:
    saida = tmp_path / "cue_narracao_0003.wav"
    caminho = gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers(
        caminho_wav_saida=saida,
        inicio_video_segundos=10.0,
        fim_video_segundos=15.5,
    )
    assert caminho.is_file()
    dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho)
    assert dur == pytest.approx(5.5, abs=0.05)


def test_helper_silencio_basico_ainda_funciona(tmp_path: Path) -> None:
    p = gravar_wav_silencio_pcm16_mono_segundos_transcribrothers(tmp_path / "s.wav", 1.25)
    assert obter_duracao_wav_pcm16_mono_segundos_transcribrothers(p) == pytest.approx(1.25, abs=0.05)
