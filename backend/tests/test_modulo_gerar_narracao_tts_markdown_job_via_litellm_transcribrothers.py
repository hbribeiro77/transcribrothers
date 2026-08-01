"""Geração de narração TTS a partir do Markdown do job (mock do proxy)."""

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
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers,
)


def _cfg() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk-teste",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )


def _pcm16_silencio(num_samples: int = 2400) -> bytes:
    return b"\x00\x00" * num_samples


def _resposta_tts_ok() -> httpx.Response:
    data_b64 = base64.b64encode(_pcm16_silencio()).decode("ascii")
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "audio": {"data": data_b64, "format": "pcm16"},
                }
            }
        ]
    }
    req = httpx.Request("POST", "https://proxy.exemplo/v1/chat/completions")
    return httpx.Response(200, json=payload, request=req)


@pytest.mark.asyncio
async def test_gerar_narracao_grava_wav_e_usa_modalities_audio(tmp_path: Path) -> None:
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=_resposta_tts_ok())
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    destino = tmp_path / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    with patch(
        "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
        return_value=mock_cm,
    ):
        meta = await gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers(
            texto_plano="Olá, isto é um teste de narração.",
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=_cfg(),
            caminho_wav_saida=destino,
        )

    assert meta.ok is True
    assert destino.is_file()
    assert meta.nome_arquivo == NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    with wave.open(str(destino), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 24000
        assert wf.getnframes() > 0
    corpo = mock_client.post.await_args.kwargs["json"]
    assert corpo["modalities"] == ["audio"]
    assert corpo["audio"]["format"] == "pcm16"


@pytest.mark.asyncio
async def test_gerar_narracao_texto_vazio_falha_sem_chamar_proxy() -> None:
    with patch(
        "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers.httpx.AsyncClient",
    ) as mock_cls:
        meta = await gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers(
            texto_plano="   ",
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=_cfg(),
            caminho_wav_saida=Path("nao_deve_existir.wav"),
        )
    assert meta.ok is False
    mock_cls.assert_not_called()
