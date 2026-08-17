"""Exclusão de cue no modal: payload menor que o manifesto reconstrói a lista."""

from __future__ import annotations

import json
from pathlib import Path

from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers,
)


def test_resolver_aceita_menos_cues_quando_janelas_acompanham(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    (work / "manifest_cues_narracao_janelas_video.json").write_text(
        json.dumps(
            {
                "versao": 1,
                "quantidade_cues": 3,
                "cues": [
                    {
                        "texto": "a",
                        "inicio_video_segundos": 0,
                        "fim_video_segundos": 1,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                    },
                    {
                        "texto": "b",
                        "inicio_video_segundos": 1,
                        "fim_video_segundos": 2,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                    },
                    {
                        "texto": "c",
                        "inicio_video_segundos": 2,
                        "fim_video_segundos": 3,
                        "origem_ancora": "markdown_t",
                        "casado": True,
                    },
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    cues, indices_tts, mapa_reuso = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["a", "c"],
        textos_tts_desejados=["", ""],
        flags_sem_narracao=[False, True],
        vozes_desejadas=["Kore", "Kore"],
        voz_padrao="Kore",
        janelas_brutas=[
            {"inicio_video_segundos": 0.0, "fim_video_segundos": 1.0},
            {"inicio_video_segundos": 2.0, "fim_video_segundos": 3.0},
        ],
    )
    assert len(cues) == 2
    assert cues[0].texto == "a"
    assert cues[0].sem_narracao is False
    assert cues[1].sem_narracao is True
    # Sem WAV no disco: "a" não reutiliza e precisa de TTS.
    assert indices_tts == [0]
    assert mapa_reuso == {}
