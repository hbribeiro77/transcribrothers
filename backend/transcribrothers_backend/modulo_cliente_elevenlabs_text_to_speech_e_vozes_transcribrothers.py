"""Cliente ElevenLabs: listar vozes e sintetizar TTS com eleven_v4 (sem turbo)."""

from __future__ import annotations

import httpx

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers import (
    MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
    extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers,
    normalizar_modelo_tts_elevenlabs_transcribrothers,
    tem_chave_elevenlabs_configurada_transcribrothers,
)

URL_BASE_API_ELEVENLABS_TRANSCRIBROTHERS = "https://api.elevenlabs.io"
_TIMEOUT_CONNECT_SEGUNDOS = 8.0
_TIMEOUT_READ_SEGUNDOS = 90.0
_OUTPUT_FORMAT_MP3 = "mp3_44100_128"


class FalhaClienteElevenlabsTranscribrothers(Exception):
    """Falha ao chamar a API da ElevenLabs (chave, rede ou HTTP)."""


def _chave_ou_falha(cfg: ConfiguracaoAmbienteTranscribrothers) -> str:
    if not tem_chave_elevenlabs_configurada_transcribrothers(cfg):
        raise FalhaClienteElevenlabsTranscribrothers(
            "ElevenLabs não configurado no servidor (defina ELEVENLABS_API_KEY)."
        )
    return (cfg.elevenlabs_api_key or "").strip()


def _timeout() -> httpx.Timeout:
    return httpx.Timeout(
        connect=_TIMEOUT_CONNECT_SEGUNDOS,
        read=_TIMEOUT_READ_SEGUNDOS,
        write=_TIMEOUT_READ_SEGUNDOS,
        pool=_TIMEOUT_CONNECT_SEGUNDOS,
    )


def _headers(api_key: str) -> dict[str, str]:
    return {
        "xi-api-key": api_key,
        "Accept": "application/json",
    }


async def listar_vozes_elevenlabs_via_get_v1_voices_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> list[dict[str, object]]:
    api_key = _chave_ou_falha(configuracao)
    url = f"{URL_BASE_API_ELEVENLABS_TRANSCRIBROTHERS}/v1/voices"
    try:
        async with httpx.AsyncClient(timeout=_timeout()) as client:
            http = await client.get(url, headers=_headers(api_key))
    except httpx.TimeoutException as exc:
        raise FalhaClienteElevenlabsTranscribrothers(
            "Tempo esgotado ao listar vozes na ElevenLabs."
        ) from exc
    except httpx.HTTPError as exc:
        raise FalhaClienteElevenlabsTranscribrothers(
            f"Falha de rede ao listar vozes na ElevenLabs: {exc}"
        ) from exc
    if http.status_code >= 400:
        trecho = (http.text or "").strip().replace("\n", " ")[:240]
        detalhe = f" — {trecho}" if trecho else ""
        raise FalhaClienteElevenlabsTranscribrothers(
            f"A ElevenLabs recusou a listagem de vozes (HTTP {http.status_code}){detalhe}"
        )
    try:
        payload = http.json()
    except ValueError as exc:
        raise FalhaClienteElevenlabsTranscribrothers(
            "A ElevenLabs respondeu, mas o JSON de /v1/voices foi inválido."
        ) from exc
    return extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers(payload)


async def sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    texto: str,
    voice_id: str,
    modelo: str | None = None,
) -> bytes:
    api_key = _chave_ou_falha(configuracao)
    texto_norm = " ".join((texto or "").split())
    voice = (voice_id or "").strip()
    if not texto_norm:
        raise FalhaClienteElevenlabsTranscribrothers("Informe o texto para sintetizar na ElevenLabs.")
    if not voice:
        raise FalhaClienteElevenlabsTranscribrothers("Informe o voice_id da ElevenLabs.")
    modelo_efetivo = normalizar_modelo_tts_elevenlabs_transcribrothers(modelo)
    url = (
        f"{URL_BASE_API_ELEVENLABS_TRANSCRIBROTHERS}/v1/text-to-speech/{voice}"
        f"?output_format={_OUTPUT_FORMAT_MP3}"
    )
    corpo = {
        "text": texto_norm,
        "model_id": modelo_efetivo,
        "language_code": "pt",
    }
    headers = {
        **_headers(api_key),
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=_timeout()) as client:
            http = await client.post(url, headers=headers, json=corpo)
    except httpx.TimeoutException as exc:
        raise FalhaClienteElevenlabsTranscribrothers(
            "Tempo esgotado ao sintetizar TTS na ElevenLabs."
        ) from exc
    except httpx.HTTPError as exc:
        raise FalhaClienteElevenlabsTranscribrothers(
            f"Falha de rede ao sintetizar TTS na ElevenLabs: {exc}"
        ) from exc
    if http.status_code >= 400:
        trecho = (http.text or "").strip().replace("\n", " ")[:240]
        detalhe = f" — {trecho}" if trecho else ""
        raise FalhaClienteElevenlabsTranscribrothers(
            f"A ElevenLabs recusou o TTS (HTTP {http.status_code}){detalhe}"
        )
    audio = http.content or b""
    if not audio:
        raise FalhaClienteElevenlabsTranscribrothers("A ElevenLabs respondeu sem áudio no TTS.")
    return audio
