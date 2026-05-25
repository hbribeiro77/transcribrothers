"""Testes de remoção de ![](assets/…) quando o PNG não existe."""

from pathlib import Path

from transcribrothers_backend.modulo_util_remover_referencias_imagens_assets_inexistentes_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_markdown_que_existem_no_disco_transcribrothers,
    remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers,
)


def test_remove_linha_imagem_quando_png_nao_existe(tmp_path: Path) -> None:
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir()
    (assets / "real.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    md = "# T\n\n![](assets/real.png)\n\n![](assets/fantasma.png)\n"
    limpo, n = remover_linhas_imagem_markdown_com_assets_png_inexistentes_transcribrothers(md, assets)
    assert n == 1
    assert "fantasma" not in limpo
    assert "real.png" in limpo


def test_listar_somente_caminhos_existentes(tmp_path: Path) -> None:
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir()
    (assets / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    md = "![](assets/a.png)\n![](assets/b.png)\n"
    lista = listar_caminhos_assets_png_em_markdown_que_existem_no_disco_transcribrothers(md, assets)
    assert lista == ["assets/a.png"]
