"""Provedor TTS da narração: LiteLLM (Gemini) vs ElevenLabs (v4, sem turbo)."""

from __future__ import annotations

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS = "litellm"
PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS = "elevenlabs"

MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS = "eleven_v4"
MODELO_TTS_ELEVENLABS_V4_TURBO_TRANSCRIBROTHERS = "eleven_v4_turbo"

_PROVEDORES_VALIDOS = frozenset(
    {
        PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
        PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
    }
)
_MODELOS_ELEVENLABS_PERMITIDOS = frozenset({MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS})


def normalizar_provedor_tts_narracao_transcribrothers(valor: object) -> str:
    texto = str(valor or "").strip().lower()
    if not texto:
        return PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS
    if texto not in _PROVEDORES_VALIDOS:
        raise ValueError(
            f"Provedor TTS «{valor}» inválido. Use litellm ou elevenlabs."
        )
    return texto


def normalizar_modelo_tts_elevenlabs_transcribrothers(valor: object) -> str:
    texto = str(valor or "").strip()
    if not texto:
        return MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    baixo = texto.lower()
    if baixo == MODELO_TTS_ELEVENLABS_V4_TURBO_TRANSCRIBROTHERS:
        raise ValueError(
            "O modelo eleven_v4_turbo não entra neste fluxo; use eleven_v4."
        )
    if baixo not in _MODELOS_ELEVENLABS_PERMITIDOS:
        raise ValueError(
            f"Modelo ElevenLabs «{texto}» não é suportado. Use eleven_v4."
        )
    return MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS


def listar_modelos_tts_elevenlabs_para_interface_transcribrothers() -> list[str]:
    return [MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS]


def provedor_tts_parece_elevenlabs_pelo_modelo_transcribrothers(modelo: object) -> bool:
    texto = str(modelo or "").strip().lower()
    return texto.startswith("eleven_")


def tem_chave_elevenlabs_configurada_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
) -> bool:
    return bool((cfg.elevenlabs_api_key or "").strip())


def _texto_rotulo_voz_elevenlabs_transcribrothers(valor: object) -> str:
    return str(valor or "").strip()


def _texto_busca_voz_elevenlabs_transcribrothers(valor: object) -> str:
    return _texto_rotulo_voz_elevenlabs_transcribrothers(valor).lower().replace("_", "-")


def _escolher_idioma_sotaque_locale_voz_elevenlabs_transcribrothers(
    item: dict[object, object],
) -> tuple[str, str, str]:
    labels = item.get("labels")
    labels_dict = labels if isinstance(labels, dict) else {}
    idioma = _texto_rotulo_voz_elevenlabs_transcribrothers(labels_dict.get("language"))
    sotaque = _texto_rotulo_voz_elevenlabs_transcribrothers(labels_dict.get("accent"))
    locale = ""
    verificadas = item.get("verified_languages")
    if isinstance(verificadas, list):
        escolhida: dict[object, object] | None = None
        for raw in verificadas:
            if not isinstance(raw, dict):
                continue
            locale_item = _texto_busca_voz_elevenlabs_transcribrothers(raw.get("locale"))
            if locale_item in {"pt-br", "ptbr"} or locale_item.startswith("pt-br"):
                escolhida = raw
                break
            if escolhida is None:
                escolhida = raw
        if escolhida is not None:
            idioma = (
                _texto_rotulo_voz_elevenlabs_transcribrothers(escolhida.get("language")) or idioma
            )
            sotaque = (
                _texto_rotulo_voz_elevenlabs_transcribrothers(escolhida.get("accent")) or sotaque
            )
            locale = _texto_rotulo_voz_elevenlabs_transcribrothers(escolhida.get("locale"))
    return idioma, sotaque, locale


def voz_elevenlabs_parece_portugues_brasil_transcribrothers(
    *,
    idioma: str,
    sotaque: str,
    locale: str,
) -> bool:
    locale_n = _texto_busca_voz_elevenlabs_transcribrothers(locale)
    idioma_n = _texto_busca_voz_elevenlabs_transcribrothers(idioma)
    sotaque_n = _texto_busca_voz_elevenlabs_transcribrothers(sotaque)
    if "pt-br" in locale_n or locale_n == "ptbr":
        return True
    if idioma_n in {"pt-br", "ptbr"}:
        return True
    idioma_pt = idioma_n in {"pt", "portuguese", "portugues", "português"}
    sotaque_br = any(token in sotaque_n for token in ("brasil", "brazil", "brasileir"))
    return idioma_pt and sotaque_br


def extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers(
    payload: object,
) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        return []
    voices = payload.get("voices")
    if not isinstance(voices, list):
        return []
    saida: list[dict[str, object]] = []
    for item in voices:
        if not isinstance(item, dict):
            continue
        voice_id = _texto_rotulo_voz_elevenlabs_transcribrothers(item.get("voice_id"))
        if not voice_id:
            continue
        nome = _texto_rotulo_voz_elevenlabs_transcribrothers(item.get("name")) or voice_id
        idioma, sotaque, locale = _escolher_idioma_sotaque_locale_voz_elevenlabs_transcribrothers(
            item
        )
        pt_br = voz_elevenlabs_parece_portugues_brasil_transcribrothers(
            idioma=idioma,
            sotaque=sotaque,
            locale=locale,
        )
        saida.append(
            {
                "id": voice_id,
                "estilo": nome,
                "idioma": idioma,
                "sotaque": sotaque,
                "locale": locale,
                "pt_br": pt_br,
            }
        )
    saida.sort(key=lambda v: (not bool(v["pt_br"]), str(v["estilo"]).casefold(), str(v["id"])))
    return saida
