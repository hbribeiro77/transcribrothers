"""Perfis de motor TTS: padrão (sagrado) vs experimental (voz), isolados para testes seguros."""

from __future__ import annotations

import math
from dataclasses import dataclass

PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = "padrao"
PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS = "experimental_voz"

CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_perfil_tts"
)
# Quantas cues TTS em paralelo (1–9; padrão 3) — padrao e experimental_voz.
# Nome histórico da chave (mantido por compatibilidade com jobs antigos).
CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_paralelismo_tts_experimental"
)
CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_temperatura_tts"
)
CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_ritmo_tts"
)
PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS = 3
PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS = 9
PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS = 1

# Temperatura TTS selecionável (UI slider 0.2–1.0, passo 0.1). Default histórico 0.4.
TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS = 0.2
TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS = 1.0
TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS = 0.1
TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = 0.4
# Aliases por perfil (fallback quando o job não grava temperatura nos steps).
TEMPERATURA_TTS_PERFIL_PADRAO_TRANSCRIBROTHERS = TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
TEMPERATURA_TTS_PERFIL_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS = (
    TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
)

# Ritmo de fala via prompt (Gemini TTS não expõe speaking_rate numérico neste fluxo).
RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS = "lento"
RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS = "normal"
RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS = "rapido"
RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS = "muito_rapido"
RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS

_IDS_RITMO_TTS_NARRACAO = frozenset(
    {
        RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
        RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
    }
)

# Linha Pace do envelope experimental.
_PACE_DIRETOR_POR_RITMO_TTS_TRANSCRIBROTHERS: dict[str, str] = {
    RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS: (
        "Ritmo deliberadamente lento e claro; pausas generosas em vírgulas e pontos; "
        "não apressar títulos nem frases longas."
    ),
    RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS: (
        "Ritmo constante e moderado; pausas naturais só em vírgulas e pontos; "
        "não acelerar em títulos nem arrastar frases longas."
    ),
    RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS: (
        "Ritmo um pouco mais ágil que o usual, ainda claro; pausas curtas; "
        "não atropelar palavras nem engolir finais."
    ),
    RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS: (
        "Ritmo acelerado e fluido; pausas mínimas; manter inteligibilidade "
        "e não soletrar."
    ),
}

# Prefixo no motor padrão (só quando ≠ normal) — tags no estilo da doc Gemini TTS.
_PREFIXO_TAG_RITMO_MOTOR_PADRAO_TTS_TRANSCRIBROTHERS: dict[str, str] = {
    RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS: "[slowly] ",
    RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS: "",
    RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS: "[fast] ",
    RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS: "[very fast] ",
}

# Envelope só no experimental: notas do diretor (consistência entre cues) + TRANSCRIPT.
# A voz de catálogo (ex.: Kore) continua em audio.voice — não inventar persona no texto.
_ENVELOPE_NOTAS_DIRETOR_TTS_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS = """\
### DIRECTOR'S NOTES
Style: Tom calmo, didático e profissional; energia estável do início ao fim; clara e acolhedora, sem drama, sem sussurro e sem entusiasmo de podcast.
Pace: {pace}
Accent: Português do Brasil, sotaque carioca leve e natural.
Breathing: Respiração discreta; não ofegar nem “atuar” a respiração.
Articulation: Pronúncia nítida; nomes e termos técnicos bem enunciados, sem soletrar.

#### TRANSCRIPT
{transcript}
"""

_IDS_PERFIS_TTS_NARRACAO = frozenset(
    {
        PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    }
)


@dataclass(frozen=True)
class OpcaoPerfilTtsNarracaoUiTranscribrothers:
    id: str
    rotulo: str
    descricao: str


@dataclass(frozen=True)
class OpcaoRitmoTtsNarracaoUiTranscribrothers:
    id: str
    rotulo: str
    descricao: str


def listar_opcoes_ritmo_tts_narracao_para_ui_transcribrothers() -> list[
    OpcaoRitmoTtsNarracaoUiTranscribrothers
]:
    return [
        OpcaoRitmoTtsNarracaoUiTranscribrothers(
            id=RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
            rotulo="Lento",
            descricao="Fala mais pausada e clara.",
        ),
        OpcaoRitmoTtsNarracaoUiTranscribrothers(
            id=RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
            rotulo="Normal (padrão)",
            descricao="Ritmo moderado do dia a dia.",
        ),
        OpcaoRitmoTtsNarracaoUiTranscribrothers(
            id=RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
            rotulo="Rápido",
            descricao="Um pouco mais ágil, ainda inteligível.",
        ),
        OpcaoRitmoTtsNarracaoUiTranscribrothers(
            id=RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
            rotulo="Muito rápido",
            descricao="Entrega acelerada; prioriza fluidez.",
        ),
    ]


