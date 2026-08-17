"""Unifica dois vídeos de entrada: stream copy rápido se compatíveis, senão reencode."""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    executar_ffmpeg_com_argumentos,
)
from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    resolver_caminho_ffprobe_transcribrothers,
)

LARGURA_NORMALIZADA_VIDEO_ENTRADA_TRANSCRIBROTHERS = 1920
ALTURA_NORMALIZADA_VIDEO_ENTRADA_TRANSCRIBROTHERS = 1080
FPS_NORMALIZADO_VIDEO_ENTRADA_TRANSCRIBROTHERS = 30
SAMPLE_RATE_AUDIO_NORMALIZADO_TRANSCRIBROTHERS = 48000

ModoConcatVideosEntradaTranscribrothers = Literal["stream_copy", "reencode"]

_logger = logging.getLogger("transcribrothers.concat_video_entrada")


@dataclass(frozen=True)
class PerfilStreamsMidiaEntradaTranscribrothers:
    codec_video: str
    largura: int
    altura: int
    taxa_fps: str
    pix_fmt: str
    codec_audio: str | None
    sample_rate_audio: int | None
    canais_audio: int | None


@dataclass(frozen=True)
class ResultadoConcatenacaoVideosEntradaTranscribrothers:
    caminho_saida: Path
    modo: ModoConcatVideosEntradaTranscribrothers


def _midia_entrada_tem_stream_audio_via_ffprobe_sync(caminho: Path) -> bool:
    perfil = _obter_perfil_streams_midia_entrada_via_ffprobe_sync(caminho)
    return perfil is not None and perfil.codec_audio is not None


async def midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers(caminho: Path) -> bool:
    return await asyncio.to_thread(_midia_entrada_tem_stream_audio_via_ffprobe_sync, caminho)


def _parsear_int_stream(valor: object) -> int | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor if valor > 0 else None
    if isinstance(valor, float):
        return int(valor) if valor > 0 else None
    if isinstance(valor, str) and valor.strip():
        try:
            n = int(float(valor.strip()))
            return n if n > 0 else None
        except ValueError:
            return None
    return None


def _extrair_perfil_de_saida_ffprobe_json(data: dict) -> PerfilStreamsMidiaEntradaTranscribrothers | None:
    streams = data.get("streams")
    if not isinstance(streams, list):
        return None
    video = None
    audio = None
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        tipo = stream.get("codec_type")
        if tipo == "video" and video is None:
            video = stream
        elif tipo == "audio" and audio is None:
            audio = stream
    if video is None:
        return None
    codec_v = str(video.get("codec_name") or "").strip().lower()
    largura = _parsear_int_stream(video.get("width"))
    altura = _parsear_int_stream(video.get("height"))
    if not codec_v or largura is None or altura is None:
        return None
    taxa = str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "").strip()
    if not taxa or taxa in {"0/0", "N/A"}:
        taxa = "desconhecida"
    pix = str(video.get("pix_fmt") or "").strip().lower() or "desconhecido"
    codec_a = None
    sample_rate = None
    canais = None
    if audio is not None:
        codec_a = str(audio.get("codec_name") or "").strip().lower() or None
        sample_rate = _parsear_int_stream(audio.get("sample_rate"))
        canais = _parsear_int_stream(audio.get("channels"))
    return PerfilStreamsMidiaEntradaTranscribrothers(
        codec_video=codec_v,
        largura=largura,
        altura=altura,
        taxa_fps=taxa,
        pix_fmt=pix,
        codec_audio=codec_a,
        sample_rate_audio=sample_rate,
        canais_audio=canais,
    )


