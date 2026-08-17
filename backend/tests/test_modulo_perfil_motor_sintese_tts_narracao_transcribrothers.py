"""Perfil TTS padrão vs experimental e corpos HTTP isolados."""

from __future__ import annotations

import pytest

from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    _montar_corpo_chat_completions_tts_motor_experimental_voz_transcribrothers,
    _montar_corpo_chat_completions_tts_motor_padrao_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
    RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
    RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
    RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
    TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers,
    normalizar_paralelismo_tts_cues_experimental_transcribrothers,
    normalizar_perfil_tts_narracao_transcribrothers,
    normalizar_ritmo_tts_narracao_transcribrothers,
    normalizar_temperatura_tts_narracao_transcribrothers,
    temperatura_tts_pelo_perfil_narracao_transcribrothers,
)


def test_normalizar_perfil_tts_padrao_e_aliases() -> None:
    assert (
        normalizar_perfil_tts_narracao_transcribrothers(None)
        == PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_perfil_tts_narracao_transcribrothers("padrao")
        == PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_perfil_tts_narracao_transcribrothers("experimental")
        == PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS
    )
    assert (
        normalizar_perfil_tts_narracao_transcribrothers("experimental_voz")
        == PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS
    )


def test_normalizar_perfil_tts_invalido() -> None:
    with pytest.raises(ValueError, match="inválido"):
        normalizar_perfil_tts_narracao_transcribrothers("motor_xyz")


def test_normalizar_paralelismo_tts_experimental_padrao_e_limites() -> None:
    assert (
        normalizar_paralelismo_tts_cues_experimental_transcribrothers(None)
        == PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS
    )
    assert normalizar_paralelismo_tts_cues_experimental_transcribrothers(1) == 1
    assert normalizar_paralelismo_tts_cues_experimental_transcribrothers("9") == 9
    with pytest.raises(ValueError, match="entre"):
        normalizar_paralelismo_tts_cues_experimental_transcribrothers(0)
    with pytest.raises(ValueError, match="entre"):
        normalizar_paralelismo_tts_cues_experimental_transcribrothers(10)


def test_normalizar_temperatura_tts_padrao_clamp_e_snap() -> None:
    assert (
        normalizar_temperatura_tts_narracao_transcribrothers(None)
        == TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    )
    assert normalizar_temperatura_tts_narracao_transcribrothers(0.4) == 0.4
    assert normalizar_temperatura_tts_narracao_transcribrothers(0.65) == 0.7
    assert normalizar_temperatura_tts_narracao_transcribrothers(0.1) == 0.2
    assert normalizar_temperatura_tts_narracao_transcribrothers(1.5) == 1.0
    assert normalizar_temperatura_tts_narracao_transcribrothers("0.8") == 0.8


def test_normalizar_ritmo_tts_padrao_e_aliases() -> None:
    assert (
        normalizar_ritmo_tts_narracao_transcribrothers(None)
        == RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    )
    assert normalizar_ritmo_tts_narracao_transcribrothers("normal") == RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS
    assert normalizar_ritmo_tts_narracao_transcribrothers("lento") == RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS
    assert normalizar_ritmo_tts_narracao_transcribrothers("rápido") == RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS
    assert (
        normalizar_ritmo_tts_narracao_transcribrothers("muito-rapido")
        == RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_ritmo_tts_narracao_transcribrothers("xyz")
        == RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    )


def test_motor_padrao_continua_texto_puro_e_temperatura_04() -> None:
    texto = "Remova o grupo."
    padrao = _montar_corpo_chat_completions_tts_motor_padrao_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
    )
    assert padrao["temperature"] == 0.4
    assert padrao["messages"] == [{"role": "user", "content": texto}]
    assert padrao["audio"]["voice"] == "Kore"
    assert temperatura_tts_pelo_perfil_narracao_transcribrothers("padrao") == 0.4
    override = _montar_corpo_chat_completions_tts_motor_padrao_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
        temperatura=0.7,
    )
    assert override["temperature"] == 0.7


def test_motor_experimental_usa_notas_do_diretor_e_temperatura_04() -> None:
    """Experimental diverge do padrão no envelope (doc Gemini TTS)."""
    texto = "Remova o grupo."
    experimental = _montar_corpo_chat_completions_tts_motor_experimental_voz_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
    )
    assert experimental["temperature"] == 0.4
    assert temperatura_tts_pelo_perfil_narracao_transcribrothers("experimental_voz") == 0.4
    override = _montar_corpo_chat_completions_tts_motor_experimental_voz_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
        temperatura=0.2,
    )
    assert override["temperature"] == 0.2
    content = experimental["messages"][0]["content"]
    assert content == (
        "### DIRECTOR'S NOTES\n"
        "Style: Tom calmo, didático e profissional; energia estável do início ao fim; "
        "clara e acolhedora, sem drama, sem sussurro e sem entusiasmo de podcast.\n"
        "Pace: Ritmo constante e moderado; pausas naturais só em vírgulas e pontos; "
        "não acelerar em títulos nem arrastar frases longas.\n"
        "Accent: Português do Brasil, sotaque carioca leve e natural.\n"
        "Breathing: Respiração discreta; não ofegar nem “atuar” a respiração.\n"
        "Articulation: Pronúncia nítida; nomes e termos técnicos bem enunciados, sem soletrar.\n"
        "\n"
        "#### TRANSCRIPT\n"
        f"{texto}\n"
    )
    assert "AUDIO PROFILE" not in content
    assert "Ana L" not in content
    assert (
        montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
            "padrao",
            f"  {texto}  ",
        )
        == texto
    )


def test_padrao_texto_puro_experimental_envelope_mesma_temperatura_04() -> None:
    texto = "Configure o DNS."
    padrao = _montar_corpo_chat_completions_tts_motor_padrao_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
    )
    experimental = _montar_corpo_chat_completions_tts_motor_experimental_voz_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
    )
    assert padrao["messages"] == [{"role": "user", "content": texto}]
    assert "#### TRANSCRIPT" in experimental["messages"][0]["content"]
    assert texto in experimental["messages"][0]["content"]
    assert padrao["temperature"] == experimental["temperature"] == 0.4


def test_ritmo_prefixo_no_padrao_e_pace_no_experimental() -> None:
    texto = "Remova o grupo."
    padrao_rapido = _montar_corpo_chat_completions_tts_motor_padrao_transcribrothers(
        texto=texto,
        modelo="gemini/gemini-2.5-flash-preview-tts",
        voz="Kore",
        ritmo="rapido",
    )
    assert padrao_rapido["messages"][0]["content"] == f"[fast] {texto}"
    padrao_lento = montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
        "padrao",
        texto,
        ritmo="lento",
    )
    assert padrao_lento == f"[slowly] {texto}"
    padrao_normal = montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
        "padrao",
        texto,
        ritmo="normal",
    )
    assert padrao_normal == texto
    exp_rapido = montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
        "experimental_voz",
        texto,
        ritmo="rapido",
    )
    assert "Pace: Ritmo um pouco mais ágil" in exp_rapido
    assert f"#### TRANSCRIPT\n{texto}" in exp_rapido
