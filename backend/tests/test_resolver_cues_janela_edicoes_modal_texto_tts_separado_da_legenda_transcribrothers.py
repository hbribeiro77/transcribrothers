"""texto_tts (pronúncia) ≠ texto da legenda: dirty TTS olha a fala efetiva."""

from __future__ import annotations

import json
from pathlib import Path

from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers,
)
from transcribrothers_backend.modulo_util_texto_efetivo_para_tts_cue_legenda_ou_override_transcribrothers import (
    texto_efetivo_para_tts_cue_narracao_transcribrothers,
)


def _gravar_manifest(
    work: Path,
    *,
    texto: str = "Configure o DNS",
    texto_tts: str = "",
    voz: str = "Kore",
) -> None:
    work.mkdir(parents=True, exist_ok=True)
    payload = {
        "versao": 1,
        "quantidade_cues": 1,
        "cues": [
            {
                "texto": texto,
                "texto_tts": texto_tts,
                "inicio_video_segundos": 0.0,
                "fim_video_segundos": 2.0,
                "origem_ancora": "markdown_t",
                "casado": True,
                "sem_narracao": False,
                "voz_tts": voz,
            }
        ],
    }
    (work / "manifest_cues_narracao_janelas_video.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_texto_efetivo_usa_override_quando_preenchido() -> None:
    assert (
        texto_efetivo_para_tts_cue_narracao_transcribrothers(
            texto_legenda="Configure o DNS",
            texto_tts="Configure o dê-êne-ésse",
        )
        == "Configure o dê-êne-ésse"
    )
    assert (
        texto_efetivo_para_tts_cue_narracao_transcribrothers(
            texto_legenda="Configure o DNS",
            texto_tts="  ",
        )
        == "Configure o DNS"
    )


def test_override_texto_tts_marca_cue_para_regenerar_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest(work, texto="Configure o DNS", texto_tts="")
    cues, indices = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["Configure o DNS"],
        textos_tts_desejados=["Configure o dê-êne-ésse"],
        flags_sem_narracao=[False],
        vozes_desejadas=["Kore"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert indices == [0]
    assert cues[0].texto == "Configure o DNS"
    assert cues[0].texto_tts == "Configure o dê-êne-ésse"


def test_so_legenda_muda_com_override_igual_nao_marca_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest(
        work,
        texto="DNS antigo",
        texto_tts="dê-êne-ésse",
    )
    cues, indices = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["Configure o DNS"],
        textos_tts_desejados=["dê-êne-ésse"],
        flags_sem_narracao=[False],
        vozes_desejadas=["Kore"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert indices == []
    assert cues[0].texto == "Configure o DNS"
    assert cues[0].texto_tts == "dê-êne-ésse"


def test_sem_override_mudanca_de_legenda_ainda_marca_tts(tmp_path: Path) -> None:
    work = tmp_path / "job"
    _gravar_manifest(work, texto="frase A", texto_tts="")
    _cues, indices = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
        work=work,
        textos_desejados=["frase B"],
        textos_tts_desejados=[""],
        flags_sem_narracao=[False],
        vozes_desejadas=["Kore"],
        voz_padrao="Kore",
        janelas_brutas=None,
    )
    assert indices == [0]
