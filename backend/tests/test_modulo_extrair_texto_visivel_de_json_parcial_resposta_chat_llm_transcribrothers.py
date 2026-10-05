from transcribrothers_backend.modulo_extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers import (
    extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers,
)


def test_sem_campo_texto_ainda_devolve_vazio() -> None:
    assert extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers('{"citacoes":[') == ""


def test_extrai_prefixo_enquanto_a_string_texto_ainda_abre() -> None:
    assert (
        extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers(
            '{"texto":"Olá **mun'
        )
        == "Olá **mun"
    )


def test_desescapa_quebra_de_linha_completa_e_ignora_escape_incompleto() -> None:
    assert (
        extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers(
            '{"texto":"linha1\\nlinha2\\'
        )
        == "linha1\nlinha2"
    )


def test_texto_completo_mesmo_com_prosa_antes_do_objeto() -> None:
    bruto = 'Combinado!\n\n{"texto":"Apliquei as **edições**.","executar":true}'
    assert (
        extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers(bruto)
        == "Apliquei as **edições**."
    )
