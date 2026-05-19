"""Roundtrip de serialização do checkpoint de transcrição multimodal por janelas."""

from pathlib import Path

from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers,
    gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers,
    resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def test_resultado_transcricao_checkpoint_roundtrip_preserva_segmentos() -> None:
    r = ResultadoTranscricaoComSegmentos(
        texto_completo="olá mundo",
        segmentos=[
            SegmentoTranscricaoComTempo(0.1, 1.2, "olá"),
            SegmentoTranscricaoComTempo(1.2, 2.0, "mundo"),
        ],
        idioma_detectado="pt",
    )
    d = resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers(r)
    r2 = dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers(d)
    assert r2.texto_completo == r.texto_completo
    assert r2.idioma_detectado == r.idioma_detectado
    assert len(r2.segmentos) == 2
    assert r2.segmentos[0].texto == "olá"


def test_gravar_checkpoint_incrementa_contagem_janelas(tmp_path: Path) -> None:
    meta = {
        "versao": 1,
        "janela_segundos": 300.0,
        "total_janelas": 3,
        "formato_audio_inline": "wav",
        "audio_bitrate_kbps": 96,
        "audio_mono": True,
        "modelo_transcricao": "gemini/x",
        "duracao_audio_ffprobe": 900.0,
        "tamanho_bytes_audio_fonte": 12345,
    }
    r0 = ResultadoTranscricaoComSegmentos(
        texto_completo="a",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "a")],
        idioma_detectado=None,
    )
    n1 = gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers(
        tmp_path,
        meta_fixa=meta,
        indice_janela_base_zero=0,
        resultado_janela=r0,
        registro_tempo_inferencia={
            "indice": 1,
            "inicio_segundos": 0.0,
            "fim_segundos": 300.0,
            "duracao_inferencia_segundos": 1.5,
        },
    )
    assert n1 == 1
    r1 = ResultadoTranscricaoComSegmentos(
        texto_completo="b",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "b")],
        idioma_detectado=None,
    )
    n2 = gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers(
        tmp_path,
        meta_fixa=meta,
        indice_janela_base_zero=1,
        resultado_janela=r1,
        registro_tempo_inferencia={
            "indice": 2,
            "inicio_segundos": 300.0,
            "fim_segundos": 600.0,
            "duracao_inferencia_segundos": 2.0,
        },
    )
    assert n2 == 2
