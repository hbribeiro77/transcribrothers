from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    _duracao_de_tags_formato_ffprobe_transcribrothers,
    _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers,
    _parsear_duracao_tag_sexagesimal_ffprobe_transcribrothers,
)


def test_extrai_duracao_do_formato_quando_presente() -> None:
    data = {"format": {"duration": "125.5"}, "streams": []}
    assert _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers(data) == 125.5


def test_extrai_duracao_do_stream_video_quando_formato_sem_duracao() -> None:
    data = {
        "format": {},
        "streams": [
            {"codec_type": "audio", "duration": "10.0"},
            {"codec_type": "video", "duration": "42.25"},
        ],
    }
    assert _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers(data) == 42.25


def test_extrai_duracao_de_qualquer_stream_como_fallback() -> None:
    data = {
        "format": {},
        "streams": [{"codec_type": "audio", "duration": "7.5"}],
    }
    assert _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers(data) == 7.5


def test_retorna_zero_quando_nenhuma_duracao() -> None:
    assert _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers({}) == 0.0


def test_extrai_duracao_da_tag_duration_webm() -> None:
    formato = {"tags": {"DURATION": "00:01:05.500000000"}}
    assert _duracao_de_tags_formato_ffprobe_transcribrothers(formato) == 65.5


def test_parsear_tag_sexagesimal() -> None:
    assert _parsear_duracao_tag_sexagesimal_ffprobe_transcribrothers("125.5") == 125.5
    assert _parsear_duracao_tag_sexagesimal_ffprobe_transcribrothers("00:02:30") == 150.0
