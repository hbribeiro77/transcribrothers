"""Testes unitários dos helpers de payload multimodal do tutorial (sem chamar LiteLLM)."""

from pathlib import Path

import pytest

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    _extrair_texto_resposta_message_openai_compat_transcribrothers,
    _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers,
    normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers,
    resolver_instrucao_prefixo_litellm_para_corpo_user_tutorial_markdown_transcribrothers,
)


def test_extrair_texto_content_string() -> None:
    assert _extrair_texto_resposta_message_openai_compat_transcribrothers({"content": "abc"}) == "abc"


def test_extrair_texto_content_lista_partes_texto() -> None:
    msg = {
        "content": [
            {"type": "text", "text": "a"},
            {"type": "text", "text": "b"},
        ]
    }
    assert _extrair_texto_resposta_message_openai_compat_transcribrothers(msg) == "ab"


def test_ler_pngs_ordem_rels(tmp_path: Path) -> None:
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    p1 = assets / "a.png"
    p2 = assets / "b.png"
    p1.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 8)
    p2.write_bytes(b"\x89PNG\r\n\x1a\n" + b"y" * 8)
    rels = [(0.0, "assets/a.png"), (1.0, "assets/b.png")]
    blobs = _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers(assets, rels)
    assert len(blobs) == 2
    assert blobs[0].startswith(b"\x89PNG")
    assert blobs[1].startswith(b"\x89PNG")


def test_normalizar_instrucao_custom_anexa_json_de_entrada_se_faltar() -> None:
    s = normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers("Seja breve.\n\n")
    assert s is not None
    assert "JSON de entrada" in s
    assert s.endswith("\n")


def test_normalizar_instrucao_custom_none_se_vazio() -> None:
    assert normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers(None) is None
    assert normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers("  \n") is None


def test_resolver_instrucao_usa_padrao_sem_imagens() -> None:
    r = resolver_instrucao_prefixo_litellm_para_corpo_user_tutorial_markdown_transcribrothers(
        usar_visao=False,
        instrucao_prefixo_litellm_custom=None,
    )
    assert r == INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS


def test_ler_pngs_arquivo_ausente(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    with pytest.raises(RuntimeError, match="ausente"):
        _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers(
            assets,
            [(0.0, "assets/inexistente.png")],
        )
