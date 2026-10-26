"""POST /api/integracao/vinhetas/previsualizar."""

from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_previsualizar_vinheta_rejeita_sem_escolha() -> None:
    with TestClient(app) as client:
        resposta = client.post(
            "/api/integracao/vinhetas/previsualizar",
            json={"titulo": "Nova seção"},
        )
    assert resposta.status_code == 422, resposta.text


def test_previsualizar_vinheta_devolve_mp4() -> None:
    with TestClient(app) as client:
        with patch(
            "transcribrothers_backend.main.baixar_mp4_renderizado_da_vinheta",
            new=AsyncMock(return_value=b"mp4-fake"),
        ) as mock_baixar:
            resposta = client.post(
                "/api/integracao/vinhetas/previsualizar",
                json={"titulo": "Nova seção", "efeito": "planos-que-abrem-espaco"},
            )
    assert resposta.status_code == 200, resposta.text
    assert resposta.headers["content-type"].startswith("video/mp4")
    assert resposta.content == b"mp4-fake"
    mock_baixar.assert_awaited_once()


def test_get_previsualizar_vinheta_devolve_mp4_para_o_player() -> None:
    with TestClient(app) as client:
        with patch(
            "transcribrothers_backend.main.baixar_mp4_renderizado_da_vinheta",
            new=AsyncMock(return_value=b"mp4-get"),
        ) as mock_baixar:
            resposta = client.get(
                "/api/integracao/vinhetas/previsualizar",
                params={"titulo": "Nova seção", "efeito": "planos-que-abrem-espaco"},
            )
    assert resposta.status_code == 200, resposta.text
    assert resposta.headers["content-type"].startswith("video/mp4")
    assert resposta.content == b"mp4-get"
    mock_baixar.assert_awaited_once()
