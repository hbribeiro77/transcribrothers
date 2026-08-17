"""Testes do resumo de debug do cache de segmentos do vídeo narrado."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_debug_cache_segmentos_video_narrado_job_transcribrothers import (
    extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers,
    inventariar_pasta_cache_segmentos_video_narrado_do_work_transcribrothers,
    montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers,
)


def test_inventario_pasta_segmentos_vazia_ou_ausente(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    info = inventariar_pasta_cache_segmentos_video_narrado_do_work_transcribrothers(work)
    assert info["pasta_existe"] is False
    assert info["quantidade_mp4"] == 0
    assert info["tem_cache_segmentos"] is False


def test_inventario_pasta_segmentos_conta_mp4(tmp_path: Path) -> None:
    work = tmp_path / "job"
    pasta = work / "segmentos_video_narrado_retarget"
    pasta.mkdir(parents=True)
    (pasta / "segmento_cache_aaa.mp4").write_bytes(b"x" * 100)
    (pasta / "segmento_cache_bbb.mp4").write_bytes(b"y" * 50)
    (pasta / "lista_concat.txt").write_text("file\n", encoding="utf-8")
    info = inventariar_pasta_cache_segmentos_video_narrado_do_work_transcribrothers(work)
    assert info["pasta_existe"] is True
    assert info["quantidade_mp4"] == 2
    assert info["bytes_pasta"] >= 150
    assert info["tem_cache_segmentos"] is True


def test_extrair_ultimo_mux_com_hits_e_meta() -> None:
    resumo = extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers(
        {
            "video_narrado_mux_segmentos_cache": 15,
            "video_narrado_mux_segmento_total": 16,
            "video_narrado_mux_fase": "concat",
            "video_narrado_mux_paralelismo": 4,
            "video_narrado_mux_encode_resolucao": "720p",
            "video_narrado_mux_encode_fps": 30,
            "pipeline_fase": "video_narrado_concluido",
            "video_com_narracao_tts": {
                "modo_montagem": "segmentos_retarget_denso_edicoes_modal",
                "quantidade_segmentos": 16,
                "gerado_em": "2026-08-15T00:00:00+00:00",
            },
        }
    )
    assert resumo is not None
    assert resumo["hits_cache"] == 15
    assert resumo["total_segmentos"] == 16
    assert resumo["fase_mux"] == "concat"
    assert resumo["modo_montagem"] == "segmentos_retarget_denso_edicoes_modal"


def test_extrair_ultimo_mux_sem_sinal_retorna_none() -> None:
    assert extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers({}) is None
    assert extrair_resumo_ultimo_mux_cache_segmentos_dos_steps_json_transcribrothers(None) is None


def test_payload_debug_agrega_disco_e_steps(tmp_path: Path) -> None:
    work = tmp_path / "job"
    pasta = work / "segmentos_video_narrado_retarget"
    pasta.mkdir(parents=True)
    (pasta / "a.mp4").write_bytes(b"z" * 20)
    payload = montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers(
        work,
        steps={
            "video_narrado_mux_segmentos_cache": 1,
            "video_narrado_mux_segmento_total": 1,
            "pipeline_origem_corrida": "edicoes_modal",
            "video_narrado_edicoes_modal_cues_sujas": 2,
            "video_narrado_edicoes_modal_wavs_reusados": 14,
        },
    )
    assert payload["segmentos"]["tem_cache_segmentos"] is True
    assert payload["segmentos"]["quantidade_mp4"] == 1
    assert payload["ultimo_mux"]["hits_cache"] == 1
    assert payload["edicoes_modal"]["cues_sujas"] == 2
    assert payload["edicoes_modal"]["wavs_reusados"] == 14
    assert payload["edicoes_modal"]["origem_corrida"] == "edicoes_modal"
    assert "segmentos_video_narrado_retarget" in payload["pastas_cache_regeneravel"]
