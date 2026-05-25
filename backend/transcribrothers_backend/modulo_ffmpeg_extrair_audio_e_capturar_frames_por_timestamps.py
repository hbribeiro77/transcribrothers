import asyncio
import subprocess
from pathlib import Path

from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    ffmpeg_disponivel_transcribrothers,
    resolver_caminho_ffmpeg_transcribrothers,
)


class ErroFfmpegTranscribrothers(RuntimeError):
    pass


def limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
    timestamp_segundos: float,
    duracao_video_segundos: float,
    *,
    margem_segundos_antes_do_fim: float = 0.05,
) -> float:
    """Evita seek além do último frame: segmentos de transcrição podem ir alguns décimos além da duração do container."""
    t = max(0.0, float(timestamp_segundos))
    d = float(duracao_video_segundos)
    if d <= 0:
        return t
    ultimo_instante_seguro = max(0.0, d - float(margem_segundos_antes_do_fim))
    return min(t, ultimo_instante_seguro)


def _ffmpeg_disponivel() -> bool:
    return ffmpeg_disponivel_transcribrothers()


def _executar_ffmpeg_subprocess_run_sync(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Roda ffmpeg no thread pool: no Windows, `asyncio.create_subprocess_exec` pode levantar `NotImplementedError` com `WindowsSelectorEventLoop`."""
    executavel = resolver_caminho_ffmpeg_transcribrothers()
    if not executavel:
        raise ErroFfmpegTranscribrothers("ffmpeg não encontrado no PATH. Instale ffmpeg e reinicie o terminal.")
    return subprocess.run(
        [executavel, *args],
        capture_output=True,
        check=False,
    )


async def executar_ffmpeg_com_argumentos(args: list[str]) -> None:
    if not _ffmpeg_disponivel():
        raise ErroFfmpegTranscribrothers(
            "ffmpeg não encontrado no PATH. Instale ffmpeg e reinicie o terminal."
        )

    proc = await asyncio.to_thread(_executar_ffmpeg_subprocess_run_sync, args)
    if proc.returncode != 0:
        msg = (proc.stderr or b"").decode(errors="replace")[-4000:]
        raise ErroFfmpegTranscribrothers(f"ffmpeg falhou (código {proc.returncode}): {msg}")


async def extrair_audio_wav_de_video_para_caminho(
    *,
    caminho_video: Path,
    caminho_audio_wav: Path,
    forcar_mono: bool = True,
) -> None:
    caminho_audio_wav.parent.mkdir(parents=True, exist_ok=True)
    args: list[str] = [
        "-y",
        "-i",
        str(caminho_video),
        "-vn",
        "-acodec",
        "pcm_s16le",
    ]
    if forcar_mono:
        args.extend(["-ar", "16000", "-ac", "1"])
    else:
        args.extend(["-ar", "48000", "-ac", "2"])
    args.append(str(caminho_audio_wav))
    await executar_ffmpeg_com_argumentos(args)


async def extrair_trecho_wav_de_arquivo_wav_por_inicio_e_duracao_segundos_para_caminho(
    *,
    caminho_wav_entrada: Path,
    inicio_segundos: float,
    duracao_segundos: float,
    caminho_wav_saida: Path,
) -> None:
    """Recorta um trecho do WAV (pcm_s16le mono 16k) com `-c copy` quando possível."""
    if duracao_segundos <= 0:
        raise ErroFfmpegTranscribrothers("Duração do trecho WAV deve ser positiva.")
    caminho_wav_saida.parent.mkdir(parents=True, exist_ok=True)
    ini = max(0.0, float(inicio_segundos))
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-ss",
            f"{ini:.3f}",
            "-i",
            str(caminho_wav_entrada),
            "-t",
            f"{float(duracao_segundos):.3f}",
            "-c",
            "copy",
            str(caminho_wav_saida),
        ]
    )


def _args_canais_audio_ffmpeg_transcribrothers(forcar_mono: bool) -> list[str]:
    return ["-ac", "1"] if forcar_mono else ["-ac", "2"]


async def converter_wav_para_mp3_para_caminho_transcribrothers(
    *,
    caminho_wav_entrada: Path,
    caminho_mp3_saida: Path,
    bitrate_kbps: int = 96,
    forcar_mono: bool = True,
) -> None:
    """Codifica o WAV extraído do vídeo em MP3 (libmp3lame) para envio inline menor ao gateway."""
    br = max(16, min(320, int(bitrate_kbps)))
    caminho_mp3_saida.parent.mkdir(parents=True, exist_ok=True)
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-i",
            str(caminho_wav_entrada),
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            f"{br}k",
            str(caminho_mp3_saida),
        ]
    )


async def converter_wav_para_opus_ogg_para_caminho_transcribrothers(
    *,
    caminho_wav_entrada: Path,
    caminho_opus_saida: Path,
    bitrate_kbps: int = 48,
    forcar_mono: bool = True,
) -> None:
    br = max(16, min(256, int(bitrate_kbps)))
    caminho_opus_saida.parent.mkdir(parents=True, exist_ok=True)
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-i",
            str(caminho_wav_entrada),
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "libopus",
            "-b:a",
            f"{br}k",
            str(caminho_opus_saida),
        ]
    )


async def converter_wav_para_aac_m4a_para_caminho_transcribrothers(
    *,
    caminho_wav_entrada: Path,
    caminho_m4a_saida: Path,
    bitrate_kbps: int = 96,
    forcar_mono: bool = True,
) -> None:
    br = max(16, min(320, int(bitrate_kbps)))
    caminho_m4a_saida.parent.mkdir(parents=True, exist_ok=True)
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-i",
            str(caminho_wav_entrada),
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "aac",
            "-b:a",
            f"{br}k",
            str(caminho_m4a_saida),
        ]
    )


async def extrair_trecho_mp3_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
    *,
    caminho_audio_entrada: Path,
    inicio_segundos: float,
    duracao_segundos: float,
    caminho_mp3_saida: Path,
    bitrate_kbps: int = 96,
    forcar_mono: bool = True,
) -> None:
    """Recorta trecho temporal e codifica em MP3 (entrada WAV ou MP3)."""
    if duracao_segundos <= 0:
        raise ErroFfmpegTranscribrothers("Duração do trecho MP3 deve ser positiva.")
    br = max(16, min(320, int(bitrate_kbps)))
    caminho_mp3_saida.parent.mkdir(parents=True, exist_ok=True)
    ini = max(0.0, float(inicio_segundos))
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-ss",
            f"{ini:.3f}",
            "-i",
            str(caminho_audio_entrada),
            "-t",
            f"{float(duracao_segundos):.3f}",
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            f"{br}k",
            str(caminho_mp3_saida),
        ]
    )


async def extrair_trecho_opus_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
    *,
    caminho_audio_entrada: Path,
    inicio_segundos: float,
    duracao_segundos: float,
    caminho_opus_saida: Path,
    bitrate_kbps: int = 48,
    forcar_mono: bool = True,
) -> None:
    if duracao_segundos <= 0:
        raise ErroFfmpegTranscribrothers("Duração do trecho Opus deve ser positiva.")
    br = max(16, min(256, int(bitrate_kbps)))
    caminho_opus_saida.parent.mkdir(parents=True, exist_ok=True)
    ini = max(0.0, float(inicio_segundos))
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-ss",
            f"{ini:.3f}",
            "-i",
            str(caminho_audio_entrada),
            "-t",
            f"{float(duracao_segundos):.3f}",
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "libopus",
            "-b:a",
            f"{br}k",
            str(caminho_opus_saida),
        ]
    )


async def extrair_trecho_aac_m4a_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
    *,
    caminho_audio_entrada: Path,
    inicio_segundos: float,
    duracao_segundos: float,
    caminho_m4a_saida: Path,
    bitrate_kbps: int = 96,
    forcar_mono: bool = True,
) -> None:
    if duracao_segundos <= 0:
        raise ErroFfmpegTranscribrothers("Duração do trecho AAC deve ser positiva.")
    br = max(16, min(320, int(bitrate_kbps)))
    caminho_m4a_saida.parent.mkdir(parents=True, exist_ok=True)
    ini = max(0.0, float(inicio_segundos))
    await executar_ffmpeg_com_argumentos(
        [
            "-y",
            "-ss",
            f"{ini:.3f}",
            "-i",
            str(caminho_audio_entrada),
            "-t",
            f"{float(duracao_segundos):.3f}",
            "-vn",
            *_args_canais_audio_ffmpeg_transcribrothers(forcar_mono),
            "-codec:a",
            "aac",
            "-b:a",
            f"{br}k",
            str(caminho_m4a_saida),
        ]
    )


async def capturar_frames_png_do_video_nos_timestamps_segundos(
    *,
    caminho_video: Path,
    timestamps_segundos: list[float],
    diretorio_saida_frames: Path,
    prefixo_nome_arquivo_longo_descritivo: str,
    largura_maxima_saida_pixeis: int | None = None,
    deslocamento_indice_nome_arquivo: int = 0,
) -> list[Path]:
    """Extrai um PNG por timestamp. `deslocamento_indice_nome_arquivo` evita colisão de nomes quando
    várias chamadas usam um único timestamp por vez (ex.: pipeline) e o offset em ms coincide após arredondamento."""
    diretorio_saida_frames.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []
    vf_scale: list[str] | None = None
    if largura_maxima_saida_pixeis is not None and largura_maxima_saida_pixeis > 0:
        w = int(largura_maxima_saida_pixeis)
        vf_scale = ["-vf", f"scale=min({w}\\,iw):-2"]
    for idx, t in enumerate(timestamps_segundos):
        indice_nome = int(deslocamento_indice_nome_arquivo) + int(idx)
        ms = int(round(max(0.0, t) * 1000))
        nome = (
            f"{prefixo_nome_arquivo_longo_descritivo}_frame_no_offset_ms_{ms:010d}_indice_{indice_nome:04d}.png"
        )
        destino = diretorio_saida_frames / nome
        args = [
            "-y",
            "-ss",
            f"{max(0.0, t):.3f}",
            "-i",
            str(caminho_video),
        ]
        if vf_scale:
            args.extend(vf_scale)
        args.extend(
            [
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(destino),
            ]
        )
        await executar_ffmpeg_com_argumentos(args)
        if not destino.is_file() or destino.stat().st_size <= 0:
            raise ErroFfmpegTranscribrothers(
                "ffmpeg encerrou sem gerar um PNG válido no caminho esperado: "
                f"{destino} (timestamp_s={t!r}, vídeo={caminho_video}). "
                "Confira se o timestamp não ultrapassa a duração real do arquivo, permissões da pasta "
                "e se o antivírus não removeu o arquivo logo após a gravação."
            )
        gerados.append(destino)
    return gerados


def reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers(
    indices: list[int],
    max_itens: int,
) -> list[int]:
    """Reduz uma lista ordenada de índices mantendo extremos e distribuição aproximadamente uniforme."""
    if max_itens <= 0 or len(indices) <= max_itens:
        return indices
    if max_itens == 1:
        return [indices[0]]
    step = (len(indices) - 1) / (max_itens - 1)
    escolhidos: list[int] = []
    for i in range(max_itens):
        j = int(round(i * step))
        escolhidos.append(indices[min(j, len(indices) - 1)])
    unicos: list[int] = []
    vistos: set[int] = set()
    for x in escolhidos:
        if x not in vistos:
            vistos.add(x)
            unicos.append(x)
    return unicos


def amostrar_timestamps_por_limite_por_minuto(
    timestamps_segundos: list[float],
    *,
    max_por_minuto: int,
    duracao_video_segundos: float,
) -> list[float]:
    indices = amostrar_indices_por_limite_por_minuto(
        n_itens=len(timestamps_segundos),
        max_por_minuto=max_por_minuto,
        duracao_video_segundos=duracao_video_segundos,
    )
    return [timestamps_segundos[i] for i in indices]


def amostrar_indices_por_limite_por_minuto(
    *,
    n_itens: int,
    max_por_minuto: int,
    duracao_video_segundos: float,
) -> list[int]:
    if n_itens <= 0:
        return []
    if max_por_minuto <= 0:
        return list(range(n_itens))
    duracao = max(1.0, duracao_video_segundos)
    max_total = max(1, int((duracao / 60.0) * max_por_minuto))
    if n_itens <= max_total:
        return list(range(n_itens))
    step = (n_itens - 1) / max(1, max_total - 1)
    escolhidos: list[int] = []
    for i in range(max_total):
        j = int(round(i * step))
        j = min(j, n_itens - 1)
        escolhidos.append(j)
    return escolhidos
