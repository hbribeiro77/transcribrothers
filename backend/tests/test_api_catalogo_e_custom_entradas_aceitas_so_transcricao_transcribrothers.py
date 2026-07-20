"""Catálogo expõe entradas_aceitas; custom herda e edita via PATCH."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_catalogo_sistema_tutorial_so_video_e_so_transcricao_aceita_audio_transcribrothers() -> None:
    with TestClient(app) as client:
        d = client.get("/api/pipelines/catalogo").json()
        tutorial = next(p for p in d["pipelines"] if p["id"] == "pipeline_inicial_tutorial")
        so_tr = next(p for p in d["pipelines"] if p["id"] == "pipeline_inicial_so_transcricao")
        assert tutorial["entradas_aceitas"] == ["video"]
        assert set(so_tr["entradas_aceitas"]) == {"video", "audio"}
        assert so_tr["executavel"] is True


def test_duplicar_so_transcricao_herda_entradas_e_patch_edita_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": "pipeline_inicial_so_transcricao"},
        )
        assert r.status_code == 200, r.text
        custom = [
            p
            for p in r.json()["pipelines"]
            if p.get("origem") == "usuario" and p["copiado_de"] == "pipeline_inicial_so_transcricao"
        ]
        assert custom
        pipeline = custom[-1]
        assert set(pipeline["entradas_aceitas"]) == {"video", "audio"}
        pipeline_id = pipeline["id"]

        r_patch = client.patch(
            f"/api/pipelines/custom/{pipeline_id}",
            json={"entradas_aceitas": ["audio"]},
        )
        assert r_patch.status_code == 200, r_patch.text
        atualizada = next(p for p in r_patch.json()["pipelines"] if p["id"] == pipeline_id)
        assert atualizada["entradas_aceitas"] == ["audio"]

        r_bad = client.patch(
            f"/api/pipelines/custom/{pipeline_id}",
            json={"entradas_aceitas": []},
        )
        assert r_bad.status_code == 400

        client.delete(f"/api/pipelines/custom/{pipeline_id}")


def test_duplicar_tutorial_herda_somente_video_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/pipelines/custom/duplicar",
            json={"fonte_id": "pipeline_inicial_tutorial"},
        )
        assert r.status_code == 200, r.text
        custom = [
            p
            for p in r.json()["pipelines"]
            if p.get("origem") == "usuario" and p["copiado_de"] == "pipeline_inicial_tutorial"
        ]
        pipeline = custom[-1]
        assert pipeline["entradas_aceitas"] == ["video"]
        client.delete(f"/api/pipelines/custom/{pipeline['id']}")
