import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
    listar_modelos_litellm_provisionados_para_interface,
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
    tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy,
    resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
    tem_credencial_para_transcricao_no_pipeline,
    tem_credencial_para_transcricao_whisper_api_openai_compativel,
    validar_e_resolver_modelo_litellm_solicitado_pelo_cliente,
)


def test_lista_vazia_usa_modelo_padrao() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_model="openai/gpt-4o-mini",
        litellm_modelos_provisionados="",
    )
    assert listar_modelos_litellm_provisionados_para_interface(cfg) == ["openai/gpt-4o-mini"]


def test_lista_csv() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_model="openai/gpt-4o-mini",
        litellm_modelos_provisionados="modelo/a, modelo/b",
    )
    assert listar_modelos_litellm_provisionados_para_interface(cfg) == ["modelo/a", "modelo/b"]


def test_whitelist_rejeita_modelo_fora_da_lista() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_model="openai/gpt-4o-mini",
        litellm_modelos_provisionados="openai/gpt-4o-mini,openai/gpt-4o",
    )
    with pytest.raises(ValueError):
        validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(cfg, "outro/modelo")


def test_sem_lista_aceita_modelo_livre() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_model="openai/gpt-4o-mini",
        litellm_modelos_provisionados="",
    )
    assert (
        validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(cfg, "provedor/meu-modelo")
        == "provedor/meu-modelo"
    )


def test_credenciais_litellm_key_prioridade() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="k-litellm",
        openai_api_key="k-openai",
        litellm_endpoint="https://proxy.example/v1",
    )
    k, b = resolver_api_key_e_api_base_para_chamada_litellm(cfg)
    assert k == "k-litellm"
    assert b == "https://proxy.example/v1"


def test_credenciais_fallback_openai_key() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        litellm_api_key="",
        openai_api_key="k-openai",
        litellm_endpoint="",
    )
    k, b = resolver_api_key_e_api_base_para_chamada_litellm(cfg)
    assert k == "k-openai"
    assert b is None


def test_tem_credencial_whisper_so_openai() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(openai_api_key="x", litellm_api_key="", litellm_endpoint="")
    assert tem_credencial_para_transcricao_whisper_api_openai_compativel(cfg) is True


def test_tem_credencial_whisper_litellm_mais_endpoint() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        openai_api_key="",
        litellm_api_key="k",
        litellm_endpoint="https://gw.example/",
    )
    assert tem_credencial_para_transcricao_whisper_api_openai_compativel(cfg) is True


def test_resolver_whisper_gateway_adiciona_v1() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        openai_api_key="",
        litellm_api_key="k",
        litellm_endpoint="https://gw.example",
    )
    key, base = resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel(cfg)
    assert key == "k"
    assert base == "https://gw.example/v1"


def test_resolver_whisper_prioridade_openai() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        openai_api_key="oa",
        litellm_api_key="lk",
        litellm_endpoint="https://gw.example",
    )
    key, base = resolver_api_key_e_base_url_para_transcricao_whisper_api_openai_compativel(cfg)
    assert key == "oa"
    assert base is None


def test_resolver_modelo_multimodal_explicito() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        transcricao_litellm_modelo="gemini/gemini-3-flash-preview",
    )
    assert resolver_modelo_para_transcricao_litellm_multimodal_audio(cfg) == "gemini/gemini-3-flash-preview"


def test_resolver_modelo_multimodal_primeiro_gemini_na_lista() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        transcricao_litellm_modelo="",
        litellm_modelos_provisionados="azure_ai/claude-haiku-4-5,gemini/gemini-3.1-flash-lite-preview",
    )
    assert (
        resolver_modelo_para_transcricao_litellm_multimodal_audio(cfg)
        == "gemini/gemini-3.1-flash-lite-preview"
    )


def test_tem_credencial_pipeline_multimodal_ok() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        transcricao_backend=TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
        litellm_api_key="k",
        litellm_endpoint="https://gw/",
        transcricao_litellm_modelo="gemini/gemini-3-pro-preview",
        openai_api_key="",
    )
    assert tem_credencial_para_transcricao_no_pipeline(cfg) is True


def test_tem_credencial_pipeline_multimodal_sem_modelo_gemini() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(
        transcricao_backend=TRANSCRICAO_BACKEND_LITELLM_MULTIMODAL_AUDIO,
        litellm_api_key="k",
        litellm_endpoint="https://gw/",
        transcricao_litellm_modelo="",
        litellm_modelos_provisionados="azure_ai/claude-haiku-4-5",
        litellm_model="azure_ai/claude-opus-4-6",
        openai_api_key="",
    )
    assert tem_credencial_para_transcricao_no_pipeline(cfg) is False


def test_tem_credencial_gateway_litellm_para_tutorial_exige_endpoint() -> None:
    assert tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(
        ConfiguracaoAmbienteTranscribrothers(
            litellm_api_key="k",
            litellm_endpoint="https://gw/",
        )
    )
    assert not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(
        ConfiguracaoAmbienteTranscribrothers(
            litellm_api_key="",
            litellm_endpoint="",
            openai_api_key="só-chave-sem-proxy",
        )
    )


def test_resolver_parametro_httpx_verify_ssl_desligado() -> None:
    cfg = ConfiguracaoAmbienteTranscribrothers(litellm_http_verify_ssl=False)
    assert resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(cfg) is False


def test_resolver_parametro_httpx_verify_ssl_ca_bundle(tmp_path) -> None:
    pem = tmp_path / "ca-interna.pem"
    pem.write_text("-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----\n", encoding="utf-8")
    cfg = ConfiguracaoAmbienteTranscribrothers(litellm_ssl_ca_bundle=str(pem))
    assert resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(cfg) == str(pem.resolve())


def test_normalizar_endpoint_litellm_para_base_url_openai_v1() -> None:
    assert normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(None) is None
    assert normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1("") is None
    assert normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1("https://gw/") == "https://gw/v1"
    assert normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1("https://gw/v1") == "https://gw/v1"
    assert normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1("https://gw/v1/") == "https://gw/v1"
