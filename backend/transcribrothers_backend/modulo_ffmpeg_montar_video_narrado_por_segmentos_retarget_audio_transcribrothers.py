"""Monta MP4 narrado: corta janela do vídeo por cue, retarget à duração do WAV e concatena."""

from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    executar_ffmpeg_com_argumentos,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    obter_duracao_wav_pcm16_mono_segundos_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
    montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)

_DURACAO_SRC_MINIMA_PARA_SETPTS_SEGUNDOS = 0.35
_DURACAO_PRECORTE_JANELA_CURTA_SEGUNDOS = 0.12
_EPS_AUDIO_VS_VIDEO_SEGUNDOS = 0.05
_NOME_SUBPASTA_SEGMENTOS = "segmentos_video_narrado_retarget"
_NOME_SUBPASTA_PRECORTE = "clips_precorte_janelas_video"
_VERSAO_CACHE_SEGMENTO = "retarget_v5_encode_prefs_scale_fps"
_PRESET_X264 = "ultrafast"
_CRF_X264 = "28"
# Com -threads 1 por processo, dá para subir o paralelismo sem briga de CPU.
_PARALELISMO_ENCODE_SEGMENTOS_PADRAO = 8
_MAX_SEGMENTOS_PASSAGEM_UNICA = 80
_ENCODER_VIDEO_CACHE: str | None = None

AtualizarProgressoMontagemSegmentosTranscribrothers = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(frozen=True)
class SegmentoVideoNarradoRetargetTranscribrothers:
    caminho_wav: Path
    inicio_video_segundos: float
    fim_video_segundos: float


def _metadados_arquivo_para_cache_transcribrothers(caminho: Path) -> str:
    st = caminho.stat()
    return f"{st.st_mtime_ns}:{st.st_size}:{caminho.resolve()}"


