"""Narração TTS por cue deve processar várias cues em paralelo (com semáforo)."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)


@pytest.mark.asyncio
async def test_gerar_narracao_tts_cues_em_paralelo_atinge_concorrencia_maior_que_um(
    tmp_path: Path,
) -> None:
    cfg = MagicMock()
    dir_wavs = tmp_path / "wavs"
    wav_concat = tmp_path / "narracao_tts_documento.wav"
    # ~2s @ 24kHz — acima do mínimo por caracteres das cues de teste.
    pcm_ok = b"\x01\x00" * 48_000

    em_voo = 0
    pico = 0
    lock = asyncio.Lock()

    async def _sintetizar_com_concorrencia(**_kwargs: object) -> bytes:
        nonlocal em_voo, pico
        async with lock:
            em_voo += 1
            pico = max(pico, em_voo)
        await asyncio.sleep(0.05)
        async with lock:
            em_voo -= 1
        return pcm_ok

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
            new=AsyncMock(side_effect=_sintetizar_com_concorrencia),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "_TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS",
            0.0,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "_TTS_PARALELISMO_CUES",
            3,
        ),
    ):
        res = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=[
                "Primeira fala narrável do documento de teste.",
                "Segunda fala narrável do documento de teste.",
                "Terceira fala narrável do documento de teste.",
            ],
            modelo="gemini/fake-tts",
            configuracao=cfg,
            diretorio_wavs_por_cue=dir_wavs,
            caminho_wav_concatenado=wav_concat,
        )

    assert res.ok is True
    assert res.quantidade_cues == 3
    assert len(res.caminhos_wav_por_cue) == 3
    assert pico >= 2, f"esperava concorrência >= 2, pico={pico}"
