"""Anexa gravação complementar, unifica video_entrada e prepara o job para pipeline completo."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_inventario_midia_fonte_e_cache_job_transcribrothers import (
    NOME_ARQUIVO_AUDIO_EXTRAIDO_TRANSCRICAO_WAV_TRANSCRIBROTHERS,
    limpar_cache_regeneravel_job_transcribrothers,
    localizar_arquivo_video_entrada_no_diretorio_job_transcribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS,
    caminho_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers,
)

NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS = "clips_entrada_originais"
NOME_VIDEO_ENTRADA_UNIFICADO_LOCAL_TRANSCRIBROTHERS = "video_entrada_arquivo_local.mp4"
NOME_ARQUIVO_TUTORIAL_GERADO_TRANSCRIBROTHERS = "tutorial_gerado_transcribrothers.md"

_CHAVES_STEPS_INVALIDAR_APOS_UNIFICAR_VIDEO_TRANSCRIBROTHERS = (
    "error_traceback",
    "error_type",
    "error_repr",
    "audio_ok",
    "audio_wav_reutilizado_retry",
    "video_entrada_reutilizado_retry",
    "transcricao_snapshot_finalizada_em_disco",
    "regeneracao_tutorial_snapshot",
    "reprocessamento_pos_transcricao_apenas",
    "transcricao_texto",
    "transcricao_segmentos",
    "pipeline_percentual",
    "tutorial_ok",
    "frames_ok",
)

_RE_NOME_SEGURO = re.compile(r"[^a-zA-Z0-9._-]+")


class ErroAnexarGravacaoComplementarTranscribrothers(ValueError):
    """Pré-condição ou falha de unificação da gravação complementar."""


def _sanitizar_trecho_nome_arquivo(nome: str, *, max_len: int = 80) -> str:
    base = Path(nome or "complementar").name
    limpo = _RE_NOME_SEGURO.sub("_", base).strip("._") or "complementar"
    return limpo[:max_len]


def _proximo_indice_clip_arquivado(pasta_clips: Path) -> int:
    maior = 0
    if not pasta_clips.is_dir():
        return 1
    for p in pasta_clips.iterdir():
        if not p.is_file():
            continue
        m = re.match(r"^(\d{3})_", p.name)
        if m:
            maior = max(maior, int(m.group(1)))
    return maior + 1


def invalidar_artefatos_derivados_apos_troca_video_entrada_transcribrothers(work: Path) -> None:
    """Remove WAV/STT/snapshot/caches que deixam de ser válidos com o vídeo unificado."""
    wav = work / NOME_ARQUIVO_AUDIO_EXTRAIDO_TRANSCRICAO_WAV_TRANSCRIBROTHERS
    wav.unlink(missing_ok=True)
    for p in work.glob("audio_extraido_para_transcricao_multimodal_inline.*"):
        if p.is_file():
            p.unlink(missing_ok=True)
    (work / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS).unlink(missing_ok=True)
    (work / NOME_ARQUIVO_TUTORIAL_GERADO_TRANSCRIBROTHERS).unlink(missing_ok=True)
    caminho_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(work).unlink(missing_ok=True)
    limpar_cache_regeneravel_job_transcribrothers(work)


def limpar_chaves_steps_json_apos_unificar_video_entrada_transcribrothers(
    steps: dict[str, Any],
) -> dict[str, Any]:
    out = dict(steps)
    for k in _CHAVES_STEPS_INVALIDAR_APOS_UNIFICAR_VIDEO_TRANSCRIBROTHERS:
        out.pop(k, None)
    return out


async def unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers(
    *,
    work: Path,
    caminho_video_complementar: Path,
    nome_original_complementar: str,
) -> dict[str, Any]:
    """
    Arquiva entrada atual + complementar, concatena e substitui `video_entrada_arquivo_local.mp4`.
    Retorna metadados para atualizar `steps_json`.
    """
    video_atual = localizar_arquivo_video_entrada_no_diretorio_job_transcribrothers(work)
    if video_atual is None or not video_atual.is_file():
        raise ErroAnexarGravacaoComplementarTranscribrothers(
            "Este job ainda não tem vídeo de entrada para unificar."
        )
    if not caminho_video_complementar.is_file():
        raise ErroAnexarGravacaoComplementarTranscribrothers(
            "Arquivo da gravação complementar não encontrado no disco."
        )

    pasta_clips = work / NOME_PASTA_CLIPS_ENTRADA_ORIGINAIS_TRANSCRIBROTHERS
    pasta_clips.mkdir(parents=True, exist_ok=True)
    idx = _proximo_indice_clip_arquivado(pasta_clips)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nome_atual_arq = f"{idx:03d}_antes_unificar_{stamp}{video_atual.suffix.lower() or '.mp4'}"
    destino_atual = pasta_clips / nome_atual_arq
    shutil.copy2(video_atual, destino_atual)

    idx_comp = idx + 1
    nome_comp_limpo = _sanitizar_trecho_nome_arquivo(nome_original_complementar)
    destino_comp = pasta_clips / f"{idx_comp:03d}_complementar_{nome_comp_limpo}"
    if destino_comp.suffix.lower() not in {".mp4", ".webm", ".mov", ".mkv", ".mpeg", ".mpg", ".avi", ".m4v"}:
        destino_comp = destino_comp.with_suffix(caminho_video_complementar.suffix.lower() or ".mp4")
    shutil.copy2(caminho_video_complementar, destino_comp)

    ext_atual = video_atual.suffix.lower() or ".mp4"
    # Pedido com a extensão atual: stream copy preserva o container; reencode vira .mp4.
    saida_tmp = work / f".video_entrada_unificado_tmp_{stamp}{ext_atual}"
    modo_concat = "reencode"
    caminho_gerado: Path | None = None
    saida_final: Path | None = None
    try:
        resultado_concat = await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
            caminho_video_a=video_atual,
            caminho_video_b=caminho_video_complementar,
            caminho_saida=saida_tmp,
        )
        modo_concat = resultado_concat.modo
        caminho_gerado = resultado_concat.caminho_saida
        saida_final = work / f"video_entrada_arquivo_local{caminho_gerado.suffix.lower()}"
        if saida_final.resolve() != caminho_gerado.resolve():
            if saida_final.exists():
                saida_final.unlink()
            caminho_gerado.replace(saida_final)
    finally:
        for candidato in (saida_tmp, caminho_gerado):
            if candidato is None or not candidato.is_file():
                continue
            if saida_final is not None and candidato.resolve() == saida_final.resolve():
                continue
            candidato.unlink(missing_ok=True)

    if saida_final is None or not saida_final.is_file():
        raise ErroAnexarGravacaoComplementarTranscribrothers(
            "Falha ao gerar o vídeo unificado de entrada."
        )

    # Remove outras entradas (drive / extensão antiga)
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in work.glob(pattern):
            if p.resolve() != saida_final.resolve() and p.is_file():
                p.unlink(missing_ok=True)

    invalidar_artefatos_derivados_apos_troca_video_entrada_transcribrothers(work)

    dur = await obter_duracao_video_segundos_via_ffprobe(saida_final)
    bytes_written = int(saida_final.stat().st_size)
    return {
        "saved_as": saida_final.name,
        "bytes_written": bytes_written,
        "duracao_video_segundos": round(float(dur), 3) if dur > 0 else None,
        "clip_arquivado_antes": destino_atual.name,
        "clip_arquivado_complementar": destino_comp.name,
        "nome_original_complementar": Path(nome_original_complementar or "").name,
        "unificado_em_utc": stamp,
        "modo_concat_video_entrada": modo_concat,
    }


def aplicar_metadados_unificacao_nos_steps_json_transcribrothers(
    steps: dict[str, Any],
    metadados: dict[str, Any],
) -> dict[str, Any]:
    out = limpar_chaves_steps_json_apos_unificar_video_entrada_transcribrothers(steps)
    out["upload_ok"] = True
    out["tipo_entrada_midia"] = "video"
    out["saved_as"] = metadados["saved_as"]
    out["bytes_written"] = metadados["bytes_written"]
    out["video_filename"] = metadados["saved_as"]
    if metadados.get("duracao_video_segundos") is not None:
        out["duracao_video_segundos"] = metadados["duracao_video_segundos"]
    historico = list(out.get("gravacoes_complementares_unificadas") or [])
    if not isinstance(historico, list):
        historico = []
    historico.append(
        {
            "unificado_em_utc": metadados.get("unificado_em_utc"),
            "clip_antes": metadados.get("clip_arquivado_antes"),
            "clip_complementar": metadados.get("clip_arquivado_complementar"),
            "nome_original_complementar": metadados.get("nome_original_complementar"),
            "bytes_written": metadados.get("bytes_written"),
            "duracao_video_segundos": metadados.get("duracao_video_segundos"),
            "modo_concat_video_entrada": metadados.get("modo_concat_video_entrada"),
        }
    )
    out["gravacoes_complementares_unificadas"] = historico
    if metadados.get("modo_concat_video_entrada"):
        out["ultimo_modo_concat_video_entrada"] = metadados["modo_concat_video_entrada"]
    out["pipeline_fase"] = "anexar_gravacao_complementar_reprocessando_pipeline_completo"
    return out
