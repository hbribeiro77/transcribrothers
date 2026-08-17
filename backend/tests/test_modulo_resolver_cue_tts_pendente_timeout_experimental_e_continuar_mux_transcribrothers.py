"""Retry manual de cue com timeout experimental e retomada do mux."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_diagnostico_tts_perfil_experimental_voz_transcribrothers import (
    CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers import (
    descartar_cue_tts_pendente_timeout_experimental_job_transcribrothers,
    gravar_cues_pendentes_timeout_nos_steps_transcribrothers,
    ler_cues_pendentes_timeout_dos_steps_transcribrothers,
    resolver_cue_tts_pendente_timeout_experimental_job_transcribrothers,
)


def test_ler_e_gravar_cues_pendentes_timeout_nos_steps() -> None:
    steps: dict = {}
    assert ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps) == []
    gravar_cues_pendentes_timeout_nos_steps_transcribrothers(
        steps,
        [{"indice": 1, "texto": "oi", "motivo": "timeout"}],
    )
    lidos = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
    assert len(lidos) == 1
    assert lidos[0]["indice"] == 1
    assert steps[CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS]


@pytest.mark.asyncio
async def test_resolver_cue_pendente_remove_da_lista_e_agenda_mux_quando_zera(
    tmp_path: Path,
) -> None:
    job_id = "job-timeout-manual"
    work = tmp_path / "jobs" / job_id
    work.mkdir(parents=True)
    (work / "wavs_narracao_por_cue").mkdir(parents=True)

    steps = {
        "pipeline_fase": FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS,
        CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS: (
            PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS
        ),
        "pipeline_video_narrado_modelo_tts": "gemini/fake-tts",
        CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS: [
            {
                "indice": 0,
                "indice_cue": 1,
                "texto": "Texto antigo",
                "voz": "Kore",
                "motivo": "timeout",
            }
        ],
    }
    row = MagicMock()
    row.steps_json = steps
    row.status = "completed"
    row.error_message = None

    session = AsyncMock()
    session.get = AsyncMock(return_value=row)
    session.commit = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=None)
    session_factory = MagicMock(return_value=session_cm)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    create_task_calls: list = []

    def _create_task_sem_rodar(coro):
        create_task_calls.append(coro)
        coro.close()
        return MagicMock()

    with (
        patch(
            "transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers."
            "_diretorio_trabalho_job",
            return_value=work,
        ),
        patch(
            "transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers."
            "sintetizar_e_gravar_wav_definitivo_cue_experimental_uma_tentativa_transcribrothers",
            new_callable=AsyncMock,
            return_value=(True, "Cue narrada com sucesso."),
        ) as sintetizar,
        patch(
            "transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers."
            "carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers",
            return_value=[],
        ),
        patch(
            "transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers."
            "asyncio.create_task",
            side_effect=_create_task_sem_rodar,
        ),
    ):
        res = await resolver_cue_tts_pendente_timeout_experimental_job_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            indice=0,
            texto="Texto reenviado",
            voz="Kore",
        )

    assert res["ok"] is True
    assert res["pendentes_restantes"] == 0
    assert res["pipeline_continuada"] is True
    sintetizar.assert_awaited_once()
    assert len(create_task_calls) == 1
    assert ler_cues_pendentes_timeout_dos_steps_transcribrothers(row.steps_json) == []


@pytest.mark.asyncio
async def test_descartar_cue_pendente_marca_sem_narracao_e_agenda_mux(
    tmp_path: Path,
) -> None:
    job_id = "job-timeout-descartar"
    work = tmp_path / "jobs" / job_id
    work.mkdir(parents=True)
    (work / "wavs_narracao_por_cue").mkdir(parents=True)

    steps = {
        "pipeline_fase": FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS,
        CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS: (
            PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS
        ),
        "pipeline_video_narrado_modelo_tts": "gemini/fake-tts",
        "narracao_tts_documento": {
            "quantidade_cues_puladas": 0,
            "previews_cues_puladas": [],
        },
        CHAVE_STEPS_JSON_CUES_PENDENTES_TIMEOUT_TTS_EXPERIMENTAL_TRANSCRIBROTHERS: [
            {
                "indice": 0,
                "indice_cue": 1,
                "texto": "Título difícil",
                "voz": "Kore",
                "motivo": "timeout",
            }
        ],
    }
    row = MagicMock()
    row.steps_json = steps
    row.status = "completed"
    row.error_message = None

    session = AsyncMock()
    session.get = AsyncMock(return_value=row)
    session.commit = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=None)
    session_factory = MagicMock(return_value=session_cm)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    create_task_calls: list = []

    def _create_task_sem_rodar(coro):
        create_task_calls.append(coro)
        coro.close()
        return MagicMock()

    cue_manifest = CueNarracaoComJanelaVideoTranscribrothers(
        texto="Título difícil",
        inicio_video_segundos=0.0,
        fim_video_segundos=2.0,
        origem_ancora="markdown_t",
        casado=True,
        sem_narracao=False,
        voz_tts="Kore",
        texto_tts="Título difícil",
    )
    cues_mutaveis = [cue_manifest]

    with (
        patch(
            "transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers."
            "_diretorio_trabalho_job",
            return_value=work,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers."
            "carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers",
            side_effect=lambda _work: cues_mutaveis,
        ),
        patch(
            "transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers."
            "gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers",
        ) as gravar_manifest,
        patch(
            "transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers."
            "asyncio.create_task",
            side_effect=_create_task_sem_rodar,
        ),
    ):
        res = await descartar_cue_tts_pendente_timeout_experimental_job_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            indice=0,
        )

    assert res["ok"] is True
    assert res["pendentes_restantes"] == 0
    assert res["pipeline_continuada"] is True
    assert "sem narração" in res["mensagem"].lower()
    assert len(create_task_calls) == 1
    assert ler_cues_pendentes_timeout_dos_steps_transcribrothers(row.steps_json) == []
    wav = work / "wavs_narracao_por_cue" / "cue_narracao_0000.wav"
    assert wav.is_file()
    gravar_manifest.assert_called_once()
    cues_gravadas = gravar_manifest.call_args.kwargs.get("cues") or gravar_manifest.call_args[1].get(
        "cues"
    )
    if cues_gravadas is None:
        cues_gravadas = gravar_manifest.call_args.kwargs["cues"]
    assert cues_gravadas[0].sem_narracao is True
    narracao = row.steps_json["narracao_tts_documento"]
    assert narracao["quantidade_cues_puladas"] == 1
