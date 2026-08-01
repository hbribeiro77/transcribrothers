"""Testes do cálculo de tamanho da pasta do job."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_calcular_tamanho_bytes_diretorio_job_pipeline_transcribrothers import (
    calcular_tamanho_bytes_diretorio_recursivo_transcribrothers,
)


def test_tamanho_pasta_inexistente_zero(tmp_path: Path) -> None:
    assert calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(tmp_path / "nao") == 0


def test_tamanho_soma_arquivos_recursivo(tmp_path: Path) -> None:
    work = tmp_path / "job"
    (work / "sub").mkdir(parents=True)
    (work / "a.bin").write_bytes(b"12345")
    (work / "sub" / "b.bin").write_bytes(b"abcdef")
    assert calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(work) == 11
