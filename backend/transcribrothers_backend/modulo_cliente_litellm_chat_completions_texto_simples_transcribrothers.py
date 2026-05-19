from __future__ import annotations

from typing import Any

import httpx

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    extrair_texto_resposta_message_openai_compat_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    _http_indica_rejeicao_response_format_json_object,
)
from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
    registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
    resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers,
)


async def litellm_chat_completions_texto_simples_transcribrothers(
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
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    log_etapa: str = "",
    log_resumo_pedido: str = "",
    log_metadados: dict[str, Any] | None = None,
    log_incluir_detalhe_resposta: bool = True,
) -> str:
    """
    POST /v1/chat/completions com `messages` só texto (role/content strings).
    """
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
    corpo: dict = {
        "model": modelo.strip(),
        "messages": mensagens,
        "temperature": float(temperature),
    }
    headers = {
        "Authorization": f"Bearer {chave}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(
        connect=max(5.0, float(httpx_timeout_connect_segundos)),
        read=max(60.0, float(httpx_timeout_read_segundos)),
        write=max(60.0, float(httpx_timeout_read_segundos)),
        pool=max(5.0, float(httpx_timeout_connect_segundos)),
    )

    def _registrar_log(*, sucesso: bool, resumo: str, detalhe: str | None = None) -> None:
        if steps_para_log_decisoes_ia is None:
            return
        meta = dict(log_metadados or {})
        if log_resumo_pedido.strip():
            meta.setdefault("pedido_resumo", log_resumo_pedido.strip()[:300])
        registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
            steps_para_log_decisoes_ia,
            etapa=log_etapa or "chat_completions",
            resumo=resumo,
            detalhe=detalhe,
            modelo=modelo,
            sucesso=sucesso,
            metadados=meta or None,
        )

    try:
        async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
            if usar_response_format_json_object:
                http = await client.post(
                    url_chat,
                    headers=headers,
                    json={**corpo, "response_format": {"type": "json_object"}},
                )
                if not http.is_success and _http_indica_rejeicao_response_format_json_object(http):
                    http = await client.post(url_chat, headers=headers, json=corpo)
            else:
                http = await client.post(url_chat, headers=headers, json=corpo)

        if http.status_code >= 400:
            trecho = (http.text or "")[:2000]
            _registrar_log(sucesso=False, resumo=f"HTTP {http.status_code} no chat", detalhe=trecho)
            raise RuntimeError(
                f"Chat LiteLLM falhou (HTTP {http.status_code}). URL: {url_chat}. Trecho: {trecho}"
            )
        body = http.json()
        try:
            choice = body["choices"][0]["message"]
            conteudo = extrair_texto_resposta_message_openai_compat_transcribrothers(choice)
        except (KeyError, IndexError, TypeError) as exc:
            _registrar_log(sucesso=False, resumo="Resposta inesperada do gateway", detalhe=repr(body)[:2000])
            raise RuntimeError(f"Resposta inesperada do gateway no chat: {body!r}") from exc
        if not isinstance(conteudo, str) or not conteudo.strip():
            _registrar_log(sucesso=False, resumo="Conteúdo vazio devolvido pelo modelo")
            raise RuntimeError("O modelo devolveu conteúdo vazio no chat.")
        texto = conteudo.strip()
        _registrar_log(
            sucesso=True,
            resumo=resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers(texto),
            detalhe=texto if log_incluir_detalhe_resposta else None,
        )
        return texto
    except RuntimeError:
        raise
    except Exception as exc:
        _registrar_log(sucesso=False, resumo=f"Erro: {type(exc).__name__}", detalhe=str(exc)[:2000])
        raise
