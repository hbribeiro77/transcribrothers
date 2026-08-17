"""Guarda-corpo e merge da preparação IA de textos de cues (sem chamar o proxy)."""

from __future__ import annotations

import pytest

from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers,
    texto_limpo_ia_e_aceitavel_contra_original_transcribrothers,
)


def test_aceita_remover_lixo_de_borda() -> None:
    original = ")., triagem com IA e redesenho de interfaces foram os focos principais."
    proposto = "triagem com IA e redesenho de interfaces foram os focos principais."
    assert texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(original, proposto)


def test_aceita_adaptacao_narravel_curta_rotulo_com_dois_pontos() -> None:
    assert texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
        "Remova o grupo:",
        "Remova o grupo.",
    )
    assert texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
        "Não é Nome Social:",
        "Não é nome social.",
    )


def test_rejeita_vazio_e_encolhimento_agressivo() -> None:
    assert not texto_limpo_ia_e_aceitavel_contra_original_transcribrothers("frase longa aqui", "")
    assert not texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
        "O usuário pode selecionar até 25 intimações por vez para distribuição em lote",
        "ok",
    )


def test_mesclar_aplica_limpeza_e_mantem_rejeitados() -> None:
    originais = [
        ")., triagem com IA.",
        "texto bom",
        "lote [01:49](",
    ]
    resposta = {
        "cues": [
            {"indice": 0, "texto": "triagem com IA."},
            {"indice": 1, "texto": "texto bom"},
            {"indice": 2, "texto": "lote"},
        ]
    }
    finais, alterados, rejeitados = mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
        originais,
        resposta,
    )
    assert finais[0] == "triagem com IA."
    assert finais[1] == "texto bom"
    assert finais[2] == "lote"
    assert alterados == [0, 2]
    assert rejeitados == []


def test_mesclar_aceita_adaptacao_narravel_moderada() -> None:
    originais = ["Remova o grupo:", "frase ok"]
    resposta = {
        "cues": [
            {"indice": 0, "texto": "Remova o grupo."},
            {"indice": 1, "texto": "frase ok"},
        ]
    }
    finais, alterados, rejeitados = mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
        originais,
        resposta,
    )
    assert finais[0] == "Remova o grupo."
    assert finais[1] == "frase ok"
    assert alterados == [0]
    assert rejeitados == []


def test_mesclar_guarda_rejeita_reescrever_demais() -> None:
    originais = ["frase original razoavelmente longa para teste"]
    resposta = {
        "cues": [
            {
                "indice": 0,
                "texto": (
                    "Esta é uma reescrita completa e muito mais longa do que o original "
                    "com vários detalhes inventados pela IA sem necessidade."
                ),
            }
        ]
    }
    finais, alterados, rejeitados = mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
        originais,
        resposta,
    )
    assert finais[0] == originais[0]
    assert alterados == []
    assert rejeitados == [0]


def test_mesclar_exige_mesma_quantidade() -> None:
    with pytest.raises(ValueError, match="Quantidade"):
        mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
            ["a", "b"],
            {"cues": [{"indice": 0, "texto": "a"}]},
        )


def test_mesclar_aceita_json_em_fence() -> None:
    originais = ["x [01:49]("]
    bruto = '```json\n{"cues":[{"indice":0,"texto":"x"}]}\n```'
    finais, alterados, _rej = mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
        originais,
        bruto,
    )
    assert finais[0] == "x"
    assert alterados == [0]
