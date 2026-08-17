"""Reuso de WAV ao inserir/excluir cue: não regenerar TTS do que ainda casa com o manifesto."""

from __future__ import annotations

import json
from pathlib import Path

from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers,
    remapar_arquivos_wav_narracao_por_mapa_indices_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    resolver_caminho_wav_narracao_por_indice_cue_transcribrothers,
)


def _gravar_manifest_tres_cues(work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    (work / "manifest_cues_narracao_janelas_video.json").write_text(
        json.dumps(
            {
                "versao": 1,
                "quantidade_cues": 3,
                "cues": [
                    {
                        "texto": "alpha",
                        "texto_tts": "",
                        "voz_tts": "Kore",
                        "inicio_video_segundos": 0,
                        "fim_video_segundos": 1,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                        "sem_narracao": False,
                    },
                    {
                        "texto": "beta",
                        "texto_tts": "",
                        "voz_tts": "Kore",
                        "inicio_video_segundos": 1,
                        "fim_video_segundos": 2,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                        "sem_narracao": False,
                    },
                    {
                        "texto": "gamma",
                        "texto_tts": "",
                        "voz_tts": "Puck",
                        "inicio_video_segundos": 2,
                        "fim_video_segundos": 3,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                        "sem_narracao": False,
                    },
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _criar_wav_minimo(caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # Cabeçalho WAV + um pouco de PCM para passar do limiar de 44 bytes.
    caminho.write_bytes(b"RIFF" + b"\x00" * 40 + b"data" + b"\x00" * 64)


def test_inserir_cue_no_meio_so_pede_tts_da_nova_e_mapeia_reuso(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest_tres_cues(work)
    dir_wavs = work / "wavs_narracao_por_cue"
    for i in range(3):
        _criar_wav_minimo(resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, i))

    cues, indices_tts, mapa_reuso = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["alpha", "NOVA", "beta", "gamma"],
        textos_tts_desejados=["", "", "", ""],
        flags_sem_narracao=[False, False, False, False],
        vozes_desejadas=["Kore", "Kore", "Kore", "Puck"],
        voz_padrao="Kore",
        janelas_brutas=[
            {"inicio_video_segundos": 0.0, "fim_video_segundos": 1.0},
            {"inicio_video_segundos": 1.0, "fim_video_segundos": 1.5},
            {"inicio_video_segundos": 1.5, "fim_video_segundos": 2.0},
            {"inicio_video_segundos": 2.0, "fim_video_segundos": 3.0},
        ],
    )
    assert len(cues) == 4
    assert indices_tts == [1]
    assert mapa_reuso == {0: 0, 2: 1, 3: 2}


def test_excluir_cue_do_meio_reusa_wavs_sem_tts_nas_sobreviventes(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest_tres_cues(work)
    dir_wavs = work / "wavs_narracao_por_cue"
    for i in range(3):
        _criar_wav_minimo(resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, i))

    cues, indices_tts, mapa_reuso = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["alpha", "gamma"],
        textos_tts_desejados=["", ""],
        flags_sem_narracao=[False, False],
        vozes_desejadas=["Kore", "Puck"],
        voz_padrao="Kore",
        janelas_brutas=[
            {"inicio_video_segundos": 0.0, "fim_video_segundos": 1.0},
            {"inicio_video_segundos": 2.0, "fim_video_segundos": 3.0},
        ],
    )
    assert len(cues) == 2
    assert indices_tts == []
    assert mapa_reuso == {0: 0, 1: 2}


def test_reordenar_cues_com_quantidade_estavel_reusa_wavs_sem_tts(tmp_path: Path) -> None:
    """Lista estável com ordem trocada: matching por texto+voz, não dirty por índice."""
    work = tmp_path / "job"
    _gravar_manifest_tres_cues(work)
    dir_wavs = work / "wavs_narracao_por_cue"
    for i in range(3):
        _criar_wav_minimo(resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, i))

    cues, indices_tts, mapa_reuso = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["gamma", "alpha", "beta"],
        textos_tts_desejados=["", "", ""],
        flags_sem_narracao=[False, False, False],
        vozes_desejadas=["Puck", "Kore", "Kore"],
        voz_padrao="Kore",
        janelas_brutas=[
            {"inicio_video_segundos": 0.0, "fim_video_segundos": 1.0},
            {"inicio_video_segundos": 1.0, "fim_video_segundos": 2.0},
            {"inicio_video_segundos": 2.0, "fim_video_segundos": 3.0},
        ],
    )
    assert len(cues) == 3
    assert indices_tts == []
    assert mapa_reuso == {0: 2, 1: 0, 2: 1}


def test_editar_uma_cue_na_lista_estavel_so_marca_ela_e_reusa_demais(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest_tres_cues(work)
    dir_wavs = work / "wavs_narracao_por_cue"
    for i in range(3):
        _criar_wav_minimo(resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, i))

    _cues, indices_tts, mapa_reuso = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["alpha", "beta EDITADA", "gamma"],
        textos_tts_desejados=["", "", ""],
        flags_sem_narracao=[False, False, False],
        vozes_desejadas=["Kore", "Kore", "Puck"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert indices_tts == [1]
    assert mapa_reuso == {0: 0, 2: 2}


def test_remapar_arquivos_wav_move_conteudo_para_novos_indices(tmp_path: Path) -> None:
    work = tmp_path / "job"
    dir_wavs = work / "wavs_narracao_por_cue"
    p0 = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, 0)
    p1 = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, 1)
    _criar_wav_minimo(p0)
    _criar_wav_minimo(p1)
    p0.write_bytes(b"RIFF" + b"A" * 80)
    p1.write_bytes(b"RIFF" + b"B" * 80)

    # Inserção no meio: antigo 1 → novo 2; novo 0 = antigo 0.
    remapar_arquivos_wav_narracao_por_mapa_indices_transcribrothers(
        work,
        {0: 0, 2: 1},
    )
    p2 = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, 2)
    assert p0.read_bytes().endswith(b"A" * 80)
    assert p2.is_file()
    assert p2.read_bytes().endswith(b"B" * 80)
