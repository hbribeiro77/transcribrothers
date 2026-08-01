"""Filtro de trechos não narráveis para TTS."""

from __future__ import annotations

from transcribrothers_backend.modulo_util_filtrar_trechos_narraveis_para_tts_transcribrothers import (
    filtrar_trechos_narraveis_para_tts_transcribrothers,
    texto_e_narravel_para_tts_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)


def test_rejeita_pontuacao_solta_e_lista_estilo_numero_ponto() -> None:
    assert texto_e_narravel_para_tts_transcribrothers(").") is False
    assert texto_e_narravel_para_tts_transcribrothers("2).") is False
    assert texto_e_narravel_para_tts_transcribrothers("…") is False
    assert texto_e_narravel_para_tts_transcribrothers("Clique em salvar.") is True


def test_filtrar_separa_narraveis_e_descartados() -> None:
    ok, lixo = filtrar_trechos_narraveis_para_tts_transcribrothers(
        ["Clique aqui.", ").", "Abra o menu.", "1)."]
    )
    assert ok == ["Clique aqui.", "Abra o menu."]
    assert ")." in lixo
    assert "1)." in lixo


def test_partir_frases_descarta_lixo_pontuacao() -> None:
    frases = partir_texto_plano_em_frases_para_legendas_transcribrothers(
        "Clique em salvar.\n).\nAbra o menu."
    )
    assert all(texto_e_narravel_para_tts_transcribrothers(f) for f in frases)
    assert not any(f.strip() == ")." for f in frases)
