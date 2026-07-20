"""API para editar passos internos de pipelines custom (Fase 2b)."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def _ids_pipelines_custom(d: dict) -> list[str]:
    return [p["id"] for p in d["pipelines"] if p.get("origem") == "usuario"]


def _criar_pipeline_tutorial_custom(client: TestClient) -> str:
    antes = client.get("/api/pipelines/catalogo").json()
    ids_antes = set(_ids_pipelines_custom(antes))
    r = client.post(
        "/api/pipelines/custom/criar",
        json={"fonte_id": "pipeline_inicial_tutorial", "titulo": "Teste passos 2b"},
    )
    assert r.status_code == 200, r.text
    depois = r.json()
    novos = [pid for pid in _ids_pipelines_custom(depois) if pid not in ids_antes]
    assert len(novos) == 1
    return novos[0]


def test_adicionar_passo_referencia_agente_biblioteca_sem_clonar_transcribrothers() -> None:
    with TestClient(app) as client:
        pipeline_id = _criar_pipeline_tutorial_custom(client)
        catalogo = client.get("/api/pipelines/catalogo").json()
        pipeline = next(p for p in catalogo["pipelines"] if p["id"] == pipeline_id)
        qtd_antes = len(pipeline["passos"])
        agentes_por_id = {a["id"]: a for a in catalogo["agentes"]}
        auditor_id = next(
            passo["agente_id"]
            for passo in pipeline["passos"]
            if agentes_por_id.get(passo["agente_id"], {}).get("handler_chave")
            == "auditor_sustentacao_tutorial"
        )
        qtd_agentes_antes = len([a for a in catalogo["agentes"] if a.get("origem") == "usuario"])

        r = client.post(
            f"/api/pipelines/custom/{pipeline_id}/passos",
            json={"agente_fonte_id": "auditor_sustentacao_tutorial"},
        )
        assert r.status_code == 200, r.text
        atualizada = next(p for p in r.json()["pipelines"] if p["id"] == pipeline_id)
        assert len(atualizada["passos"]) == qtd_antes + 1
        assert atualizada["passos"][-1]["agente_id"] == auditor_id
        qtd_agentes_depois = len([a for a in r.json()["agentes"] if a.get("origem") == "usuario"])
        assert qtd_agentes_depois == qtd_agentes_antes

        client.delete(f"/api/pipelines/custom/{pipeline_id}")


def test_remover_passo_nao_apaga_agente_ainda_referenciado_por_outra_pipeline_transcribrothers() -> None:
    with TestClient(app) as client:
        id_a = _criar_pipeline_tutorial_custom(client)
        id_b = _criar_pipeline_tutorial_custom(client)
        catalogo = client.get("/api/pipelines/catalogo").json()
        pipe_a = next(p for p in catalogo["pipelines"] if p["id"] == id_a)
        passo_remover = pipe_a["passos"][-1]
        agente_id = passo_remover["agente_id"]

        r = client.delete(f"/api/pipelines/custom/{id_a}/passos/{passo_remover['id']}")
        assert r.status_code == 200, r.text
        assert agente_id in {a["id"] for a in r.json()["agentes"]}

        client.delete(f"/api/pipelines/custom/{id_a}")
        client.delete(f"/api/pipelines/custom/{id_b}")


def test_reordenar_passos_exige_lista_completa_transcribrothers() -> None:
    with TestClient(app) as client:
        pipeline_id = _criar_pipeline_tutorial_custom(client)
        pipeline = next(p for p in client.get("/api/pipelines/catalogo").json()["pipelines"] if p["id"] == pipeline_id)
        passos = list(pipeline["passos"])
        invertidos = list(reversed(passos))
        ids_invertidos = [p["id"] for p in invertidos]

        r = client.put(
            f"/api/pipelines/custom/{pipeline_id}/passos/ordem",
            json={"passo_ids_ordenados": ids_invertidos},
        )
        assert r.status_code == 200, r.text
        reordenada = next(p for p in r.json()["pipelines"] if p["id"] == pipeline_id)
        assert [p["id"] for p in reordenada["passos"]] == ids_invertidos

        r_erro = client.put(
            f"/api/pipelines/custom/{pipeline_id}/passos/ordem",
            json={"passo_ids_ordenados": ids_invertidos[:-1]},
        )
        assert r_erro.status_code == 400

        client.delete(f"/api/pipelines/custom/{pipeline_id}")


def test_remover_passo_exige_pelo_menos_um_e_limpa_agente_orfao_transcribrothers() -> None:
    with TestClient(app) as client:
        pipeline_id = _criar_pipeline_tutorial_custom(client)
        ids_agentes_antes = {
            a["id"]
            for a in client.get("/api/pipelines/catalogo").json()["agentes"]
            if a.get("origem") == "usuario"
        }
        # Variante explícita: só esta pipeline a referencia → ao remover o passo, vira órfã.
        r_dup = client.post(
            "/api/agentes/custom/duplicar",
            json={"fonte_id": "auditor_sustentacao_notas"},
        )
        assert r_dup.status_code == 200, r_dup.text
        agente_variante_id = next(
            a["id"]
            for a in r_dup.json()["agentes"]
            if a.get("origem") == "usuario" and a["id"] not in ids_agentes_antes
        )

        r_add = client.post(
            f"/api/pipelines/custom/{pipeline_id}/passos",
            json={"agente_fonte_id": agente_variante_id},
        )
        assert r_add.status_code == 200, r_add.text
        atualizada = next(p for p in r_add.json()["pipelines"] if p["id"] == pipeline_id)
        passo_variante = next(p for p in atualizada["passos"] if p["agente_id"] == agente_variante_id)

        r = client.delete(f"/api/pipelines/custom/{pipeline_id}/passos/{passo_variante['id']}")
        assert r.status_code == 200, r.text
        assert agente_variante_id not in {a["id"] for a in r.json()["agentes"]}

        atualizada = next(p for p in r.json()["pipelines"] if p["id"] == pipeline_id)
        while len(atualizada["passos"]) > 1:
            passo_id = atualizada["passos"][-1]["id"]
            r_loop = client.delete(f"/api/pipelines/custom/{pipeline_id}/passos/{passo_id}")
            assert r_loop.status_code == 200, r_loop.text
            atualizada = next(p for p in r_loop.json()["pipelines"] if p["id"] == pipeline_id)

        unico = atualizada["passos"][0]
        r_ultimo = client.delete(f"/api/pipelines/custom/{pipeline_id}/passos/{unico['id']}")
        assert r_ultimo.status_code == 400

        client.delete(f"/api/pipelines/custom/{pipeline_id}")
