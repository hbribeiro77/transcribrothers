"""Testes de nomenclatura e resolução de exibição para imagens anotadas."""

from transcribrothers_backend.modulo_util_nomenclatura_e_metadados_anotacao_imagens_tutorial_assets_png_transcribrothers import (
    derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers,
    mesclar_registro_anotacao_apos_gravar_png_anotado_transcribrothers,
    resolver_nome_arquivo_png_para_exibicao_no_tutorial_transcribrothers,
    substituir_referencia_asset_png_no_markdown_por_nome_arquivo_transcribrothers,
)


def test_derivar_nome_anotado() -> None:
    assert (
        derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers("frame_01.png")
        == "frame_01.anotado.png"
    )


def test_resolver_exibicao_anotado_quando_configurado() -> None:
    steps = mesclar_registro_anotacao_apos_gravar_png_anotado_transcribrothers({}, "frame_01.png")
    assert (
        resolver_nome_arquivo_png_para_exibicao_no_tutorial_transcribrothers(
            "frame_01.png",
            steps,
            arquivo_anotado_existe=True,
        )
        == "frame_01.anotado.png"
    )


def test_substituir_referencia_no_markdown() -> None:
    md = "![cap](assets/frame_01.png)\n"
    out = substituir_referencia_asset_png_no_markdown_por_nome_arquivo_transcribrothers(
        md,
        "frame_01.png",
        "frame_01.anotado.png",
    )
    assert "assets/frame_01.anotado.png" in out
    assert "assets/frame_01.png" not in out