def calcular_chave_cache_segmento_retarget_audio_transcribrothers(
    *,
    caminho_video: Path,
    segmento: SegmentoVideoNarradoRetargetTranscribrothers,
    duracao_audio_segundos: float,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    """Fingerprint estável: reusa o MP4 do segmento se vídeo/WAV/janela/encode não mudaram."""
    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    ini = max(0.0, float(segmento.inicio_video_segundos))
    fim = max(ini, float(segmento.fim_video_segundos))
    payload = "|".join(
        [
            _VERSAO_CACHE_SEGMENTO,
            _metadados_arquivo_para_cache_transcribrothers(caminho_video),
            _metadados_arquivo_para_cache_transcribrothers(segmento.caminho_wav),
            f"{ini:.6f}",
            f"{fim:.6f}",
            f"{float(duracao_audio_segundos):.6f}",
            _PRESET_X264,
            _CRF_X264,
            prefs.chave_cache_transcribrothers(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resolver_paralelismo_encode_segmentos_transcribrothers(
    solicitado: int | None = None,
) -> int:
    if solicitado is not None and solicitado >= 1:
        return min(32, int(solicitado))
    env = (os.environ.get("TRANSCRIBROTHERS_FFMPEG_SEGMENTOS_PARALELOS") or "").strip()
    if env.isdigit() and int(env) >= 1:
        return min(32, int(env))
    cpus = os.cpu_count() or 2
    return max(1, min(_PARALELISMO_ENCODE_SEGMENTOS_PADRAO, max(1, cpus)))


def _ffmpeg_tem_encoder_transcribrothers(nome_encoder: str) -> bool:
    try:
        proc = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    texto = f"{proc.stdout}\n{proc.stderr}"
    return f" {nome_encoder} " in f" {texto} "


def resolver_encoder_video_montagem_narrado_transcribrothers(
    *,
    forcar_libx264: bool = False,
) -> str:
    """
    Preferência: h264_nvenc (GPU) quando disponível — um encode único fica bem mais rápido.
    Override: TRANSCRIBROTHERS_FFMPEG_ENCODER=libx264|h264_nvenc|auto
    """
    global _ENCODER_VIDEO_CACHE
    if forcar_libx264:
        return "libx264"
    env = (os.environ.get("TRANSCRIBROTHERS_FFMPEG_ENCODER") or "auto").strip().lower()
    if env in {"libx264", "x264", "cpu"}:
        return "libx264"
    if env in {"h264_nvenc", "nvenc", "gpu"}:
        return "h264_nvenc"
    if _ENCODER_VIDEO_CACHE is not None:
        return _ENCODER_VIDEO_CACHE
    _ENCODER_VIDEO_CACHE = (
        "h264_nvenc" if _ffmpeg_tem_encoder_transcribrothers("h264_nvenc") else "libx264"
    )
    return _ENCODER_VIDEO_CACHE


def _argumentos_encoder_video_transcribrothers(encoder: str) -> list[str]:
    if encoder == "h264_nvenc":
        return [
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p1",
            "-cq",
            "28",
            "-pix_fmt",
            "yuv420p",
        ]
    return [
        "-c:v",
        "libx264",
        "-preset",
        _PRESET_X264,
        "-crf",
        _CRF_X264,
        "-pix_fmt",
        "yuv420p",
    ]


def calcular_duracao_precorte_clip_janela_video_transcribrothers(
    inicio_video_segundos: float,
    fim_video_segundos: float,
    *,
    duracao_audio_segundos: float,
) -> float:
    """
    Duração do clip extraído da origem — limitada à fala.

    - Janela >> WAV: corta só ~duração do WAV (play 1× do início da janela).
    - WAV > janela: corta a janela; o filter completa com freeze.
    - Janela minúscula: pedaço mínimo para freeze.
    """
    ini = max(0.0, float(inicio_video_segundos))
    fim = max(ini, float(fim_video_segundos))
    dur_janela = max(0.0, fim - ini)
    dur_audio = max(0.05, float(duracao_audio_segundos))
    if dur_janela < _DURACAO_SRC_MINIMA_PARA_SETPTS_SEGUNDOS:
        return _DURACAO_PRECORTE_JANELA_CURTA_SEGUNDOS
    if dur_audio <= dur_janela:
        return dur_audio
    return dur_janela


def segmentos_aceitam_montagem_passagem_unica_transcribrothers(
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    *,
    duracoes_audio_segundos: list[float],
) -> bool:
    """Passagem única aceita cues curtas (freeze) e longas (play 1× / tpad)."""
    if not segmentos:
        return False
    if len(segmentos) != len(duracoes_audio_segundos):
        return False
    if len(segmentos) > _MAX_SEGMENTOS_PASSAGEM_UNICA:
        return False
    for dur in duracoes_audio_segundos:
        if float(dur) <= 0.05:
            return False
    return True


def _filtro_video_passagem_unica_um_segmento_transcribrothers(
    *,
    idx_v: int,
    indice_saida: int,
    dur_src: float,
    dur_audio: float,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    """
    Nunca comprime minutos de tela em segundos de fala (setpts acelerado).
    Play 1× do trecho necessário; se a fala for maior, freeze (tpad/loop).
    """
    dur_a = max(0.05, float(dur_audio))
    dur_s = max(0.0, float(dur_src))
    scale = montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(
        preferencias_encode
    )
    if dur_s < _DURACAO_SRC_MINIMA_PARA_SETPTS_SEGUNDOS:
        return (
            f"[{idx_v}:v]trim=start=0:end=0.05,"
            f"loop=loop=-1:size=1:start=0,"
            f"trim=duration={dur_a:.6f},"
            f"setpts=PTS-STARTPTS,{scale}[v{indice_saida}]"
        )
    if dur_a > dur_s + _EPS_AUDIO_VS_VIDEO_SEGUNDOS:
        pad = dur_a - dur_s
        return (
            f"[{idx_v}:v]trim=duration={dur_s:.6f},setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={pad:.6f},"
            f"{scale},setpts=PTS-STARTPTS[v{indice_saida}]"
        )
    return (
        f"[{idx_v}:v]trim=duration={dur_a:.6f},setpts=PTS-STARTPTS,"
        f"{scale}[v{indice_saida}]"
    )


def montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    *,
    duracoes_audio_segundos: list[float],
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    """
    Pares de input (vídeo cortado com -ss/-t, WAV): índices 0,2,4… = vídeo; 1,3,5… = áudio.
    Um encode no fim (concat no filter) — evita N encodes separados.
    """
    if len(segmentos) != len(duracoes_audio_segundos):
        raise ValueError("Quantidade de durações não bate com segmentos.")
    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    linhas: list[str] = []
    elos: list[str] = []
    for i, (seg, dur_audio) in enumerate(
        zip(segmentos, duracoes_audio_segundos, strict=True)
    ):
        ini = max(0.0, float(seg.inicio_video_segundos))
        fim = max(ini, float(seg.fim_video_segundos))
        dur_src = max(0.0, fim - ini)
        dur_a = max(0.05, float(dur_audio))
        idx_v = i * 2
        idx_a = i * 2 + 1
        linhas.append(
            _filtro_video_passagem_unica_um_segmento_transcribrothers(
                idx_v=idx_v,
                indice_saida=i,
                dur_src=dur_src,
                dur_audio=dur_a,
                preferencias_encode=prefs,
            )
        )
        linhas.append(
            f"[{idx_a}:a]atrim=0:{dur_a:.6f},asetpts=PTS-STARTPTS,"
            f"aformat=sample_fmts=fltp:channel_layouts=mono[a{i}]"
        )
        elos.append(f"[v{i}][a{i}]")
    linhas.append("".join(elos) + f"concat=n={len(segmentos)}:v=1:a=1[vout][aout]")
    return ";\n".join(linhas) + "\n"


def _argumentos_inputs_passagem_unica_a_partir_clips_transcribrothers(
    *,
    caminhos_clips: list[Path],
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
) -> list[str]:
    """Pares clip pré-cortado + WAV (clips já começam em t=0)."""
    if len(caminhos_clips) != len(segmentos):
        raise ValueError("Quantidade de clips não bate com segmentos.")
    args: list[str] = ["-y"]
    for clip, seg in zip(caminhos_clips, segmentos, strict=True):
        args.extend(["-i", str(clip), "-i", str(seg.caminho_wav)])
    return args


async def _extrair_clip_precorte_janela_video_transcribrothers(
    *,
    caminho_video: Path,
    inicio_video_segundos: float,
    duracao_corte_segundos: float,
    caminho_clip_saida: Path,
) -> None:
    """
    Extrai só a janela da origem para um MP4 pequeno.
    Tenta stream copy (rápido); se falhar, reencode ultrafast só desse pedaço.
    """
    ini = max(0.0, float(inicio_video_segundos))
    dur = max(_DURACAO_PRECORTE_JANELA_CURTA_SEGUNDOS, float(duracao_corte_segundos))
    caminho_clip_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_clip_saida.is_file():
        caminho_clip_saida.unlink()

    args_copy = [
        "-y",
        "-ss",
        f"{ini:.6f}",
        "-t",
        f"{dur:.6f}",
        "-i",
        str(caminho_video),
        "-an",
        "-c:v",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        str(caminho_clip_saida),
    ]
    try:
        await executar_ffmpeg_com_argumentos(args_copy)
        if caminho_clip_saida.is_file() and caminho_clip_saida.stat().st_size > 0:
            return
    except Exception:
        if caminho_clip_saida.is_file():
            caminho_clip_saida.unlink()

    args_reencode = [
        "-y",
        "-ss",
        f"{ini:.6f}",
        "-i",
        str(caminho_video),
        "-t",
        f"{dur:.6f}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        _PRESET_X264,
        "-crf",
        _CRF_X264,
        "-pix_fmt",
        "yuv420p",
        "-threads",
        "1",
        str(caminho_clip_saida),
    ]
    await executar_ffmpeg_com_argumentos(args_reencode)
    if not caminho_clip_saida.is_file() or caminho_clip_saida.stat().st_size <= 0:
        raise RuntimeError(f"ffmpeg não gerou o clip pré-corte {caminho_clip_saida.name}.")


async def _extrair_clips_precorte_janelas_em_paralelo_transcribrothers(
    *,
    caminho_video: Path,
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    duracoes_audio_segundos: list[float],
    diretorio_clips: Path,
    atualizar_progresso: AtualizarProgressoMontagemSegmentosTranscribrothers | None,
    paralelismo: int | None = None,
) -> tuple[list[Path], list[float]]:
    """Corta da origem só o necessário para cada fala (com -t), em paralelo."""
    if len(segmentos) != len(duracoes_audio_segundos):
        raise ValueError("Quantidade de durações de áudio não bate com segmentos.")
    diretorio_clips.mkdir(parents=True, exist_ok=True)
    total = len(segmentos)
    workers = _resolver_paralelismo_encode_segmentos_transcribrothers(paralelismo)
    semaforo = asyncio.Semaphore(workers)
    progresso_lock = asyncio.Lock()
    concluidos = 0
    caminhos: list[Path | None] = [None] * total
    duracoes: list[float] = [0.0] * total

    async def _um(indice: int, seg: SegmentoVideoNarradoRetargetTranscribrothers) -> None:
        nonlocal concluidos
        dur_corte = calcular_duracao_precorte_clip_janela_video_transcribrothers(
            seg.inicio_video_segundos,
            seg.fim_video_segundos,
            duracao_audio_segundos=float(duracoes_audio_segundos[indice]),
        )
        destino = diretorio_clips / f"clip_precorte_{indice:04d}.mp4"
        async with semaforo:
            await _extrair_clip_precorte_janela_video_transcribrothers(
                caminho_video=caminho_video,
                inicio_video_segundos=seg.inicio_video_segundos,
                duracao_corte_segundos=dur_corte,
                caminho_clip_saida=destino,
            )
        caminhos[indice] = destino
        duracoes[indice] = dur_corte
        if atualizar_progresso is not None:
            async with progresso_lock:
                concluidos += 1
                await atualizar_progresso(
                    {
                        "video_narrado_mux_fase": "precorte",
                        "video_narrado_mux_segmento_indice": concluidos,
                        "video_narrado_mux_segmento_total": total,
                        "video_narrado_mux_paralelismo": workers,
                    }
                )

    if atualizar_progresso is not None:
        await atualizar_progresso(
            {
                "video_narrado_mux_fase": "precorte",
                "video_narrado_mux_segmento_indice": 0,
                "video_narrado_mux_segmento_total": total,
                "video_narrado_mux_paralelismo": workers,
            }
        )
    await asyncio.gather(*[_um(i, seg) for i, seg in enumerate(segmentos)])
    finais: list[Path] = []
    for i, p in enumerate(caminhos):
        if p is None or not p.is_file():
            raise RuntimeError(f"Clip pré-corte {i} não foi gerado.")
        finais.append(p)
    return finais, duracoes


async def _montar_passagem_unica_filter_complex_transcribrothers(
    *,
    caminho_video: Path,
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    duracoes_audio_segundos: list[float],
    diretorio_trabalho: Path,
    caminho_saida: Path,
    atualizar_progresso: AtualizarProgressoMontagemSegmentosTranscribrothers | None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> Path:
    """
    1) Pré-corta cada janela da origem para um clip pequeno (paralelo, sempre com -t).
    2) Um encode: filter_complex só nos clips + WAVs (não reabre o screencast longo N vezes).
    """
    dir_segs = diretorio_trabalho / _NOME_SUBPASTA_SEGMENTOS
    dir_clips = dir_segs / _NOME_SUBPASTA_PRECORTE
    dir_segs.mkdir(parents=True, exist_ok=True)

    caminhos_clips, duracoes_clips = await _extrair_clips_precorte_janelas_em_paralelo_transcribrothers(
        caminho_video=caminho_video,
        segmentos=segmentos,
        duracoes_audio_segundos=duracoes_audio_segundos,
        diretorio_clips=dir_clips,
        atualizar_progresso=atualizar_progresso,
    )

    # Filter enxerga cada clip em t=0 com a duração do pré-corte.
    segmentos_clips = [
        SegmentoVideoNarradoRetargetTranscribrothers(
            caminho_wav=seg.caminho_wav,
            inicio_video_segundos=0.0,
            fim_video_segundos=dur_clip,
        )
        for seg, dur_clip in zip(segmentos, duracoes_clips, strict=True)
    ]

    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    script_path = dir_segs / "filter_complex_passagem_unica_retarget.txt"
    script = montar_script_filter_complex_passagem_unica_retarget_transcribrothers(
        segmentos_clips,
        duracoes_audio_segundos=duracoes_audio_segundos,
        preferencias_encode=prefs,
    )
    script_path.write_text(script, encoding="utf-8", newline="\n")

    encoder = resolver_encoder_video_montagem_narrado_transcribrothers()
    if atualizar_progresso is not None:
        await atualizar_progresso(
            {
                "video_narrado_mux_fase": "passagem_unica",
                "video_narrado_mux_segmento_indice": 0,
                "video_narrado_mux_segmento_total": len(segmentos),
                "video_narrado_mux_paralelismo": 1,
                "video_narrado_mux_segmentos_cache": 0,
                "video_narrado_mux_encoder": encoder,
                "video_narrado_mux_encode_resolucao": prefs.resolucao,
                "video_narrado_mux_encode_fps": int(prefs.fps),
            }
        )

    base_args = _argumentos_inputs_passagem_unica_a_partir_clips_transcribrothers(
        caminhos_clips=caminhos_clips,
        segmentos=segmentos_clips,
    )
    cauda = [
        "-filter_complex_script",
        str(script_path),
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        *_argumentos_encoder_video_transcribrothers(encoder),
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(caminho_saida),
    ]

    if caminho_saida.is_file():
        caminho_saida.unlink()
    try:
        await executar_ffmpeg_com_argumentos([*base_args, *cauda])
    except Exception:
        if encoder != "h264_nvenc":
            raise
        if atualizar_progresso is not None:
            await atualizar_progresso(
                {
                    "video_narrado_mux_fase": "passagem_unica",
                    "video_narrado_mux_encoder": "libx264",
                    "video_narrado_mux_segmento_total": len(segmentos),
                }
            )
        if caminho_saida.is_file():
            caminho_saida.unlink()
        cauda_cpu = [
            "-filter_complex_script",
            str(script_path),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            *_argumentos_encoder_video_transcribrothers("libx264"),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            str(caminho_saida),
        ]
        await executar_ffmpeg_com_argumentos([*base_args, *cauda_cpu])
        encoder = "libx264"

    if not caminho_saida.is_file():
        raise RuntimeError("ffmpeg (passagem única) não gerou o MP4 narrado.")
    if atualizar_progresso is not None:
        await atualizar_progresso(
            {
                "video_narrado_mux_fase": "passagem_unica_ok",
                "video_narrado_mux_segmento_indice": len(segmentos),
                "video_narrado_mux_segmento_total": len(segmentos),
                "video_narrado_mux_encoder": encoder,
            }
        )
    return caminho_saida


async def _gerar_segmento_mp4_retarget_audio_via_ffmpeg_transcribrothers(
    *,
    caminho_video: Path,
    segmento: SegmentoVideoNarradoRetargetTranscribrothers,
    caminho_mp4_saida: Path,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> None:
    dur_audio = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(segmento.caminho_wav)
    if dur_audio <= 0.05:
        raise RuntimeError(f"WAV de segmento sem duração útil: {segmento.caminho_wav.name}")

    ini = max(0.0, float(segmento.inicio_video_segundos))
    dur_corte = calcular_duracao_precorte_clip_janela_video_transcribrothers(
        segmento.inicio_video_segundos,
        segmento.fim_video_segundos,
        duracao_audio_segundos=dur_audio,
    )
    caminho_mp4_saida.parent.mkdir(parents=True, exist_ok=True)

    # -threads 1: vários encodes em paralelo sem cada um pegar todos os cores.
    threads_args = ["-threads", "1"]
    scale = montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(
        preferencias_encode
    )

    if dur_corte < _DURACAO_SRC_MINIMA_PARA_SETPTS_SEGUNDOS:
        filtro_v = (
            "trim=start=0:end=0.05,"
            "loop=loop=-1:size=1:start=0,"
            f"trim=duration={dur_audio:.6f},"
            f"setpts=PTS-STARTPTS,{scale}"
        )
    elif dur_audio > dur_corte + _EPS_AUDIO_VS_VIDEO_SEGUNDOS:
        pad = dur_audio - dur_corte
        filtro_v = (
            f"trim=duration={dur_corte:.6f},setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={pad:.6f},"
            f"{scale},setpts=PTS-STARTPTS"
        )
    else:
        filtro_v = f"trim=duration={dur_audio:.6f},setpts=PTS-STARTPTS,{scale}"

    args = [
        "-y",
        *threads_args,
        "-ss",
        f"{ini:.6f}",
        "-t",
        f"{dur_corte:.6f}",
        "-i",
        str(caminho_video),
        "-i",
        str(segmento.caminho_wav),
        "-filter_complex",
        f"[0:v]{filtro_v}[v]",
        "-map",
        "[v]",
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-preset",
        _PRESET_X264,
        "-crf",
        _CRF_X264,
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-t",
        f"{dur_audio:.6f}",
        str(caminho_mp4_saida),
    ]

    await executar_ffmpeg_com_argumentos(args)
    if not caminho_mp4_saida.is_file():
        raise RuntimeError(f"ffmpeg não gerou o segmento {caminho_mp4_saida.name}.")


async def _montar_paralelo_com_cache_transcribrothers(
    *,
    caminho_video: Path,
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    diretorio_trabalho: Path,
    caminho_saida: Path,
    atualizar_progresso: AtualizarProgressoMontagemSegmentosTranscribrothers | None,
    paralelismo_encode: int | None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> Path:
    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    dir_segs = diretorio_trabalho / _NOME_SUBPASTA_SEGMENTOS
    dir_segs.mkdir(parents=True, exist_ok=True)
    total = len(segmentos)
    caminhos_seg: list[Path | None] = [None] * total
    paralelismo = _resolver_paralelismo_encode_segmentos_transcribrothers(paralelismo_encode)
    semaforo = asyncio.Semaphore(paralelismo)
    progresso_lock = asyncio.Lock()
    concluidos = 0
    reusados_cache = 0

    async def _atualizar(fase: str, indice: int | None = None) -> None:
        if atualizar_progresso is None:
            return
        payload: dict[str, Any] = {
            "video_narrado_mux_segmento_total": total,
            "video_narrado_mux_fase": fase,
            "video_narrado_mux_paralelismo": paralelismo,
            "video_narrado_mux_segmentos_cache": reusados_cache,
            "video_narrado_mux_encode_resolucao": prefs.resolucao,
            "video_narrado_mux_encode_fps": int(prefs.fps),
        }
        if indice is not None:
            payload["video_narrado_mux_segmento_indice"] = indice
        else:
            payload["video_narrado_mux_segmento_indice"] = concluidos
        await atualizar_progresso(payload)

    async def _processar_um(indice: int, seg: SegmentoVideoNarradoRetargetTranscribrothers) -> None:
        nonlocal concluidos, reusados_cache
        if not seg.caminho_wav.is_file():
            raise FileNotFoundError(f"WAV do segmento {indice} não encontrado: {seg.caminho_wav}")
        dur_audio = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(seg.caminho_wav)
        chave = calcular_chave_cache_segmento_retarget_audio_transcribrothers(
            caminho_video=caminho_video,
            segmento=seg,
            duracao_audio_segundos=dur_audio,
            preferencias_encode=prefs,
        )
        caminho_cache = dir_segs / f"segmento_cache_{chave[:24]}.mp4"
        if caminho_cache.is_file() and caminho_cache.stat().st_size > 0:
            caminhos_seg[indice] = caminho_cache
            async with progresso_lock:
                reusados_cache += 1
                concluidos += 1
                await _atualizar("segmento_cache", concluidos)
            return

        async with semaforo:
            await _gerar_segmento_mp4_retarget_audio_via_ffmpeg_transcribrothers(
                caminho_video=caminho_video,
                segmento=seg,
                caminho_mp4_saida=caminho_cache,
                preferencias_encode=prefs,
            )
        caminhos_seg[indice] = caminho_cache
        async with progresso_lock:
            concluidos += 1
            await _atualizar("segmento", concluidos)

    await _atualizar("iniciando", 0)
    await asyncio.gather(*[_processar_um(i, seg) for i, seg in enumerate(segmentos)])

    caminhos_finais: list[Path] = []
    for i, p in enumerate(caminhos_seg):
        if p is None or not p.is_file():
            raise RuntimeError(f"Segmento {i} não foi gerado.")
        caminhos_finais.append(p)

    await _atualizar("concat", total)

    lista_concat = dir_segs / "lista_concat_segmentos_narrados.txt"
    linhas = []
    for p in caminhos_finais:
        caminho_esc = str(p.resolve()).replace("\\", "/").replace("'", r"'\''")
        linhas.append(f"file '{caminho_esc}'")
    lista_concat.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")

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
    if not caminho_saida.is_file():
        raise RuntimeError("ffmpeg concluiu o concat sem gerar o MP4 narrado.")
    return caminho_saida


async def montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
    *,
    caminho_video: Path,
    segmentos: list[SegmentoVideoNarradoRetargetTranscribrothers],
    diretorio_trabalho: Path,
    diretorio_saida: Path,
    nome_arquivo_saida: str = NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
    atualizar_progresso: AtualizarProgressoMontagemSegmentosTranscribrothers | None = None,
    paralelismo_encode: int | None = None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> Path:
    """
    Preferência: pré-corte paralelo das janelas + 1 encode (filter_complex nos clips).
    Fallback: segmentos em paralelo + cache.
    Encode (resolução/FPS) vem de `preferencias_encode` (padrão app: 1080p @ 30 fps).
    """
    if not caminho_video.is_file():
        raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {caminho_video}")
    if not segmentos:
        raise ValueError("Nenhum segmento de vídeo narrado para montar.")

    for i, seg in enumerate(segmentos):
        if not seg.caminho_wav.is_file():
            raise FileNotFoundError(f"WAV do segmento {i} não encontrado: {seg.caminho_wav}")

    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    saida = diretorio_saida / nome_arquivo_saida
    duracoes = [
        obter_duracao_wav_pcm16_mono_segundos_transcribrothers(s.caminho_wav) for s in segmentos
    ]

    if segmentos_aceitam_montagem_passagem_unica_transcribrothers(
        segmentos,
        duracoes_audio_segundos=duracoes,
    ):
        try:
            return await _montar_passagem_unica_filter_complex_transcribrothers(
                caminho_video=caminho_video,
                segmentos=segmentos,
                duracoes_audio_segundos=duracoes,
                diretorio_trabalho=diretorio_trabalho,
                caminho_saida=saida,
                atualizar_progresso=atualizar_progresso,
                preferencias_encode=prefs,
            )
        except Exception:
            # Fallback seguro se o filter_complex falhar (ffmpeg antigo, etc.).
            if atualizar_progresso is not None:
                await atualizar_progresso(
                    {
                        "video_narrado_mux_fase": "fallback_paralelo",
                        "video_narrado_mux_segmento_total": len(segmentos),
                    }
                )

    return await _montar_paralelo_com_cache_transcribrothers(
        caminho_video=caminho_video,
        segmentos=segmentos,
        diretorio_trabalho=diretorio_trabalho,
        caminho_saida=saida,
        atualizar_progresso=atualizar_progresso,
        paralelismo_encode=paralelismo_encode,
        preferencias_encode=prefs,
    )
