"""Resiliência da transcrição multimodal: content em lista, retry em vazio, exceção específica."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    ErroConteudoVazioTranscricaoMultimodalTranscribrothers,
    TranscriberLiteLLmMultimodalAudioJsonSegmentos,
    extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers,
)


def test_extrair_texto_de_content_string() -> None:
    assert (
        extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers(
            {"content": '{"idioma":"pt","segmentos":[]}'}
        )
        == '{"idioma":"pt","segmentos":[]}'
    )


def test_extrair_texto_de_content_lista_de_partes() -> None:
    msg = {
        "content": [
            {"type": "text", "text": '{"idioma":"pt","segmentos":['},
            {"type": "text", "text": '{"inicio_segundos":0,"fim_segundos":1,"texto":"oi"}]}'},
        ]
    }
    texto = extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers(msg)
    assert '"idioma":"pt"' in texto
    assert "oi" in texto


def test_extrair_texto_content_lista_vazia_ou_null_e_vazio() -> None:
    assert extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers({"content": []}) == ""
    assert extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers({"content": None}) == ""
    assert extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers({"content": "  "}) == ""
    assert extrair_texto_conteudo_message_transcricao_multimodal_transcribrothers({}) == ""


def _resposta_chat(payload: dict) -> httpx.Response:
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    return httpx.Response(200, json=payload, request=req)


def _payload_content(content: object) -> dict:
    return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}


JSON_OK = '{"idioma":"pt","segmentos":[{"inicio_segundos":0.0,"fim_segundos":1.0,"texto":"fala"}]}'


def _montar_transcriber() -> TranscriberLiteLLmMultimodalAudioJsonSegmentos:
    return TranscriberLiteLLmMultimodalAudioJsonSegmentos(
        model="gemini/teste",
        api_key="k",
        api_base="https://proxy.exemplo/v1",
        httpx_verify=False,
        usar_response_format_json_object=False,
    )


def _patch_cliente_com_posts(*respostas: httpx.Response):
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=list(respostas))
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = False
    return patch(
        "transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos.httpx.AsyncClient",
        return_value=mock_cm,
    ), mock_client


@pytest.mark.asyncio
async def test_transcrever_aceita_content_como_lista_de_partes(tmp_path: Path) -> None:
    audio = tmp_path / "janela.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 12)
    patcher, mock_client = _patch_cliente_com_posts(
        _resposta_chat(_payload_content([{"type": "text", "text": JSON_OK}])),
    )
    with patcher:
        resultado = await _montar_transcriber().transcrever_arquivo_audio_com_segmentos(audio)
    assert "fala" in resultado.texto_completo
    assert mock_client.post.await_count == 1


@pytest.mark.asyncio
async def test_transcrever_retenta_quando_content_vazio_e_recupera(tmp_path: Path) -> None:
    audio = tmp_path / "janela.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 12)
    patcher, mock_client = _patch_cliente_com_posts(
        _resposta_chat(_payload_content("")),
        _resposta_chat(_payload_content(JSON_OK)),
    )
    with patcher:
        resultado = await _montar_transcriber().transcrever_arquivo_audio_com_segmentos(audio)
    assert "fala" in resultado.texto_completo
    assert mock_client.post.await_count == 2


@pytest.mark.asyncio
async def test_transcrever_esgota_tentativas_em_vazio_e_levanta_erro_especifico(tmp_path: Path) -> None:
    audio = tmp_path / "janela.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 12)
    patcher, mock_client = _patch_cliente_com_posts(
        _resposta_chat(_payload_content("")),
        _resposta_chat(_payload_content(None)),
        _resposta_chat(_payload_content([])),
    )
    with patcher:
        with pytest.raises(ErroConteudoVazioTranscricaoMultimodalTranscribrothers) as ei:
            await _montar_transcriber().transcrever_arquivo_audio_com_segmentos(audio)
    assert "conteúdo vazio" in str(ei.value).lower()
    assert mock_client.post.await_count == 3
