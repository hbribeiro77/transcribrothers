"""Escolhe frame da galeria (|Δt| <= 5s) ou captura um frame novo no vídeo do job."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers,
    proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    FrameCatalogoChatAskTranscribrothers,
)

DELTA_MAXIMO_SEGUNDOS_FRAME_GALERIA_CHAT_ASK_TRANSCRIBROTHERS = 5.0

CapturarFrameChatAskTranscribrothers = Callable[..., Awaitable[tuple[float, str, str, str]]]


@dataclass(frozen=True)
class ImagemResolvidaChatAskTranscribrothers:
    caminho_relativo: str
    instante_segundos: float
    origem: str


def _frame_galeria_mais_proximo_chat_ask_transcribrothers(
    catalogo: list[FrameCatalogoChatAskTranscribrothers],
    instante_segundos: float,
) -> FrameCatalogoChatAskTranscribrothers | None:
    melhor: FrameCatalogoChatAskTranscribrothers | None = None
    melhor_delta = DELTA_MAXIMO_SEGUNDOS_FRAME_GALERIA_CHAT_ASK_TRANSCRIBROTHERS
    for frame in catalogo:
        delta = abs(float(frame.instante_segundos) - float(instante_segundos))
        if melhor is None or delta < melhor_delta:
            if delta <= DELTA_MAXIMO_SEGUNDOS_FRAME_GALERIA_CHAT_ASK_TRANSCRIBROTHERS:
                melhor = frame
                melhor_delta = delta
    return melhor


async def resolver_imagens_chat_ask_por_instantes_transcribrothers(
    *,
    instantes_segundos: list[float],
    catalogo: list[FrameCatalogoChatAskTranscribrothers],
    caminho_video: Path | None,
    diretorio_trabalho_job: Path,
    steps_json: dict[str, Any],
    capturar_frame: CapturarFrameChatAskTranscribrothers,
) -> tuple[list[ImagemResolvidaChatAskTranscribrothers], dict[str, Any]]:
    steps = dict(steps_json or {})
    imagens: list[ImagemResolvidaChatAskTranscribrothers] = []
    video_disponivel = caminho_video is not None and caminho_video.is_file()
    for instante in instantes_segundos:
        frame = _frame_galeria_mais_proximo_chat_ask_transcribrothers(catalogo, float(instante))
        if frame is not None:
            imagens.append(
                ImagemResolvidaChatAskTranscribrothers(
                    caminho_relativo=frame.caminho_relativo,
                    instante_segundos=float(frame.instante_segundos),
                    origem="galeria",
                )
            )
            continue
        if not video_disponivel:
            continue
        indice = proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers(steps)
        try:
            t_efetivo, nome_arquivo, caminho_rel, _snippet = await capturar_frame(
                caminho_video=caminho_video,
                diretorio_trabalho_job=diretorio_trabalho_job,
                timestamp_segundos_solicitado=float(instante),
                indice_nome_arquivo=indice,
            )
        except Exception:
            continue
        steps = mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers(
            steps,
            timestamp_segundos_solicitado=float(instante),
            timestamp_segundos_efetivo=float(t_efetivo),
            nome_arquivo=str(nome_arquivo),
            caminho_relativo=str(caminho_rel),
            origem="chat_ask",
        )
        imagens.append(
            ImagemResolvidaChatAskTranscribrothers(
                caminho_relativo=str(caminho_rel),
                instante_segundos=float(t_efetivo),
                origem="captura_sob_demanda",
            )
        )
    return imagens, steps
