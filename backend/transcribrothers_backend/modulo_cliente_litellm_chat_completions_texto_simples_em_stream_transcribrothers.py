"""POST /v1/chat/completions com stream=true; rende pedaços de content."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

import httpx

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers import (
    coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    _http_indica_rejeicao_response_format_json_object,
)


def extrair_delta_content_de_linha_sse_chat_completions_transcribrothers(linha: str) -> str:
    cortada = (linha or "").strip()
    if not cortada.startswith("data:"):
        return ""
    payload = cortada[5:].strip()
    if not payload or payload == "[DONE]":
        return ""
    try:
        data = json.loads(payload)
        choice = data["choices"][0]
        delta = choice.get("delta") if isinstance(choice, dict) else None
        if not isinstance(delta, dict):
            return ""
        conteudo = delta.get("content")
        return conteudo if isinstance(conteudo, str) else ""
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return ""


async def litellm_chat_completions_texto_simples_em_stream_transcribrothers(
    *,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    mensagens: list[dict[str, str]],
    temperature: float = 0.25,
    usar_response_format_json_object: bool = False,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
) -> AsyncIterator[str]:
    chave = (api_key or "").strip()
    if not chave:
        raise RuntimeError(
            "Chave do proxy ausente: defina LITELLM_API_KEY no servidor (a mesma credencial que o LiteLLM espera)."
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise RuntimeError(
            "LITELLM_ENDPOINT é obrigatório: o backend só chama o seu proxy LiteLLM (POST …/v1/chat/completions)."
        )
    url_chat = f"{base_v1}/chat/completions"
    corpo: dict[str, Any] = {
        "model": modelo.strip(),
        "messages": mensagens,
        "temperature": float(temperature),
        "stream": True,
    }
    if usar_response_format_json_object:
        corpo["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {chave}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    timeout = httpx.Timeout(
        connect=max(5.0, float(httpx_timeout_connect_segundos)),
        read=max(60.0, float(httpx_timeout_read_segundos)),
        write=max(60.0, float(httpx_timeout_read_segundos)),
        pool=max(5.0, float(httpx_timeout_connect_segundos)),
    )
    async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
        async with client.stream("POST", url_chat, headers=headers, json=corpo) as http:
            if not http.is_success and usar_response_format_json_object:
                trecho = (await http.aread()).decode("utf-8", errors="replace")
                classe = type(
                    "HttpFakeRejeicaoJsonObjectTranscribrothers",
                    (),
                    {"status_code": http.status_code, "text": trecho},
                )()
                if _http_indica_rejeicao_response_format_json_object(classe):
                    corpo_sem_fmt = dict(corpo)
                    corpo_sem_fmt.pop("response_format", None)
                    async with client.stream(
                        "POST", url_chat, headers=headers, json=corpo_sem_fmt
                    ) as http_retry:
                        if http_retry.status_code >= 400:
                            trecho_retry = (await http_retry.aread()).decode(
                                "utf-8", errors="replace"
                            )[:2000]
                            raise RuntimeError(
                                f"Chat LiteLLM em stream falhou (HTTP {http_retry.status_code}). "
                                f"URL: {url_chat}. Trecho: {trecho_retry}"
                            )
                        async for linha in http_retry.aiter_lines():
                            pedaco = extrair_delta_content_de_linha_sse_chat_completions_transcribrothers(
                                linha
                            )
                            if pedaco:
                                yield pedaco
                    return
            if http.status_code >= 400:
                trecho = (await http.aread()).decode("utf-8", errors="replace")[:2000]
                raise RuntimeError(
                    f"Chat LiteLLM em stream falhou (HTTP {http.status_code}). "
                    f"URL: {url_chat}. Trecho: {trecho}"
                )
            async for linha in http.aiter_lines():
                pedaco = extrair_delta_content_de_linha_sse_chat_completions_transcribrothers(linha)
                if pedaco:
                    yield pedaco


async def obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers(
    *,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str,
    mensagens: list[dict[str, str]],
    temperature: float,
    emitir_delta_texto: Callable[[str], Awaitable[None]] | None,
) -> str:
    if emitir_delta_texto is None:
        return await litellm_chat_completions_texto_simples_transcribrothers(
            modelo=modelo,
            api_key=api_key,
            api_base=api_base,
            httpx_verify=httpx_verify,
            mensagens=mensagens,
            temperature=temperature,
            usar_response_format_json_object=True,
        )
    try:
        bruto = await coletar_texto_chat_litellm_com_deltas_visiveis_transcribrothers(
            litellm_chat_completions_texto_simples_em_stream_transcribrothers(
                modelo=modelo,
                api_key=api_key,
                api_base=api_base,
                httpx_verify=httpx_verify,
                mensagens=mensagens,
                temperature=temperature,
                usar_response_format_json_object=True,
            ),
            emitir_delta_texto=emitir_delta_texto,
        )
        if (bruto or "").strip():
            return bruto
    except Exception:
        pass
    return await litellm_chat_completions_texto_simples_transcribrothers(
        modelo=modelo,
        api_key=api_key,
        api_base=api_base,
        httpx_verify=httpx_verify,
        mensagens=mensagens,
        temperature=temperature,
        usar_response_format_json_object=True,
    )
