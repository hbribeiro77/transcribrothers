"""Isolamento de jobs criados por testes de API.

Alguns testes exercitam rotas reais que gravam em `backend/data`. Esta limpeza evita
que esses jobs apareçam depois na modal de "abrir projeto" do ambiente local.
"""

from __future__ import annotations

import shutil
import sqlite3
import time
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
    params_hist = [(j,) for j in job_ids]
    params_jobs = [(j,) for j in job_ids]
    ultimo_erro: sqlite3.OperationalError | None = None
    for tentativa in range(12):
        con = sqlite3.connect(db_path, timeout=30)
        try:
            con.execute("PRAGMA busy_timeout = 30000")
            con.executemany(
                "DELETE FROM historico_versoes_tutorial_markdown_job_transcribrothers WHERE job_id = ?",
                params_hist,
            )
            con.executemany("DELETE FROM jobs_pipeline_transcribrothers WHERE id = ?", params_jobs)
            con.commit()
            return
        except sqlite3.OperationalError as erro:
            ultimo_erro = erro
            if "locked" not in str(erro).lower():
                raise
            time.sleep(0.05 * (tentativa + 1))
        finally:
            con.close()
    if ultimo_erro is not None:
        raise ultimo_erro


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
