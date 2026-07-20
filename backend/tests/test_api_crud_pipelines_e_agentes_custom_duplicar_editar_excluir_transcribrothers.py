"""CRUD de pipelines e agentes custom via API REST."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def _ids_pipelines_custom(d: dict) -> list[str]:
    return [p["id"] for p in d["pipelines"] if p.get("origem") == "usuario"]


def test_duplicar_pipeline_inicial_tutorial_cria_custom_editavel_transcribrothers() -> None:
    with TestClient(app) as client:
        antes = client.get("/api/pipelines/catalogo").json()
        ids_antes = set(_ids_pipelines_custom(antes))

        r = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": "pipeline_inicial_tutorial"},
        )
        assert r.status_code == 200, r.text
        depois = r.json()
        novos = [pid for pid in _ids_pipelines_custom(depois) if pid not in ids_antes]
        assert len(novos) == 1
        pipeline_id = novos[0]
        pipeline = next(p for p in depois["pipelines"] if p["id"] == pipeline_id)
        assert pipeline["copiado_de"] == "pipeline_inicial_tutorial"
        assert pipeline["editavel"] is True
        assert pipeline["executavel"] is True
        assert pipeline["origem"] == "usuario"

        agentes_custom = [a for a in depois["agentes"] if a.get("origem") == "usuario"]
        assert len(agentes_custom) >= 5

        r_patch_sistema = client.patch(
            "/api/pipelines/custom/pipeline_inicial_tutorial",
            json={"titulo": "Hack"},
        )
        assert r_patch_sistema.status_code == 404

        gerador = next(
            a for a in agentes_custom if a.get("handler_chave") == "gerador_tutorial_markdown"
        )
        prompts = list(gerador["prompts"])
        assert prompts
        prompts[0] = {**prompts[0], "texto": "Prompt custom de teste para gerador."}
        r_agente = client.patch(
            f"/api/agentes/custom/{gerador['id']}",
            json={"prompts": prompts},
        )
        assert r_agente.status_code == 200, r_agente.text
        gerador_atualizado = next(
            a for a in r_agente.json()["agentes"] if a["id"] == gerador["id"]
        )
        assert "Prompt custom de teste" in gerador_atualizado["prompts"][0]["texto"]

        r_del = client.delete(f"/api/pipelines/custom/{pipeline_id}")
        assert r_del.status_code == 200
        assert pipeline_id not in _ids_pipelines_custom(r_del.json())


def test_duplicar_pipeline_custom_reutiliza_agentes_sem_clonar_transcribrothers() -> None:
    with TestClient(app) as client:
        ids_antes = set(_ids_pipelines_custom(client.get("/api/pipelines/catalogo").json()))
        r1 = client.post(
            "/api/pipelines/custom/criar",
            json={"fonte_id": "pipeline_inicial_tutorial", "titulo": "Origem share"},
        )
        assert r1.status_code == 200, r1.text
        origem_id = next(pid for pid in _ids_pipelines_custom(r1.json()) if pid not in ids_antes)
        qtd_agentes_antes = len([a for a in r1.json()["agentes"] if a.get("origem") == "usuario"])
        origem = next(p for p in r1.json()["pipelines"] if p["id"] == origem_id)
        agentes_origem = [passo["agente_id"] for passo in origem["passos"]]

        ids_apos_origem = set(_ids_pipelines_custom(r1.json()))
        r2 = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": origem_id},
        )
        assert r2.status_code == 200, r2.text
        copia_id = next(pid for pid in _ids_pipelines_custom(r2.json()) if pid not in ids_apos_origem)
        copia = next(p for p in r2.json()["pipelines"] if p["id"] == copia_id)
        assert [passo["agente_id"] for passo in copia["passos"]] == agentes_origem
        qtd_agentes_depois = len([a for a in r2.json()["agentes"] if a.get("origem") == "usuario"])
        assert qtd_agentes_depois == qtd_agentes_antes

        client.delete(f"/api/pipelines/custom/{copia_id}")
        client.delete(f"/api/pipelines/custom/{origem_id}")


def test_duplicar_pipeline_fluxo2_custom_nao_executavel_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": "regeneracao_markdown"},
        )
        assert r.status_code == 200, r.text
        d = r.json()
        custom = [p for p in d["pipelines"] if p.get("origem") == "usuario" and p["copiado_de"] == "regeneracao_markdown"]
        assert len(custom) >= 1
        assert custom[-1]["executavel"] is False
        client.delete(f"/api/pipelines/custom/{custom[-1]['id']}")
