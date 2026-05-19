from transcribrothers_backend.modulo_util_remover_referencia_imagem_asset_markdown_tutorial_transcribrothers import (
    markdown_tutorial_referencia_imagem_asset_transcribrothers,
    remover_referencia_imagem_asset_do_markdown_tutorial_transcribrothers,
)


def test_remover_referencia_imagem_e_link_temporal_abaixo() -> None:
    md = "# t\n\n![](assets/cap.png)\n\n[ver](?t=12)\n\nTexto."
    out = remover_referencia_imagem_asset_do_markdown_tutorial_transcribrothers(md, "cap.png")
    assert "cap.png" not in out
    assert "?t=12" not in out
    assert "Texto." in out


def test_markdown_referencia_detecta_asset() -> None:
    md = "![](assets/foo.anotado.png)"
    assert markdown_tutorial_referencia_imagem_asset_transcribrothers(md, "foo.png") is True
