"""Transcrição multimodal em janelas de áudio (WAV, MP3, Opus, AAC) + mesclagem de segmentos com offset temporal."""

from __future__ import annotations

import asyncio
import shutil
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    extrair_trecho_aac_m4a_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers,
    extrair_trecho_mp3_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers,
    extrair_trecho_opus_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers,
    extrair_trecho_wav_de_arquivo_wav_por_inicio_e_duracao_segundos_para_caminho,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    TranscriberLiteLLmMultimodalAudioJsonSegmentos,
)

_DURACAO_MINIMA_SUBDIVIDIR_JANELA_TRANSCRICAO_SEGUNDOS = 6.0


def _erro_parse_json_resposta_modelo_transcricao(exc: BaseException) -> bool:
    if not isinstance(exc, ValueError):
        return False
    msg = str(exc)
    return "interpretar o JSON retornado pelo modelo de transcrição" in msg


async def _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers(
    *,
    transcriber: TranscriberLiteLLmMultimodalAudioJsonSegmentos,
    caminho_audio_completo: Path,
    caminho_janela: Path,
    inicio_segundos: float,
    duracao_segundos: float,
    formato_audio_inline: str,
    bitrate_audio_kbps: int,
    forcar_mono: bool,
    diretorio_temporario_janelas: Path,
    sufixo_arquivo_temp: str,
) -> ResultadoTranscricaoComSegmentos:
    """Tenta a janela inteira; em JSON truncado/inválido, subdivide o trecho e mescla (offset local)."""
    try:
        return await transcriber.transcrever_arquivo_audio_com_segmentos(caminho_janela)
    except ValueError as exc:
        if not _erro_parse_json_resposta_modelo_transcricao(exc):
            raise
        if duracao_segundos <= _DURACAO_MINIMA_SUBDIVIDIR_JANELA_TRANSCRICAO_SEGUNDOS:
            raise
    fmt = str(formato_audio_inline or "wav").strip().lower()
    if fmt not in ("wav", "mp3", "opus", "aac"):
        fmt = "wav"
    ext = {"wav": ".wav", "mp3": ".mp3", "opus": ".opus", "aac": ".m4a"}[fmt]
    meio = duracao_segundos / 2.0
    metades: list[tuple[float, float]] = [(0.0, meio), (meio, duracao_segundos - meio)]
    parciais: list[tuple[float, ResultadoTranscricaoComSegmentos]] = []
    for loc_inicio, loc_dur in metades:
        if loc_dur <= 0.05:
            continue
        saida = diretorio_temporario_janelas / f"{sufixo_arquivo_temp}_sub_{int(loc_inicio * 1000)}{ext}"
        await _extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers(
            caminho_audio_completo=caminho_audio_completo,
            formato_audio_inline=fmt,
            bitrate_audio_kbps=bitrate_audio_kbps,
            forcar_mono=forcar_mono,
            inicio_segundos=inicio_segundos + loc_inicio,
            duracao_segundos=loc_dur,
            caminho_saida=saida,
        )
        try:
            res = await transcriber.transcrever_arquivo_audio_com_segmentos(saida)
        finally:
            try:
                saida.unlink(missing_ok=True)
            except OSError:
                pass
        parciais.append((loc_inicio, res))
    if not parciais:
        raise exc
    return _mesclar_resultados_transcricao_com_offset_temporal_segundos(parciais)


def _listar_janelas_temporais_segundos_para_transcricao_multimodal(
    duracao_total_segundos: float,
    janela_segundos: float,
) -> list[tuple[float, float]]:
    """Retorna lista de (inicio_segundos, duracao_segundos) cobrindo [0, duracao_total)."""
    if duracao_total_segundos <= 0 or janela_segundos <= 0:
        return [(0.0, max(0.01, duracao_total_segundos))]
    out: list[tuple[float, float]] = []
    t = 0.0
    w = float(janela_segundos)
    while t < duracao_total_segundos - 1e-6:
        restante = duracao_total_segundos - t
        dur = min(w, restante)
        if dur > 0.05:
            out.append((t, dur))
        t += w
    if not out:
        out.append((0.0, max(0.01, duracao_total_segundos)))
    return out


