"""Promoção de prévia TTS validada a WAV definitivo da cue."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_promover_preview_tts_cue_validada_para_wav_definitivo_narracao_transcribrothers import (
    gravar_meta_preview_tts_cue_narracao_transcribrothers,
    previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers,
    promover_preview_tts_cue_para_wav_definitivo_transcribrothers,
    promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers,
)


def _gravar_wav_falso(caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(b"RIFF" + b"\x00" * 80)


def test_previa_valida_bate_texto_e_voz(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_wav_falso(
        work / "wavs_narracao_por_cue" / "preview_cue_narracao_0000.wav"
    )
    gravar_meta_preview_tts_cue_narracao_transcribrothers(
        work=work,
        indice_zero_based=0,
        texto="  Olá   mundo  ",
        voz_tts="Aoede",
        modelo="gemini/gemini-2.5-flash-preview-tts",
    )
    assert previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers(
        work=work,
        indice_zero_based=0,
        texto="Olá mundo",
        voz_tts="aoede",
    )
    assert not previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers(
        work=work,
        indice_zero_based=0,
        texto="Olá mundo",
        voz_tts="Kore",
    )
    assert not previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers(
        work=work,
        indice_zero_based=0,
        texto="outro texto",
        voz_tts="Aoede",
    )


def test_promove_preview_para_cue_narracao(tmp_path: Path) -> None:
    work = tmp_path / "job"
    preview = work / "wavs_narracao_por_cue" / "preview_cue_narracao_0001.wav"
    _gravar_wav_falso(preview)
    gravar_meta_preview_tts_cue_narracao_transcribrothers(
        work=work,
        indice_zero_based=1,
        texto="frase validada",
        voz_tts="Kore",
    )
    definitivo = promover_preview_tts_cue_para_wav_definitivo_transcribrothers(
        work=work,
        indice_zero_based=1,
        texto="frase validada",
        voz_tts="Kore",
    )
    assert definitivo is not None
    assert definitivo.name == "cue_narracao_0001.wav"
    assert definitivo.is_file()
    assert definitivo.read_bytes() == preview.read_bytes()


def test_lista_promove_e_deixa_restante_para_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    for i, texto in ((0, "com previa"), (1, "sem previa")):
        if i == 0:
            _gravar_wav_falso(
                work / "wavs_narracao_por_cue" / f"preview_cue_narracao_{i:04d}.wav"
            )
            gravar_meta_preview_tts_cue_narracao_transcribrothers(
                work=work,
                indice_zero_based=i,
                texto=texto,
                voz_tts="Kore",
            )
    ainda, promovidos, caminhos = (
        promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers(
            work=work,
            indices_sujos=[0, 1],
            textos_por_indice=["com previa", "sem previa"],
            vozes_por_indice=["Kore", "Kore"],
            flags_sem_narracao=[False, False],
            quantidade_cues_estavel=True,
        )
    )
    assert promovidos == [0]
    assert ainda == [1]
    assert 0 in caminhos


def test_quantidade_instavel_nao_promove(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_wav_falso(work / "wavs_narracao_por_cue" / "preview_cue_narracao_0000.wav")
    gravar_meta_preview_tts_cue_narracao_transcribrothers(
        work=work,
        indice_zero_based=0,
        texto="x",
        voz_tts="Kore",
    )
    ainda, promovidos, caminhos = (
        promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers(
            work=work,
            indices_sujos=[0],
            textos_por_indice=["x"],
            vozes_por_indice=["Kore"],
            flags_sem_narracao=[False],
            quantidade_cues_estavel=False,
        )
    )
    assert ainda == [0]
    assert promovidos == []
    assert caminhos == {}
