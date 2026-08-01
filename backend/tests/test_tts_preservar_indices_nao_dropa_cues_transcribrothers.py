"""TTS com preservar_indices_da_entrada mantém 1 WAV por cue de entrada."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)


@pytest.mark.asyncio
async def test_preservar_indices_gera_wav_mesmo_para_cue_nao_narravel(
    tmp_path: Path,
) -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="sk-teste",
        litellm_endpoint="https://proxy.exemplo/v1",
        litellm_http_verify_ssl=False,
    )
    trechos = [
        "frase narrável completa com letras suficientes",
        ").",  # lixo: vira silêncio, mas mantém índice
        "outra frase narrável também ok",
    ]
    dir_wavs = tmp_path / "wavs"
    concat = tmp_path / "concat.wav"

    # PCM longo o bastante para não ser tratado como truncagem (mín. ~0.035s/char).
    pcm_fake = b"\x01\x00" * int(24000 * 3.0)

    with (
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "resolver_api_key_e_api_base_para_chamada_litellm",
            return_value=("sk-teste", "https://proxy.exemplo/v1"),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1",
            return_value="https://proxy.exemplo/v1",
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm",
            return_value=False,
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "_sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers",
            new=AsyncMock(return_value=pcm_fake),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        resultado = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=trechos,
            modelo="gemini/gemini-2.5-flash-preview-tts",
            configuracao=cfg,
            diretorio_wavs_por_cue=dir_wavs,
            caminho_wav_concatenado=concat,
            preservar_indices_da_entrada=True,
        )

    assert resultado.ok, resultado.mensagem
    assert len(resultado.caminhos_wav_por_cue) == 3
    assert len(resultado.duracoes_por_cue_segundos) == 3
    assert resultado.quantidade_cues_puladas == 0
    # Sem preservar_indices, o filtro interno droparia o ").".
    assert (dir_wavs / "cue_narracao_0000.wav").is_file()
    assert (dir_wavs / "cue_narracao_0001.wav").is_file()
    assert (dir_wavs / "cue_narracao_0002.wav").is_file()
    assert concat.is_file()
