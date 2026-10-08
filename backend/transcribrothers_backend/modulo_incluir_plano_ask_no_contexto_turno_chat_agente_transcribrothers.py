"""Plano do Ask (sem tools) entra no contexto do Agente para virar ferramenta."""

from __future__ import annotations

from typing import Any


def texto_plano_ask_para_contexto_agente_transcribrothers(historico: list[Any]) -> str | None:
    for item in reversed(historico or []):
        papel = (getattr(item, "papel", None) or "").strip()
        modo = (getattr(item, "modo", None) or "").strip()
        if papel not in {"assistente", "agente"}:
            continue
        if papel == "agente" or modo == "agente":
            continue
        if papel != "assistente" and modo != "ask":
            continue
        if modo and modo != "ask":
            continue
        propostas = getattr(item, "propostas_ferramenta", None)
        if isinstance(propostas, list) and propostas:
            continue
        unica = getattr(item, "proposta_ferramenta", None)
        if isinstance(unica, dict) and unica.get("nome"):
            continue
        texto = (getattr(item, "texto", None) or "").strip()
        if texto:
            return texto
        return None
    return None
