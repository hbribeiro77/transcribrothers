"""Formata segundos para rótulo [M:SS] e parâmetro ?t= usados em snippets Markdown."""

from __future__ import annotations


def formatar_segundos_video_como_rotulo_mm_ss_para_markdown_transcribrothers(segundos: float) -> str:
    s = max(0, int(segundos))
    m = s // 60
    r = s % 60
    return f"{m}:{r:02d}"


def formatar_segundos_video_como_parametro_link_temporal_t_transcribrothers(segundos: float) -> str:
    """Valor para `?t=` — inteiro quando possível, senão até 2 casas decimais."""
    t = max(0.0, float(segundos))
    arred = round(t, 2)
    if abs(arred - round(arred)) < 1e-6:
        return str(int(round(arred)))
    return f"{arred:.2f}".rstrip("0").rstrip(".")


def montar_snippet_markdown_insercao_frame_manual_video_tutorial_transcribrothers(
    *,
    caminho_relativo_assets: str,
    timestamp_segundos: float,
) -> str:
    rotulo = formatar_segundos_video_como_rotulo_mm_ss_para_markdown_transcribrothers(timestamp_segundos)
    param_t = formatar_segundos_video_como_parametro_link_temporal_t_transcribrothers(timestamp_segundos)
    caminho = caminho_relativo_assets.strip().replace("\\", "/")
    if not caminho.startswith("assets/"):
        caminho = f"assets/{caminho.split('/')[-1]}"
    return f"![Tela em {rotulo}]({caminho})\n\n[{rotulo}](?t={param_t})"


def montar_snippet_markdown_insercao_imagem_colada_clipboard_markdown_tutorial_transcribrothers(
    *,
    caminho_relativo_assets: str,
) -> str:
    caminho = caminho_relativo_assets.strip().replace("\\", "/")
    if not caminho.startswith("assets/"):
        caminho = f"assets/{caminho.split('/')[-1]}"
    return f"![Imagem colada]({caminho})"
