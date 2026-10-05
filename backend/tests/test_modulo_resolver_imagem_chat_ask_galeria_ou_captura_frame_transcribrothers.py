"""Galeria até 5s ou captura sob demanda para imagens do chat Ask."""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from transcribrothers_backend.modulo_constante_chave_steps_json_frames_manuais_capturados_video_tutorial_transcribrothers import (
    CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    FrameCatalogoChatAskTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers import (
    resolver_imagens_chat_ask_por_instantes_transcribrothers,
)


@pytest.mark.asyncio
async def test_escolhe_galeria_quando_delta_ate_5(tmp_path: Path) -> None:
    capturar = AsyncMock()
    imagens, _steps = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[10.0],
        catalogo=[FrameCatalogoChatAskTranscribrothers("assets/a.png", 12.0)],
        caminho_video=None,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=capturar,
    )
    assert imagens[0].origem == "galeria"
    assert imagens[0].caminho_relativo == "assets/a.png"
    capturar.assert_not_called()


@pytest.mark.asyncio
async def test_captura_quando_delta_maior_que_5(tmp_path: Path) -> None:
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"0")

    async def _cap(**kwargs):
        return (80.0, "frame_manual.png", "assets/frame_manual.png", "!")

    imagens, steps = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[80.0],
        catalogo=[FrameCatalogoChatAskTranscribrothers("assets/a.png", 12.0)],
        caminho_video=video,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=_cap,
    )
    assert imagens[0].origem == "captura_sob_demanda"
    assert imagens[0].caminho_relativo == "assets/frame_manual.png"
    registros = steps[CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS]
    assert registros[0]["origem"] == "chat_ask"
    assert registros[0]["caminho_relativo"] == "assets/frame_manual.png"


@pytest.mark.asyncio
async def test_sem_video_ou_captura_falha_omite_a_imagem(tmp_path: Path) -> None:
    capturar = AsyncMock(side_effect=RuntimeError("ffmpeg"))
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"0")
    imagens_sem_video, steps_sem_video = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[80.0],
        catalogo=[FrameCatalogoChatAskTranscribrothers("assets/a.png", 12.0)],
        caminho_video=None,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=capturar,
    )
    assert imagens_sem_video == []
    assert steps_sem_video == {}
    capturar.assert_not_called()

    imagens_falha, steps_falha = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[80.0],
        catalogo=[],
        caminho_video=video,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=capturar,
    )
    assert imagens_falha == []
    assert steps_falha == {}
