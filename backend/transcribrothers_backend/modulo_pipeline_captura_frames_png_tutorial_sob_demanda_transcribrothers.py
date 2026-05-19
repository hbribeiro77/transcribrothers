"""Captura de frames do vídeo apenas nos instantes pedidos (ex.: links ?t= do rascunho do tutorial)."""

from __future__ import annotations

import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    amostrar_indices_por_limite_por_minuto,
    capturar_frames_png_do_video_nos_timestamps_segundos,
    limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers,
    reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers,
)

_MARGEM_DEDUPE_TIMESTAMPS_CAPTURA_PADRAO_SEGUNDOS = 2.0


def limite_maximo_capturas_frames_tutorial_transcribrothers(
    duracao_video_segundos: float,
    *,
    max_frames_per_minute: int,
    tutorial_max_frames_total: int,
) -> int:
    duracao = max(1.0, float(duracao_video_segundos))
    por_minuto = max(1, int((duracao / 60.0) * max(1, int(max_frames_per_minute))))
    teto = int(tutorial_max_frames_total)
    if teto > 0:
        return min(por_minuto, teto)
    return por_minuto


def _deduplicar_timestamps_segundos_proximos_transcribrothers(
    timestamps: list[float],
    *,
    margem_segundos: float = _MARGEM_DEDUPE_TIMESTAMPS_CAPTURA_PADRAO_SEGUNDOS,
) -> list[float]:
    if not timestamps:
        return []
    ordenados = sorted(float(t) for t in timestamps)
    saida = [ordenados[0]]
    for t in ordenados[1:]:
        if t - saida[-1] >= float(margem_segundos):
            saida.append(t)
    return saida


def _reduzir_timestamps_para_no_maximo_uniforme_transcribrothers(
    timestamps: list[float],
    max_itens: int,
) -> list[float]:
    if max_itens <= 0 or len(timestamps) <= max_itens:
        return list(timestamps)
    if max_itens == 1:
        return [timestamps[0]]
    step = (len(timestamps) - 1) / (max_itens - 1)
    escolhidos: list[float] = []
    for i in range(max_itens):
        j = int(round(i * step))
        escolhidos.append(timestamps[min(j, len(timestamps) - 1)])
    return escolhidos


def extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
    markdown_rascunho_tutorial: str,
    *,
    duracao_video_segundos: float,
    margem_minima_segundos_entre_links_temporais: float,
) -> list[float]:
    """Candidatos `?t=` do rascunho, deduplicados pela margem configurável."""
    dur = max(0.0, float(duracao_video_segundos))
    ts = extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers(
        markdown_rascunho_tutorial
    )
    margem = max(0.5, float(margem_minima_segundos_entre_links_temporais))
    ts = _deduplicar_timestamps_segundos_proximos_transcribrothers(ts, margem_segundos=margem)
    if dur > 0:
        ts = [min(max(0.0, t), dur) for t in ts]
    return ts


