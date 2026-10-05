"""Cliente HTTP ElevenLabs: GET /v1/voices e POST /v1/text-to-speech (eleven_v4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_cliente_elevenlabs_text_to_speech_e_vozes_transcribrothers import (
    FalhaClienteElevenlabsTranscribrothers,
    listar_vozes_elevenlabs_via_get_v1_voices_transcribrothers,
    sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers import (
    MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
)


def _cfg(chave: str = "sk-teste") -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(elevenlabs_api_key=chave)


def _resposta(status: int, *, json_body: dict | None = None, content: bytes = b"") -> httpx.Response:
    req = httpx.Request("GET", "https://api.elevenlabs.io/v1/voices")
    if json_body is not None:
        return httpx.Response(status, json=json_body, request=req)
    return httpx.Response(status, content=content, request=req)


def _patch_client(mock_client: AsyncMock):
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    return patch(
        "transcribrothers_backend.modulo_cliente_elevenlabs_text_to_speech_e_vozes_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    )


@pytest.mark.asyncio
async def test_listar_vozes_sem_chave_levanta_falha() -> None:
    with pytest.raises(FalhaClienteElevenlabsTranscribrothers, match="ELEVENLABS_API_KEY"):
        await listar_vozes_elevenlabs_via_get_v1_voices_transcribrothers(configuracao=_cfg(""))


@pytest.mark.asyncio
async def test_listar_vozes_get_v1_voices_devolve_ids_e_nomes() -> None:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        return_value=_resposta(
            200,
            json_body={"voices": [{"voice_id": "voz1", "name": "Rachel"}]},
        )
    )
    with _patch_client(mock_client):
        vozes = await listar_vozes_elevenlabs_via_get_v1_voices_transcribrothers(
            configuracao=_cfg()
        )
    assert vozes[0]["id"] == "voz1"
    assert vozes[0]["estilo"] == "Rachel"
    assert vozes[0]["pt_br"] is False
    assert mock_client.get.await_args.args[0] == "https://api.elevenlabs.io/v1/voices"
    assert mock_client.get.await_args.kwargs["headers"]["xi-api-key"] == "sk-teste"


@pytest.mark.asyncio
async def test_sintetizar_v4_posta_modelo_e_idioma_pt_e_devolve_bytes() -> None:
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta(200, content=b"ID3fake-mp3"))
    with _patch_client(mock_client):
        audio = await sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers(
            configuracao=_cfg(),
            texto="Olá, tutorial.",
            voice_id="voz1",
        )
    assert audio == b"ID3fake-mp3"
    url = mock_client.post.await_args.args[0]
    assert url.startswith("https://api.elevenlabs.io/v1/text-to-speech/voz1")
    assert "output_format=mp3_44100_128" in url
    corpo = mock_client.post.await_args.kwargs["json"]
    assert corpo["model_id"] == MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    assert corpo["language_code"] == "pt"
    assert corpo["text"] == "Olá, tutorial."
    assert mock_client.post.await_args.kwargs["headers"]["xi-api-key"] == "sk-teste"


@pytest.mark.asyncio
async def test_sintetizar_http_erro_levanta_falha() -> None:
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta(401, json_body={"detail": "invalid"}))
    with _patch_client(mock_client):
        with pytest.raises(FalhaClienteElevenlabsTranscribrothers, match="401"):
            await sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers(
                configuracao=_cfg(),
                texto="oi",
                voice_id="voz1",
            )
