"""Classifica slugs do GET /v1/models e cruza com a allowlist do Transcribrothers."""

from transcribrothers_backend.modulo_catalogo_modelos_litellm_proxy_classificacao_e_allowlist_transcribrothers import (
    CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_CODIGO_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_EMBEDDING_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_ESPECIALIDADE_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_RERANK_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_STT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    CATEGORIA_TTS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS,
    classificar_categoria_slug_modelo_litellm_transcribrothers,
    extrair_ids_e_owned_by_da_resposta_openai_models_transcribrothers,
    montar_catalogo_modelos_litellm_proxy_transcribrothers,
)


def test_classifica_tts_stt_embed_rerank_codigo_e_especialidade_pelo_slug() -> None:
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers(
            "gemini/gemini-2.5-flash-preview-tts"
        )
        == CATEGORIA_TTS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("azure/gpt-4o-mini-transcribe")
        == CATEGORIA_STT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("transcritor")
        == CATEGORIA_STT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("azure_ai/embed-v-4-0")
        == CATEGORIA_EMBEDDING_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("cohere-rerank-v4.0-pro")
        == CATEGORIA_RERANK_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("azure/gpt-5.3-codex")
        == CATEGORIA_CODIGO_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("codestral-2501")
        == CATEGORIA_CODIGO_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("triagem-de-intimacoes")
        == CATEGORIA_ESPECIALIDADE_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )


def test_classifica_gemini_e_claude_como_chat() -> None:
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("gemini/gemini-3.8-flash")
        == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("azure_ai/claude-sonnet-5")
        == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        classificar_categoria_slug_modelo_litellm_transcribrothers("FW-GLM-5.3")
        == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    )


def test_extrai_ids_da_resposta_openai_models_e_ignora_vazios() -> None:
    itens = extrair_ids_e_owned_by_da_resposta_openai_models_transcribrothers(
        {
            "object": "list",
            "data": [
                {"id": "gemini/gemini-3.8-flash", "owned_by": "openai"},
                {"id": "  "},
                "nao-dict",
                {"id": "azure_ai/claude-sonnet-5", "owned_by": "azure"},
            ],
        }
    )
    assert itens == [
        ("gemini/gemini-3.8-flash", "openai"),
        ("azure_ai/claude-sonnet-5", "azure"),
    ]


def test_catalogo_marca_alias_prefixado_e_alias_curto_como_nao_uteis_para_tutorial() -> None:
    catalogo = montar_catalogo_modelos_litellm_proxy_transcribrothers(
        itens_proxy=[
            ("Kimi-K2.6", "openai"),
            ("azure_ai/Kimi-K2.6", "openai"),
            ("opus", "openai"),
            ("azure_ai/claude-opus-5", "openai"),
        ],
        allowlist=["azure_ai/Kimi-K2.6"],
    )
    por_id = {m.id: m for m in catalogo.modelos}
    assert por_id["azure_ai/Kimi-K2.6"].util_para_tutorial is True
    assert por_id["azure_ai/Kimi-K2.6"].na_allowlist is True
    assert por_id["azure_ai/Kimi-K2.6"].categoria == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    assert por_id["Kimi-K2.6"].util_para_tutorial is False
    assert por_id["Kimi-K2.6"].categoria == CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    assert por_id["opus"].util_para_tutorial is False
    assert por_id["opus"].categoria == CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    assert por_id["azure_ai/claude-opus-5"].util_para_tutorial is True
    assert por_id["azure_ai/claude-opus-5"].na_allowlist is False


def test_catalogo_lista_allowlist_ausente_no_proxy_e_nao_marca_tts_como_util_tutorial() -> None:
    catalogo = montar_catalogo_modelos_litellm_proxy_transcribrothers(
        itens_proxy=[
            ("gemini/gemini-3.1-flash-lite", "openai"),
            ("gemini/gemini-2.5-flash-preview-tts", "openai"),
        ],
        allowlist=[
            "gemini/gemini-3.1-flash-lite",
            "gemini/gemini-3-pro-preview",
            "glm-5.2",
        ],
    )
    por_id = {m.id: m for m in catalogo.modelos}
    assert por_id["gemini/gemini-2.5-flash-preview-tts"].util_para_tutorial is False
    assert por_id["gemini/gemini-2.5-flash-preview-tts"].categoria == CATEGORIA_TTS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    assert catalogo.allowlist_ausente_no_proxy == [
        "gemini/gemini-3-pro-preview",
        "glm-5.2",
    ]
