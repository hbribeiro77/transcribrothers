"""POST /criar e PUT /ordem para pipelines custom — ordem de exibição no catálogo."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def _ids_pipelines_custom(d: dict) -> list[str]:
    return [p["id"] for p in d.get("pipelines", []) if p.get("origem") == "usuario"]


def _pipelines_custom_ordenadas(d: dict) -> list[dict]:
    custom = [p for p in d.get("pipelines", []) if p.get("origem") == "usuario"]
    return sorted(custom, key=lambda p: (p.get("ordem") if p.get("ordem") is not None else 10**9, p["id"]))


def test_criar_pipeline_custom_a_partir_de_molde_tutorial_transcribrothers() -> None:
    with TestClient(app) as client:
        antes = client.get("/api/pipelines/catalogo").json()
        ids_antes = set(_ids_pipelines_custom(antes))
        r = client.post(
            "/api/pipelines/custom/criar",
            json={
                "fonte_id": "pipeline_inicial_tutorial",
                "titulo": "Meu tutorial DIS",
                "descricao": "Pipeline custom de tutorial para testes.",
            },
        )
        assert r.status_code == 200, r.text
        depois = r.json()
        novos = [pid for pid in _ids_pipelines_custom(depois) if pid not in ids_antes]
        assert len(novos) == 1
        criada = next(p for p in depois["pipelines"] if p["id"] == novos[0])
        assert criada["titulo"] == "Meu tutorial DIS"
        assert criada["copiado_de"] == "pipeline_inicial_tutorial"
        assert criada.get("ordem") is not None
        client.delete(f"/api/pipelines/custom/{novos[0]}")


def test_duas_criacoes_mesmo_molde_reutilizam_agentes_biblioteca_transcribrothers() -> None:
    with TestClient(app) as client:
        ids_criados: list[str] = []
        try:
            r1 = client.post(
                "/api/pipelines/custom/criar",
                json={"fonte_id": "pipeline_inicial_tutorial", "titulo": "Lib A"},
            )
            assert r1.status_code == 200, r1.text
            ids_criados.append(_ids_pipelines_custom(r1.json())[-1])
            p1 = next(p for p in r1.json()["pipelines"] if p["id"] == ids_criados[0])
            agentes_p1 = [passo["agente_id"] for passo in p1["passos"]]
            qtd_agentes_apos_primeira = len(
                [a for a in r1.json()["agentes"] if a.get("origem") == "usuario"]
            )

            r2 = client.post(
                "/api/pipelines/custom/criar",
                json={"fonte_id": "pipeline_inicial_tutorial", "titulo": "Lib B"},
            )
            assert r2.status_code == 200, r2.text
            ids_criados.append(_ids_pipelines_custom(r2.json())[-1])
            p2 = next(p for p in r2.json()["pipelines"] if p["id"] == ids_criados[1])
            agentes_p2 = [passo["agente_id"] for passo in p2["passos"]]
            assert agentes_p1 == agentes_p2
            qtd_agentes_apos_segunda = len(
                [a for a in r2.json()["agentes"] if a.get("origem") == "usuario"]
            )
            assert qtd_agentes_apos_segunda == qtd_agentes_apos_primeira
        finally:
            for pid in ids_criados:
                client.delete(f"/api/pipelines/custom/{pid}")


def test_criar_pipeline_custom_molde_fluxo2_retorna_400_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/pipelines/custom/criar",
            json={"fonte_id": "regeneracao_markdown", "titulo": "Não deve criar"},
        )
        assert r.status_code == 400
        assert "molde" in r.json()["detail"].lower() or "executável" in r.json()["detail"].lower()


def test_reordenar_pipelines_custom_inverte_ordem_no_catalogo_transcribrothers() -> None:
    with TestClient(app) as client:
        ids_criados: list[str] = []
        try:
            for titulo in ("A ordem", "B ordem", "C ordem"):
                r = client.post(
                    "/api/pipelines/custom/criar",
                    json={"fonte_id": "pipeline_inicial_notas_proposta", "titulo": titulo},
                )
                assert r.status_code == 200, r.text
                novos = _ids_pipelines_custom(r.json())
                ids_criados.append(novos[-1])

            catalogo_antes_put = client.get("/api/pipelines/catalogo").json()
            todos_custom_ids = _ids_pipelines_custom(catalogo_antes_put)
            nova_ordem = [
                *reversed(ids_criados),
                *[pid for pid in todos_custom_ids if pid not in ids_criados],
            ]
            r_put = client.put(
                "/api/pipelines/custom/ordem",
                json={"pipeline_ids_ordenados": nova_ordem},
            )
            assert r_put.status_code == 200, r_put.text
            ordenadas = _pipelines_custom_ordenadas(r_put.json())
            ids_ordenados_nossos = [p["id"] for p in ordenadas if p["id"] in ids_criados]
            assert ids_ordenados_nossos == list(reversed(ids_criados))
        finally:
            for pid in ids_criados:
                client.delete(f"/api/pipelines/custom/{pid}")


def test_reordenar_pipelines_custom_lista_incompleta_retorna_400_transcribrothers() -> None:
    with TestClient(app) as client:
        r_criar = client.post(
            "/api/pipelines/custom/criar",
            json={"fonte_id": "pipeline_inicial_tutorial", "titulo": "Só uma"},
        )
        assert r_criar.status_code == 200
        pid = _ids_pipelines_custom(r_criar.json())[-1]
        try:
            r = client.put("/api/pipelines/custom/ordem", json={"pipeline_ids_ordenados": []})
            assert r.status_code == 400
        finally:
            client.delete(f"/api/pipelines/custom/{pid}")
