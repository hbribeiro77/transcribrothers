from transcribrothers_backend.modulo_util_sanitizar_referencias_assets_png_markdown_contra_catalogo_frames_transcribrothers import (
    sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers,
)

CATALOGO = [
    (
        31.7,
        "assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000031700_indice_0004.png",
    ),
    (
        255.0,
        "assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000255000_indice_0012.png",
    ),
]


def test_mantem_caminho_valido() -> None:
    md = "![](assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000031700_indice_0004.png)"
    out, aj = sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers(md, CATALOGO)
    assert out == md
    assert aj == []


def test_corrige_nome_inventado_com_ms_correto() -> None:
    md = "![](assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000255000_exemplo_bloqueio_01.png)"
    out, aj = sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers(md, CATALOGO)
    assert "indice_0012" in out
    assert "exemplo_bloqueio" not in out
    assert aj and aj[0]["acao"] == "substituido"


def test_remove_caminho_sem_correspondencia() -> None:
    md = "Texto\n\n![](assets/inexistente_totalmente.png)\n\nFim"
    out, aj = sanitizar_referencias_assets_png_no_markdown_contra_catalogo_frames_transcribrothers(md, CATALOGO)
    assert "inexistente" not in out
    assert aj[0]["acao"] == "removido"
