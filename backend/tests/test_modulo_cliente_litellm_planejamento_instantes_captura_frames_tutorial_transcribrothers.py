"""Testes do planejamento de instantes de captura (parse e alinhamento aos candidatos)."""

from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    alinhar_instantes_plano_litellm_aos_candidatos_transcribrothers,
    aplicar_resultado_planejamento_com_fallback_minimo_transcribrothers,
    parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers,
)


def test_parsear_e_alinhar_instantes_aos_candidatos() -> None:
    candidatos = [12.5, 60.0, 61.0, 120.0]
    texto = '{"instantes_segundos_para_capturar":[12.4, 60.2, 999], "mensagem_resumo":"ok"}'
    parsed = parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers(texto)
    alinhados = alinhar_instantes_plano_litellm_aos_candidatos_transcribrothers(
        parsed.instantes_segundos_para_capturar,
        candidatos,
    )
    assert 12.5 in alinhados
    assert 60.0 in alinhados
    assert 999 not in alinhados
    assert len(alinhados) == 2


def test_fallback_minimo_um_candidato_quando_plano_vazio() -> None:
    candidatos = [5.0, 30.0]
    escolhidos = aplicar_resultado_planejamento_com_fallback_minimo_transcribrothers([], candidatos)
    assert escolhidos == [5.0]
