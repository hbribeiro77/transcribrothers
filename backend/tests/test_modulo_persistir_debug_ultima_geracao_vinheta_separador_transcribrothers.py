from pathlib import Path

from transcribrothers_backend.modulo_debug_cache_segmentos_video_narrado_job_transcribrothers import (
    montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers,
)
from transcribrothers_backend.modulo_persistir_debug_ultima_geracao_vinheta_separador_transcribrothers import (
    gravar_debug_ultima_geracao_vinheta_separador_transcribrothers,
    ler_debug_ultima_geracao_vinheta_separador_transcribrothers,
)


def test_grava_e_le_o_relatorio_da_ultima_vinheta(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    relatorio = {
        "titulo": "Pré-requisito",
        "tempos_ms": {"total": 18234, "render_vinhetas": 17120},
        "largura": 1366,
        "altura": 768,
    }

    gravar_debug_ultima_geracao_vinheta_separador_transcribrothers(work, relatorio)
    lido = ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work)

    assert lido is not None
    assert lido["titulo"] == "Pré-requisito"
    assert lido["tempos_ms"]["total"] == 18234
    assert lido["largura"] == 1366


def test_ler_sem_arquivo_devolve_none(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    assert ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work) is None


def test_payload_do_debug_inclui_a_ultima_vinheta(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    gravar_debug_ultima_geracao_vinheta_separador_transcribrothers(
        work,
        {"titulo": "Consulta", "tempos_ms": {"total": 900}},
    )

    payload = montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers(work, steps={})

    assert payload["ultima_vinheta"]["titulo"] == "Consulta"
    assert payload["ultima_vinheta"]["tempos_ms"]["total"] == 900


def test_payload_do_debug_sem_vinheta_fica_nulo(tmp_path: Path) -> None:
    work = tmp_path / "job"
    work.mkdir()
    payload = montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers(work, steps={})
    assert payload["ultima_vinheta"] is None
