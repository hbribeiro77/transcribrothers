import asyncio
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
    ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)

_JOB_INEXISTENTE = "00000000-0000-4000-8000-000000000099"


def test_chat_agente_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.post(f"/api/jobs/{_JOB_INEXISTENTE}/chat-agente", json={"mensagem": "oi"})
        assert r.status_code == 404


def test_chat_agente_nao_altera_markdown_e_devolve_proposta() -> None:
    jid = novo_id_job()
    markdown = "# Jornada\n\nO usuário abre o sistema."
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_agente_transcribrothers(sf, jid, markdown=markdown))
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_agente_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value=(
                        '{"texto":"Sugiro incluir na Visão Geral.",'
                        '"citacoes":[],"instantes_imagem_segundos":[],'
                        '"ferramentas":['
                        '{"nome":"edicao_parcial","titulo_secao_heading":"Visão Geral",'
                        '"instrucoes":"Inclua o parágrafo do envio no chat."},'
                        '{"nome":"edicao_parcial","titulo_secao_heading":"Dúvidas em aberto",'
                        '"instrucoes":"Adicionar novo item à lista: \'e-mail vs ofício\'."}]}'
                    )
                ),
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-agente",
                    json={"mensagem": "bola um texto e onde encaixar"},
                )
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["texto"] == "Sugiro incluir na Visão Geral."
            assert body["proposta_ferramenta"]["nome"] == "edicao_parcial"
            assert body["proposta_ferramenta"]["titulo_secao_heading"] == "Visão Geral"
            assert len(body["propostas_ferramenta"]) == 2
            assert body["propostas_ferramenta"][1]["titulo_secao_heading"] == "Dúvidas em aberto"
            agente = next(i for i in body["historico"] if i["papel"] == "agente")
            assert agente["proposta_ferramenta"]["nome"] == "edicao_parcial"
            job = client.get(f"/api/jobs/{jid}").json()
            assert job["result_markdown"] == markdown
            assert job["status"] == StatusJobTranscribrothers.completed.value
        finally:
            _limpar_job_chat_agente_transcribrothers(sf, data_dir, jid)


def test_chat_agente_confirmacao_informal_chama_modelo_e_executa_proposta() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_agente_transcribrothers(sf, jid, markdown="# Doc\n\ntexto"))
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            anexar_item_historico_chat_ask_agente_no_work_transcribrothers(
                work,
                ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
                    papel="agente",
                    modo="agente",
                    texto="Sugiro incluir o WhatsApp no Assistido Digital.",
                    criado_em="2026-10-04T14:54:57+00:00",
                    citacoes=[],
                    imagens=[],
                    estado=None,
                    tipo_pipeline=None,
                    proposta_ferramenta={
                        "nome": "edicao_parcial",
                        "titulo_secao_heading": "O que foi discutido",
                        "instrucoes": "No item 'Assistido Digital', acrescentar: 'WhatsApp.'",
                    },
                    propostas_ferramenta=[
                        {
                            "nome": "edicao_parcial",
                            "titulo_secao_heading": "O que foi discutido",
                            "instrucoes": "No item 'Assistido Digital', acrescentar: 'WhatsApp.'",
                        }
                    ],
                ),
            )
            litellm = AsyncMock(
                return_value=(
                    '{"texto":"Aplicando o lote.","citacoes":[],'
                    '"instantes_imagem_segundos":[],"executar":true,'
                    '"ferramentas":[{"nome":"edicao_parcial",'
                    '"titulo_secao_heading":"O que foi discutido",'
                    '"instrucoes":"No item \'Assistido Digital\', acrescentar: \'WhatsApp.\'"}]}'
                )
            )
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_agente_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=litellm,
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-agente",
                    json={"mensagem": "manda brasa"},
                )
            assert r.status_code == 200, r.text
            assert litellm.await_count == 1
            body = r.json()
            assert body["executar_proposta"] is True
            assert body["historico"][-1]["executar_proposta"] is True
            assert body["proposta_ferramenta"]["nome"] == "edicao_parcial"
            assert body["proposta_ferramenta"]["titulo_secao_heading"] == "O que foi discutido"
        finally:
            _limpar_job_chat_agente_transcribrothers(sf, data_dir, jid)


def test_chat_agente_forcar_injeta_proposta_se_modelo_omitir() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_agente_transcribrothers(sf, jid, markdown="# Doc\n\ntexto"))
            with patch(
                "transcribrothers_backend.modulo_orquestrar_turno_chat_agente_job_transcribrothers.obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers",
                new=AsyncMock(
                    return_value='{"texto":"ok","citacoes":[],"instantes_imagem_segundos":[],"ferramentas":[]}'
                ),
            ):
                r = client.post(
                    f"/api/jobs/{jid}/chat-agente",
                    json={
                        "mensagem": "aprofunda",
                        "forcar_ferramenta": "revisao_profunda",
                    },
                )
            assert r.status_code == 200, r.text
            assert r.json()["proposta_ferramenta"]["nome"] == "revisao_profunda"
            assert r.json()["proposta_ferramenta"]["instrucoes"] == "aprofunda"
        finally:
            _limpar_job_chat_agente_transcribrothers(sf, data_dir, jid)


async def _inserir_job_chat_agente_transcribrothers(
    session_factory,
    job_id: str,
    markdown: str | None,
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
                steps_json={},
            )
        )
        await session.commit()


async def _remover_job_se_existir_transcribrothers(session_factory, job_id: str) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is not None:
            await session.delete(row)
            await session.commit()


def _limpar_job_chat_agente_transcribrothers(session_factory, data_dir: Path, job_id: str) -> None:
    asyncio.run(_remover_job_se_existir_transcribrothers(session_factory, job_id))
    work = data_dir / "jobs" / job_id
    if work.is_dir():
        shutil.rmtree(work, ignore_errors=True)
