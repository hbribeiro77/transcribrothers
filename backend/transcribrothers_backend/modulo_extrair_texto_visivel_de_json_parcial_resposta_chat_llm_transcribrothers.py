"""Extrai o campo `texto` de um JSON de chat ainda incompleto (stream)."""

from __future__ import annotations

import json
import re

_RE_INICIO_VALOR_TEXTO_JSON_TRANSCRIBROTHERS = re.compile(
    r'"texto"\s*:\s*"',
    re.DOTALL,
)


def _desescapar_prefixo_string_json_transcribrothers(cru: str) -> str:
    saida: list[str] = []
    indice = 0
    while indice < len(cru):
        caractere = cru[indice]
        if caractere != "\\":
            saida.append(caractere)
            indice += 1
            continue
        if indice + 1 >= len(cru):
            break
        seguinte = cru[indice + 1]
        if seguinte == "n":
            saida.append("\n")
            indice += 2
        elif seguinte == "t":
            saida.append("\t")
            indice += 2
        elif seguinte == "r":
            saida.append("\r")
            indice += 2
        elif seguinte == '"':
            saida.append('"')
            indice += 2
        elif seguinte == "\\":
            saida.append("\\")
            indice += 2
        elif seguinte == "/":
            saida.append("/")
            indice += 2
        elif seguinte == "u" and indice + 5 < len(cru):
            saida.append(chr(int(cru[indice + 2 : indice + 6], 16)))
            indice += 6
        elif seguinte == "u":
            break
        else:
            saida.append(seguinte)
            indice += 2
    return "".join(saida)


def extrair_texto_visivel_de_json_parcial_resposta_chat_llm_transcribrothers(acumulado: str) -> str:
    fonte = acumulado or ""
    try:
        data = json.loads(fonte[fonte.find("{") :] if "{" in fonte else fonte)
        if isinstance(data, dict) and isinstance(data.get("texto"), str):
            return data["texto"]
    except json.JSONDecodeError:
        pass
    match = _RE_INICIO_VALOR_TEXTO_JSON_TRANSCRIBROTHERS.search(fonte)
    if match is None:
        return ""
    resto = fonte[match.end() :]
    bruto: list[str] = []
    escape = False
    for caractere in resto:
        if escape:
            bruto.append("\\")
            bruto.append(caractere)
            escape = False
            continue
        if caractere == "\\":
            escape = True
            continue
        if caractere == '"':
            break
        bruto.append(caractere)
    return _desescapar_prefixo_string_json_transcribrothers("".join(bruto))
