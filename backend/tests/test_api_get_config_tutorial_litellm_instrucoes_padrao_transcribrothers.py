"""GET /api/config/transcribrothers/tutorial-litellm-instrucoes-padrao."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_get_tutorial_litellm_instrucoes_padrao_retorna_textos_esperados() -> None:
    with TestClient(app) as client:
        r = client.get("/api/config/transcribrothers/tutorial-litellm-instrucoes-padrao")
        assert r.status_code == 200
        d = r.json()
        assert "instrucao_sem_imagens" in d and "instrucao_com_imagens" in d
        assert "instrucao_sem_imagens_documento_autonomo_sem_video" in d
        assert "instrucao_com_imagens_documento_autonomo_sem_video" in d
        for chave in (
            "instrucao_sem_imagens",
            "instrucao_com_imagens",
            "instrucao_sem_imagens_documento_autonomo_sem_video",
            "instrucao_com_imagens_documento_autonomo_sem_video",
        ):
            assert "JSON de entrada" in d[chave]
        assert "Proibido usar links temporais para vídeo" in d["instrucao_sem_imagens_documento_autonomo_sem_video"]
