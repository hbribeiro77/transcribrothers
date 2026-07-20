"""POST /api/jobs/{id}/gerar-outro-formato — reprocessamento pós-transcrição com novo destino."""

import asyncio
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)
from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
    ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers import (
    carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers,
)


async def _inserir_job_concluido_tutorial_com_snapshot_transcribrothers(
    session_factory,
    *,
    job_id: str,
    markdown: str,
    destino: str = "gerar_tutorial",
) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="",
                file_id="",
                error_message=None,
                result_markdown=markdown,
                steps_json={
                    "destino_apos_transcricao": destino,
                    "transcricao_snapshot_finalizada_em_disco": True,
                    "upload_ok": True,
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()


def _preparar_work_job_com_video_e_snapshot_transcribrothers(data_dir: Path, job_id: str) -> Path:
    work = data_dir / "jobs" / job_id
    work.mkdir(parents=True, exist_ok=True)
    (work / "video_entrada_arquivo_local.webm").write_bytes(b"\x1a\x45\xdf\xa3" + b"\x00" * 64)
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(
        work,
        ResultadoTranscricaoComSegmentos(
            texto_completo="texto transcrito para outro formato",
            segmentos=[
                SegmentoTranscricaoComTempo(inicio_segundos=0.0, fim_segundos=1.5, texto="olá"),
            ],
            idioma_detectado="pt",
        ),
    )
    return work


def _patches_credenciais_litellm_gerar_outro_formato_transcribrothers(stack: ExitStack) -> None:
    stack.enter_context(
        patch(
            "transcribrothers_backend.main.tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy",
            return_value=True,
        )
    )
    stack.enter_context(
        patch(
            "transcribrothers_backend.main.tem_credencial_para_transcricao_no_pipeline",
            return_value=True,
        )
    )


def test_gerar_outro_formato_job_inexistente_retorna_404() -> None:
    with ExitStack() as stack:
        _patches_credenciais_litellm_gerar_outro_formato_transcribrothers(stack)
        with TestClient(app) as client:
            r = client.post(
                "/api/jobs/job-inexistente-gerar-outro-formato/gerar-outro-formato",
                json={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
            )
            assert r.status_code == 404


def test_gerar_outro_formato_sem_snapshot_retorna_400() -> None:
    jid = novo_id_job()
    with ExitStack() as stack:
        _patches_credenciais_litellm_gerar_outro_formato_transcribrothers(stack)
        stack.enter_context(patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona"))
        with TestClient(app) as client:
            sf = client.app.state.session_factory
            data_dir: Path = client.app.state.data_dir
            try:
                asyncio.run(
                    _inserir_job_concluido_tutorial_com_snapshot_transcribrothers(
                        sf,
                        job_id=jid,
                        markdown="# Tutorial\n",
                    )
                )
                work = data_dir / "jobs" / jid
                work.mkdir(parents=True, exist_ok=True)
                (work / "video_entrada_arquivo_local.webm").write_bytes(b"\x00" * 32)

                r = client.post(
                    f"/api/jobs/{jid}/gerar-outro-formato",
                    json={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
                )
                assert r.status_code == 400
                assert "transcrição" in r.json()["detail"].lower()
            finally:
                client.delete(f"/api/jobs/{jid}")


def test_gerar_outro_formato_projeto_em_branco_retorna_400() -> None:
    jid = novo_id_job()
    with ExitStack() as stack:
        _patches_credenciais_litellm_gerar_outro_formato_transcribrothers(stack)
        with TestClient(app) as client:
            sf = client.app.state.session_factory
            data_dir: Path = client.app.state.data_dir
            try:
                asyncio.run(
                    _inserir_job_concluido_tutorial_com_snapshot_transcribrothers(
                        sf,
                        job_id=jid,
                        markdown="# Em branco\n",
                        destino="projeto_em_branco",
                    )
                )
                _preparar_work_job_com_video_e_snapshot_transcribrothers(data_dir, jid)

                r = client.post(
                    f"/api/jobs/{jid}/gerar-outro-formato",
                    json={"destino_apos_transcricao": "gerar_tutorial"},
                )
                assert r.status_code == 400
                assert "branco" in r.json()["detail"].lower()
            finally:
                client.delete(f"/api/jobs/{jid}")


def test_gerar_outro_formato_tutorial_para_notas_backup_historico_e_agenda_pipeline() -> None:
    jid = novo_id_job()
    with ExitStack() as stack:
        _patches_credenciais_litellm_gerar_outro_formato_transcribrothers(stack)
        mock_agendar = stack.enter_context(
            patch("transcribrothers_backend.main.agendar_pipeline_job_em_task_assincrona")
        )
        with TestClient(app) as client:
            sf = client.app.state.session_factory
            data_dir: Path = client.app.state.data_dir
            try:
                asyncio.run(
                    _inserir_job_concluido_tutorial_com_snapshot_transcribrothers(
                        sf,
                        job_id=jid,
                        markdown="# Tutorial original\n\nconteúdo",
                    )
                )
                _preparar_work_job_com_video_e_snapshot_transcribrothers(data_dir, jid)

                r = client.post(
                    f"/api/jobs/{jid}/gerar-outro-formato",
                    json={"destino_apos_transcricao": "notas_proposta_funcionalidade"},
                )
                assert r.status_code == 200, r.text
                body = r.json()
                assert body["status"] == "pending"
                assert body["result_markdown"] is None
                assert body["steps_json"]["destino_apos_transcricao"] == "notas_proposta_funcionalidade"
                assert body["steps_json"]["reprocessamento_pos_transcricao_apenas"] is True
                assert body["steps_json"]["reprocessamento_destino_anterior"] == "gerar_tutorial"
                mock_agendar.assert_called_once()

                r_hist = client.get(f"/api/jobs/{jid}/tutorial-markdown/historico-versoes")
                assert r_hist.status_code == 200
                historico = r_hist.json()
                assert any(
                    h.get("origem") == ORIGEM_HISTORICO_BACKUP_ANTES_OUTRO_FORMATO_TUTORIAL_TRANSCRIBROTHERS
                    for h in historico
                )
            finally:
                client.delete(f"/api/jobs/{jid}")


def test_get_job_inclui_pode_gerar_outro_formato_quando_elegivel() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = client.app.state.session_factory
        data_dir: Path = client.app.state.data_dir
        try:
            asyncio.run(
                _inserir_job_concluido_tutorial_com_snapshot_transcribrothers(
                    sf,
                    job_id=jid,
                    markdown="# x",
                )
            )
            _preparar_work_job_com_video_e_snapshot_transcribrothers(data_dir, jid)

            r = client.get(f"/api/jobs/{jid}")
            assert r.status_code == 200
            assert r.json()["steps_json"].get("pode_gerar_outro_formato") is True
        finally:
            client.delete(f"/api/jobs/{jid}")


def test_helper_carregar_snapshot_para_reprocessamento_preenche_steps(tmp_path: Path) -> None:
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(
        tmp_path,
        ResultadoTranscricaoComSegmentos(
            texto_completo="abc",
            segmentos=[],
            idioma_detectado=None,
        ),
    )
    steps: dict = {"reprocessamento_pos_transcricao_apenas": True}
    resultado = carregar_transcricao_snapshot_para_reprocessamento_pos_transcricao_transcribrothers(
        tmp_path,
        steps,
    )
    assert resultado.texto_completo == "abc"
    assert steps["transcricao_snapshot_finalizada_em_disco"] is True
    assert steps["pipeline_fase"] == "transcricao_reutilizada_gerar_outro_formato"
