"""Histórico do chat Ask/Agente do documento do job — persistência JSON no diretório de trabalho."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NOME_ARQUIVO_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS = (
    "historico_chat_ask_agente_documento_job.json"
)
TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS = 40


@dataclass
class ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    papel: str
    modo: str
    texto: str
    criado_em: str
    citacoes: list[dict]
    imagens: list[dict]
    estado: str | None
    tipo_pipeline: str | None
    proposta_ferramenta: dict | None = None
    propostas_ferramenta: list[dict] | None = None
    executar_proposta: bool = False


def caminho_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job: Path) -> Path:
    return (
        diretorio_trabalho_job
        / NOME_ARQUIVO_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS
    )


def item_historico_chat_ask_agente_para_dict_transcribrothers(
    item: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
) -> dict[str, Any]:
    return {
        "papel": item.papel,
        "modo": item.modo,
        "texto": item.texto,
        "criado_em": item.criado_em,
        "citacoes": item.citacoes,
        "imagens": item.imagens,
        "estado": item.estado,
        "tipo_pipeline": item.tipo_pipeline,
        "proposta_ferramenta": item.proposta_ferramenta,
        "propostas_ferramenta": item.propostas_ferramenta,
        "executar_proposta": bool(item.executar_proposta),
    }


def dict_para_item_historico_chat_ask_agente_transcribrothers(
    raw: dict,
) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers | None:
    if not isinstance(raw, dict):
        return None
    papel = raw.get("papel")
    modo = raw.get("modo")
    texto = raw.get("texto")
    criado_em = raw.get("criado_em")
    if not isinstance(papel, str) or not isinstance(modo, str):
        return None
    if not isinstance(texto, str) or not isinstance(criado_em, str):
        return None
    citacoes = raw.get("citacoes")
    imagens = raw.get("imagens")
    if not isinstance(citacoes, list):
        citacoes = []
    if not isinstance(imagens, list):
        imagens = []
    estado = raw.get("estado")
    tipo_pipeline = raw.get("tipo_pipeline")
    if estado is not None and not isinstance(estado, str):
        estado = None
    if tipo_pipeline is not None and not isinstance(tipo_pipeline, str):
        tipo_pipeline = None
    proposta_raw = raw.get("proposta_ferramenta")
    proposta_ferramenta = proposta_raw if isinstance(proposta_raw, dict) else None
    propostas_raw = raw.get("propostas_ferramenta")
    propostas_ferramenta = (
        [item for item in propostas_raw if isinstance(item, dict)]
        if isinstance(propostas_raw, list)
        else None
    )
    return ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel=papel,
        modo=modo,
        texto=texto,
        criado_em=criado_em,
        citacoes=citacoes,
        imagens=imagens,
        estado=estado,
        tipo_pipeline=tipo_pipeline,
        proposta_ferramenta=proposta_ferramenta,
        propostas_ferramenta=propostas_ferramenta,
        executar_proposta=raw.get("executar_proposta") is True,
    )


def _aplicar_teto_itens_historico_transcribrothers(
    itens: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
) -> list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]:
    teto = TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS
    if len(itens) <= teto:
        return itens
    return itens[-teto:]


def gravar_historico_chat_ask_agente_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
    itens: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
) -> None:
    itens_gravados = _aplicar_teto_itens_historico_transcribrothers(itens)
    path = caminho_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job)
    payload: dict[str, Any] = {
        "versao": 1,
        "itens": [item_historico_chat_ask_agente_para_dict_transcribrothers(i) for i in itens_gravados],
    }
    diretorio_trabalho_job.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def carregar_historico_chat_ask_agente_do_work_transcribrothers(
    diretorio_trabalho_job: Path,
) -> list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]:
    path = caminho_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    raw_itens = data.get("itens")
    if not isinstance(raw_itens, list):
        return []
    out: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers] = []
    for raw in raw_itens:
        item = dict_para_item_historico_chat_ask_agente_transcribrothers(raw)
        if item is not None:
            out.append(item)
    return out


def anexar_item_historico_chat_ask_agente_no_work_transcribrothers(
    diretorio_trabalho_job: Path,
    item: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
) -> list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]:
    itens = carregar_historico_chat_ask_agente_do_work_transcribrothers(diretorio_trabalho_job)
    itens.append(item)
    itens = _aplicar_teto_itens_historico_transcribrothers(itens)
    gravar_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job, itens)
    return itens