def _obter_perfil_streams_midia_entrada_via_ffprobe_sync(
    caminho: Path,
) -> PerfilStreamsMidiaEntradaTranscribrothers | None:
    executavel = resolver_caminho_ffprobe_transcribrothers()
    if not executavel:
        return None
    proc = subprocess.run(
        [
            executavel,
            "-v",
            "error",
            "-show_streams",
            "-of",
            "json",
            str(caminho),
        ],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        data = json.loads((proc.stdout or b"{}").decode(errors="replace"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return _extrair_perfil_de_saida_ffprobe_json(data)


async def obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers(
    caminho: Path,
) -> PerfilStreamsMidiaEntradaTranscribrothers | None:
    return await asyncio.to_thread(_obter_perfil_streams_midia_entrada_via_ffprobe_sync, caminho)


def perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(
    perfil_a: PerfilStreamsMidiaEntradaTranscribrothers,
    perfil_b: PerfilStreamsMidiaEntradaTranscribrothers,
) -> bool:
    if perfil_a.codec_video != perfil_b.codec_video:
        return False
    if perfil_a.largura != perfil_b.largura or perfil_a.altura != perfil_b.altura:
        return False
    if perfil_a.pix_fmt != perfil_b.pix_fmt:
        return False
    if (
        perfil_a.taxa_fps != "desconhecida"
        and perfil_b.taxa_fps != "desconhecida"
        and perfil_a.taxa_fps != perfil_b.taxa_fps
    ):
        return False
    tem_audio_a = perfil_a.codec_audio is not None
    tem_audio_b = perfil_b.codec_audio is not None
    if tem_audio_a != tem_audio_b:
        return False
    if not tem_audio_a:
        return True
    return (
        perfil_a.codec_audio == perfil_b.codec_audio
        and perfil_a.sample_rate_audio == perfil_b.sample_rate_audio
        and perfil_a.canais_audio == perfil_b.canais_audio
    )


def _escrever_lista_concat_demuxer(caminhos: list[Path], lista_txt: Path) -> None:
    linhas = []
    for p in caminhos:
        caminho_esc = str(p.resolve()).replace("\\", "/").replace("'", r"'\''")
        linhas.append(f"file '{caminho_esc}'")
    lista_txt.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")


async def _concat_demuxer_stream_copy_transcribrothers(
    *,
    caminho_video_a: Path,
    caminho_video_b: Path,
    caminho_saida: Path,
) -> None:
    with tempfile.TemporaryDirectory(prefix="tb_concat_copy_") as tmp:
        lista = Path(tmp) / "lista_concat_stream_copy.txt"
        _escrever_lista_concat_demuxer([caminho_video_a, caminho_video_b], lista)
        args = [
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista),
            "-c",
            "copy",
            str(caminho_saida),
        ]
        await executar_ffmpeg_com_argumentos(args)


def _filtro_video_normalizado() -> str:
    w = LARGURA_NORMALIZADA_VIDEO_ENTRADA_TRANSCRIBROTHERS
    h = ALTURA_NORMALIZADA_VIDEO_ENTRADA_TRANSCRIBROTHERS
    fps = FPS_NORMALIZADO_VIDEO_ENTRADA_TRANSCRIBROTHERS
    return (
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={fps},setsar=1,format=yuv420p[vout]"
    )


async def _normalizar_um_video_entrada_para_mp4_intermediario_transcribrothers(
    *,
    caminho_entrada: Path,
    caminho_saida_mp4: Path,
    tem_audio: bool,
) -> None:
    filtro_v = _filtro_video_normalizado()
    sr = SAMPLE_RATE_AUDIO_NORMALIZADO_TRANSCRIBROTHERS
    if tem_audio:
        filtro = f"{filtro_v};[0:a]aformat=sample_rates={sr}:channel_layouts=stereo[aout]"
        args = [
            "-y",
            "-i",
            str(caminho_entrada),
            "-filter_complex",
            filtro,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(caminho_saida_mp4),
        ]
    else:
        filtro = (
            f"{filtro_v};"
            f"anullsrc=channel_layout=stereo:sample_rate={sr}[aSilent];"
            f"[aSilent]aformat=sample_rates={sr}:channel_layouts=stereo[aout]"
        )
        args = [
            "-y",
            "-i",
            str(caminho_entrada),
            "-filter_complex",
            filtro,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(caminho_saida_mp4),
        ]
    await executar_ffmpeg_com_argumentos(args)
    if not caminho_saida_mp4.is_file() or caminho_saida_mp4.stat().st_size <= 0:
        raise RuntimeError(f"ffmpeg não gerou o intermediário normalizado: {caminho_saida_mp4.name}")


async def _concat_via_reencode_normalizado_transcribrothers(
    *,
    caminho_video_a: Path,
    caminho_video_b: Path,
    caminho_saida: Path,
) -> None:
    tem_a = await midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers(caminho_video_a)
    tem_b = await midia_entrada_tem_stream_audio_via_ffprobe_transcribrothers(caminho_video_b)

    with tempfile.TemporaryDirectory(prefix="tb_concat_entrada_") as tmp:
        dir_tmp = Path(tmp)
        norm_a = dir_tmp / "norm_a.mp4"
        norm_b = dir_tmp / "norm_b.mp4"
        await _normalizar_um_video_entrada_para_mp4_intermediario_transcribrothers(
            caminho_entrada=caminho_video_a,
            caminho_saida_mp4=norm_a,
            tem_audio=tem_a,
        )
        await _normalizar_um_video_entrada_para_mp4_intermediario_transcribrothers(
            caminho_entrada=caminho_video_b,
            caminho_saida_mp4=norm_b,
            tem_audio=tem_b,
        )

        lista_concat = dir_tmp / "lista_concat_videos_entrada.txt"
        _escrever_lista_concat_demuxer([norm_a, norm_b], lista_concat)
        args_concat = [
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista_concat),
            "-c",
            "copy",
            str(caminho_saida),
        ]
        await executar_ffmpeg_com_argumentos(args_concat)


async def concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
    *,
    caminho_video_a: Path,
    caminho_video_b: Path,
    caminho_saida: Path,
) -> ResultadoConcatenacaoVideosEntradaTranscribrothers:
    if not caminho_video_a.is_file():
        raise FileNotFoundError(f"Vídeo A não encontrado: {caminho_video_a}")
    if not caminho_video_b.is_file():
        raise FileNotFoundError(f"Vídeo B não encontrado: {caminho_video_b}")

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_saida.exists():
        caminho_saida.unlink()

    perfil_a = await obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers(caminho_video_a)
    perfil_b = await obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers(caminho_video_b)
    mesma_extensao = caminho_video_a.suffix.lower() == caminho_video_b.suffix.lower()
    tentar_copy = (
        mesma_extensao
        and perfil_a is not None
        and perfil_b is not None
        and perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(perfil_a, perfil_b)
    )

    if tentar_copy:
        try:
            await _concat_demuxer_stream_copy_transcribrothers(
                caminho_video_a=caminho_video_a,
                caminho_video_b=caminho_video_b,
                caminho_saida=caminho_saida,
            )
            if caminho_saida.is_file() and caminho_saida.stat().st_size > 0:
                _logger.info(
                    "concat video_entrada modo=stream_copy a=%s b=%s saida=%s",
                    caminho_video_a.name,
                    caminho_video_b.name,
                    caminho_saida.name,
                )
                return ResultadoConcatenacaoVideosEntradaTranscribrothers(
                    caminho_saida=caminho_saida,
                    modo="stream_copy",
                )
        except ErroFfmpegTranscribrothers as exc:
            _logger.warning(
                "stream_copy falhou; fallback reencode. a=%s b=%s erro=%s",
                caminho_video_a.name,
                caminho_video_b.name,
                exc,
            )
            caminho_saida.unlink(missing_ok=True)

    # Reencode sempre produz MP4 H.264/AAC (mesmo se o pedido tinha outra extensão).
    saida_reencode = (
        caminho_saida
        if caminho_saida.suffix.lower() == ".mp4"
        else caminho_saida.with_suffix(".mp4")
    )
    if saida_reencode.exists():
        saida_reencode.unlink()
    await _concat_via_reencode_normalizado_transcribrothers(
        caminho_video_a=caminho_video_a,
        caminho_video_b=caminho_video_b,
        caminho_saida=saida_reencode,
    )
    if not saida_reencode.is_file() or saida_reencode.stat().st_size <= 0:
        raise RuntimeError("ffmpeg concluiu o concat sem gerar o MP4 unificado de entrada.")
    _logger.info(
        "concat video_entrada modo=reencode a=%s b=%s saida=%s",
        caminho_video_a.name,
        caminho_video_b.name,
        saida_reencode.name,
    )
    return ResultadoConcatenacaoVideosEntradaTranscribrothers(
        caminho_saida=saida_reencode,
        modo="reencode",
    )
