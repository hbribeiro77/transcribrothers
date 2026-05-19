from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

TRANSCRICAO_BACKEND_OPENAI_WHISPER = "openai_whisper"
TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO = "litellm_multimodal_audio"


def normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(
    endpoint: str | None,
) -> str | None:
    """Garante sufixo `/v1` na URL do proxy (rotas no formato usado pelo LiteLLM proxy, ex. `/v1/chat/completions`)."""
    raw = (endpoint or "").strip()
    if not raw:
        return None
    b = raw.rstrip("/")
    return b if b.endswith("/v1") else f"{b}/v1"


def listar_modelos_litellm_provisionados_para_interface(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> list[str]:
    """Lista para o select na UI. Se `LITELLM_MODELOS_PROVISIONADOS` estiver vazio, devolve só o padrão."""
    raw = (cfg.litellm_modelos_provisionados or "").strip()
    if not raw:
        m = (cfg.litellm_model or "").strip()
        return [m] if m else []
    return [x.strip() for x in raw.split(",") if x.strip()]


def validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    modelo_solicitado: str | None,
) -> str:
    escolha = (modelo_solicitado or "").strip() or (cfg.litellm_model or "").strip()
    if not escolha:
        raise ValueError("Nenhum modelo LiteLLM configurado (LITELLM_MODEL).")
    permitidos = listar_modelos_litellm_provisionados_para_interface(cfg)
    lista_fixa = (cfg.litellm_modelos_provisionados or "").strip()
    if lista_fixa and escolha not in permitidos:
        raise ValueError(
            "Modelo não está na lista permitida pelo servidor. "
            f"Opções: {', '.join(permitidos)}"
        )
    return escolha


def tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    """O pipeline sempre gera o tutorial via `POST …/v1/chat/completions` no proxy; exige chave + endpoint."""
    k, b = resolver_api_key_e_api_base_para_chamada_litellm(cfg)
    return bool(k and b)


def resolver_api_key_e_api_base_para_chamada_litellm(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> tuple[str | None, str | None]:
    """Chave do proxy: `LITELLM_API_KEY` (preferencial). Se vazia, usa `OPENAI_API_KEY` só como nome alternativo de env (mesmo token do proxy). Base: `LITELLM_ENDPOINT`."""
    key = (cfg.litellm_api_key or "").strip() or (cfg.openai_api_key or "").strip() or None
    base = (cfg.litellm_endpoint or "").strip().rstrip("/") or None
    return (key, base)


def tem_credencial_para_transcricao_whisper_api_openai_compativel(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    """Transcrição Whisper: proxy LiteLLM (`LITELLM_API_KEY` + `LITELLM_ENDPOINT`) ou, em instalações mistas, só chave em `OPENAI_API_KEY` apontando para API de transcrições compatível."""
    if (cfg.openai_api_key or "").strip():
        return True
    lk = (cfg.litellm_api_key or "").strip()
    lb = (cfg.litellm_endpoint or "").strip()
    return bool(lk and lb)


def normalizar_backend_transcricao_audio_configurado(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    v = (cfg.transcricao_backend or TRANSCRICAO_BACKEND_OPENAI_WHISPER).strip().lower()
    if v == TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO:
        return TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO
    return TRANSCRICAO_BACKEND_OPENAI_WHISPER


def resolver_modelo_para_transcricao_litellm_multimodal_audio(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    """Modelo gemini/... (ou outro aceito pelo gateway) para transcrição multimodal."""
    explicit = (cfg.transcricao_litellm_modelo or "").strip()
    if explicit:
        return explicit
    for m in listar_modelos_litellm_provisionados_para_interface(cfg):
        if m.lower().startswith("gemini/"):
            return m
    lm = (cfg.litellm_model or "").strip()
    if lm.lower().startswith("gemini/"):
        return lm
    return ""


def tem_credencial_para_transcricao_no_pipeline(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    if normalizar_backend_transcricao_audio_configurado(cfg) == TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO:
        lk = (cfg.litellm_api_key or "").strip()
        lb = (cfg.litellm_endpoint or "").strip()
        if not (lk and lb):
            return False
        return bool(resolver_modelo_para_transcricao_litellm_multimodal_audio(cfg))
    return tem_credencial_para_transcricao_whisper_api_openai_compativel(cfg)


def resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> tuple[str, str | None]:
    """(api_key, base_url). Preferência: `LITELLM_API_KEY` + `LITELLM_ENDPOINT` (proxy). `base_url` None só se existir `OPENAI_API_KEY` para fluxo legado com API pública de transcrições."""
    oa = (cfg.openai_api_key or "").strip()
    if oa:
        return (oa, None)
    lk = (cfg.litellm_api_key or "").strip()
    lb = (cfg.litellm_endpoint or "").strip().rstrip("/")
    if lk and lb:
        base = lb if lb.endswith("/v1") else f"{lb}/v1"
        return (lk, base)
    raise RuntimeError(
        "Sem credencial para transcrição (Whisper): defina LITELLM_API_KEY e LITELLM_ENDPOINT no proxy, "
        "ou OPENAI_API_KEY apenas se for usar o endpoint público de transcrições compatível com o SDK."
    )


def resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool | str:
    """Argumento `verify` de `httpx.AsyncClient` / TLS do cliente OpenAI: `True`, `False` ou caminho PEM."""
    ca = (cfg.litellm_ssl_ca_bundle or "").strip()
    if ca:
        p = Path(ca)
        if not p.is_file():
            raise ValueError(
                "LITELLM_SSL_CA_BUNDLE deve apontar para um arquivo PEM existente no servidor. "
                f"Caminho recebido: {ca}"
            )
        return str(p.resolve())
    if not cfg.litellm_http_verify_ssl:
        return False
    return True
