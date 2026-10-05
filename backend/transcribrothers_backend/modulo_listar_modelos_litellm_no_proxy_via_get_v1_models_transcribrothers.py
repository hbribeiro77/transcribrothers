"""Lista modelos no proxy LiteLLM via GET /v1/models (sem expor a chave ao navegador)."""

from __future__ import annotations

import httpx

from transcribrothers_backend.modulo_catalogo_modelos_litellm_proxy_classificacao_e_allowlist_transcribrothers import (
    CatalogoModelosLitellmProxyTranscribrothers,
    extrair_ids_e_owned_by_da_resposta_openai_models_transcribrothers,
    montar_catalogo_modelos_litellm_proxy_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)

_TIMEOUT_CONNECT_SEGUNDOS = 5.0
_TIMEOUT_READ_SEGUNDOS = 20.0


class FalhaListarModelosLitellmProxyTranscribrothers(Exception):
    """Falha ao consultar o catálogo do proxy (credencial, rede ou HTTP)."""


async def obter_catalogo_modelos_litellm_no_proxy_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    allowlist: list[str],
) -> CatalogoModelosLitellmProxyTranscribrothers:
    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        raise FalhaListarModelosLitellmProxyTranscribrothers(
            "Proxy LiteLLM não configurado no servidor "
            "(defina LITELLM_API_KEY e LITELLM_ENDPOINT)."
        )

    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise FalhaListarModelosLitellmProxyTranscribrothers("LITELLM_ENDPOINT inválido no servidor.")

    url_models = f"{base_v1}/models"
    timeout = httpx.Timeout(
        connect=_TIMEOUT_CONNECT_SEGUNDOS,
        read=_TIMEOUT_READ_SEGUNDOS,
        write=_TIMEOUT_READ_SEGUNDOS,
        pool=_TIMEOUT_CONNECT_SEGUNDOS,
    )
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
            http = await client.get(url_models, headers=headers)
    except httpx.TimeoutException as exc:
        raise FalhaListarModelosLitellmProxyTranscribrothers(
            f"Tempo esgotado ao listar modelos no proxy (limite {_TIMEOUT_READ_SEGUNDOS:.0f}s)."
        ) from exc
    except httpx.HTTPError as exc:
        raise FalhaListarModelosLitellmProxyTranscribrothers(
            f"Falha de rede ao chamar o proxy: {exc}"
        ) from exc

    if http.status_code >= 400:
        trecho = (http.text or "").strip().replace("\n", " ")[:300]
        detalhe = f" — {trecho}" if trecho else ""
        raise FalhaListarModelosLitellmProxyTranscribrothers(
            f"O proxy recusou a listagem de modelos (HTTP {http.status_code}){detalhe}"
        )

    try:
        payload = http.json()
    except ValueError as exc:
        raise FalhaListarModelosLitellmProxyTranscribrothers(
            "O proxy respondeu, mas o JSON de /v1/models foi inválido."
        ) from exc

    itens = extrair_ids_e_owned_by_da_resposta_openai_models_transcribrothers(payload)
    return montar_catalogo_modelos_litellm_proxy_transcribrothers(
        itens_proxy=itens,
        allowlist=allowlist,
    )