def _mesclar_resultados_transcricao_com_offset_temporal_segundos(
    resultados: list[tuple[float, ResultadoTranscricaoComSegmentos]],
) -> ResultadoTranscricaoComSegmentos:
    """Cada tupla é (offset_segundos_no_audio_completo, resultado_da_janela)."""
    todos: list[SegmentoTranscricaoComTempo] = []
    textos: list[str] = []
    idioma: str | None = None
    for offset, res in resultados:
        if idioma is None and res.idioma_detectado:
            idioma = res.idioma_detectado
        for seg in res.segmentos:
            todos.append(
                SegmentoTranscricaoComTempo(
                    inicio_segundos=offset + seg.inicio_segundos,
                    fim_segundos=offset + seg.fim_segundos,
                    texto=seg.texto,
                )
            )
        if res.texto_completo.strip():
            textos.append(res.texto_completo.strip())
    texto_completo = " ".join(textos).strip()
    if not todos and texto_completo:
        todos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=0.0,
                fim_segundos=0.0,
                texto=texto_completo,
            )
        )
    if not texto_completo and todos:
        texto_completo = " ".join(s.texto for s in todos).strip()
    return ResultadoTranscricaoComSegmentos(
        texto_completo=texto_completo,
        segmentos=todos,
        idioma_detectado=idioma,
    )


async def _extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers(
    *,
    caminho_audio_completo: Path,
    formato_audio_inline: str,
    bitrate_audio_kbps: int,
    forcar_mono: bool,
    inicio_segundos: float,
    duracao_segundos: float,
    caminho_saida: Path,
) -> None:
    fmt = str(formato_audio_inline or "wav").strip().lower()
    if fmt == "mp3":
        await extrair_trecho_mp3_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
            caminho_audio_entrada=caminho_audio_completo,
            inicio_segundos=inicio_segundos,
            duracao_segundos=duracao_segundos,
            caminho_mp3_saida=caminho_saida,
            bitrate_kbps=bitrate_audio_kbps,
            forcar_mono=forcar_mono,
        )
    elif fmt == "opus":
        await extrair_trecho_opus_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
            caminho_audio_entrada=caminho_audio_completo,
            inicio_segundos=inicio_segundos,
            duracao_segundos=duracao_segundos,
            caminho_opus_saida=caminho_saida,
            bitrate_kbps=bitrate_audio_kbps,
            forcar_mono=forcar_mono,
        )
    elif fmt == "aac":
        await extrair_trecho_aac_m4a_de_arquivo_audio_por_inicio_e_duracao_segundos_para_caminho_transcribrothers(
            caminho_audio_entrada=caminho_audio_completo,
            inicio_segundos=inicio_segundos,
            duracao_segundos=duracao_segundos,
            caminho_m4a_saida=caminho_saida,
            bitrate_kbps=bitrate_audio_kbps,
            forcar_mono=forcar_mono,
        )
    else:
        await extrair_trecho_wav_de_arquivo_wav_por_inicio_e_duracao_segundos_para_caminho(
            caminho_wav_entrada=caminho_audio_completo,
            inicio_segundos=inicio_segundos,
            duracao_segundos=duracao_segundos,
            caminho_wav_saida=caminho_saida,
        )


