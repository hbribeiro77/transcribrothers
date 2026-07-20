"""GET /api/pipelines/catalogo — catálogo de pipelines para a UI de documentação."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_get_catalogo_pipelines_disponiveis_retorna_sete_pipelines_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.get("/api/pipelines/catalogo")
        assert r.status_code == 200
        d = r.json()
        assert "pipeline_identificador" in d
        assert isinstance(d["pipelines"], list)
        pipelines_sistema = [p for p in d["pipelines"] if p.get("origem") == "sistema"]
        assert len(pipelines_sistema) == 7
        assert isinstance(d["agentes"], list)
        agentes_sistema = [a for a in d["agentes"] if a.get("origem") == "sistema"]
        assert len(agentes_sistema) >= 20
        ids = {p["id"] for p in pipelines_sistema}
        assert "pipeline_inicial_tutorial" in ids
        assert "pipeline_inicial_so_transcricao" in ids
        assert "regeneracao_markdown" in ids
        assert "edicao_parcial_secao" in ids
        tutorial = next(p for p in pipelines_sistema if p["id"] == "pipeline_inicial_tutorial")
        assert tutorial["editavel"] is False
        assert tutorial["executavel"] is True
        so_tr = next(p for p in pipelines_sistema if p["id"] == "pipeline_inicial_so_transcricao")
        assert set(so_tr.get("entradas_aceitas") or []) == {"video", "audio"}


def test_get_catalogo_pipeline_tutorial_gerador_tem_agente_com_prompt_nao_vazio_transcribrothers() -> None:
    with TestClient(app) as client:
        d = client.get("/api/pipelines/catalogo").json()
        tutorial = next(p for p in d["pipelines"] if p["id"] == "pipeline_inicial_tutorial")
        gerador_passo = next(s for s in tutorial["passos"] if s["id"] == "gerador")
        assert gerador_passo["rotulo"] == "Gerador (tutorial)"
        assert gerador_passo["agente_id"] == "gerador_tutorial_markdown"
        agente = next(a for a in d["agentes"] if a["id"] == "gerador_tutorial_markdown")
        assert len(agente["prompts"]) >= 1
        com_texto = [p for p in agente["prompts"] if (p.get("texto") or "").strip()]
        assert len(com_texto) >= 1
        assert com_texto[0].get("chave")
        assert "editor técnico" in com_texto[0]["texto"].lower()
        assert "pipeline_inicial_tutorial" in agente["pipelines_ids"]
