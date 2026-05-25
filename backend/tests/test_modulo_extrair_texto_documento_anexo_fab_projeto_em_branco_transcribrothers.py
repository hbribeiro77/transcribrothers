"""Extração de texto de documentos para anexo FAB."""

import pytest

from transcribrothers_backend.modulo_util_extrair_texto_documento_anexo_contexto_fab_projeto_em_branco_transcribrothers import (
    extrair_texto_documento_anexo_contexto_fab_transcribrothers,
    truncar_texto_documento_para_limite_anexo_fab_transcribrothers,
)


def test_extrai_markdown_e_txt_utf8() -> None:
    md = extrair_texto_documento_anexo_contexto_fab_transcribrothers(
        nome_arquivo="notas.md",
        conteudo_bytes=b"# Titulo\n\nCorpo do anexo.",
    )
    assert "Corpo do anexo" in md

    txt = extrair_texto_documento_anexo_contexto_fab_transcribrothers(
        nome_arquivo="legislacao.txt",
        conteudo_bytes="Art. 1\nParagrafo".encode("utf-8"),
    )
    assert txt.startswith("Art. 1")


def test_rejeita_formato_desconhecido() -> None:
    with pytest.raises(ValueError, match="não suportado"):
        extrair_texto_documento_anexo_contexto_fab_transcribrothers(
            nome_arquivo="planilha.xlsx",
            conteudo_bytes=b"xxx",
        )


def test_truncar_respeita_limite() -> None:
    longo = "a" * 50_000
    curto, truncado = truncar_texto_documento_para_limite_anexo_fab_transcribrothers(longo)
    assert truncado is True
    assert curto.endswith("…")
    assert len(curto) <= 48_000 + 1
