"""Diagnóstico + timeout 30s só no perfil experimental_voz (padrão sagrado intacto)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from transcribrothers_backend.modulo_diagnostico_tts_perfil_experimental_voz_transcribrothers import (
    TTS_TIMEOUT_READ_EXPERIMENTAL_VOZ_SEGUNDOS,
    aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    ErroTtsRespostaVaziaRetryavelTranscribrothers,
    _TTS_TIMEOUT_READ_SEGUNDOS,
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
)


def test_timeout_read_experimental_90s_e_padrao_continua_180s() -> None:
    assert TTS_TIMEOUT_READ_EXPERIMENTAL_VOZ_SEGUNDOS == 90.0
    assert _TTS_TIMEOUT_READ_SEGUNDOS == 180.0
    assert TTS_TIMEOUT_READ_EXPERIMENTAL_VOZ_SEGUNDOS != _TTS_TIMEOUT_READ_SEGUNDOS


def test_aplicar_diagnostico_nos_steps_so_quando_ha_payload() -> None:
    steps: dict = {}
    aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers(steps, None)
    assert "video_narrado_tts_diagnostico_experimental" not in steps
    aplicar_diagnostico_tts_experimental_nos_steps_json_transcribrothers(
        steps,
        {"perfil_tts": "experimental_voz", "resumo_texto": "x"},
    )
    assert steps["video_narrado_tts_diagnostico_experimental"]["resumo_texto"] == "x"


@pytest.mark.asyncio
async def test_perfil_padrao_nao_gera_diagnostico_experimental(tmp_path: Path) -> None:
    cfg = MagicMock()
    pcm_ok = b"\x01\x00" * 24000  # ~1s
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
            return_value=pcm_ok,
        ),
    ):
        res = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=["O usuário pode selecionar até 25 intimações por vez."],
            modelo="gemini/fake-tts",
            configuracao=cfg,
            diretorio_wavs_por_cue=tmp_path / "wavs",
            caminho_wav_concatenado=tmp_path / "narracao.wav",
            perfil_tts=PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        )
    assert res.ok is True
    assert res.diagnostico_experimental is None


@pytest.mark.asyncio
async def test_experimental_pulada_registra_indice_e_motivo_no_diagnostico(
    tmp_path: Path,
) -> None:
    cfg = MagicMock()
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
            "_sintetizar_pcm16_trecho_tts_motor_experimental_voz_via_litellm_transcribrothers",
            new_callable=AsyncMock,
            side_effect=ErroTtsRespostaVaziaRetryavelTranscribrothers(
                "Resposta TTS sem choices (proxy/modelo devolveu lista vazia ou ausente)."
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
            diretorio_wavs_por_cue=tmp_path / "wavs",
            caminho_wav_concatenado=tmp_path / "narracao.wav",
            perfil_tts=PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
        )
    assert res.ok is True
    assert res.quantidade_cues_puladas == 1
    assert res.diagnostico_experimental is not None
    diag = res.diagnostico_experimental
    assert diag["timeout_read_segundos"] == 90.0
    assert diag["quantidade_cues_puladas"] == 1
    assert len(diag["cues_puladas"]) == 1
    pulada = diag["cues_puladas"][0]
    assert pulada["indice_cue"] == 1
    assert pulada["motivo"]
    assert "DIAGNOSTICO TTS EXPERIMENTAL" in diag["resumo_texto"]
    assert "PULADAS:" in diag["resumo_texto"]


@pytest.mark.asyncio
async def test_experimental_timeout_vira_pendente_manual_sem_falhar_job(
    tmp_path: Path,
) -> None:
    cfg = MagicMock()
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
            "_sintetizar_pcm16_trecho_tts_motor_experimental_voz_via_litellm_transcribrothers",
            new_callable=AsyncMock,
            side_effect=httpx.ReadTimeout("read timeout"),
        ),
        patch(
            "transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers."
            "asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        res = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
            trechos=["Configure o DNS do servidor de produção com cuidado."],
            modelo="gemini/fake-tts",
            configuracao=cfg,
            diretorio_wavs_por_cue=tmp_path / "wavs",
            caminho_wav_concatenado=tmp_path / "narracao.wav",
            perfil_tts=PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
        )
    assert res.ok is True
    assert "reenvio manual" in res.mensagem.lower()
    assert len(res.cues_pendentes_timeout) == 1
    pendente = res.cues_pendentes_timeout[0]
    assert pendente["indice"] == 0
    assert pendente["motivo"] == "timeout"
    assert "DNS" in pendente["texto"]
    assert res.quantidade_cues_puladas == 0
    assert res.diagnostico_experimental is not None
    assert res.diagnostico_experimental["falha"] is None
    assert res.diagnostico_experimental["quantidade_timeouts"] == 1
    assert res.diagnostico_experimental["timeout_read_segundos"] == 90.0
