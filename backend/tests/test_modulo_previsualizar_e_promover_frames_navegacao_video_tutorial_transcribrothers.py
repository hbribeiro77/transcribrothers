import asyncio
from pathlib import Path
from unittest.mock import patch

from transcribrothers_backend.modulo_previsualizar_e_promover_frames_navegacao_video_tutorial_transcribrothers import (
    NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS,
    capturar_frames_previsualizacao_navegacao_video_tutorial_transcribrothers,
    descartar_arquivos_previsualizacao_navegacao_frame_tutorial_transcribrothers,
    diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers,
    promover_frame_previsualizacao_para_assets_tutorial_transcribrothers,
)

_PNG_MINIMO = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


def test_captura_previa_grava_so_na_pasta_temporaria_e_nao_em_assets(tmp_path: Path) -> None:
    video = tmp_path / "entrada.mp4"
    video.write_bytes(b"fake-mp4")
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir()
    (assets / "tela.png").write_bytes(_PNG_MINIMO)
    nome_preview = (
        "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032100_indice_0000.png"
    )

    async def _fake_ffmpeg(**kwargs):
        dest: Path = kwargs["diretorio_saida_frames"]
        dest.mkdir(parents=True, exist_ok=True)
        caminho = dest / nome_preview
        caminho.write_bytes(_PNG_MINIMO)
        return [caminho]

    async def _run() -> list:
        with (
            patch(
                "transcribrothers_backend.modulo_previsualizar_e_promover_frames_navegacao_video_tutorial_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
                return_value=120.0,
            ),
            patch(
                "transcribrothers_backend.modulo_previsualizar_e_promover_frames_navegacao_video_tutorial_transcribrothers.capturar_frames_png_do_video_nos_timestamps_segundos",
                side_effect=_fake_ffmpeg,
            ),
        ):
            return await capturar_frames_previsualizacao_navegacao_video_tutorial_transcribrothers(
                caminho_video=video,
                diretorio_trabalho_job=tmp_path,
                timestamps_segundos=[32.1],
            )

    itens = asyncio.run(_run())
    assert len(itens) == 1
    assert itens[0]["nome_arquivo"] == nome_preview
    preview_dir = diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(tmp_path)
    assert (preview_dir / nome_preview).is_file()
    assert not (assets / nome_preview).is_file()
    assert (assets / "tela.png").is_file()
    assert preview_dir.name == NOME_DIRETORIO_PREVISUALIZACAO_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS


def test_promover_copia_para_assets_e_descartar_nao_apaga_png_do_documento(tmp_path: Path) -> None:
    preview_dir = diretorio_previsualizacao_frames_navegacao_tutorial_transcribrothers(tmp_path)
    preview_dir.mkdir(parents=True)
    assets = tmp_path / "assets_exportados_para_markdown"
    assets.mkdir()
    (assets / "tela.png").write_bytes(_PNG_MINIMO)
    (assets / "tela.anotado.png").write_bytes(_PNG_MINIMO)
    nome_a = "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032100_indice_0000.png"
    nome_b = "preview_navegacao_frame_tutorial_frame_no_offset_ms_0000032500_indice_0001.png"
    (preview_dir / nome_a).write_bytes(_PNG_MINIMO)
    (preview_dir / nome_b).write_bytes(_PNG_MINIMO)

    nome_asset, caminho_rel = promover_frame_previsualizacao_para_assets_tutorial_transcribrothers(
        diretorio_trabalho_job=tmp_path,
        nome_arquivo_preview=nome_a,
        indice_nome_arquivo_asset=7,
    )
    assert caminho_rel.startswith("assets/")
    assert (assets / nome_asset).is_file()
    assert nome_asset.startswith("screenshot_manual_transcribrothers_")
    assert (assets / "tela.png").is_file()
    assert (assets / "tela.anotado.png").is_file()

    descartar_arquivos_previsualizacao_navegacao_frame_tutorial_transcribrothers(
        diretorio_trabalho_job=tmp_path,
        nomes_para_apagar=[nome_a, nome_b, "tela.png", "tela.anotado.png"],
        nomes_protegidos=["tela.png", "tela.anotado.png"],
    )
    assert not (preview_dir / nome_a).is_file()
    assert not (preview_dir / nome_b).is_file()
    assert (assets / "tela.png").is_file()
    assert (assets / "tela.anotado.png").is_file()
    assert (assets / nome_asset).is_file()
