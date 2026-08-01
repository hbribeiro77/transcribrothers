"""Janelas de vídeo, WAV por cue e validação anti-sobreposição."""

from __future__ import annotations

import asyncio
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    ErroValidacaoJanelasVideoCuesTranscribrothers,
    JanelaVideoCueEntradaTranscribrothers,
    validar_janelas_video_cues_sem_sobreposicao_transcribrothers,
)


def test_validar_janelas_rejeita_sobreposicao() -> None:
    try:
        validar_janelas_video_cues_sem_sobreposicao_transcribrothers(
            [
                JanelaVideoCueEntradaTranscribrothers(0.0, 2.0),
                JanelaVideoCueEntradaTranscribrothers(1.5, 3.0),
            ]
        )
        raise AssertionError("deveria falhar")
    except ErroValidacaoJanelasVideoCuesTranscribrothers as e:
        assert "sobrepõ" in str(e).lower() or "sobrepo" in str(e).lower()


def test_validar_janelas_aceita_sequencia_com_folga() -> None:
    validar_janelas_video_cues_sem_sobreposicao_transcribrothers(
        [
            JanelaVideoCueEntradaTranscribrothers(0.0, 1.0),
            JanelaVideoCueEntradaTranscribrothers(1.1, 2.0),
        ]
    )


def _job_com_manifest_e_wav(client: TestClient) -> str:
    criado = client.post("/api/jobs/projeto-em-branco")
    assert criado.status_code == 200
    job_id = criado.json()["id"]
    data_dir = Path(app.state.data_dir)
    work = data_dir / "jobs" / job_id
    work.mkdir(parents=True, exist_ok=True)
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
        work=work,
        cues=[
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="um",
                inicio_video_segundos=0.0,
                fim_video_segundos=1.0,
                origem_ancora="markdown_t",
                casado=True,
            ),
            CueNarracaoComJanelaVideoTranscribrothers(
                texto="dois",
                inicio_video_segundos=1.1,
                fim_video_segundos=2.5,
                origem_ancora="markdown_t",
                casado=True,
            ),
        ],
    )
    dir_wavs = work / "wavs_narracao_por_cue"
    dir_wavs.mkdir(parents=True, exist_ok=True)
    # WAV mínimo válido (header + 1 frame) — tamanho > 44
    (dir_wavs / "cue_narracao_0000.wav").write_bytes(b"RIFF" + b"\x00" * 50)
    (dir_wavs / "cue_narracao_0001.wav").write_bytes(b"RIFF" + b"\x00" * 50)

    async def _completed() -> None:
        async with app.state.session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            assert row is not None
            row.status = "completed"
            await session.commit()

    asyncio.run(_completed())
    return job_id


def test_get_janelas_e_wav_por_cue() -> None:
    with TestClient(app) as client:
        job_id = _job_com_manifest_e_wav(client)
        r = client.get(f"/api/jobs/{job_id}/janelas-video-cues-narracao")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["quantidade_cues"] == 2
        assert body["cues"][0]["tem_wav"] is True
        assert body["cues"][0]["url_wav"].endswith("/wavs-narracao-por-cue/0")

        wav = client.get(f"/api/jobs/{job_id}/wavs-narracao-por-cue/0")
        assert wav.status_code == 200
        assert wav.headers["content-type"].startswith("audio/")


def test_put_janelas_rejeita_sobreposicao() -> None:
    with TestClient(app) as client:
        job_id = _job_com_manifest_e_wav(client)
        r = client.put(
            f"/api/jobs/{job_id}/janelas-video-cues-narracao",
            json={
                "janelas": [
                    {"inicio_video_segundos": 0.0, "fim_video_segundos": 2.0},
                    {"inicio_video_segundos": 1.5, "fim_video_segundos": 3.0},
                ],
            },
        )
        assert r.status_code == 400


def test_put_janelas_ok() -> None:
    with TestClient(app) as client:
        job_id = _job_com_manifest_e_wav(client)
        r = client.put(
            f"/api/jobs/{job_id}/janelas-video-cues-narracao",
            json={
                "janelas": [
                    {"inicio_video_segundos": 0.0, "fim_video_segundos": 1.2},
                    {"inicio_video_segundos": 1.3, "fim_video_segundos": 2.8},
                ],
            },
        )
        assert r.status_code == 200, r.text
        assert r.json()["cues"][0]["fim_video_segundos"] == 1.2
