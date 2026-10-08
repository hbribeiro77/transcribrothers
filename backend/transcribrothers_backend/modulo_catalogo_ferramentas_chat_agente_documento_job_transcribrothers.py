"""Allowlist e parse das ferramentas propostas no turno do Agente."""

from __future__ import annotations

import json
from typing import Any

from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    extrair_primeiro_objeto_json_de_texto_llm_transcribrothers,
)

NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS = "edicao_parcial"
NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS = "revisao_profunda"
NOME_FERRAMENTA_SEM_VIDEO_CHAT_AGENTE_TRANSCRIBROTHERS = "sem_video"

NOMES_FERRAMENTAS_PROPOSTA_CHAT_AGENTE_TRANSCRIBROTHERS = frozenset(
    {
        NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
        NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS,
        NOME_FERRAMENTA_SEM_VIDEO_CHAT_AGENTE_TRANSCRIBROTHERS,
    }
)


def _texto_ou_nulo(valor: object) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(
    valor: object,
) -> list[str]:
    if not isinstance(valor, list):
        return []
    saida: list[str] = []
    vistos: set[str] = set()
    for item in valor:
        texto = _texto_ou_nulo(item)
        if texto is None or texto in vistos:
            continue
        vistos.add(texto)
        saida.append(texto)
    return saida


def extrair_caminhos_relativos_de_imagens_historico_chat_agente_transcribrothers(
    imagens: list[dict] | None,
) -> list[str]:
    saida: list[str] = []
    for imagem in imagens or []:
        if not isinstance(imagem, dict):
            continue
        rel = _texto_ou_nulo(imagem.get("caminho_relativo"))
        if rel is not None:
            saida.append(rel)
    return normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(saida)


def anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers(
    proposta: dict[str, Any] | None,
    *fontes_caminhos: list[str] | None,
) -> dict[str, Any] | None:
    if proposta is None:
        return None
    out = dict(proposta)
    caminhos = normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(
        out.get("caminhos_imagens")
    )
    if out.get("nome") != NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS:
        out["caminhos_imagens"] = caminhos
        return out
    vistos = set(caminhos)
    for fonte in fontes_caminhos:
        for rel in normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(fonte):
            if rel in vistos:
                continue
            vistos.add(rel)
            caminhos.append(rel)
    out["caminhos_imagens"] = caminhos
    return out


def limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers(
    texto: str,
    texto_bruto: str,
) -> str:
    candidato = (texto or "").strip()
    fonte = texto_bruto if (texto_bruto or "").strip() else candidato
    if '"ferramentas"' not in candidato and not candidato.startswith("{"):
        return texto
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(fonte)
        data = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError):
        idx = candidato.find("{")
        return candidato[:idx].strip() if idx > 0 else texto
    if isinstance(data, dict):
        inner = data.get("texto")
        if isinstance(inner, str) and inner.strip() and '"ferramentas"' not in inner:
            return inner.strip()
    idx = candidato.find("{")
    return candidato[:idx].strip() if idx > 0 else texto


def parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(
    texto_bruto: str,
) -> bool | None:
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or "executar" not in data:
        return None
    valor = data.get("executar")
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        return valor.strip().casefold() in {"true", "1", "sim", "yes"}
    return None


def parsear_estado_resposta_modelo_chat_agente_transcribrothers(
    texto_bruto: str,
) -> str | None:
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    bruto = data.get("estado")
    if not isinstance(bruto, str):
        return None
    estado = bruto.strip().casefold()
    if estado in {"aplicando", "rascunho"}:
        return estado
    return None


def resposta_agente_precisa_retry_por_aplicar_sem_ferramentas_transcribrothers(
    *,
    estado: str | None,
    quantidade_ferramentas: int,
    flag_executar: bool | None,
) -> bool:
    if quantidade_ferramentas > 0:
        return False
    if estado == "rascunho":
        return False
    return True


def decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
    *,
    flag_executar: bool | None,
    quantidade_propostas: int,
    estado: str | None = None,
) -> bool:
    if quantidade_propostas <= 0:
        return False
    if estado == "rascunho":
        return False
    if estado == "aplicando":
        return True
    if flag_executar is False:
        return False
    return True


def parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers(
    texto_bruto: str,
) -> list[dict[str, Any]]:
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data = json.loads(raw_json)
    except (ValueError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    return parsear_ferramentas_resposta_modelo_chat_agente_transcribrothers(data.get("ferramentas"))


def parsear_ferramentas_de_tool_calls_openai_chat_agente_transcribrothers(
    tool_calls: object,
) -> list[dict[str, Any]]:
    if not isinstance(tool_calls, list):
        return []
    saida: list[dict[str, Any]] = []
    for item in tool_calls:
        if not isinstance(item, dict):
            continue
        funcao = item.get("function")
        if not isinstance(funcao, dict):
            continue
        nome = _texto_ou_nulo(funcao.get("name")) or _texto_ou_nulo(item.get("name"))
        if nome not in NOMES_FERRAMENTAS_PROPOSTA_CHAT_AGENTE_TRANSCRIBROTHERS:
            continue
        argumentos_raw = funcao.get("arguments")
        argumentos: dict[str, Any] = {}
        if isinstance(argumentos_raw, str) and argumentos_raw.strip():
            try:
                lido = json.loads(argumentos_raw)
            except json.JSONDecodeError:
                lido = None
            if isinstance(lido, dict):
                argumentos = lido
        elif isinstance(argumentos_raw, dict):
            argumentos = argumentos_raw
        saida.append(
            {
                "nome": nome,
                "titulo_secao_heading": _texto_ou_nulo(argumentos.get("titulo_secao_heading")),
                "instrucoes": _texto_ou_nulo(argumentos.get("instrucoes")),
                "caminhos_imagens": normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(
                    argumentos.get("caminhos_imagens")
                ),
                "reescrever_secao": argumentos.get("reescrever_secao") is True,
            }
        )
    return saida


def mesclar_ferramentas_json_e_tool_calls_openai_chat_agente_transcribrothers(
    *,
    ferramentas_json: list[dict[str, Any]] | None,
    ferramentas_tool_calls: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    json_tools = [item for item in (ferramentas_json or []) if isinstance(item, dict)]
    if json_tools:
        return json_tools
    return [item for item in (ferramentas_tool_calls or []) if isinstance(item, dict)]


def parsear_ferramentas_resposta_modelo_chat_agente_transcribrothers(
    bruto: object,
) -> list[dict[str, Any]]:
    if not isinstance(bruto, list):
        return []
    saida: list[dict[str, Any]] = []
    for item in bruto:
        if not isinstance(item, dict):
            continue
        nome = _texto_ou_nulo(item.get("nome")) or _texto_ou_nulo(item.get("tool"))
        if nome not in NOMES_FERRAMENTAS_PROPOSTA_CHAT_AGENTE_TRANSCRIBROTHERS:
            continue
        saida.append(
            {
                "nome": nome,
                "titulo_secao_heading": _texto_ou_nulo(item.get("titulo_secao_heading")),
                "instrucoes": _texto_ou_nulo(item.get("instrucoes")),
                "caminhos_imagens": normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(
                    item.get("caminhos_imagens")
                ),
                "reescrever_secao": item.get("reescrever_secao") is True,
            }
        )
    return saida


def escolher_propostas_ferramenta_chat_agente_transcribrothers(
    *,
    ferramentas: list[dict[str, Any]],
    forcar_ferramenta: str | None,
    mensagem_usuario: str,
) -> list[dict[str, Any]]:
    forcar = (forcar_ferramenta or "").strip()
    if forcar and forcar not in NOMES_FERRAMENTAS_PROPOSTA_CHAT_AGENTE_TRANSCRIBROTHERS:
        forcar = ""
    saida: list[dict[str, Any]] = []
    for item in ferramentas:
        nome = item.get("nome")
        if nome not in NOMES_FERRAMENTAS_PROPOSTA_CHAT_AGENTE_TRANSCRIBROTHERS:
            continue
        if forcar and nome != forcar:
            continue
        instrucoes = item.get("instrucoes") or (mensagem_usuario or "").strip() or None
        saida.append(
            {
                "nome": nome,
                "titulo_secao_heading": item.get("titulo_secao_heading"),
                "instrucoes": instrucoes,
                "caminhos_imagens": normalizar_caminhos_imagens_proposta_ferramenta_chat_agente_transcribrothers(
                    item.get("caminhos_imagens")
                ),
                "reescrever_secao": item.get("reescrever_secao") is True,
            }
        )
    if not saida and forcar:
        saida.append(
            {
                "nome": forcar,
                "titulo_secao_heading": None,
                "instrucoes": (mensagem_usuario or "").strip() or None,
                "caminhos_imagens": [],
                "reescrever_secao": False,
            }
        )
    return saida


def escolher_proposta_ferramenta_chat_agente_transcribrothers(
    *,
    ferramentas: list[dict[str, Any]],
    forcar_ferramenta: str | None,
    mensagem_usuario: str,
) -> dict[str, Any] | None:
    propostas = escolher_propostas_ferramenta_chat_agente_transcribrothers(
        ferramentas=ferramentas,
        forcar_ferramenta=forcar_ferramenta,
        mensagem_usuario=mensagem_usuario,
    )
    return propostas[0] if propostas else None
