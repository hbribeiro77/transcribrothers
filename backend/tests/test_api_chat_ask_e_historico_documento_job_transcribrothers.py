"""GET e POST /api/jobs/{id}/chat-historico e POST /api/jobs/{id}/chat-ask."""

import asyncio
import json
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

from sqlalchemy.orm.attributes import flag_modified
from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)

_JOB_INEXISTENTE = "00000000-0000-4000-8000-000000000099"
_DETALHE_JOB_NAO_ENCONTRADO = "Job não encontrado."
_MENSAGEM_SEM_FONTE = "Não há Markdown nem transcrição neste job para o Ask."


def test_chat_historico_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.get(f"/api/jobs/{_JOB_INEXISTENTE}/chat-historico")
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO


def test_chat_ask_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(f"/api/jobs/{_JOB_INEXISTENTE}/chat-ask", json={"mensagem": "oi"})
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO


def test_chat_ask_stream_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(f"/api/jobs/{_JOB_INEXISTENTE}/chat-ask-stream", json={"mensagem": "oi"})
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO


def test_post_chat_historico_anexa_turno_agente_gerando() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown="# Jornada\n\ntexto"))
            r = client.post(
                f"/api/jobs/{jid}/chat-historico",
                json={
                    "papel": "agente",
                    "modo": "agente",
                    "texto": "tom mais formal",
                    "estado": "gerando",
                    "tipo_pipeline": "tutorial",
                },
            )
            assert r.status_code == 200, r.text
            body = r.json()
            assert len(body["historico"]) == 1
            item = body["historico"][0]
            assert item["papel"] == "agente"
            assert item["modo"] == "agente"
            assert item["texto"] == "tom mais formal"
            assert item["estado"] == "gerando"
            assert item["tipo_pipeline"] == "tutorial"
            assert isinstance(item["criado_em"], str) and item["criado_em"]
            hist = client.get(f"/api/jobs/{jid}/chat-historico")
            assert hist.status_code == 200
            assert len(hist.json()["historico"]) == 1
            assert hist.json()["historico"][0]["estado"] == "gerando"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_post_chat_historico_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(
            f"/api/jobs/{_JOB_INEXISTENTE}/chat-historico",
            json={
                "papel": "agente",
                "modo": "agente",
                "texto": "oi",
                "estado": "gerando",
                "tipo_pipeline": "tutorial",
            },
        )
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO


