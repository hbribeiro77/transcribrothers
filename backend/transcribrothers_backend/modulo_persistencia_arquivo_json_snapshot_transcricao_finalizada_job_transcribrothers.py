"""Snapshot em disco da transcrição concluída — retomar pipeline após falha sem retranscrever."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_persistencia_arquivo_json_checkpoint_transcricao_multimodal_litellm_por_janelas_transcribrothers import (
    dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers,
    resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)

NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS = (
    "snapshot_transcricao_finalizada_job_transcribrothers.json"
)
NOME_ARQUIVO_RASCUNHO_NOTAS_PROPOSTA_FUNCIONALIDADE_SEM_IMAGENS_TRANSCRIBROTHERS = (
    "rascunho_notas_proposta_funcionalidade_sem_imagens.md"
)


def caminho_snapshot_transcricao_finalizada_no_work_transcribrothers(diretorio_trabalho_job: Path) -> Path:
    return diretorio_trabalho_job / NOME_ARQUIVO_SNAPSHOT_TRANSCRICAO_FINALIZADA_JOB_TRANSCRIBROTHERS


def caminho_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(diretorio_trabalho_job: Path) -> Path:
    return (
        diretorio_trabalho_job
        / NOME_ARQUIVO_RASCUNHO_NOTAS_PROPOSTA_FUNCIONALIDADE_SEM_IMAGENS_TRANSCRIBROTHERS
    )


def gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
    transcricao: ResultadoTranscricaoComSegmentos,
) -> None:
    """Persiste transcrição após sucesso para retry retomar em etapas posteriores (ex.: rascunho LiteLLM)."""
    path = caminho_snapshot_transcricao_finalizada_no_work_transcribrothers(diretorio_trabalho_job)
    payload: dict[str, Any] = {
        "versao": 1,
        **resultado_transcricao_com_segmentos_para_dict_checkpoint_transcribrothers(transcricao),
    }
    diretorio_trabalho_job.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
    diretorio_trabalho_job: Path,
) -> ResultadoTranscricaoComSegmentos | None:
    path = caminho_snapshot_transcricao_finalizada_no_work_transcribrothers(diretorio_trabalho_job)
    if not path.is_file() or path.stat().st_size < 8:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    resultado = dict_para_resultado_transcricao_com_segmentos_checkpoint_transcribrothers(data)
    if not (resultado.texto_completo or "").strip() and not resultado.segmentos:
        return None
    return resultado


def gravar_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
    markdown_rascunho: str,
) -> None:
    path = caminho_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(diretorio_trabalho_job)
    diretorio_trabalho_job.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(markdown_rascunho, encoding="utf-8")
    tmp.replace(path)


def carregar_rascunho_notas_proposta_sem_imagens_do_work_se_existir_transcribrothers(
    diretorio_trabalho_job: Path,
) -> str | None:
    path = caminho_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(diretorio_trabalho_job)
    if not path.is_file():
        return None
    try:
        texto = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return texto if texto.strip() else None
