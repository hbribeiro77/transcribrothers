"""Receita única de transição entre seções ## no pipeline de vídeo narrado."""

from __future__ import annotations

from typing import Any

from transcribrothers_backend.modulo_inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers import (
    DURACAO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS,
    EFEITO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO,
)

CHAVE_STEPS_TRANSICOES_SECAO_VIDEO_NARRADO_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_transicoes_secao"
)

_EFEITOS_OK = frozenset(
    {
        "linhas-que-desenham-o-lugar",
        "barras-que-se-cruzam",
        "planos-que-abrem-espaco",
    }
)
_DURACOES_OK = frozenset({2.0, 5.0})


def normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers(
    bruto: Any,
) -> dict[str, Any]:
    if not isinstance(bruto, dict):
        return {
            "incluir": False,
            "efeito": EFEITO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO,
            "duracao_segundos": DURACAO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS,
            "vinheta_id": None,
        }
    incluir = bool(bruto.get("incluir"))
    efeito = str(bruto.get("efeito") or "").strip()
    if efeito not in _EFEITOS_OK:
        efeito = EFEITO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO
    try:
        duracao = float(bruto.get("duracao_segundos"))
    except (TypeError, ValueError):
        duracao = DURACAO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS
    if duracao not in _DURACOES_OK:
        duracao = DURACAO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS
    vinheta_id = str(bruto.get("vinheta_id") or "").strip() or None
    return {
        "incluir": incluir,
        "efeito": efeito,
        "duracao_segundos": duracao,
        "vinheta_id": vinheta_id,
    }