def test_chat_historico_vazio_200() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown="# Jornada\n\ntexto"))
            r = client.get(f"/api/jobs/{jid}/chat-historico")
            assert r.status_code == 200
            assert r.json()["historico"] == []
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_sem_fonte_409() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=None))
            r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "oi"})
            assert r.status_code == 409
            assert r.json()["detail"] == _MENSAGEM_SEM_FONTE
            hist = client.get(f"/api/jobs/{jid}/chat-historico")
            assert hist.status_code == 200
            assert hist.json()["historico"] == []
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_nao_altera_markdown_e_devolve_texto() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"jornada do usuario","citacoes":[],"instantes_imagem_segundos":[]}'
                ),
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "qual a jornada?"})
            assert r.status_code == 200
            body = r.json()
            assert body["texto"] == "jornada do usuario"
            assert body["citacoes"] == []
            assert body["imagens"] == []
            assert len(body["historico"]) == 2
            assert body["historico"][0]["papel"] == "usuario"
            assert body["historico"][0]["modo"] == "ask"
            assert body["historico"][0]["texto"] == "qual a jornada?"
            assert body["historico"][1]["papel"] == "assistente"
            assert body["historico"][1]["texto"] == "jornada do usuario"
            assert body["historico"][1]["imagens"] == []
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            assert job["status"] == StatusJobTranscribrothers.completed.value
            hist = client.get(f"/api/jobs/{jid}/chat-historico")
            assert hist.status_code == 200
            assert hist.json()["historico"] == body["historico"]
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_imagem_da_galeria_sem_alterar_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            snap = work / "snapshot_transcricao_finalizada_job_transcribrothers.json"
            snap.write_text(
                json.dumps(
                    {"caminhos_frames_rel_job": [[12.0, "assets/tela_jornada.png"]]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"veja a tela","citacoes":[],"instantes_imagem_segundos":[12]}'
                ),
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "mostra a tela"})
            assert r.status_code == 200
            body = r.json()
            assert body["texto"] == "veja a tela"
            assert body["imagens"][0]["origem"] == "galeria"
            assert body["imagens"][0]["caminho_relativo"] == "assets/tela_jornada.png"
            assert body["imagens"][0]["url"] == f"/api/jobs/{jid}/assets/tela_jornada.png"
            assert body["imagens"][0]["instante_segundos"] == 12.0
            assert body["historico"][1]["imagens"][0]["origem"] == "galeria"
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_sem_video_avisa_no_texto_e_nao_altera_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"segue o texto","citacoes":[],"instantes_imagem_segundos":[80]}'
                ),
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "mostra a tela"})
            assert r.status_code == 200
            body = r.json()
            assert body["imagens"] == []
            assert "Não foi possível incluir a tela pedida." in body["texto"]
            assert body["texto"].startswith("segue o texto")
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_captura_persiste_steps_json_sem_alterar_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            (work / "video_entrada_arquivo_local.mp4").write_bytes(b"0")

            async def _cap(**kwargs):
                return (80.0, "frame_manual.png", "assets/frame_manual.png", "![tela](assets/frame_manual.png)")

            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"tela capturada","citacoes":[],"instantes_imagem_segundos":[80]}'
                ),
            ), patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers",
                new=_cap,
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "mostra a tela"})
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["imagens"][0]["origem"] == "captura_sob_demanda"
            assert body["imagens"][0]["caminho_relativo"] == "assets/frame_manual.png"
            assert "![tela]" not in body["texto"]
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            registros = job["steps_json"]["frames_manuais_capturados_video_tutorial"]
            assert registros[0]["origem"] == "chat_ask"
            assert registros[0]["caminho_relativo"] == "assets/frame_manual.png"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_captura_nao_apaga_steps_json_gravado_durante_litellm() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            (work / "video_entrada_arquivo_local.mp4").write_bytes(b"0")

            async def _litellm_grava_preview(**_kwargs):
                async with sf() as session:
                    row = await session.get(JobPipelineTranscribrothers, jid)
                    assert row is not None
                    steps = dict(row.steps_json or {})
                    steps["preview_gravada_durante_litellm"] = {"marcador": "nao-apagar"}
                    row.steps_json = steps
                    flag_modified(row, "steps_json")
                    await session.commit()
                return '{"texto":"tela capturada","citacoes":[],"instantes_imagem_segundos":[80]}'

            async def _cap(**kwargs):
                return (80.0, "frame_manual.png", "assets/frame_manual.png", "![tela](assets/frame_manual.png)")

            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=_litellm_grava_preview,
            ), patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers",
                new=_cap,
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "mostra a tela"})
            assert r.status_code == 200, r.text
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            assert job["steps_json"]["preview_gravada_durante_litellm"] == {"marcador": "nao-apagar"}
            registros = job["steps_json"]["frames_manuais_capturados_video_tutorial"]
            assert registros[0]["origem"] == "chat_ask"
            assert registros[0]["caminho_relativo"] == "assets/frame_manual.png"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_usa_litellm_model_do_corpo_e_nao_o_do_job() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(
                _inserir_job_chat_ask_transcribrothers(
                    sf,
                    jid,
                    markdown=markdown,
                    steps_json={"litellm_model": "azure_ai/claude-haiku-4-5"},
                )
            )
            mock_llm = AsyncMock(
                return_value='{"texto":"ok","citacoes":[],"instantes_imagem_segundos":[]}'
            )
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=mock_llm,
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-ask",
                    json={
                        "mensagem": "qual a jornada?",
                        "litellm_model": "gemini/gemini-3-flash-preview",
                    },
                )
            assert r.status_code == 200, r.text
            mock_llm.assert_awaited()
            assert mock_llm.await_args.kwargs["modelo"] == "gemini/gemini-3-flash-preview"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_falha_litellm_502_sem_alterar_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\ntexto"
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(side_effect=RuntimeError("proxy indisponível")),
            ):
                r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "qual a jornada?"})
            assert r.status_code == 502
            assert "proxy indisponível" in r.json()["detail"]
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            assert job["status"] == StatusJobTranscribrothers.completed.value
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_resolver_frame_galeria_nao_altera_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            snap = work / "snapshot_transcricao_finalizada_job_transcribrothers.json"
            snap.write_text(
                json.dumps(
                    {"caminhos_frames_rel_job": [[12.0, "assets/tela_jornada.png"]]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            r = client.post(f"/api/jobs/{jid}/chat-ask-resolver-frame", json={"instante_segundos": 12.0})
            assert r.status_code == 200
            assert r.json()["origem"] == "galeria"
            assert r.json()["caminho_relativo"] == "assets/tela_jornada.png"
            assert "snippet_markdown" not in r.json()
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_resolver_frame_captura_nao_altera_markdown() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            (work / "video_entrada_arquivo_local.mp4").write_bytes(b"0")

            async def _cap(**kwargs):
                return (80.0, "frame_manual.png", "assets/frame_manual.png", "![tela](assets/frame_manual.png)")

            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers",
                new=_cap,
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-ask-resolver-frame",
                    json={"instante_segundos": 80.0},
                )
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["origem"] == "captura_sob_demanda"
            assert body["caminho_relativo"] == "assets/frame_manual.png"
            assert "snippet_markdown" not in body
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            registros = job["steps_json"]["frames_manuais_capturados_video_tutorial"]
            assert registros[0]["origem"] == "chat_ask"
            assert registros[0]["caminho_relativo"] == "assets/frame_manual.png"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_chat_ask_instante_anexo_grava_imagem_no_turno_usuario() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown=markdown))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            snap = work / "snapshot_transcricao_finalizada_job_transcribrothers.json"
            snap.write_text(
                json.dumps(
                    {"caminhos_frames_rel_job": [[12.0, "assets/tela_jornada.png"]]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"resposta","citacoes":[],"instantes_imagem_segundos":[]}'
                ),
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-ask",
                    json={"mensagem": "o que tem nessa tela?", "instante_anexo_segundos": 12.0},
                )
            assert r.status_code == 200
            usuario = next(i for i in r.json()["historico"] if i["papel"] == "usuario")
            assert usuario["imagens"][0]["instante_segundos"] == 12.0
            assert usuario["imagens"][0]["origem"] == "galeria"
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_delete_chat_historico_esvazia_arquivo() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown="# Doc"))
            client.post(
                f"/api/jobs/{jid}/chat-historico",
                json={"papel": "usuario", "modo": "ask", "texto": "oi"},
            )
            r = client.delete(f"/api/jobs/{jid}/chat-historico")
            assert r.status_code == 200, r.text
            assert r.json()["historico"] == []
            hist = client.get(f"/api/jobs/{jid}/chat-historico")
            assert hist.json()["historico"] == []
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_delete_chat_historico_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.delete(f"/api/jobs/{_JOB_INEXISTENTE}/chat-historico")
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO


async def _inserir_job_chat_ask_transcribrothers(
    session_factory,
    job_id: str,
    markdown: str | None,
    steps_json: dict | None = None,
) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.upload_local,
                drive_url="Arquivo local: test.mp4",
                file_id="-",
                error_message=None,
                result_markdown=markdown,
                steps_json=steps_json or {},
            )
        )
        await session.commit()


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()


def _limpar_job_chat_ask_transcribrothers(session_factory, data_dir: Path, job_id: str) -> None:
    asyncio.run(_remover_job_se_existir_transcribrothers(session_factory, job_id))
    work = data_dir / "jobs" / job_id
    if work.is_dir():
        shutil.rmtree(work, ignore_errors=True)
