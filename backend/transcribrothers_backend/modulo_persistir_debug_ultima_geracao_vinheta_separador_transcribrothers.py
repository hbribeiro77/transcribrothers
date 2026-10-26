"""Grava e lê o relatório da última geração de vinheta do separador no job."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

NOME_ARQUIVO_DEBUG_ULTIMA_VINHETA_SEPARADOR = "debug_ultima_geracao_vinheta_separador.json"


def caminho_do_debug_ultima_geracao_vinheta_separador_transcribrothers(work: Path) -> Path:
    return Path(work) / NOME_ARQUIVO_DEBUG_ULTIMA_VINHETA_SEPARADOR


def gravar_debug_ultima_geracao_vinheta_separador_transcribrothers(
    work: Path,
    relatorio: dict[str, Any],
) -> Path:
    caminho = caminho_do_debug_ultima_geracao_vinheta_separador_transcribrothers(work)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work: Path) -> dict[str, Any] | None:
    caminho = caminho_do_debug_ultima_geracao_vinheta_separador_transcribrothers(work)
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None
    return dados if isinstance(dados, dict) else None
