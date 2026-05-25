"""Testes de reescrita Markdown com URLs /uploads/ do GitLab."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers import (
    preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers,
    reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers,
)


def test_reescrever_substituir_assets_por_url_gitlab() -> None:
    md = "# T\n\n![cap](assets/a.png)\n\n![b](assets/b.png)"
    mapa = {
        "assets/a.png": "/uploads/secret1/a.png",
        "assets/b.png": "/uploads/secret2/b.png",
    }
    out = reescrever_markdown_tutorial_substituindo_assets_png_por_urls_upload_gitlab_transcribrothers(md, mapa)
    assert "/uploads/secret1/a.png" in out
    assert "/uploads/secret2/b.png" in out
    assert "assets/a.png" not in out


@pytest.mark.asyncio
async def test_preparar_descricao_faz_upload_e_reescreve(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "foto.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    md = "# Doc\n\n![tela](assets/foto.png)\n"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo",
        gitlab_token="tok",
    )

    async def _fake_upload(*_a, **_k):
        return "/uploads/abc123/foto.png"

    with patch(
        "transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers.upload_arquivo_png_markdown_gitlab_projeto_transcribrothers",
        new_callable=AsyncMock,
        side_effect=_fake_upload,
    ):
        out, enviadas, ignoradas = await preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers(
            cfg,
            md,
            assets,
            None,
            incluir_imagens_png_markdown=True,
        )

    assert enviadas == 1
    assert ignoradas == 0
    assert "/uploads/abc123/foto.png" in out
    assert "assets/foto.png" not in out


@pytest.mark.asyncio
async def test_preparar_descricao_envia_png_para_project_path_gitlab_dinamico(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "foto.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    md = "# Doc\n\n![tela](assets/foto.png)\n"
    cfg = ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo",
        gitlab_token="tok",
    )
    chamadas: list[dict[str, object]] = []

    async def _fake_upload(*_a, **kwargs):
        chamadas.append(dict(kwargs))
        return "/uploads/abc123/foto.png"

    with patch(
        "transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers.upload_arquivo_png_markdown_gitlab_projeto_transcribrothers",
        new_callable=AsyncMock,
        side_effect=_fake_upload,
    ):
        out, enviadas, ignoradas = await preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers(
            cfg,
            md,
            assets,
            None,
            incluir_imagens_png_markdown=True,
            project_path_gitlab="grupo/projeto-destino",
        )

    assert enviadas == 1
    assert ignoradas == 0
    assert "/uploads/abc123/foto.png" in out
    assert chamadas[0]["project_path_gitlab"] == "grupo/projeto-destino"
