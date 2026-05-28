"""Isolamento de jobs criados por testes de API.

Alguns testes exercitam rotas reais que gravam em `backend/data`. Esta limpeza evita
que esses jobs apareçam depois na modal de "abrir projeto" do ambiente local.
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import obter_configuracao


def _resolver_data_dir_testes_transcribrothers() -> Path:
    return obter_configuracao().transcribrothers_data_dir.resolve()


def _caminho_banco_jobs_transcribrothers() -> Path:
    return _resolver_data_dir_testes_transcribrothers() / "transcribrothers.sqlite3"


def _listar_ids_jobs_persistidos_transcribrothers(db_path: Path) -> set[str]:
    if not db_path.is_file():
        return set()
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute("SELECT id FROM jobs_pipeline_transcribrothers").fetchall()
    except sqlite3.OperationalError:
        return set()
    finally:
        con.close()
    return {str(row[0]) for row in rows}


def _apagar_jobs_persistidos_transcribrothers(db_path: Path, job_ids: set[str]) -> None:
    if not job_ids or not db_path.is_file():
        return
    con = sqlite3.connect(db_path, timeout=15)
    try:
        con.executemany("DELETE FROM historico_versoes_tutorial_markdown_job_transcribrothers WHERE job_id = ?", [(j,) for j in job_ids])
        con.executemany("DELETE FROM jobs_pipeline_transcribrothers WHERE id = ?", [(j,) for j in job_ids])
        con.commit()
    finally:
        con.close()


def _apagar_pastas_jobs_persistidos_transcribrothers(data_dir: Path, job_ids: set[str]) -> None:
    jobs_dir = data_dir / "jobs"
    for job_id in job_ids:
        shutil.rmtree(jobs_dir / job_id, ignore_errors=True)


@pytest.fixture(autouse=True)
def limpar_jobs_criados_por_teste_transcribrothers():
    """Remove somente os jobs novos criados pelo teste corrente."""
    data_dir = _resolver_data_dir_testes_transcribrothers()
    db_path = _caminho_banco_jobs_transcribrothers()
    antes = _listar_ids_jobs_persistidos_transcribrothers(db_path)
    yield
    depois = _listar_ids_jobs_persistidos_transcribrothers(db_path)
    novos = depois - antes
    _apagar_jobs_persistidos_transcribrothers(db_path, novos)
    _apagar_pastas_jobs_persistidos_transcribrothers(data_dir, novos)
