"""Prévia TTS por cue: metadados + promoção a WAV definitivo (sem re-narrar)."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    normalizar_texto_cue_para_comparacao_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
    normalizar_voz_tts_gemini_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    nome_subpasta_wavs_narracao_por_cue_transcribrothers,
    resolver_caminho_wav_narracao_por_indice_cue_transcribrothers,
)


def caminho_preview_tts_cue_narracao_no_work_transcribrothers(
    work: Path,
    indice_zero_based: int,
) -> Path:
    if indice_zero_based < 0:
        raise ValueError("Índice de cue inválido.")
    return (
        work
        / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
        / f"preview_cue_narracao_{indice_zero_based:04d}.wav"
    )


def caminho_meta_preview_tts_cue_narracao_no_work_transcribrothers(
    work: Path,
    indice_zero_based: int,
) -> Path:
    if indice_zero_based < 0:
        raise ValueError("Índice de cue inválido.")
    return (
        work
        / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
        / f"preview_cue_narracao_{indice_zero_based:04d}.meta.json"
    )


@dataclass(frozen=True)
class MetaPreviewTtsCueNarracaoTranscribrothers:
    texto: str
    voz_tts: str
    modelo: str = ""
    gerado_em: str = ""


def _normalizar_voz_meta_transcribrothers(voz: str | None) -> str:
    try:
        return normalizar_voz_tts_gemini_transcribrothers(
            (voz or "").strip() or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
        )
    except ValueError:
        return VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS


def gravar_meta_preview_tts_cue_narracao_transcribrothers(
    *,
    work: Path,
    indice_zero_based: int,
    texto: str,
    voz_tts: str,
    modelo: str = "",
) -> Path:
    meta = {
        "texto": normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
        "voz_tts": _normalizar_voz_meta_transcribrothers(voz_tts),
        "modelo": (modelo or "").strip(),
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }
    caminho = caminho_meta_preview_tts_cue_narracao_no_work_transcribrothers(
        work, indice_zero_based
    )
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho


def carregar_meta_preview_tts_cue_narracao_transcribrothers(
    work: Path,
    indice_zero_based: int,
) -> MetaPreviewTtsCueNarracaoTranscribrothers | None:
    caminho = caminho_meta_preview_tts_cue_narracao_no_work_transcribrothers(
        work, indice_zero_based
    )
    if not caminho.is_file():
        return None
    try:
        raw: Any = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    texto = str(raw.get("texto") or "").strip()
    if not texto:
        return None
    return MetaPreviewTtsCueNarracaoTranscribrothers(
        texto=normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
        voz_tts=_normalizar_voz_meta_transcribrothers(str(raw.get("voz_tts") or "")),
        modelo=str(raw.get("modelo") or "").strip(),
        gerado_em=str(raw.get("gerado_em") or "").strip(),
    )


def previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers(
    *,
    work: Path,
    indice_zero_based: int,
    texto: str,
    voz_tts: str,
) -> bool:
    caminho_wav = caminho_preview_tts_cue_narracao_no_work_transcribrothers(
        work, indice_zero_based
    )
    if not caminho_wav.is_file() or caminho_wav.stat().st_size <= 44:
        return False
    meta = carregar_meta_preview_tts_cue_narracao_transcribrothers(work, indice_zero_based)
    if meta is None:
        return False
    texto_norm = normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto)
    voz_norm = _normalizar_voz_meta_transcribrothers(voz_tts)
    return meta.texto == texto_norm and meta.voz_tts == voz_norm


def promover_preview_tts_cue_para_wav_definitivo_transcribrothers(
    *,
    work: Path,
    indice_zero_based: int,
    texto: str,
    voz_tts: str,
) -> Path | None:
    """
    Se a prévia no disco bate com texto+voz, copia para cue_narracao_XXXX.wav.
    Devolve o caminho definitivo ou None se não promoveu.
    """
    if not previa_tts_cue_e_valida_para_texto_e_voz_transcribrothers(
        work=work,
        indice_zero_based=indice_zero_based,
        texto=texto,
        voz_tts=voz_tts,
    ):
        return None
    caminho_preview = caminho_preview_tts_cue_narracao_no_work_transcribrothers(
        work, indice_zero_based
    )
    dir_wavs = work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    caminho_definitivo = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(
        dir_wavs, indice_zero_based
    )
    caminho_definitivo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(caminho_preview, caminho_definitivo)
    return caminho_definitivo


def promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers(
    *,
    work: Path,
    indices_sujos: list[int],
    textos_por_indice: list[str],
    vozes_por_indice: list[str],
    flags_sem_narracao: list[bool],
    quantidade_cues_estavel: bool,
) -> tuple[list[int], list[int], dict[int, Path]]:
    """
    Promove prévias válidas nos índices sujos (só se a quantidade de cues não mudou).

    Retorna: (índices ainda TTS, índices promovidos, mapa índice→caminho WAV promovido).
    """
    if not quantidade_cues_estavel:
        return list(indices_sujos), [], {}
    ainda_tts: list[int] = []
    promovidos: list[int] = []
    caminhos: dict[int, Path] = {}
    for i in indices_sujos:
        if i < 0 or i >= len(textos_por_indice):
            ainda_tts.append(i)
            continue
        if flags_sem_narracao[i]:
            continue
        promovido = promover_preview_tts_cue_para_wav_definitivo_transcribrothers(
            work=work,
            indice_zero_based=i,
            texto=textos_por_indice[i],
            voz_tts=vozes_por_indice[i],
        )
        if promovido is not None:
            promovidos.append(i)
            caminhos[i] = promovido
        else:
            ainda_tts.append(i)
    return ainda_tts, promovidos, caminhos
