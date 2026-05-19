"""Checkpoint em JSON no diretório do job para retomar transcrição multimodal LiteLLM por janelas após falha."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS = 1
NOME_ARQUIVO_CHECKPOINT_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS = (
    "checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers.json"
)


def caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
) -> Path:
    return diretorio_trabalho_job / NOME_ARQUIVO_CHECKPOINT_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS


def apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers(
    diretorio_trabalho_job: Path,
) -> None:
    p = caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers(
        diretorio_trabalho_job
    )
    try:
        p.unlink(missing_ok=True)
    except OSError:
        pass


def resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers(
    r: ResultadoTranscricaoComSegmentos,
) -> dict[str, Any]:
    return {
        "texto_completo": r.texto_completo,
        "idioma_detectado": r.idioma_detectado,
        "segmentos": [asdict(s) for s in r.segmentos],
    }


def dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers(
    d: dict[str, Any],
) -> ResultadoTranscricaoComSegmentos:
    segmentos_raw = d.get("segmentos") or []
    segmentos: list[SegmentoTranscricaoComTempo] = []
    for s in segmentos_raw:
        if not isinstance(s, dict):
            continue
        segmentos.append(
            SegmentoTranscricaoComTempo(
                inicio_segundos=float(s.get("inicio_segundos", 0.0)),
                fim_segundos=float(s.get("fim_segundos", 0.0)),
                texto=str(s.get("texto") or ""),
            )
        )
    idioma = d.get("idioma_detectado")
    idioma_s = str(idioma) if idioma is not None else None
    return ResultadoTranscricaoComSegmentos(
        texto_completo=str(d.get("texto_completo") or ""),
        segmentos=segmentos,
        idioma_detectado=idioma_s,
    )


def _gravar_json_atomico_para_caminho_transcribrothers(caminho: Path, payload: dict[str, Any]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(caminho)


def gravar_ou_mesclar_checkpoint_transcricao_multimodal_janelas_transcribrothers(
    diretorio_trabalho_job: Path,
    *,
    meta_fixa: dict[str, Any],
    indice_janela_base_zero: int,
    resultado_janela: ResultadoTranscricaoComSegmentos,
    registro_tempo_inferencia: dict[str, Any],
) -> int:
    """Atualiza o checkpoint com um trecho concluído. Retorna quantos trechos ficaram salvos."""
    path = caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers(
        diretorio_trabalho_job
    )
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {**meta_fixa, "janelas_concluidas": {}, "registros_tempo_inferencia": []}
    jc = data.get("janelas_concluidas")
    if not isinstance(jc, dict):
        jc = {}
    jc[str(int(indice_janela_base_zero))] = resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers(
        resultado_janela
    )
    data["janelas_concluidas"] = jc
    regs = data.get("registros_tempo_inferencia")
    if not isinstance(regs, list):
        regs = []
    alvo_ind = int(registro_tempo_inferencia.get("indice", indice_janela_base_zero + 1))
    regs = [x for x in regs if isinstance(x, dict) and int(x.get("indice", -1)) != alvo_ind]
    regs.append(registro_tempo_inferencia)
    regs.sort(key=lambda x: int(x.get("indice", 0)))
    data["registros_tempo_inferencia"] = regs
    for k, v in meta_fixa.items():
        data[k] = v
    _gravar_json_atomico_para_caminho_transcribrothers(path, data)
    return len(jc)


def carregar_checkpoint_transcricao_multimodal_janelas_se_valido_transcribrothers(
    diretorio_trabalho_job: Path,
    *,
    caminho_audio_fonte: Path,
    janela_segundos: float,
    formato_audio_inline: str,
    audio_bitrate_kbps: int,
    audio_mono: bool,
    modelo_transcricao: str,
    duracao_audio_ffprobe_atual: float,
    total_janelas_esperado: int,
) -> tuple[dict[int, ResultadoTranscricaoComSegmentos], list[dict[str, Any]]] | None:
    path = caminho_arquivo_checkpoint_transcricao_multimodal_janelas_no_work_transcribrothers(
        diretorio_trabalho_job
    )
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers(
            diretorio_trabalho_job
        )
        return None
    if not isinstance(raw, dict):
        return None
    if int(raw.get("versao", 0)) != CHECKPOINT_VERSAO_ATUAL_TRANSCRICAO_MULTIMODAL_JANELAS_TRANSCRIBROTHERS:
        apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers(
            diretorio_trabalho_job
        )
        return None

    def _invalidar_checkpoint_incompativel_transcribrothers() -> None:
        apagar_arquivo_checkpoint_transcricao_multimodal_janelas_se_existir_transcribrothers(
            diretorio_trabalho_job
        )

    if abs(float(raw.get("janela_segundos", -1.0)) - float(janela_segundos)) > 1e-3:
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    if str(raw.get("formato_audio_inline", "")).strip().lower() != str(formato_audio_inline).strip().lower():
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    br_ckpt = raw.get("audio_bitrate_kbps", raw.get("bitrate_mp3_kbps", -1))
    try:
        br_ckpt_i = int(br_ckpt)
    except (TypeError, ValueError):
        br_ckpt_i = -1
    if br_ckpt_i != int(audio_bitrate_kbps):
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    mono_ckpt = raw.get("audio_mono")
    if mono_ckpt is None:
        if not bool(audio_mono):
            _invalidar_checkpoint_incompativel_transcribrothers()
            return None
    elif bool(mono_ckpt) != bool(audio_mono):
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    if str(raw.get("modelo_transcricao", "")).strip() != str(modelo_transcricao).strip():
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    if int(raw.get("total_janelas", -1)) != int(total_janelas_esperado):
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    if abs(float(raw.get("duracao_audio_ffprobe", -1.0)) - float(duracao_audio_ffprobe_atual)) > 0.75:
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    if not caminho_audio_fonte.is_file():
        return None
    tamanho_esperado = int(raw.get("tamanho_bytes_audio_fonte", -1))
    if tamanho_esperado >= 0 and caminho_audio_fonte.stat().st_size != tamanho_esperado:
        _invalidar_checkpoint_incompativel_transcribrothers()
        return None
    jc = raw.get("janelas_concluidas")
    if not isinstance(jc, dict) or not jc:
        return None
    out_map: dict[int, ResultadoTranscricaoComSegmentos] = {}
    for k, v in jc.items():
        try:
            ik = int(k)
        except (TypeError, ValueError):
            continue
        if not (0 <= ik < total_janelas_esperado):
            continue
        if not isinstance(v, dict):
            continue
        out_map[ik] = dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers(v)
    if not out_map:
        return None
    regs_raw = raw.get("registros_tempo_inferencia")
    registros: list[dict[str, Any]] = []
    if isinstance(regs_raw, list):
        for item in regs_raw:
            if isinstance(item, dict):
                registros.append(item)
        registros.sort(key=lambda x: int(x.get("indice", 0)))
    return (out_map, registros)
