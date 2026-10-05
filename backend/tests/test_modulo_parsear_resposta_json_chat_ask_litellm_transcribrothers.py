from transcribrothers_backend.modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers import (
    parsear_resposta_json_chat_ask_litellm_transcribrothers,
)


def test_parseia_json_puro() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers(
        '{"texto":"jornada","citacoes":[{"tipo":"transcricao","rotulo":"12:40","instante_segundos":760,"heading":null}],"instantes_imagem_segundos":[760]}'
    )
    assert r.texto == "jornada"
    assert r.citacoes[0].instante_segundos == 760
    assert r.instantes_imagem_segundos == [760.0]


def test_parseia_json_dentro_de_cerca_markdown() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers(
        'veja:\n```json\n{"texto":"ok","citacoes":[],"instantes_imagem_segundos":[]}\n```'
    )
    assert r.texto == "ok"


def test_sem_json_usa_texto_bruto() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers("resposta solta")
    assert r.texto == "resposta solta"
    assert r.citacoes == []


def test_parseia_json_quando_modelo_prefixa_prosa_antes_do_objeto() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers(
        'Combinado! Vou aplicar as seis inclusões.\n\n'
        '{"texto":"Apliquei as edições combinadas.","citacoes":[],"instantes_imagem_segundos":[]}'
    )
    assert r.texto == "Apliquei as edições combinadas."
    assert r.citacoes == []
