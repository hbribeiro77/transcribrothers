"""Mudança de voz por cue marca a cue para regenerar TTS no modal Assistir."""

from __future__ import annotations

import json
from pathlib import Path

from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers,
)


def _gravar_manifest_minimo(work: Path, *, voz: str = "Kore") -> None:
    work.mkdir(parents=True, exist_ok=True)
    payload = {
        "versao": 1,
        "quantidade_cues": 2,
        "cues": [
            {
                "texto": "primeira cue",
                "inicio_video_segundos": 0.0,
                "fim_video_segundos": 2.0,
                "origem_ancora": "markdown_t",
                "casado": True,
                "sem_narracao": False,
                "voz_tts": voz,
            },
            {
                "texto": "segunda cue",
                "inicio_video_segundos": 2.0,
                "fim_video_segundos": 4.0,
                "origem_ancora": "markdown_t",
                "casado": True,
                "sem_narracao": False,
                "voz_tts": voz,
            },
        ],
    }
    (work / "manifest_cues_narracao_janelas_video.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_mudanca_de_voz_em_uma_cue_entra_nos_indices_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest_minimo(work, voz="Kore")
    cues, indices, _mapa = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["primeira cue", "segunda cue"],
        flags_sem_narracao=[False, False],
        vozes_desejadas=["Aoede", "Kore"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert len(cues) == 2
    assert cues[0].voz_tts == "Aoede"
    assert cues[1].voz_tts == "Kore"
    assert indices == [0]


def test_mesma_voz_nao_marca_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest_minimo(work, voz="Kore")
    _cues, indices, _mapa = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["primeira cue", "segunda cue"],
        flags_sem_narracao=[False, False],
        vozes_desejadas=["Kore", "Kore"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert indices == []
