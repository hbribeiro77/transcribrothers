"""Cria cópia do vídeo do job com a faixa de áudio substituída pela narração TTS (WAV)."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    executar_ffmpeg_com_argumentos,
)

NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS = "video_com_narracao_tts.mp4"
CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS = "video_com_narracao_tts"


async def substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers(
    *,
    caminho_video: Path,
    caminho_narracao_wav: Path,
    diretorio_saida: Path,
    nome_arquivo_saida: str = NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
) -> Path:
    """
    Mantém o vídeo (stream copy) e troca o áudio pelo WAV da narração (AAC).
    Usa `-shortest`: o resultado termina no fim do fluxo mais curto (vídeo ou narração).
    """
    if not caminho_video.is_file():
        raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {caminho_video}")
    if not caminho_narracao_wav.is_file():
        raise FileNotFoundError(f"Arquivo de narração WAV não encontrado: {caminho_narracao_wav}")

    diretorio_saida.mkdir(parents=True, exist_ok=True)
    saida = diretorio_saida / nome_arquivo_saida
    args = [
        "-y",
        "-i",
        str(caminho_video),
        "-i",
        str(caminho_narracao_wav),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(saida),
    ]
    await executar_ffmpeg_com_argumentos(args)
    if not saida.is_file():
        raise RuntimeError("ffmpeg concluiu sem gerar o arquivo de vídeo com narração.")
    return saida
