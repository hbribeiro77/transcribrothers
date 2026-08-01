"""Chunks + concat de narração TTS."""

from __future__ import annotations

import base64
import wave
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers,
    gerar_narracao_tts_wav_a_partir_lista_trechos_via_litellm_transcribrothers,
    gerar_narracao_tts_wav_em_chunks_concatenados_via_litellm_transcribrothers,
    partir_texto_em_chunks_para_narracao_tts_transcribrothers,
    validar_duracao_wav_narracao_compativel_com_texto_transcribrothers,
)


def test_partir_texto_em_chunks_respeita_limite() -> None:
    texto = ("Frase curta. " * 40).strip()
    chunks = partir_texto_em_chunks_para_narracao_tts_transcribrothers(texto, max_chars=80)
    assert len(chunks) > 1
    assert all(len(c) <= 80 for c in chunks)
    assert "Frase curta" in " ".join(chunks)


def _pcm(n: int = 100) -> bytes:
    return b"\x01\x00" * n


def _resp_tts() -> httpx.Response:
    data = base64.b64encode(_pcm(50)).decode("ascii")
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    return httpx.Response(
        200,
        json={"choices": [{"message": {"audio": {"data": data, "format": "pcm16"}}}]},
        request=req,
    )


@pytest.mark.asyncio
async def test_gerar_narracao_chunks_concatena_pcm(tmp_path: Path) -> None:
    texto = ("Palavra. " * 200).strip()
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resp_tts())
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    destino = tmp_path / "narracao_tts_documento.wav"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )
    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
            return_value=mock_cm,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        r = await gerar_narracao_tts_wav_em_chunks_concatenados_via_litellm_transcribrothers(
            texto_plano=texto,
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=cfg,
            caminho_wav_saida=destino,
            max_chars_chunk=100,
        )

    assert r.ok is True
    assert r.quantidade_chunks > 1
    assert mock_client.post.await_count == r.quantidade_chunks
    assert destino.is_file()
    with wave.open(str(destino), "rb") as wf:
        assert wf.getnframes() > 50


def test_expandir_trechos_cues_parte_cue_longa() -> None:
    longa = ("Palavra. " * 80).strip()
    out = expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers(
        ["Oi curto.", longa, ""],
        max_chars=100,
    )
    assert out[0] == "Oi curto."
    assert len(out) > 2
    assert all(len(t) <= 100 for t in out)


def _resp_tts_com_pcm_longo(segundos: float = 1.2) -> httpx.Response:
    samples = int(24000 * segundos)
    data = base64.b64encode(b"\x01\x00" * samples).decode("ascii")
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    return httpx.Response(
        200,
        json={"choices": [{"message": {"audio": {"data": data, "format": "pcm16"}}}]},
        request=req,
    )


@pytest.mark.asyncio
async def test_gerar_narracao_lista_trechos_chama_sintese_por_cue(tmp_path: Path) -> None:
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resp_tts_com_pcm_longo(1.2))
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    destino = tmp_path / "narracao_tts_documento.wav"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )
    trechos = ["Primeira cue curta.", "Segunda cue curta.", "Terceira cue curta."]
    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
            return_value=mock_cm,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        r = await gerar_narracao_tts_wav_a_partir_lista_trechos_via_litellm_transcribrothers(
            trechos=trechos,
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=cfg,
            caminho_wav_saida=destino,
        )

    assert r.ok is True, r.mensagem
    assert r.quantidade_chunks == 3
    assert mock_client.post.await_count == 3
    assert destino.is_file()


def test_validar_duracao_wav_rejeita_narracao_curta(tmp_path: Path) -> None:
    caminho = tmp_path / "curto.wav"
    with wave.open(str(caminho), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * 100)
    erro = validar_duracao_wav_narracao_compativel_com_texto_transcribrothers(
        caminho_wav=caminho,
        texto_caracteres=500,
    )
    assert erro is not None
    assert "curta" in erro.lower()


@pytest.mark.asyncio
async def test_gerar_narracao_lista_choices_vazia_mensagem_clara_com_indice(tmp_path: Path) -> None:
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    resp_vazio = httpx.Response(200, json={"choices": []}, request=req)
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=resp_vazio)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    destino = tmp_path / "narracao_tts_documento.wav"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )
    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
            return_value=mock_cm,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        r = await gerar_narracao_tts_wav_a_partir_lista_trechos_via_litellm_transcribrothers(
            trechos=["Primeiro trecho ok.", "Segundo trecho problema."],
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=cfg,
            caminho_wav_saida=destino,
        )

    assert r.ok is False
    assert "choices" in r.mensagem.lower()
    assert "1/2" in r.mensagem
    assert "Primeiro trecho" in r.mensagem
    # 3 tentativas no trecho 1 (retry) e para antes do trecho 2
    assert mock_client.post.await_count == 3


@pytest.mark.asyncio
async def test_gerar_narracao_lista_retry_recupera_apos_choices_vazio(tmp_path: Path) -> None:
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    resp_vazio = httpx.Response(200, json={"choices": []}, request=req)
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=[resp_vazio, _resp_tts_com_pcm_longo(2.2)])
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    destino = tmp_path / "narracao_tts_documento.wav"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )
    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
            return_value=mock_cm,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        r = await gerar_narracao_tts_wav_a_partir_lista_trechos_via_litellm_transcribrothers(
            trechos=["Só uma cue."],
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=cfg,
            caminho_wav_saida=destino,
        )

    assert r.ok is True, r.mensagem
    assert mock_client.post.await_count == 2
    corpo = mock_client.post.await_args_list[-1].kwargs["json"]
    assert corpo["messages"][0]["content"] == "Só uma cue."
