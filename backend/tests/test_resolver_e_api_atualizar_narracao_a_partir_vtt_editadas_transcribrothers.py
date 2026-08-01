"""Resolver de cues sujas + POST atualizar-narracao-a-partir-legendas-vtt-editadas."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

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
from transcribrothers_backend.modulo_pipeline_atualizar_narracao_a_partir_legendas_vtt_editadas_job_transcribrothers import (
    resolver_cues_janela_e_indices_sujos_para_atualizacao_vtt_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
)


def test_resolver_detecta_apenas_cues_sujas_com_manifest(tmp_path: Path) -> None:
    work = tmp_path
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    cues = [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto="primeira",
            inicio_video_segundos=0.0,
            fim_video_segundos=1.0,
            origem_ancora="markdown_t",
            casado=True,
        ),
        CueNarracaoComJanelaVideoTranscribrothers(
            texto="segunda",
            inicio_video_segundos=1.0,
            fim_video_segundos=2.0,
            origem_ancora="markdown_t",
            casado=True,
        ),
        CueNarracaoComJanelaVideoTranscribrothers(
            texto="terceira",
            inicio_video_segundos=2.0,
            fim_video_segundos=3.0,
            origem_ancora="markdown_t",
            casado=True,
        ),
    ]
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(work=work, cues=cues)
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
        diretorio_assets=assets,
        cues=[
            CueLegendaAlinhadaTranscribrothers(
                texto="primeira",
                inicio_segundos=0.0,
                fim_segundos=1.0,
                casado=True,
            ),
            CueLegendaAlinhadaTranscribrothers(
                texto="segunda ALTERADA",
                inicio_segundos=1.0,
                fim_segundos=2.0,
                casado=True,
            ),
            CueLegendaAlinhadaTranscribrothers(
                texto="terceira",
                inicio_segundos=2.0,
                fim_segundos=3.0,
                casado=True,
            ),
        ],
    )
    cues_finais, indices, origem = resolver_cues_janela_e_indices_sujos_para_atualizacao_vtt_transcribrothers(
        work=work,
        assets=assets,
        markdown="# x\n\n[a](?t=0)\n\nprimeira\n\n[b](?t=1)\n\nsegunda\n\n[c](?t=2)\n\nterceira\n",
        duracao_video=10.0,
    )
    assert origem == "manifest"
    assert indices == [1]
    assert cues_finais[1].texto == "segunda ALTERADA"
    assert cues_finais[1].inicio_video_segundos == 1.0


def test_post_atualizar_narracao_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/jobs/00000000-0000-0000-0000-000000000000/atualizar-narracao-a-partir-legendas-vtt-editadas",
            json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
        )
    assert r.status_code == 404


def test_post_atualizar_narracao_sem_vtt_400() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        assert criado.status_code == 200
        job_id = criado.json()["id"]

        async def _completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_completed())
        r = client.post(
            f"/api/jobs/{job_id}/atualizar-narracao-a-partir-legendas-vtt-editadas",
            json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
        )
    assert r.status_code == 400
    assert "vtt" in r.json()["detail"].lower() or "legendas" in r.json()["detail"].lower()


def test_post_atualizar_narracao_agenda_task_quando_pronto() -> None:
    with TestClient(app) as client:
        criado = client.post("/api/jobs/projeto-em-branco")
        job_id = criado.json()["id"]
        data_dir = Path(app.state.data_dir)
        work = data_dir / "jobs" / job_id
        assets = work / "assets_exportados_para_markdown"
        assets.mkdir(parents=True, exist_ok=True)
        (work / "wavs_narracao_por_cue").mkdir(parents=True, exist_ok=True)
        (work / "video_entrada_arquivo_local.mp4").write_bytes(b"fake")
        (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\noi\n",
            encoding="utf-8",
        )

        async def _completed() -> None:
            async with app.state.session_factory() as session:
                row = await session.get(JobPipelineTranscribrothers, job_id)
                assert row is not None
                row.status = "completed"
                await session.commit()

        asyncio.run(_completed())

        with patch(
            "transcribrothers_backend.main.agendar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_task_assincrona"
        ) as mock_agendar:
            with patch(
                "transcribrothers_backend.main.resolver_modelo_tts_para_narracao_documento_transcribrothers",
                return_value="gemini/gemini-2.5-flash-preview-tts",
            ):
                r = client.post(
                    f"/api/jobs/{job_id}/atualizar-narracao-a-partir-legendas-vtt-editadas",
                    json={"litellm_model": "gemini/gemini-2.5-flash-preview-tts"},
                )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "generating_tutorial"
        mock_agendar.assert_called_once()
