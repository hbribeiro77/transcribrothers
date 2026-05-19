"""Testes da API de histórico de versões do tutorial Markdown (lista, conteúdo, restaurar)."""

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from starlette.testclient import TestClient

from transcribrothers_backend.main import app
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    HistoricoVersaoTutorialMarkdownJobTranscribrothers,
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    novo_id_job,
)


async def _inserir_job_concluido_com_markdown_para_teste_historico_tutorial_transcribrothers(
    session_factory,
    job_id: str,
    markdown: str,
) -> None:
    async with session_factory() as session:
        session.add(
            JobPipelineTranscribrothers(
                id=job_id,
                status=StatusJobTranscribrothers.completed.value,
                source_kind=OrigemEntradaJobTranscribrothers.drive,
                drive_url="https://example.invalid/historico-tutorial-markdown",
                file_id="hist1",
                error_message=None,
                result_markdown=markdown,
                steps_json={},
            )
        )
        await session.commit()


async def _inserir_linha_historico_tutorial_markdown_para_teste_transcribrothers(
    session_factory,
    *,
    job_id: str,
    conteudo_markdown: str,
    origem: str = "edicao_manual",
) -> int:
    async with session_factory() as session:
        row = HistoricoVersaoTutorialMarkdownJobTranscribrothers(
            job_id=job_id,
            criado_em=datetime.now(timezone.utc),
            origem=origem,
            conteudo_markdown=conteudo_markdown,
        )
        session.add(row)
        await session.flush()
        rid = int(row.id)
        await session.commit()
        return rid


def test_get_historico_versoes_tutorial_lista_job_inexistente_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.get(
            "/api/jobs/00000000-0000-4000-8000-000000000033/tutorial-markdown/historico-versoes",
        )
        assert r.status_code == 404


def test_get_conteudo_historico_tutorial_versao_inexistente_retorna_404() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = client.app.state.session_factory
        try:
            asyncio.run(
                _inserir_job_concluido_com_markdown_para_teste_historico_tutorial_transcribrothers(
                    sf,
                    jid,
                    "# x",
                )
            )
            r = client.get(f"/api/jobs/{jid}/tutorial-markdown/historico-versoes/999999")
            assert r.status_code == 404
        finally:
            client.delete(f"/api/jobs/{jid}")


def test_post_restaurar_historico_tutorial_repoe_markdown_e_ficheiro_transcribrothers() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = client.app.state.session_factory
        data_dir: Path = client.app.state.data_dir
        try:
            asyncio.run(
                _inserir_job_concluido_com_markdown_para_teste_historico_tutorial_transcribrothers(
                    sf,
                    jid,
                    "# atual",
                )
            )
            hid = asyncio.run(
                _inserir_linha_historico_tutorial_markdown_para_teste_transcribrothers(
                    sf,
                    job_id=jid,
                    conteudo_markdown="# backup\n\nparagrafo",
                    origem="edicao_manual",
                )
            )
            work = data_dir / "jobs" / jid
            work.mkdir(parents=True, exist_ok=True)
            (work / "tutorial_gerado_transcribrothers.md").write_text("# atual\n", encoding="utf-8", newline="\n")

            r_list = client.get(f"/api/jobs/{jid}/tutorial-markdown/historico-versoes")
            assert r_list.status_code == 200
            body = r_list.json()
            assert isinstance(body, list) and len(body) >= 1

            r_get = client.get(f"/api/jobs/{jid}/tutorial-markdown/historico-versoes/{hid}")
            assert r_get.status_code == 200
            assert r_get.json()["markdown"].strip().startswith("# backup")

            r_post = client.post(f"/api/jobs/{jid}/tutorial-markdown/historico-versoes/{hid}/restaurar")
            assert r_post.status_code == 200
            assert "# backup" in (r_post.json().get("result_markdown") or "")

            texto_ficheiro = (work / "tutorial_gerado_transcribrothers.md").read_text(encoding="utf-8")
            assert "# backup" in texto_ficheiro
        finally:
            client.delete(f"/api/jobs/{jid}")
