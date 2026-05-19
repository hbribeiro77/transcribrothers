"""Acumula entradas legíveis de decisões/respostas da IA em `steps_json` para a modal de status."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CHAVE_STEPS_JSON_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS = "log_decisoes_ia_pipeline"

_MAX_ENTRADAS_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS = 120
_MAX_CHARS_RESUMO_LOG_DECISOES_IA_TRANSCRIBROTHERS = 500
_MAX_CHARS_DETALHE_LOG_DECISOES_IA_TRANSCRIBROTHERS = 6000


def _truncar_texto_log_decisoes_ia_transcribrothers(texto: str, limite: int) -> str:
    t = (texto or "").strip()
    if len(t) <= limite:
        return t
    return t[: limite - 1] + "…"


def registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
    steps: dict[str, Any],
    *,
    etapa: str,
    resumo: str,
    detalhe: str | None = None,
    modelo: str | None = None,
    sucesso: bool = True,
    metadados: dict[str, Any] | None = None,
    em_iso: str | None = None,
) -> None:
    """Anexa uma entrada ao log do job (mais recente por último)."""
    etapa_limpa = (etapa or "ia").strip() or "ia"
    entrada: dict[str, Any] = {
        "em": em_iso or datetime.now(timezone.utc).isoformat(),
        "etapa": etapa_limpa,
        "resumo": _truncar_texto_log_decisoes_ia_transcribrothers(
            resumo, _MAX_CHARS_RESUMO_LOG_DECISOES_IA_TRANSCRIBROTHERS
        ),
        "sucesso": bool(sucesso),
    }
    if modelo and str(modelo).strip():
        entrada["modelo"] = str(modelo).strip()
    if detalhe and str(detalhe).strip():
        entrada["detalhe"] = _truncar_texto_log_decisoes_ia_transcribrothers(
            str(detalhe), _MAX_CHARS_DETALHE_LOG_DECISOES_IA_TRANSCRIBROTHERS
        )
    if metadados:
        entrada["metadados"] = metadados

    existente = steps.get(CHAVE_STEPS_JSON_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS)
    lista: list[dict[str, Any]]
    if isinstance(existente, list):
        lista = [e for e in existente if isinstance(e, dict)]
    else:
        lista = []
    lista.append(entrada)
    if len(lista) > _MAX_ENTRADAS_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS:
        lista = lista[-_MAX_ENTRADAS_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS :]
    steps[CHAVE_STEPS_JSON_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS] = lista


def resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers(
    texto: str,
    *,
    max_chars: int = 400,
) -> str:
    """Uma linha curta para o campo `resumo` a partir da resposta bruta."""
    t = (texto or "").strip().replace("\r\n", "\n")
    if not t:
        return "(resposta vazia)"
    linha = t.split("\n", 1)[0].strip()
    if len(linha) > max_chars:
        return linha[: max_chars - 1] + "…"
    if len(t) > len(linha):
        return f"{linha} …"
    return linha
