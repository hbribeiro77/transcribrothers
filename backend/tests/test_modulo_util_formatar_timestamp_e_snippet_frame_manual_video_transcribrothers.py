"""Testes de formatação e snippet Markdown para frame manual."""

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_formatar_timestamp_segundos_para_snippet_markdown_link_temporal_transcribrothers import (
    formatar_segundos_video_como_parametro_link_temporal_t_transcribrothers,
    formatar_segundos_video_como_rotulo_mm_ss_para_markdown_transcribrothers,
    montar_snippet_markdown_insercao_frame_manual_video_tutorial_transcribrothers,
    montar_snippet_markdown_insercao_imagem_colada_clipboard_markdown_tutorial_transcribrothers,
)


def test_rotulo_mm_ss() -> None:
    assert formatar_segundos_video_como_rotulo_mm_ss_para_markdown_transcribrothers(83) == "1:23"


def test_parametro_t() -> None:
    assert formatar_segundos_video_como_parametro_link_temporal_t_transcribrothers(83.0) == "83"
    assert formatar_segundos_video_como_parametro_link_temporal_t_transcribrothers(83.5) == "83.5"


def test_snippet_markdown() -> None:
    s = montar_snippet_markdown_insercao_frame_manual_video_tutorial_transcribrothers(
        caminho_relativo_assets="assets/foo.png",
        timestamp_segundos=83,
    )
    assert "![Tela em 1:23](assets/foo.png)" in s
    assert "[1:23](?t=83)" in s


def test_snippet_markdown_imagem_colada_clipboard() -> None:
    snippet = montar_snippet_markdown_insercao_imagem_colada_clipboard_markdown_tutorial_transcribrothers(
        caminho_relativo_assets="assets/imagem_colada_clipboard_transcribrothers_indice_0001.png",
    )
    assert snippet == "![Imagem colada](assets/imagem_colada_clipboard_transcribrothers_indice_0001.png)"


def test_proximo_indice_pelo_historico_steps() -> None:
    steps = {
        "frames_manuais_capturados_video_tutorial": [{"nome_arquivo": "a.png"}, {"nome_arquivo": "b.png"}],
    }
    assert proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers(steps) == 2
