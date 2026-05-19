"""Testes do parser tolerante de JSON na resposta do modelo de transcrição multimodal."""

import json

from unittest.mock import MagicMock

import pytest

from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    _colapsar_repeticao_palavra_consecutiva_em_texto_segmento_transcricao,
    _extrair_json_do_texto_resposta_llm,
    _extrair_objeto_transcricao_de_json_possivelmente_truncado,
    _http_indica_rejeicao_response_format_json_object,
)


def test_http_indica_retry_quando_corpo_menciona_response_format() -> None:
    r = MagicMock()
    r.status_code = 400
    r.text = "Unknown parameter: response_format"
    assert _http_indica_rejeicao_response_format_json_object(r) is True


def test_http_indica_retry_json_object_no_texto() -> None:
    r = MagicMock()
    r.status_code = 422
    r.text = "model does not support json_object mode"
    assert _http_indica_rejeicao_response_format_json_object(r) is True


def test_http_nao_indica_retry_erro_generico() -> None:
    r = MagicMock()
    r.status_code = 400
    r.text = "invalid_api_key"
    assert _http_indica_rejeicao_response_format_json_object(r) is False


def test_http_nao_indica_retry_401() -> None:
    r = MagicMock()
    r.status_code = 401
    r.text = "response_format blah"
    assert _http_indica_rejeicao_response_format_json_object(r) is False


def test_parse_json_transcricao_valido_minimo() -> None:
    raw = '{"idioma":"pt","segmentos":[{"inicio_segundos":0,"fim_segundos":1,"texto":"ok"}]}'
    obj = _extrair_json_do_texto_resposta_llm(raw)
    assert obj["idioma"] == "pt"
    assert len(obj["segmentos"]) == 1


def test_parse_json_com_quebra_de_linha_literal_dentro_de_texto() -> None:
    # json.loads puro falharia; o normalizador escapa dentro da string.
    raw = (
        '{"idioma":"pt","segmentos":[{"inicio_segundos":0,"fim_segundos":2,'
        '"texto":"primeira linha\nsegunda linha"}]}'
    )
    with pytest.raises(json.JSONDecodeError):
        json.loads(raw)
    obj = _extrair_json_do_texto_resposta_llm(raw)
    assert "primeira linha" in obj["segmentos"][0]["texto"]
    assert "segunda linha" in obj["segmentos"][0]["texto"]


def test_parse_json_com_virgula_final_e_texto_extra() -> None:
    raw = 'Aqui está:\n{"idioma":"pt","segmentos":[],}\nFim.'
    obj = _extrair_json_do_texto_resposta_llm(raw)
    assert obj["segmentos"] == []


def test_parse_json_em_bloco_markdown() -> None:
    raw = '```json\n{"idioma":"pt","segmentos":[]}\n```'
    obj = _extrair_json_do_texto_resposta_llm(raw)
    assert obj["idioma"] == "pt"


def test_colapsar_repeticao_palavra_nao_em_loop() -> None:
    texto = "não" + ", não" * 18
    out = _colapsar_repeticao_palavra_consecutiva_em_texto_segmento_transcricao(texto)
    assert out == "não"


def test_recupera_segmentos_completos_de_json_truncado() -> None:
    raw = (
        '{"idioma":"pt","segmentos":['
        '{"inicio_segundos":0.0,"fim_segundos":3.5,"texto":"primeira frase."},'
        '{"inicio_segundos":4.5,"fim_segundos":10.0,"texto":"segunda frase."},'
        '{"inicio_segundos":17.0,"fim_segundos":26.0,"texto":"terceira, '
    )
    obj = _extrair_objeto_transcricao_de_json_possivelmente_truncado(raw)
    assert obj is not None
    assert len(obj["segmentos"]) == 2
    assert obj["segmentos"][0]["texto"] == "primeira frase."


def test_parse_json_truncado_via_extracao_segmentos_completos() -> None:
    raw = (
        '{"idioma":"pt","segmentos":['
        '{"inicio_segundos":0.0,"fim_segundos":3.5,"texto":"ok um."},'
        '{"inicio_segundos":4.0,"fim_segundos":8.0,"texto":"ok dois."},'
        '{"inicio_segundos":9.0,"fim_segundos":12.0,"texto":"não, não, não, não, não, não, não, não, não, não, não, não'
    )
    obj = _extrair_json_do_texto_resposta_llm(raw)
    assert len(obj["segmentos"]) == 2
    assert obj["segmentos"][1]["texto"] == "ok dois."
