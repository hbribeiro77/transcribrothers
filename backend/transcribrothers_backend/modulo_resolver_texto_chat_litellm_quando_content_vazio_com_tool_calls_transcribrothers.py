"""Quando o modelo só devolve tool_calls (content vazio), monta JSON de rascunho com o plano na bolha."""

from __future__ import annotations

import json
from typing import Any

_ROTULO_FERRAMENTA_RASCUNHO_TRANSCRIBROTHERS: dict[str, str] = {
    "sem_video": "Documento inteiro",
    "edicao_parcial": "Edição de seção",
    "revisao_profunda": "Revisão profunda",
}

_LIMITE_INSTRUCOES_NO_TEXTO_RASCUNHO_TRANSCRIBROTHERS = 1200


def _argumentos_tool_call_como_dict_transcribrothers(item: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    funcao = item.get("function")
    if not isinstance(funcao, dict):
        return "", {}
    nome = str(funcao.get("name") or "").strip()
    bruto = funcao.get("arguments")
    if isinstance(bruto, dict):
        return nome, bruto
    if not isinstance(bruto, str) or not bruto.strip():
        return nome, {}
    try:
        parsed = json.loads(bruto)
    except json.JSONDecodeError:
        return nome, {}
    if not isinstance(parsed, dict):
        return nome, {}
    return nome, parsed


def _encurtar_instrucoes_rascunho_transcribrothers(texto: str) -> str:
    limpo = texto.strip()
    limite = _LIMITE_INSTRUCOES_NO_TEXTO_RASCUNHO_TRANSCRIBROTHERS
    if len(limpo) <= limite:
        return limpo
    return limpo[:limite].rstrip() + "…"


def montar_texto_plano_rascunho_a_partir_de_tool_calls_transcribrothers(
    tool_calls: list[dict[str, Any]] | None,
) -> str:
    blocos: list[str] = []
    for item in tool_calls or []:
        if not isinstance(item, dict):
            continue
        nome, args = _argumentos_tool_call_como_dict_transcribrothers(item)
        if not nome:
            continue
        rotulo = _ROTULO_FERRAMENTA_RASCUNHO_TRANSCRIBROTHERS.get(nome, nome)
        heading = str(args.get("titulo_secao_heading") or "").strip()
        instrucoes = _encurtar_instrucoes_rascunho_transcribrothers(str(args.get("instrucoes") or ""))
        titulo = f"{rotulo} — {heading}" if heading else rotulo
        if instrucoes:
            blocos.append(f"**{titulo}:** {instrucoes}")
        else:
            blocos.append(f"**{titulo}**")
    introducao = (
        "Sugestão de alteração (ainda não alterei nada no documento). "
        "Use **Aplicar** se quiser seguir com o plano abaixo."
    )
    if not blocos:
        return introducao
    return introducao + "\n\n" + "\n\n".join(blocos)


def montar_json_chat_agente_quando_so_houve_tool_calls_transcribrothers(
    tool_calls: list[dict[str, Any]] | None = None,
) -> str:
    return json.dumps(
        {
            "texto": montar_texto_plano_rascunho_a_partir_de_tool_calls_transcribrothers(tool_calls),
            "estado": "rascunho",
            "executar": False,
            "citacoes": [],
            "instantes_imagem_segundos": [],
            "ferramentas": [],
        },
        ensure_ascii=False,
    )


def resolver_texto_chat_litellm_content_ou_tool_calls_transcribrothers(
    conteudo: str | None,
    tool_calls: list[dict[str, Any]] | None,
) -> str:
    texto = (conteudo or "").strip()
    if texto:
        return texto
    if tool_calls:
        return montar_json_chat_agente_quando_so_houve_tool_calls_transcribrothers(tool_calls)
    raise RuntimeError("O modelo devolveu conteúdo vazio no chat.")
