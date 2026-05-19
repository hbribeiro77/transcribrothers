"""Testes da formatação de mensagem de erro HTTP (504 nginx) na transcrição multimodal."""

from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    _mensagem_runtime_erro_http_gateway_transcricao_multimodal,
    _trecho_corpo_http_gateway_para_mensagem_erro_transcricao_multimodal,
)


def test_trecho_html_nginx_extrai_titulo() -> None:
    html = "<html><head><title>504 Gateway Time-out</title></head><body>...</body></html>"
    t = _trecho_corpo_http_gateway_para_mensagem_erro_transcricao_multimodal(html)
    assert "504" in t
    assert "Gateway" in t


def test_mensagem_504_menciona_proxy_read_timeout_e_httpx() -> None:
    msg = _mensagem_runtime_erro_http_gateway_transcricao_multimodal(
        status_code=504,
        url="https://exemplo/v1/chat/completions",
        corpo="<html><title>504 Gateway Time-out</title></html>",
        httpx_timeout_read_segundos=7200.0,
    )
    assert "504" in msg
    assert "proxy_read_timeout" in msg
    assert "7200" in msg
    assert "JANELA" in msg or "janela" in msg
