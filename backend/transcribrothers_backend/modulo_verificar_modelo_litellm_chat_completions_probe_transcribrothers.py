"""Probe barato: POST /v1/chat/completions para validar se um modelo responde no proxy.

Chat texto: exige conteúdo textual.
TTS (slug com `-tts`): exige modalities/audio e resposta com áudio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)

_PROBE_TIMEOUT_CONNECT_SEGUNDOS = 5.0
_PROBE_TIMEOUT_READ_SEGUNDOS = 15.0
_PROBE_MAX_TOKENS = 8
_PROBE_MENSAGEM_USER_CHAT = "Responda apenas com a palavra: ok"
_PROBE_MENSAGEM_USER_TTS = "Diga apenas: olá."
_PROBE_TTS_VOICE = "Kore"
_PROBE_TTS_AUDIO_FORMAT = "pcm16"


@dataclass(frozen=True)
class ResultadoVerificacaoModeloLitellmProbeTranscribrothers:
    ok: bool
    modelo: str
    mensagem: str


def modelo_litellm_parece_tts_pelo_slug_transcribrothers(modelo: str) -> bool:
    """Heurística: slugs Gemini/LiteLLM de TTS costumam conter `-tts` (ex.: preview-tts, flash-tts)."""
    s = (modelo or "").strip().lower()
    if not s:
        return False
    return "-tts" in s or s.endswith("/tts") or "/tts-" in s


def _mensagem_tem_audio_util_na_resposta_chat_transcribrothers(message: dict[str, Any]) -> bool:
    audio = message.get("audio")
    if isinstance(audio, dict):
        data = audio.get("data") or audio.get("id") or audio.get("url")
        if isinstance(data, str) and data.strip():
            return True
        if data is not None and not isinstance(data, str):
            return True
    conteudo = message.get("content")
    if isinstance(conteudo, list):
        for parte in conteudo:
            if not isinstance(parte, dict):
                continue
            tipo = str(parte.get("type") or "").lower()
            if "audio" in tipo:
                if parte.get("audio") or parte.get("data") or parte.get("input_audio"):
                    return True
            if isinstance(parte.get("inline_data"), dict) and parte["inline_data"].get("data"):
                mime = str(parte["inline_data"].get("mime_type") or "").lower()
                if mime.startswith("audio/"):
                    return True
    return False


def _extrair_texto_conteudo_message_chat_transcribrothers(message: dict[str, Any]) -> str:
    conteudo = message.get("content")
    if isinstance(conteudo, list):
        partes: list[str] = []
        for p in conteudo:
            if isinstance(p, dict) and isinstance(p.get("text"), str):
                partes.append(p["text"])
            elif isinstance(p, str):
                partes.append(p)
        return "".join(partes).strip()
    if isinstance(conteudo, str):
        return conteudo.strip()
    return ""


def _montar_corpo_probe_chat_texto_transcribrothers(modelo: str) -> dict[str, Any]:
    return {
        "model": modelo,
        "messages": [{"role": "user", "content": _PROBE_MENSAGEM_USER_CHAT}],
        "temperature": 0,
        "max_tokens": _PROBE_MAX_TOKENS,
    }


def _montar_corpo_probe_tts_audio_transcribrothers(modelo: str) -> dict[str, Any]:
    return {
        "model": modelo,
        "messages": [{"role": "user", "content": _PROBE_MENSAGEM_USER_TTS}],
        "modalities": ["audio"],
        "audio": {
            "voice": _PROBE_TTS_VOICE,
            "format": _PROBE_TTS_AUDIO_FORMAT,
        },
        # Alguns proxies LiteLLM filtram params OpenAI; isso força áudio/modalities.
        "allowed_openai_params": ["audio", "modalities"],
        "temperature": 0,
        "max_tokens": 64,
    }


async def verificar_modelo_litellm_via_chat_completions_probe_transcribrothers(
    *,
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> ResultadoVerificacaoModeloLitellmProbeTranscribrothers:
    """
    Chama o proxy com um pedido mínimo.
    - Chat: confirma texto.
    - TTS (slug): confirma áudio via modalities/audio.
    Não valida STT/visão do pipeline do Transcribrothers.
    """
    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo="",
            mensagem="Informe o identificador do modelo LiteLLM.",
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem=(
                "Proxy LiteLLM não configurado no servidor "
                "(defina LITELLM_API_KEY e LITELLM_ENDPOINT)."
            ),
        )

    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem="LITELLM_ENDPOINT inválido no servidor.",
        )

    modo_tts = modelo_litellm_parece_tts_pelo_slug_transcribrothers(modelo_norm)
    url_chat = f"{base_v1}/chat/completions"
    corpo = (
        _montar_corpo_probe_tts_audio_transcribrothers(modelo_norm)
        if modo_tts
        else _montar_corpo_probe_chat_texto_transcribrothers(modelo_norm)
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(
        connect=_PROBE_TIMEOUT_CONNECT_SEGUNDOS,
        read=_PROBE_TIMEOUT_READ_SEGUNDOS,
        write=_PROBE_TIMEOUT_READ_SEGUNDOS,
        pool=_PROBE_TIMEOUT_CONNECT_SEGUNDOS,
    )
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)

    try:
        async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
            http = await client.post(url_chat, headers=headers, json=corpo)
    except httpx.TimeoutException:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem=(
                f"Tempo esgotado ao testar o modelo (limite {_PROBE_TIMEOUT_READ_SEGUNDOS:.0f}s). "
                "Confira o proxy ou tente de novo."
            ),
        )
    except httpx.HTTPError as exc:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem=f"Falha de rede ao chamar o proxy: {exc}",
        )

    if http.status_code >= 400:
        trecho = (http.text or "").strip().replace("\n", " ")[:400]
        detalhe = f" — {trecho}" if trecho else ""
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem=f"O proxy rejeitou o modelo (HTTP {http.status_code}){detalhe}",
        )

    try:
        body = http.json()
        choice = body["choices"][0]["message"]
        if not isinstance(choice, dict):
            raise TypeError("message não é objeto")
    except (KeyError, IndexError, TypeError, ValueError):
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem="O proxy respondeu, mas o formato da resposta de chat foi inesperado.",
        )

    if modo_tts:
        if _mensagem_tem_audio_util_na_resposta_chat_transcribrothers(choice):
            return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
                ok=True,
                modelo=modelo_norm,
                mensagem="Modelo TTS respondeu com áudio ao probe.",
            )
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem="O proxy aceitou o pedido TTS, mas a resposta veio sem áudio útil.",
        )

    texto = _extrair_texto_conteudo_message_chat_transcribrothers(choice)
    if not texto:
        return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
            ok=False,
            modelo=modelo_norm,
            mensagem="O modelo respondeu sem texto útil no probe de chat.",
        )

    return ResultadoVerificacaoModeloLitellmProbeTranscribrothers(
        ok=True,
        modelo=modelo_norm,
        mensagem="Modelo respondeu ao probe de chat.",
    )
