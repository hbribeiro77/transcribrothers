"""Diretriz de conteúdo das legendas (presets da limpeza IA)."""

from __future__ import annotations

from transcribrothers_backend.modulo_diretriz_conteudo_legendas_narracao_transcribrothers import (
    DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
    DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
    diretriz_conteudo_permite_reescrever_texto_transcribrothers,
    limites_crescimento_guarda_limpeza_pela_diretriz_transcribrothers,
    listar_opcoes_diretriz_conteudo_legendas_para_ui_transcribrothers,
    normalizar_diretriz_conteudo_legendas_transcribrothers,
    texto_extra_prompt_limpeza_pela_diretriz_conteudo_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    _montar_mensagens_limpeza_cues_transcribrothers,
    texto_limpo_ia_e_aceitavel_contra_original_transcribrothers,
)


def test_normalizar_diretriz_padrao_e_aliases() -> None:
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers(None)
        == DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers("conservador")
        == DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS
    )
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers("mais-falavel")
        == DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS
    )
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers("didático")
        == DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers("descontraído")
        == DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS
    )
    assert (
        normalizar_diretriz_conteudo_legendas_transcribrothers("xyz")
        == DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS
    )


def test_texto_extra_prompt_vazio_no_conservador_e_forte_nos_outros() -> None:
    assert texto_extra_prompt_limpeza_pela_diretriz_conteudo_legendas_transcribrothers(
        "conservador"
    ) == ""
    falavel = texto_extra_prompt_limpeza_pela_diretriz_conteudo_legendas_transcribrothers(
        "mais_falavel"
    )
    assert "DIRETRIZ ATIVA: mais falável" in falavel
    assert "Agora vamos ver" in falavel
    assert "DIRETRIZ ATIVA: mais descontraído" in (
        texto_extra_prompt_limpeza_pela_diretriz_conteudo_legendas_transcribrothers(
            "mais_descontraido"
        )
    )


def test_montar_mensagens_limpeza_anexa_diretriz_e_pede_reescrever() -> None:
    msgs_padrao = _montar_mensagens_limpeza_cues_transcribrothers(["Olá."])
    msgs_falavel = _montar_mensagens_limpeza_cues_transcribrothers(
        ["Olá."],
        diretriz_conteudo="mais_falavel",
    )
    assert "DIRETRIZ ATIVA" not in msgs_padrao[0]["content"]
    assert "DIRETRIZ ATIVA: mais falável" in msgs_falavel[0]["content"]
    assert "reescreva o texto conforme o tom pedido" in msgs_falavel[1]["content"]
    assert "reescreva o texto conforme o tom pedido" not in msgs_padrao[1]["content"]


def test_guarda_aceita_expansao_maior_com_preset_reescrita() -> None:
    original = "Validação de Nome Social"
    # Crescimento > 48 chars: rejeitado no conservador; aceito no mais_falavel.
    proposto = (
        "Agora vamos ver a validação de nome social no portal, "
        "neste passo do tutorial de forma clara."
    )
    assert len(proposto) - len(original) > 48
    assert not texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
        original,
        proposto,
        diretriz_conteudo="conservador",
    )
    assert texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
        original,
        proposto,
        diretriz_conteudo="mais_falavel",
    )
    assert diretriz_conteudo_permite_reescrever_texto_transcribrothers("mais_descontraido")
    rel, abs_chars = limites_crescimento_guarda_limpeza_pela_diretriz_transcribrothers(
        "mais_descontraido"
    )
    assert rel >= 1.0
    assert abs_chars >= 100


def test_listar_opcoes_ui_quatro_presets() -> None:
    ids = [o.id for o in listar_opcoes_diretriz_conteudo_legendas_para_ui_transcribrothers()]
    assert ids == [
        DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    ]
