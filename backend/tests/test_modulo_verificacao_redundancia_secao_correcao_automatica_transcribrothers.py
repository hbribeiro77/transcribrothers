from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
    deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers,
)


def test_deve_corrigir_quando_redundancia_e_habilitado():
    assert deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
        {"sucesso": True, "classificacao_global": "redundancia"},
        correcao_automatica_habilitada=True,
        correcao_automatica_incluir_classificacao_atencao=False,
    )


def test_nao_corrigir_quando_ok():
    assert not deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
        {"sucesso": True, "classificacao_global": "ok"},
        correcao_automatica_habilitada=True,
        correcao_automatica_incluir_classificacao_atencao=False,
    )


def test_atencao_so_se_flag_ligada():
    assert deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
        {"sucesso": True, "classificacao_global": "atencao"},
        correcao_automatica_habilitada=True,
        correcao_automatica_incluir_classificacao_atencao=True,
    )


def test_nao_corrigir_quando_correcao_desligada():
    assert not deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
        {"sucesso": True, "classificacao_global": "redundancia"},
        correcao_automatica_habilitada=False,
        correcao_automatica_incluir_classificacao_atencao=True,
    )
