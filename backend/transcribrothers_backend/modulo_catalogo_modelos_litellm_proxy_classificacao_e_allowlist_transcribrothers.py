"""Classifica slugs do catálogo LiteLLM (`GET /v1/models`) e cruza com a allowlist do app."""

from __future__ import annotations

from dataclasses import dataclass

CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "chat"
CATEGORIA_TTS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "tts"
CATEGORIA_STT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "stt"
CATEGORIA_EMBEDDING_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "embedding"
CATEGORIA_RERANK_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "rerank"
CATEGORIA_CODIGO_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "codigo"
CATEGORIA_ESPECIALIDADE_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "especialidade"
CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS = "alias"

_PREFIXOS_PROVEDOR_LITELLM_TRANSCRIBROTHERS = (
    "azure_ai/",
    "azure/",
    "gemini/",
    "openai/",
    "vertex_ai/",
)
_ALIASES_CURTOS_CHAT_LITELLM_TRANSCRIBROTHERS = frozenset({"opus", "fable", "haiku", "sonnet"})


@dataclass(frozen=True)
class ItemCatalogoModeloLitellmProxyTranscribrothers:
    id: str
    owned_by: str
    categoria: str
    util_para_tutorial: bool
    na_allowlist: bool


@dataclass(frozen=True)
class CatalogoModelosLitellmProxyTranscribrothers:
    modelos: list[ItemCatalogoModeloLitellmProxyTranscribrothers]
    allowlist_ausente_no_proxy: list[str]


def classificar_categoria_slug_modelo_litellm_transcribrothers(slug: str) -> str:
    s = (slug or "").strip().lower()
    if not s:
        return CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if s in _ALIASES_CURTOS_CHAT_LITELLM_TRANSCRIBROTHERS:
        return CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "-tts" in s or s.endswith("/tts") or "/tts-" in s:
        return CATEGORIA_TTS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "embed" in s:
        return CATEGORIA_EMBEDDING_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "rerank" in s:
        return CATEGORIA_RERANK_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "transcribe" in s or "transcritor" in s or "whisper" in s:
        return CATEGORIA_STT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "codex" in s or "codestral" in s:
        return CATEGORIA_CODIGO_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    if "triagem" in s:
        return CATEGORIA_ESPECIALIDADE_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
    return CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS


def extrair_ids_e_owned_by_da_resposta_openai_models_transcribrothers(
    payload: object,
) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    saida: list[tuple[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        identificador = str(item.get("id") or "").strip()
        if not identificador:
            continue
        owned = str(item.get("owned_by") or "").strip()
        saida.append((identificador, owned))
    return saida


def _slug_tem_prefixo_provedor_litellm_transcribrothers(slug: str) -> bool:
    baixo = slug.lower()
    return any(baixo.startswith(p) for p in _PREFIXOS_PROVEDOR_LITELLM_TRANSCRIBROTHERS)


def _slug_e_alias_de_versao_prefixada_no_conjunto_transcribrothers(
    slug: str,
    ids_proxy: set[str],
) -> bool:
    if _slug_tem_prefixo_provedor_litellm_transcribrothers(slug):
        return False
    baixo = slug.lower()
    for prefixo in _PREFIXOS_PROVEDOR_LITELLM_TRANSCRIBROTHERS:
        candidato = prefixo + baixo
        for existente in ids_proxy:
            if existente.lower() == candidato:
                return True
    return False


def montar_catalogo_modelos_litellm_proxy_transcribrothers(
    *,
    itens_proxy: list[tuple[str, str]],
    allowlist: list[str],
) -> CatalogoModelosLitellmProxyTranscribrothers:
    ids_proxy = {identificador for identificador, _ in itens_proxy if identificador.strip()}
    allow_norm = [a.strip() for a in allowlist if (a or "").strip()]
    allow_set = {a.lower() for a in allow_norm}
    ids_proxy_lower = {i.lower() for i in ids_proxy}

    modelos: list[ItemCatalogoModeloLitellmProxyTranscribrothers] = []
    for identificador, owned_by in itens_proxy:
        slug = (identificador or "").strip()
        if not slug:
            continue
        categoria = classificar_categoria_slug_modelo_litellm_transcribrothers(slug)
        if categoria == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS and (
            _slug_e_alias_de_versao_prefixada_no_conjunto_transcribrothers(slug, ids_proxy)
        ):
            categoria = CATEGORIA_ALIAS_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
        util = categoria == CATEGORIA_CHAT_SLUG_MODELO_LITELLM_TRANSCRIBROTHERS
        modelos.append(
            ItemCatalogoModeloLitellmProxyTranscribrothers(
                id=slug,
                owned_by=(owned_by or "").strip(),
                categoria=categoria,
                util_para_tutorial=util,
                na_allowlist=slug.lower() in allow_set,
            )
        )

    ausentes = [a for a in allow_norm if a.lower() not in ids_proxy_lower]
    return CatalogoModelosLitellmProxyTranscribrothers(
        modelos=modelos,
        allowlist_ausente_no_proxy=ausentes,
    )
