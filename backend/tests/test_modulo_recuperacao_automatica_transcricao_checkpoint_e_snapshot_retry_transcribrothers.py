"""Recuperação automática a partir de checkpoint multimodal completo."""

import json
from pathlib import Path

import pytest

from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_CHECKPOINT_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
    resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers,
)
from transcribrothers_backend.modulo_recuperacao_automatica_transcricao_checkpoint_e_snapshot_retry_transcribrothers import (
    contar_janelas_concluidas_no_checkpoint_multimodal_bruto_transcribrothers,
    tentar_mesclar_transcricao_de_checkpoint_multimodal_bruto_se_todas_janelas_concluidas_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def _segmento_dict(texto: str, inicio: float = 0.0, fim: float = 2.0) -> dict:
    r = ResultadoTranscricaoComSegmentos(
        texto_completo=texto,
        segmentos=[SegmentoTranscricaoComTempo(inicio_segundos=inicio, fim_segundos=fim, texto=texto)],
        idioma_detectado="pt",
    )
    return resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers(r)


def test_contar_janelas_no_checkpoint_bruto() -> None:
    raw = {"total_janelas": 3, "janelas_concluidas": {"0": {}, "1": {}, "2": {}}}
    assert contar_janelas_concluidas_no_checkpoint_multimodal_bruto_transcribrothers(raw) == (3, 3)


def test_mescla_checkpoint_bruto_quando_todas_janelas_concluidas() -> None:
    raw = {
        "versao": CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
        "janela_segundos": 30.0,
        "total_janelas": 2,
        "janelas_concluidas": {
            "0": _segmento_dict("primeiro trecho"),
            "1": _segmento_dict("segundo trecho", inicio=0.0, fim=1.0),
        },
    }
    resultado = tentar_mesclar_transcricao_de_checkpoint_multimodal_bruto_se_todas_janelas_concluidas_transcribrothers(
        raw,
        duracao_audio_ffprobe=55.0,
    )
    assert resultado is not None
    assert "primeiro" in resultado.texto_completo
    assert "segundo" in resultado.texto_completo


def test_nao_mescla_checkpoint_bruto_parcial() -> None:
    raw = {
        "versao": CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
        "janela_segundos": 30.0,
        "total_janelas": 5,
        "janelas_concluidas": {"0": _segmento_dict("só um")},
    }
    assert (
        tentar_mesclar_transcricao_de_checkpoint_multimodal_bruto_se_todas_janelas_concluidas_transcribrothers(
            raw,
            duracao_audio_ffprobe=120.0,
        )
        is None
    )


@pytest.mark.asyncio
async def test_recuperacao_automatica_via_checkpoint_validado_no_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock

    from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
        ConfiguracaoAmbienteTranscribrothers,
    )
    from transcribrothers_backend.modulo_recuperacao_automatica_transcricao_checkpoint_e_snapshot_retry_transcribrothers import (
        tentar_recuperar_transcricao_automatica_antes_de_reexecutar_pipeline_transcribrothers,
    )

    wav = tmp_path / "audio_extraido_para_transcricao.wav"
    wav.write_bytes(b"\x00" * 4096)
    payload = {
        "versao": CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS,
        "janela_segundos": 30.0,
        "total_janelas": 1,
        "formato_audio_inline": "wav",
        "audio_bitrate_kbps": 32,
        "audio_mono": True,
        "modelo_transcricao": "gemini/test",
        "duracao_audio_ffprobe": 10.0,
        "tamanho_bytes_audio_fonte": wav.stat().st_size,
        "janelas_concluidas": {"0": _segmento_dict("trecho único")},
        "registros_tempo_inferencia": [],
    }
    (tmp_path / NOME_ARQUIVO_CHECKPOINT_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS).write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    cfg = ConfiguracaoAmbienteTranscribrothers.model_construct(
        transcricao_backend="litellm_multimodal_audio",
        transcricao_litellm_modelo="gemini/test",
        transcricao_multimodal_formato_audio_inline="wav",
        transcricao_multimodal_audio_bitrate_kbps=32,
        transcricao_multimodal_audio_mono=True,
        transcricao_multimodal_janela_segundos=30,
        litellm_model="gemini/test",
    )

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_recuperacao_automatica_transcricao_checkpoint_e_snapshot_retry_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        AsyncMock(return_value=10.0),
    )

    recuperado, meta = await tentar_recuperar_transcricao_automatica_antes_de_reexecutar_pipeline_transcribrothers(
        diretorio_trabalho_job=tmp_path,
        caminho_audio_wav=wav,
        configuracao=cfg,
        configuracao_exec_transcricao_mm=cfg,
        steps={},
    )
    assert recuperado is not None
    assert "trecho" in recuperado.texto_completo
    assert meta.get("transcricao_recuperacao_automatica") in (
        "checkpoint_multimodal_completo_validado",
        "checkpoint_multimodal_completo_bruto",
    )
