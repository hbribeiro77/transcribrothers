"""Valida e grava JSON de cliques de reprodução de bug no diretório do job."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException, UploadFile

from transcribrothers_backend.modulo_staging_video_importacao_recbrothers_transcribrothers import (
    NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS,
)

_LIMITE_BYTES_JSON_CLIQUES = 2 * 1024 * 1024


def validar_conteudo_json_cliques_reproducao_bug_transcribrothers(conteudo: bytes) -> int:
    """Valida bytes do JSON; retorna quantidade de cliques. Levanta ValueError se inválido."""
    if len(conteudo) > _LIMITE_BYTES_JSON_CLIQUES:
        raise ValueError("JSON de cliques excede 2 MB.")
    try:
        parsed = json.loads(conteudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("JSON de cliques inválido.") from e
    lista = parsed.get("cliques") if isinstance(parsed, dict) else parsed
    if not isinstance(lista, list):
        raise ValueError("JSON de cliques deve conter array 'cliques'.")
    return len(lista)


def gravar_json_cliques_reproducao_bug_no_diretorio_job_transcribrothers(
    work: Path,
    conteudo: bytes,
) -> int:
    """Grava cliques no job; retorna total de cliques."""
    total = validar_conteudo_json_cliques_reproducao_bug_transcribrothers(conteudo)
    destino = work / NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS
    destino.write_bytes(conteudo)
    return total


async def validar_e_gravar_upload_cliques_json_reproducao_bug_job_transcribrothers(
    work: Path,
    cliques_json: UploadFile,
) -> int:
    """Lê upload, valida e grava no job. Levanta HTTPException em erro de validação."""
    conteudo = await cliques_json.read()
    await cliques_json.close()
    try:
        return gravar_json_cliques_reproducao_bug_no_diretorio_job_transcribrothers(work, conteudo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def job_possui_arquivo_cliques_reproducao_bug_transcribrothers(work: Path) -> bool:
    return (work / NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS).is_file()
