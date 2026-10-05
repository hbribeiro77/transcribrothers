"""Janela multimodal: subdividir trecho com content vazio e, se persistir, usar placeholder."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers import (
    TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS,
    _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers,
    montar_resultado_placeholder_janela_transcricao_conteudo_vazio_transcribrothers,
    transcrever_wav_litellm_multimodal_em_janelas_com_callback_progresso_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    ErroConteudoVazioTranscricaoMultimodalTranscribrothers,
)


def test_placeholder_janela_tem_segmento_com_texto_padrao() -> None:
    r = montar_resultado_placeholder_janela_transcricao_conteudo_vazio_transcribrothers(
        duracao_segundos=30.0,
    )
    assert r.texto_completo == TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS
    assert len(r.segmentos) == 1
    assert r.segmentos[0].texto == TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS
    assert r.segmentos[0].fim_segundos == 30.0


@pytest.mark.asyncio
async def test_janela_curta_com_content_vazio_vira_placeholder(tmp_path: Path) -> None:
    transcriber = MagicMock()
    transcriber.transcrever_arquivo_audio_com_segmentos = AsyncMock(
        side_effect=ErroConteudoVazioTranscricaoMultimodalTranscribrothers(
            "Modelo multimodal retornou conteúdo vazio na transcrição."
        )
    )
    janela = tmp_path / "janela.wav"
    janela.write_bytes(b"x")
    resultado = await _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers(
        transcriber=transcriber,
        caminho_audio_completo=janela,
        caminho_janela=janela,
        inicio_segundos=0.0,
        duracao_segundos=4.0,
        formato_audio_inline="wav",
        bitrate_audio_kbps=96,
        forcar_mono=True,
        diretorio_temporario_janelas=tmp_path,
        sufixo_arquivo_temp="janela_curta",
    )
    assert resultado.texto_completo == TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS
    transcriber.transcrever_arquivo_audio_com_segmentos.assert_awaited_once()


@pytest.mark.asyncio
async def test_janela_longa_com_content_vazio_subdivide_e_mescla_metades(tmp_path: Path, monkeypatch) -> None:
    ok = ResultadoTranscricaoComSegmentos(
        texto_completo="metade boa",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 5.0, "metade boa")],
        idioma_detectado="pt",
    )
    transcriber = MagicMock()
    transcriber.transcrever_arquivo_audio_com_segmentos = AsyncMock(
        side_effect=[
            ErroConteudoVazioTranscricaoMultimodalTranscribrothers("vazio"),
            ok,
            ErroConteudoVazioTranscricaoMultimodalTranscribrothers("vazio"),
        ]
    )

    async def _noop_extrair(**_kwargs) -> None:
        return None

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers."
        "_extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers",
        _noop_extrair,
    )
    janela = tmp_path / "janela.wav"
    janela.write_bytes(b"x")
    resultado = await _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers(
        transcriber=transcriber,
        caminho_audio_completo=janela,
        caminho_janela=janela,
        inicio_segundos=1500.0,
        duracao_segundos=30.0,
        formato_audio_inline="wav",
        bitrate_audio_kbps=96,
        forcar_mono=True,
        diretorio_temporario_janelas=tmp_path,
        sufixo_arquivo_temp="janela_longa",
    )
    assert "metade boa" in resultado.texto_completo
    assert TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS in resultado.texto_completo
    assert transcriber.transcrever_arquivo_audio_com_segmentos.await_count == 3


@pytest.mark.asyncio
async def test_pipeline_paralelo_nao_aborta_quando_uma_janela_fica_so_placeholder(
    tmp_path: Path, monkeypatch
) -> None:
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"x")
    dir_janelas = tmp_path / "janelas"

    async def _duracao(_path) -> float:
        return 60.0

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers."
        "obter_duracao_video_segundos_via_ffprobe",
        _duracao,
    )

    async def _noop_extrair(**_kwargs) -> None:
        return None

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers."
        "_extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers",
        _noop_extrair,
    )

    ok = ResultadoTranscricaoComSegmentos(
        texto_completo="janela ok",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 30.0, "janela ok")],
        idioma_detectado="pt",
    )

    async def _resiliente(**kwargs):
        if kwargs["inicio_segundos"] < 1.0:
            return ok
        raise ErroConteudoVazioTranscricaoMultimodalTranscribrothers(
            "Modelo multimodal retornou conteúdo vazio na transcrição."
        )

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_janelas_mesclagem_segmentos_transcribrothers."
        "_transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers",
        _resiliente,
    )

    transcriber = MagicMock()
    mesclado = await transcrever_wav_litellm_multimodal_em_janelas_com_callback_progresso_transcribrothers(
        transcriber=transcriber,
        caminho_audio_completo=audio,
        formato_audio_inline="wav",
        janela_segundos=30.0,
        diretorio_temporario_janelas=dir_janelas,
        atualizar_progresso=None,
        max_janelas_em_paralelo=2,
    )
    assert "janela ok" in mesclado.texto_completo
    assert TEXTO_PLACEHOLDER_JANELA_TRANSCRICAO_CONTEUDO_VAZIO_TRANSCRIBROTHERS in mesclado.texto_completo