def resolver_timestamps_segundos_captura_frames_sob_demanda_tutorial_transcribrothers(
    *,
    markdown_rascunho_tutorial: str,
    transcricao: ResultadoTranscricaoComSegmentos,
    duracao_video_segundos: float,
    max_frames_per_minute: int,
    tutorial_max_frames_total: int,
    margem_minima_segundos_entre_links_temporais: float = _MARGEM_DEDUPE_TIMESTAMPS_CAPTURA_PADRAO_SEGUNDOS,
    timestamps_pre_planejados: list[float] | None = None,
) -> list[float]:
    """Instantes a capturar: candidatos do rascunho (ou pré-planejados); se vazio, fallback na transcrição."""
    dur = max(0.0, float(duracao_video_segundos))
    margem = max(0.5, float(margem_minima_segundos_entre_links_temporais))
    max_total = limite_maximo_capturas_frames_tutorial_transcribrothers(
        dur if dur > 0 else 1.0,
        max_frames_per_minute=max_frames_per_minute,
        tutorial_max_frames_total=tutorial_max_frames_total,
    )

    if timestamps_pre_planejados is not None:
        ts = list(timestamps_pre_planejados)
    else:
        ts = extrair_candidatos_timestamps_captura_do_rascunho_tutorial_transcribrothers(
            markdown_rascunho_tutorial,
            duracao_video_segundos=dur,
            margem_minima_segundos_entre_links_temporais=margem,
        )
    if not ts:
        n_seg = len(transcricao.segmentos)
        indices = list(range(n_seg)) if n_seg else []
        if not indices and dur > 0:
            indices = [0]
        indices = amostrar_indices_por_limite_por_minuto(
            n_itens=len(indices) or 1,
            max_por_minuto=max_frames_per_minute,
            duracao_video_segundos=dur if dur > 0 else 1.0,
        )
        indices = reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers(
            indices,
            tutorial_max_frames_total,
        )
        segmentos = (
            [transcricao.segmentos[i] for i in indices if i < len(transcricao.segmentos)]
            if transcricao.segmentos
            else []
        )
        if not segmentos and dur > 0:
            segmentos = [
                SegmentoTranscricaoComTempo(
                    inicio_segundos=0.0,
                    fim_segundos=max(1.0, dur),
                    texto="",
                )
            ]
        ts = [
            max(0.0, (s.inicio_segundos + s.fim_segundos) / 2.0) for s in segmentos
        ]

    ts = _deduplicar_timestamps_segundos_proximos_transcribrothers(ts, margem_segundos=margem)
    ts = _reduzir_timestamps_para_no_maximo_uniforme_transcribrothers(ts, max_total)
    if not ts:
        ts = [0.0]
    return ts


async def capturar_frames_png_tutorial_para_timestamps_segundos_transcribrothers(
    *,
    caminho_video: Path,
    timestamps_segundos: list[float],
    duracao_video_segundos: float,
    frames_dir: Path,
    assets_dir: Path,
    prefixo_nome_arquivo: str = "screenshot_tutorial_transcribrothers",
    largura_maxima_saida_pixeis: int | None = None,
    ao_atualizar_progresso_captura: (
        Callable[[int, int, float], Awaitable[None]] | None
    ) = None,
) -> list[tuple[float, str]]:
    """Extrai PNGs no vídeo e copia para `assets/`; devolve `(t_segundos, assets/nome.png)`."""
    dur = max(0.0, float(duracao_video_segundos))
    total = len(timestamps_segundos)
    paths: list[Path] = []
    for i, t in enumerate(timestamps_segundos):
        t_extracao = limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
            float(t),
            dur,
        )
        if ao_atualizar_progresso_captura:
            await ao_atualizar_progresso_captura(i + 1, total, float(t_extracao))
        chunk = await capturar_frames_png_do_video_nos_timestamps_segundos(
            caminho_video=caminho_video,
            timestamps_segundos=[float(t_extracao)],
            diretorio_saida_frames=frames_dir,
            prefixo_nome_arquivo_longo_descritivo=prefixo_nome_arquivo,
            largura_maxima_saida_pixeis=largura_maxima_saida_pixeis,
            deslocamento_indice_nome_arquivo=i,
        )
        paths.extend(chunk)

    if not paths:
        extra = await capturar_frames_png_do_video_nos_timestamps_segundos(
            caminho_video=caminho_video,
            timestamps_segundos=[0.0],
            diretorio_saida_frames=frames_dir,
            prefixo_nome_arquivo_longo_descritivo=f"{prefixo_nome_arquivo}_fallback",
            largura_maxima_saida_pixeis=largura_maxima_saida_pixeis,
        )
        paths = extra[:1]
        timestamps_segundos = [0.0]

    assets_dir.mkdir(parents=True, exist_ok=True)
    rels: list[tuple[float, str]] = []
    for i, p in enumerate(paths):
        dest = assets_dir / p.name
        shutil.copy2(p, dest)
        t_rel = float(timestamps_segundos[i]) if i < len(timestamps_segundos) else 0.0
        rels.append((t_rel, f"assets/{dest.name}"))
    return rels
