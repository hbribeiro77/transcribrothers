"""Testes de extração de H1 para coluna da lista de jobs."""

from transcribrothers_backend.modulo_util_extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers import (
    extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers,
)


def test_extrair_h1_simples() -> None:
    assert extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers("# Olá\n\nCorpo.") == "Olá"


def test_extrair_h1_ignora_h2() -> None:
    md = "## Sub\n\n# Principal\n"
    assert extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers(md) == "Principal"


def test_extrair_h1_none_se_sem_h1() -> None:
    assert extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers("Só texto.\n\n## Dois") is None


def test_extrair_h1_none_se_vazio() -> None:
    assert extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers(None) is None
    assert extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers("  \n  ") is None


def test_extrair_h1_truncagem() -> None:
    longo = "# " + "x" * 300
    out = extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers(
        longo,
        max_caracteres=10,
    )
    assert out is not None
    assert len(out) == 10
    assert out.endswith("…")