def normalizar_ritmo_tts_narracao_transcribrothers(valor: object) -> str:
    """None/vazio/inválido → normal. Aceita aliases comuns."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    texto = str(valor).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "lento": RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
        "slow": RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
        "calmo": RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
        "normal": RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        "padrao": RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        "padrão": RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        "default": RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        "moderado": RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
        "rapido": RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        "rápido": RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        "fast": RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        "agil": RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        "ágil": RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
        "muito_rapido": RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
        "muito_rápido": RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
        "very_fast": RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
        "muito-rapido": RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
    }
    if texto in aliases:
        return aliases[texto]
    if texto in _IDS_RITMO_TTS_NARRACAO:
        return texto
    return RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS


def texto_pace_diretor_pelo_ritmo_tts_narracao_transcribrothers(ritmo: object) -> str:
    rid = normalizar_ritmo_tts_narracao_transcribrothers(ritmo)
    return _PACE_DIRETOR_POR_RITMO_TTS_TRANSCRIBROTHERS[
        rid
        if rid in _PACE_DIRETOR_POR_RITMO_TTS_TRANSCRIBROTHERS
        else RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS
    ]


def listar_opcoes_perfil_tts_narracao_para_ui_transcribrothers() -> list[
    OpcaoPerfilTtsNarracaoUiTranscribrothers
]:
    return [
        OpcaoPerfilTtsNarracaoUiTranscribrothers(
            id=PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
            rotulo="Padrão (estável)",
            descricao="Motor sagrado: texto puro; comportamento estável. Use no dia a dia.",
        ),
        OpcaoPerfilTtsNarracaoUiTranscribrothers(
            id=PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
            rotulo="Experimental (voz)",
            descricao=(
                "Motor isolado: notas do diretor "
                "(tom calmo estável, ritmo moderado, carioca leve). "
                "Padrão permanece texto puro."
            ),
        ),
    ]


def normalizar_perfil_tts_narracao_transcribrothers(valor: object) -> str:
    texto = str(valor or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not texto:
        return PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    aliases = {
        "padrao": PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        "padrão": PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        "default": PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        "sagrado": PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        "experimental": PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
        "experimental_voz": PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
        "exp": PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    }
    if texto in aliases:
        return aliases[texto]
    if texto in _IDS_PERFIS_TTS_NARRACAO:
        return texto
    raise ValueError(
        f"Perfil TTS «{valor}» inválido. Use "
        f"«{PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS}» ou "
        f"«{PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS}»."
    )


def rotulo_perfil_tts_narracao_para_ui_transcribrothers(perfil: object) -> str:
    try:
        pid = normalizar_perfil_tts_narracao_transcribrothers(perfil)
    except ValueError:
        pid = PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    for op in listar_opcoes_perfil_tts_narracao_para_ui_transcribrothers():
        if op.id == pid:
            return op.rotulo
    return pid


def temperatura_tts_pelo_perfil_narracao_transcribrothers(perfil: object) -> float:
    """Fallback histórico por perfil (ambos 0.4) quando não há temperatura no job."""
    pid = normalizar_perfil_tts_narracao_transcribrothers(perfil)
    if pid == PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS:
        return float(TEMPERATURA_TTS_PERFIL_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS)
    return float(TEMPERATURA_TTS_PERFIL_PADRAO_TRANSCRIBROTHERS)


def normalizar_temperatura_tts_narracao_transcribrothers(valor: object) -> float:
    """
    Clamp 0.2–1.0 e snap ao passo 0.1. None/vazio/inválido → 0.4.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return float(TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS)
    try:
        f = float(valor)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float(TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS)
    if not math.isfinite(f):
        return float(TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS)
    f = max(
        TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS,
        min(TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS, f),
    )
    passo = TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS
    # half-up (evita banker's rounding de round() em *.5)
    n = int(math.floor((f / passo) + 0.5 + 1e-9))
    return round(n * passo, 1)


def normalizar_paralelismo_tts_cues_experimental_transcribrothers(valor: object) -> int:
    """
    Paralelismo de cues TTS (padrao e experimental_voz).
    Aceita int/str; None/vazio → padrão 3. Fora de 1–9 → ValueError.
    Nome histórico da função (mantido por compatibilidade).
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS
    try:
        n = int(valor)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Paralelismo TTS inválido. Use um inteiro entre "
            f"{PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS} e "
            f"{PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS}."
        ) from exc
    if (
        n < PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS
        or n > PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS
    ):
        raise ValueError(
            "Paralelismo TTS deve estar entre "
            f"{PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS} e "
            f"{PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS} "
            f"(recebido: {n})."
        )
    return n


def montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
    perfil: object,
    texto_a_narrar: str,
    ritmo: object = None,
) -> str:
    """
    Texto enviado em messages[].content.

    Padrão (sagrado): texto a narrar; se ritmo ≠ normal, prefixa tag Gemini ([slowly]/[fast]/…).
    Experimental: DIRECTOR'S NOTES com Pace conforme ritmo + TRANSCRIPT; voz em audio.voice.
    """
    pid = normalizar_perfil_tts_narracao_transcribrothers(perfil)
    rid = normalizar_ritmo_tts_narracao_transcribrothers(ritmo)
    transcript = (texto_a_narrar or "").strip()
    if not transcript:
        return ""
    if pid == PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS:
        return _ENVELOPE_NOTAS_DIRETOR_TTS_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS.format(
            pace=texto_pace_diretor_pelo_ritmo_tts_narracao_transcribrothers(rid),
            transcript=transcript,
        )
    prefixo = _PREFIXO_TAG_RITMO_MOTOR_PADRAO_TTS_TRANSCRIBROTHERS.get(rid, "")
    return f"{prefixo}{transcript}" if prefixo else transcript
