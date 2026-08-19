"""Testes do checkpoint Salvar projeto (sem gerar MP4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers import (
    salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def _gravar_manifesto_duas_cues(work: Path) -> None:
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
        work=work,
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="um",
                inicio_video_segundos=0.0,
                fim_video_segundos=2.0,
                origem_ancora="markdown_t",
                casado=True,
                sem_narracao=False,
                voz_tts="Kore",
                texto_tts="",
                id_fonte_video="",
            ),
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="dois",
                inicio_video_segundos=2.0,
                fim_video_segundos=5.0,
                origem_ancora="markdown_t",
                casado=True,
                sem_narracao=False,
                voz_tts="Kore",
                texto_tts="",
                id_fonte_video="",
            ),
        ],
    )


def test_salvar_estado_editor_grava_vtt_e_manifesto_com_fonte_e_sem_narracao(
    tmp_path: Path,
) -> None:
    work = tmp_path / "job"
    assets = work / "assets"
    assets.mkdir(parents=True)
    _gravar_manifesto_duas_cues(work)

    r = salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers(
        job_id="job-teste",
        work=work,
        diretorio_assets=assets,
        steps_json={},
        cues_brutas=[
            {
                "inicio_segundos": 0.0,
                "fim_segundos": 3.5,
                "texto": "Nova funcionalidade",
                "sem_narracao": True,
                "voz_tts": "Kore",
                "texto_tts": "",
            },
            {
                "inicio_segundos": 3.5,
                "fim_segundos": 8.0,
                "texto": "dois editado",
                "sem_narracao": False,
                "voz_tts": "Puck",
                "texto_tts": "dois editado fala",
            },
        ],
        janelas_brutas=[
            {
                "inicio_video_segundos": 0.0,
                "fim_video_segundos": 3.5,
                "id_fonte_video": "mabcdef123456",
            },
            {
                "inicio_video_segundos": 10.0,
                "fim_video_segundos": 14.0,
                "id_fonte_video": "entrada",
            },
        ],
        voz_padrao_job="Kore",
    )
    assert r.quantidade_cues == 2
    assert (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).is_file()
    assert r.steps_json_atualizado.get("editor_video_narrado_audio_mp4_desatualizado") is True
    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    assert manifest is not None
    assert len(manifest) == 2
    assert manifest[0].sem_narracao is True
    assert manifest[0].id_fonte_video == "mabcdef123456"
    assert manifest[1].voz_tts == "Puck"
    assert "dois editado fala" in manifest[1].texto_tts
    vtt = (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).read_text(
        encoding="utf-8"
    )
    assert "Nova funcionalidade" in vtt or "sem narração" in vtt.lower()


def test_salvar_estado_editor_promove_previa_tts_valida_para_wav_definitivo(
    tmp_path: Path,
) -> None:
    """Prévia regenerada no editor deve virar cue_narracao_XXXX no checkpoint."""
    from transcribrothers_backend.modulo_promover_preview_tts_cue_validada_para_wav_definitivo_narracao_transcribrothers import (
        gravar_meta_preview_tts_cue_narracao_transcribrothers,
    )

    work = tmp_path / "job"
    assets = work / "assets"
    assets.mkdir(parents=True)
    _gravar_manifesto_duas_cues(work)

    dir_wavs = work / "wavs_narracao_por_cue"
    dir_wavs.mkdir(parents=True)
    # WAV antigo (conteúdo A) e prévia nova (conteúdo B) da cue 1.
    (dir_wavs / "cue_narracao_0001.wav").write_bytes(b"RIFF" + b"OLD_" + b"\x00" * 76)
    preview = dir_wavs / "preview_cue_narracao_0001.wav"
    preview.write_bytes(b"RIFF" + b"NEW_" + b"\x00" * 76)
    gravar_meta_preview_tts_cue_narracao_transcribrothers(
        work=work,
        indice_zero_based=1,
        texto="dois editado fala",
        voz_tts="Puck",
    )

    r = salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers(
        job_id="job-teste",
        work=work,
        diretorio_assets=assets,
        steps_json={},
        cues_brutas=[
            {
                "inicio_segundos": 0.0,
                "fim_segundos": 2.0,
                "texto": "um",
                "sem_narracao": False,
                "voz_tts": "Kore",
            },
            {
                "inicio_segundos": 2.0,
                "fim_segundos": 5.0,
                "texto": "dois editado",
                "sem_narracao": False,
                "voz_tts": "Puck",
                "texto_tts": "dois editado fala",
            },
        ],
        janelas_brutas=[
            {"inicio_video_segundos": 0.0, "fim_video_segundos": 2.0},
            {"inicio_video_segundos": 2.0, "fim_video_segundos": 5.0},
        ],
        voz_padrao_job="Kore",
    )
    assert r.previews_promovidas == 1
    assert 1 in r.indices_previews_promovidas
    assert r.steps_json_atualizado.get("editor_video_narrado_audio_mp4_desatualizado") is True
    definitivo = dir_wavs / "cue_narracao_0001.wav"
    assert definitivo.read_bytes() == preview.read_bytes()
    assert definitivo.read_bytes().startswith(b"RIFFNEW_")


def test_salvar_estado_editor_exige_janelas_ao_mudar_quantidade(tmp_path: Path) -> None:
    work = tmp_path / "job"
    assets = work / "assets"
    assets.mkdir(parents=True)
    _gravar_manifesto_duas_cues(work)
    with pytest.raises(ValueError, match="não bate"):
        salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers(
            job_id="job-teste",
            work=work,
            diretorio_assets=assets,
            steps_json={},
            cues_brutas=[
                {
                    "inicio_segundos": 0.0,
                    "fim_segundos": 2.0,
                    "texto": "só uma",
                    "sem_narracao": False,
                }
            ],
            janelas_brutas=[
                {"inicio_video_segundos": 0.0, "fim_video_segundos": 2.0},
                {"inicio_video_segundos": 2.0, "fim_video_segundos": 4.0},
            ],
        )
