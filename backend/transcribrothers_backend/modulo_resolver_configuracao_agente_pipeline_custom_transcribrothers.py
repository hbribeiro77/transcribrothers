"""Resolve prompts e modelos LiteLLM de agentes custom gravados no snapshot do job (`steps_json`)."""

from __future__ import annotations

from typing import Any

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    validar_e_resolver_modelo_litellm_solicitado_pelo_cliente,
)


def _mapa_agentes_custom_de_steps_transcribrothers(steps: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = steps.get("pipeline_custom_agentes")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for handler, cfg in raw.items():
        if isinstance(handler, str) and isinstance(cfg, dict):
            out[handler] = cfg
    return out


def resolver_modelo_agente_pipeline_custom_transcribrothers(
    handler_chave: str,
    steps: dict[str, Any],
    modelo_job: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
) -> str:
    cfg_agente = _mapa_agentes_custom_de_steps_transcribrothers(steps).get(handler_chave) or {}
    modelo_agente = (cfg_agente.get("modelo_litellm") or "").strip() or None
    modelo_solicitado = modelo_agente or (modelo_job or "").strip() or None
    return validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(configuracao, modelo_solicitado)


def resolver_prompt_agente_pipeline_custom_transcribrothers(
    handler_chave: str,
    chave_prompt: str,
    steps: dict[str, Any],
    default: str,
) -> str:
    cfg_agente = _mapa_agentes_custom_de_steps_transcribrothers(steps).get(handler_chave) or {}
    prompts = cfg_agente.get("prompts")
    if not isinstance(prompts, list):
        return default
    for item in prompts:
        if not isinstance(item, dict):
            continue
        if str(item.get("chave") or "") == chave_prompt:
            texto = str(item.get("texto") or "").strip()
            if texto:
                return texto
    return default


def montar_snapshot_pipeline_custom_agentes_para_steps_json_transcribrothers(
    agentes_rows: list[Any],
) -> dict[str, dict[str, Any]]:
    """Monta mapa handler_chave → config para gravar no job."""
    out: dict[str, dict[str, Any]] = {}
    for row in agentes_rows:
        handler = str(getattr(row, "handler_chave", "") or "").strip()
        if not handler:
            continue
        prompts = getattr(row, "prompts_json", None) or []
        out[handler] = {
            "agente_custom_id": str(getattr(row, "id", "") or ""),
            "modelo_litellm": (getattr(row, "modelo_litellm", None) or "").strip() or None,
            "prompts": prompts if isinstance(prompts, list) else [],
        }
    return out


def montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers(
    pipeline_row: Any,
    agentes_rows: list[Any],
) -> dict[str, Any]:
    """Snapshot de pipeline custom: metadados, passos (ordem/rótulos) e agentes (prompts/modelo)."""
    mapa_agente_handler: dict[str, str] = {}
    for row in agentes_rows:
        aid = str(getattr(row, "id", "") or "").strip()
        handler = str(getattr(row, "handler_chave", "") or "").strip()
        if aid and handler:
            mapa_agente_handler[aid] = handler

    passos_snap: list[dict[str, str]] = []
    for passo in getattr(pipeline_row, "passos_json", None) or []:
        if not isinstance(passo, dict):
            continue
        aid = str(passo.get("agente_id") or "").strip()
        passos_snap.append(
            {
                "id": str(passo.get("id") or ""),
                "rotulo": str(passo.get("rotulo") or ""),
                "descricao": str(passo.get("descricao") or ""),
                "handler_chave": mapa_agente_handler.get(aid, ""),
            }
        )

    return {
        "pipeline_custom_id": str(getattr(pipeline_row, "id", "") or ""),
        "pipeline_custom_copiado_de": str(getattr(pipeline_row, "copiado_de", "") or ""),
        "pipeline_custom_titulo": str(getattr(pipeline_row, "titulo", "") or ""),
        "pipeline_custom_descricao": str(getattr(pipeline_row, "descricao", "") or ""),
        "pipeline_custom_passos": passos_snap,
        "pipeline_custom_agentes": montar_snapshot_pipeline_custom_agentes_para_steps_json_transcribrothers(
            agentes_rows
        ),
    }