async def transcrever_wav_litellm_multimodal_em_janelas_com_callback_progresso_transcribrothers(
    *,
    transcriber: TranscriberLiteLLmMultimodalAudioJsonSegmentos,
    caminho_audio_completo: Path,
    formato_audio_inline: str = "wav",
    bitrate_audio_kbps: int = 96,
    forcar_mono: bool = True,
    janela_segundos: float,
    diretorio_temporario_janelas: Path,
    atualizar_progresso: Callable[[dict[str, Any]], Awaitable[None]] | None,
    max_janelas_em_paralelo: int = 5,
    janelas_ja_concluidas: dict[int, ResultadoTranscricaoComSegmentos] | None = None,
    registros_tempo_inferencia_iniciais: list[dict[str, Any]] | None = None,
    apos_persistir_janela_nova_concluida: (
        Callable[[int, float, float, ResultadoTranscricaoComSegmentos, float], Awaitable[None]] | None
    ) = None,
) -> ResultadoTranscricaoComSegmentos:
    """Transcreve o áudio em fatias (WAV ou MP3); chama `atualizar_progresso` antes de cada POST ao gateway.

    `janelas_ja_concluidas` (índice base 0) permite retomar sem reenviar trechos já transcritos.
    `apos_persistir_janela_nova_concluida` é chamado após cada trecho novo concluído com sucesso (para checkpoint).
    """
    fmt = str(formato_audio_inline or "wav").strip().lower()
    if fmt not in ("wav", "mp3", "opus", "aac"):
        fmt = "wav"
    ext = {"wav": ".wav", "mp3": ".mp3", "opus": ".opus", "aac": ".m4a"}[fmt]
    br = max(16, min(320, int(bitrate_audio_kbps)))
    if fmt == "opus":
        br = max(16, min(256, br))

    preexistentes: dict[int, ResultadoTranscricaoComSegmentos] = dict(janelas_ja_concluidas or {})

    dur = await obter_duracao_video_segundos_via_ffprobe(caminho_audio_completo)
    if dur <= 0 or janela_segundos <= 0:
        if atualizar_progresso:
            await atualizar_progresso(
                {
                    "pipeline_fase": "transcrevendo_audio_litellm_multimodal_arquivo_unico",
                    "transcricao_janelas_total": 1,
                    "transcricao_janela_indice": 1,
                }
            )
        t0 = time.perf_counter()
        resultado_unico = await transcriber.transcrever_arquivo_audio_com_segmentos(caminho_audio_completo)
        elapsed = time.perf_counter() - t0
        if atualizar_progresso:
            fim_v = max(0.0, float(dur))
            await atualizar_progresso(
                {
                    "pipeline_fase": "transcrevendo_audio_litellm_multimodal_arquivo_unico",
                    "transcricao_janelas_total": 1,
                    "transcricao_janela_indice": 1,
                    "transcricao_janelas_registros_tempo_inferencia": [
                        {
                            "indice": 1,
                            "inicio_segundos": 0.0,
                            "fim_segundos": round(fim_v, 2),
                            "duracao_inferencia_segundos": round(elapsed, 2),
                        }
                    ],
                }
            )
        return resultado_unico

    janelas = _listar_janelas_temporais_segundos_para_transcricao_multimodal(dur, janela_segundos)
    diretorio_temporario_janelas.mkdir(parents=True, exist_ok=True)
    try:
        usar_paralelo = len(janelas) > 1 and max_janelas_em_paralelo > 1
        if not usar_paralelo:
            acumulado: list[tuple[float, ResultadoTranscricaoComSegmentos]] = []
            registros_tempo_inferencia: list[dict[str, Any]] = [
                dict(x) for x in (registros_tempo_inferencia_iniciais or [])
            ]
            registros_tempo_inferencia.sort(key=lambda r: int(r["indice"]))
            for idx, (inicio, duracao) in enumerate(janelas):
                if idx in preexistentes:
                    acumulado.append((inicio, preexistentes[idx]))
                    continue
                if atualizar_progresso:
                    await atualizar_progresso(
                        {
                            "pipeline_fase": "transcrevendo_audio_janela_litellm_multimodal",
                            "transcricao_janela_indice": idx + 1,
                            "transcricao_janelas_total": len(janelas),
                            "transcricao_janela_inicio_segundos": round(inicio, 2),
                            "transcricao_janela_fim_segundos": round(inicio + duracao, 2),
                            "transcricao_janela_duracao_segundos": round(duracao, 2),
                            "transcricao_janelas_registros_tempo_inferencia": list(registros_tempo_inferencia),
                            "transcricao_multimodal_retomando_trechos": len(preexistentes),
                        }
                    )
                saida = diretorio_temporario_janelas / f"janela_transcricao_litellm_{idx:04d}{ext}"
                await _extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers(
                    caminho_audio_completo=caminho_audio_completo,
                    formato_audio_inline=fmt,
                    bitrate_audio_kbps=br,
                    forcar_mono=forcar_mono,
                    inicio_segundos=inicio,
                    duracao_segundos=duracao,
                    caminho_saida=saida,
                )
                t0 = time.perf_counter()
                parcial = await _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers(
                    transcriber=transcriber,
                    caminho_audio_completo=caminho_audio_completo,
                    caminho_janela=saida,
                    inicio_segundos=inicio,
                    duracao_segundos=duracao,
                    formato_audio_inline=fmt,
                    bitrate_audio_kbps=br,
                    forcar_mono=forcar_mono,
                    diretorio_temporario_janelas=diretorio_temporario_janelas,
                    sufixo_arquivo_temp=f"janela_transcricao_litellm_{idx:04d}",
                )
                elapsed = time.perf_counter() - t0
                registros_tempo_inferencia.append(
                    {
                        "indice": idx + 1,
                        "inicio_segundos": round(inicio, 2),
                        "fim_segundos": round(inicio + duracao, 2),
                        "duracao_inferencia_segundos": round(elapsed, 2),
                    }
                )
                registros_tempo_inferencia.sort(key=lambda r: int(r["indice"]))
                if apos_persistir_janela_nova_concluida:
                    await apos_persistir_janela_nova_concluida(idx, inicio, duracao, parcial, elapsed)
                if atualizar_progresso:
                    await atualizar_progresso(
                        {
                            "pipeline_fase": "transcrevendo_audio_janela_litellm_multimodal",
                            "transcricao_janela_indice": idx + 1,
                            "transcricao_janelas_total": len(janelas),
                            "transcricao_janela_inicio_segundos": round(inicio, 2),
                            "transcricao_janela_fim_segundos": round(inicio + duracao, 2),
                            "transcricao_janela_duracao_segundos": round(duracao, 2),
                            "transcricao_janelas_registros_tempo_inferencia": list(registros_tempo_inferencia),
                            "transcricao_multimodal_retomando_trechos": len(preexistentes),
                        }
                    )
                acumulado.append((inicio, parcial))
                try:
                    saida.unlink(missing_ok=True)
                except OSError:
                    pass
            acumulado.sort(key=lambda item: item[0])
            return _mesclar_resultados_transcricao_com_offset_temporal_segundos(acumulado)

        max_p = max(1, min(int(max_janelas_em_paralelo), 32))
        total = len(janelas)
        sem = asyncio.Semaphore(max_p)
        lock = asyncio.Lock()
        lock_registros = asyncio.Lock()
        base_concluidas = len(preexistentes)
        novas_concluidas = 0
        registros_tempo_inferencia = [dict(x) for x in (registros_tempo_inferencia_iniciais or [])]
        registros_tempo_inferencia.sort(key=lambda r: int(r["indice"]))

        trabalhos: list[tuple[int, float, float, Path]] = []
        for idx, (inicio, duracao) in enumerate(janelas):
            if idx in preexistentes:
                continue
            saida = diretorio_temporario_janelas / f"janela_transcricao_litellm_{idx:04d}{ext}"
            await _extrair_trecho_audio_para_janela_transcricao_multimodal_transcribrothers(
                caminho_audio_completo=caminho_audio_completo,
                formato_audio_inline=fmt,
                bitrate_audio_kbps=br,
                forcar_mono=forcar_mono,
                inicio_segundos=inicio,
                duracao_segundos=duracao,
                caminho_saida=saida,
            )
            trabalhos.append((idx, inicio, duracao, saida))

        if atualizar_progresso:
            await atualizar_progresso(
                {
                    "pipeline_fase": "transcrevendo_audio_janelas_litellm_multimodal_paralelo",
                    "transcricao_janelas_total": total,
                    "transcricao_janelas_concluidas": base_concluidas,
                    "transcricao_janelas_paralelo_max": max_p,
                    "transcricao_janelas_registros_tempo_inferencia": list(registros_tempo_inferencia),
                    "transcricao_multimodal_retomando_trechos": base_concluidas,
                }
            )

        pares_existentes = [(janelas[i][0], preexistentes[i]) for i in sorted(preexistentes)]

        if not trabalhos:
            return _mesclar_resultados_transcricao_com_offset_temporal_segundos(
                sorted(pares_existentes, key=lambda item: item[0])
            )

        async def transcrever_um_trecho(
            idx: int, inicio: float, duracao: float, saida: Path
        ) -> tuple[float, ResultadoTranscricaoComSegmentos]:
            nonlocal novas_concluidas
            async with sem:
                if atualizar_progresso:
                    async with lock_registros:
                        snap_reg = list(registros_tempo_inferencia)
                    await atualizar_progresso(
                        {
                            "pipeline_fase": "transcrevendo_audio_janelas_litellm_multimodal_paralelo",
                            "transcricao_janelas_total": total,
                            "transcricao_janela_indice": idx + 1,
                            "transcricao_janela_inicio_segundos": round(inicio, 2),
                            "transcricao_janela_fim_segundos": round(inicio + duracao, 2),
                            "transcricao_janela_duracao_segundos": round(duracao, 2),
                            "transcricao_janelas_paralelo_max": max_p,
                            "transcricao_janelas_registros_tempo_inferencia": snap_reg,
                            "transcricao_multimodal_retomando_trechos": base_concluidas,
                        }
                    )
                t0 = time.perf_counter()
                try:
                    parcial = await _transcrever_arquivo_janela_litellm_resiliente_falha_parse_json_transcribrothers(
                        transcriber=transcriber,
                        caminho_audio_completo=caminho_audio_completo,
                        caminho_janela=saida,
                        inicio_segundos=inicio,
                        duracao_segundos=duracao,
                        formato_audio_inline=fmt,
                        bitrate_audio_kbps=br,
                        forcar_mono=forcar_mono,
                        diretorio_temporario_janelas=diretorio_temporario_janelas,
                        sufixo_arquivo_temp=f"janela_transcricao_litellm_{idx:04d}",
                    )
                finally:
                    try:
                        saida.unlink(missing_ok=True)
                    except OSError:
                        pass
                elapsed = time.perf_counter() - t0
                if apos_persistir_janela_nova_concluida:
                    await apos_persistir_janela_nova_concluida(idx, inicio, duracao, parcial, elapsed)
                async with lock_registros:
                    registros_tempo_inferencia.append(
                        {
                            "indice": idx + 1,
                            "inicio_segundos": round(inicio, 2),
                            "fim_segundos": round(inicio + duracao, 2),
                            "duracao_inferencia_segundos": round(elapsed, 2),
                        }
                    )
                    registros_tempo_inferencia.sort(key=lambda r: int(r["indice"]))
                    snap_full = list(registros_tempo_inferencia)
                async with lock:
                    novas_concluidas += 1
                    c = base_concluidas + novas_concluidas
                if atualizar_progresso:
                    await atualizar_progresso(
                        {
                            "pipeline_fase": "transcrevendo_audio_janelas_litellm_multimodal_paralelo",
                            "transcricao_janelas_total": total,
                            "transcricao_janelas_concluidas": c,
                            "transcricao_janelas_paralelo_max": max_p,
                            "transcricao_janelas_registros_tempo_inferencia": snap_full,
                            "transcricao_multimodal_retomando_trechos": base_concluidas,
                        }
                    )
                return (inicio, parcial)

        resultados_gather = await asyncio.gather(
            *[transcrever_um_trecho(idx, ini, dur, p) for idx, ini, dur, p in trabalhos],
            return_exceptions=True,
        )
        for item in resultados_gather:
            if isinstance(item, BaseException):
                raise item
        pares_novos = sorted(resultados_gather, key=lambda item: item[0])
        pares = sorted(pares_existentes + list(pares_novos), key=lambda item: item[0])
        return _mesclar_resultados_transcricao_com_offset_temporal_segundos(pares)
    finally:
        if diretorio_temporario_janelas.is_dir():
            try:
                shutil.rmtree(diretorio_temporario_janelas, ignore_errors=True)
            except OSError:
                pass


listar_janelas_temporais_segundos_para_transcricao_multimodal_litellm_transcribrothers = (
    _listar_janelas_temporais_segundos_para_transcricao_multimodal
)
mesclar_resultados_transcricao_com_offset_temporal_segundos_transcribrothers = (
    _mesclar_resultados_transcricao_com_offset_temporal_segundos
)
