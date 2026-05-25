import asyncio
import json
import subprocess
from pathlib import Path

from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    resolver_caminho_ffprobe_transcribrothers,
)


def _parsear_duracao_tag_sexagesimal_ffprobe_transcribrothers(valor: str) -> float:
    bruto = (valor or "").strip()
    if not bruto:
        return 0.0
    try:
        numero = float(bruto)
        return numero if numero > 0 else 0.0
    except ValueError:
        pass
    partes = bruto.split(":")
    try:
        if len(partes) == 3:
            horas, minutos, segundos = partes
            return int(horas) * 3600 + int(minutos) * 60 + float(segundos)
        if len(partes) == 2:
            minutos, segundos = partes
            return int(minutos) * 60 + float(segundos)
    except ValueError:
        return 0.0
    return 0.0


def _duracao_de_tags_formato_ffprobe_transcribrothers(formato: dict) -> float:
    tags = formato.get("tags")
    if not isinstance(tags, dict):
        return 0.0
    for chave in ("DURATION", "duration", "Duration"):
        bruto = tags.get(chave)
        if bruto is None:
            continue
        dur = _parsear_duracao_tag_sexagesimal_ffprobe_transcribrothers(str(bruto))
        if dur > 0:
            return dur
    return 0.0


def _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers(data: dict) -> float:
    formato = data.get("format") if isinstance(data.get("format"), dict) else {}
    dur_formato = float(formato.get("duration") or 0.0)
    if dur_formato > 0:
        return dur_formato
    dur_tags = _duracao_de_tags_formato_ffprobe_transcribrothers(formato)
    if dur_tags > 0:
        return dur_tags
    streams = data.get("streams")
    if not isinstance(streams, list):
        return 0.0
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        if stream.get("codec_type") != "video":
            continue
        dur_stream = float(stream.get("duration") or 0.0)
        if dur_stream > 0:
            return dur_stream
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        dur_stream = float(stream.get("duration") or 0.0)
        if dur_stream > 0:
            return dur_stream
    return 0.0


def _executar_ffprobe_duracao_json_sync(
    executavel_ffprobe: str,
    caminho_video: str,
    *,
    probesize: str | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Mesma razão do ffmpeg: evitar `create_subprocess_exec` no Windows com loop incompatível."""
    args = [
        executavel_ffprobe,
        "-v",
        "error",
    ]
    if probesize:
        args.extend(["-probesize", probesize, "-analyzeduration", probesize])
    args.extend(
        [
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            caminho_video,
        ]
    )
    return subprocess.run(args, capture_output=True, check=False)


def _executar_ffprobe_ultimo_pts_video_sync(
    executavel_ffprobe: str,
    caminho_video: str,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            executavel_ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "packet=pts_time",
            "-of",
            "csv=p=0",
            caminho_video,
        ],
        capture_output=True,
        check=False,
    )


def _duracao_pelo_ultimo_pts_video_ffprobe_transcribrothers(
    executavel_ffprobe: str,
    caminho_video: Path,
) -> float:
    if caminho_video.suffix.lower() != ".webm":
        return 0.0
    proc = _executar_ffprobe_ultimo_pts_video_sync(executavel_ffprobe, str(caminho_video))
    if proc.returncode != 0:
        return 0.0
    texto = (proc.stdout or b"").decode(errors="replace").strip()
    if not texto:
        return 0.0
    ultima_linha = ""
    for linha in texto.splitlines():
        linha_limpa = linha.strip()
        if linha_limpa:
            ultima_linha = linha_limpa
    if not ultima_linha:
        return 0.0
    try:
        dur = float(ultima_linha)
    except ValueError:
        return 0.0
    return dur if dur > 0 else 0.0


def _obter_duracao_video_segundos_via_ffprobe_sync(caminho_video: Path) -> float:
    executavel = resolver_caminho_ffprobe_transcribrothers()
    if not executavel:
        return 0.0
    if not caminho_video.is_file():
        return 0.0

    for probesize in (None, "32M"):
        proc = _executar_ffprobe_duracao_json_sync(executavel, str(caminho_video), probesize=probesize)
        stdout = proc.stdout or b""
        if proc.returncode != 0:
            continue
        try:
            data = json.loads(stdout.decode() or "{}")
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        dur = _extrair_duracao_segundos_de_saida_json_ffprobe_transcribrothers(data)
        if dur > 0:
            return dur

    return _duracao_pelo_ultimo_pts_video_ffprobe_transcribrothers(executavel, caminho_video)


async def obter_duracao_video_segundos_via_ffprobe(caminho_video: Path) -> float:
    return await asyncio.to_thread(_obter_duracao_video_segundos_via_ffprobe_sync, caminho_video)
