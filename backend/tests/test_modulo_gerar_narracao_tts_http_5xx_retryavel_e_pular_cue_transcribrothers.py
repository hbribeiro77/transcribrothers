"""HTTP 5xx/429 no TTS: retry e, se persistir, pular cue com silêncio."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    ErroTtsRespostaVaziaRetryavelTranscribrothers,
    _http_status_proxy_tts_e_retryavel_transcribrothers,
    _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers,
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)


def test_http_status_5xx_e_429_sao_retryaveis() -> None:
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(500) is True
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(503) is True
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(429) is True
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(400) is False
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(401) is False
    assert _http_status_proxy_tts_e_retryavel_transcribrothers(200) is False


@pytest.mark.asyncio
async def test_retry_recupera_apos_http_500_transitório() -> None:
    pcm_ok = b"\x01\x00" * 2400  # 0.1s @ 24kHz mono
    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "_sintetizar_pcm16_trecho_tts_via_litellm_transcribrothers",
            new_callable=AsyncMock,
            side_effect=[
                ErroTtsRespostaVaziaRetryavelTranscribrothers(
                    "Proxy rejeitou a narração TTS (HTTP 500) — InternalServerError"
                ),
                pcm_ok,
            ],
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        out = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
            texto="O usuário pode selecionar até 25 intimações.",
            modelo="gemini/fake-tts",
            api_key="k",
            base_v1="https://example.test/v1",
            httpx_verify=False,
            voz="Kore",
            max_tentativas=3,
        )
    assert out == pcm_ok


@pytest.mark.asyncio
async def test_cue_pulada_com_silencio_apos_http_500_persistente(tmp_path: Path) -> None:
    cfg = MagicMock()
    dir_wavs = tmp_path / "wavs"
    wav_concat = tmp_path / "narracao_tts_documento.wav"

    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "resolver_api_key_e_api_base_para_chamada_litellm",
            return_value=("k", "https://example.test"),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1",
            return_value="https://example.test/v1",
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "_sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers",
            new_callable=AsyncMock,
            side_effect=ErroTtsRespostaVaziaRetryavelTranscribrothers(
                "Após 3 tentativa(s): Proxy rejeitou a narração TTS (HTTP 500)"
            ),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        res = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=["O usuário pode selecionar até 25 intimações por vez."],
            modelo="gemini/fake-tts",
            configuracao=cfg,
            diretorio_wavs_por_cue=dir_wavs,
            caminho_wav_concatenado=wav_concat,
        )

    assert res.ok is True
    assert res.quantidade_cues == 1
    assert res.quantidade_cues_puladas == 1
    assert len(res.caminhos_wav_por_cue) == 1
    assert res.caminhos_wav_por_cue[0].is_file()
    assert wav_concat.is_file()
    assert res.duracoes_por_cue_segundos[0] > 0.2
