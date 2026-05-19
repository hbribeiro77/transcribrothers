"""Nomenclatura e leitura/escrita de metadados de imagens anotadas (original + .anotado.png)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from transcribrothers_backend.modulo_constante_chave_steps_json_anotacoes_imagens_tutorial_assets_png_transcribrothers import (
    CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS,
    SUFIXO_NOME_ARQUIVO_PNG_ANOTADO_ANTES_EXTENSAO_TRANSCRIBROTHERS,
)

VersaoExibicaoImagemTutorialTranscribrothers = Literal["original", "anotado"]


def nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome: str) -> bool:
    n = nome.strip()
    if not n or "/" in n or "\\" in n or ".." in n:
        return False
    if not n.lower().endswith(".png"):
        return False
    if SUFIXO_NOME_ARQUIVO_PNG_ANOTADO_ANTES_EXTENSAO_TRANSCRIBROTHERS in n.lower():
        return False
    return True


def derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original: str) -> str:
    if not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome_original):
        raise ValueError("Nome de arquivo PNG original inválido para anotação.")
    base = nome_original[:-4]
    return f"{base}{SUFIXO_NOME_ARQUIVO_PNG_ANOTADO_ANTES_EXTENSAO_TRANSCRIBROTHERS}.png"


def obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(
    steps_json: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if not steps_json:
        return {}
    raw = steps_json.get(CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS)
    if not isinstance(raw, dict):
        return {}
    saida: dict[str, dict[str, Any]] = {}
    for chave, valor in raw.items():
        if isinstance(chave, str) and isinstance(valor, dict):
            saida[chave] = dict(valor)
    return saida


def registro_anotacao_imagem_para_resposta_api_transcribrothers(
    nome_original: str,
    registro: dict[str, Any],
    arquivo_anotado_existe: bool,
) -> dict[str, Any]:
    nome_anotado = registro.get("nome_arquivo_anotado")
    if not isinstance(nome_anotado, str) or not nome_anotado:
        nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original)
    exibir = registro.get("exibir_no_tutorial")
    if exibir not in ("original", "anotado"):
        exibir = "anotado" if arquivo_anotado_existe else "original"
    return {
        "nome_arquivo_original": nome_original,
        "nome_arquivo_anotado": nome_anotado,
        "exibir_no_tutorial": exibir,
        "tem_arquivo_anotado": arquivo_anotado_existe,
        "atualizado_em": registro.get("atualizado_em"),
    }


def resolver_nome_arquivo_png_para_exibicao_no_tutorial_transcribrothers(
    nome_original: str,
    steps_json: dict[str, Any] | None,
    *,
    arquivo_anotado_existe: bool | None = None,
) -> str:
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(steps_json)
    reg = mapa.get(nome_original)
    if not reg:
        return nome_original
    nome_anotado = reg.get("nome_arquivo_anotado")
    if not isinstance(nome_anotado, str) or not nome_anotado:
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original)
        except ValueError:
            return nome_original
    exibir = reg.get("exibir_no_tutorial")
    if exibir != "anotado":
        return nome_original
    if arquivo_anotado_existe is False:
        return nome_original
    return nome_anotado


def mesclar_registro_anotacao_apos_gravar_png_anotado_transcribrothers(
    steps_json: dict[str, Any],
    nome_original: str,
    *,
    exibir_no_tutorial: VersaoExibicaoImagemTutorialTranscribrothers = "anotado",
) -> dict[str, Any]:
    novo = dict(steps_json)
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(novo)
    nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original)
    mapa[nome_original] = {
        "nome_arquivo_anotado": nome_anotado,
        "exibir_no_tutorial": exibir_no_tutorial,
        "tem_arquivo_anotado": True,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }
    novo[CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS] = mapa
    return novo


def mesclar_registro_exibicao_imagem_tutorial_transcribrothers(
    steps_json: dict[str, Any],
    nome_original: str,
    versao: VersaoExibicaoImagemTutorialTranscribrothers,
) -> dict[str, Any]:
    if versao not in ("original", "anotado"):
        raise ValueError("Versão de exibição inválida.")
    novo = dict(steps_json)
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(novo)
    reg = dict(mapa.get(nome_original) or {})
    reg["nome_arquivo_anotado"] = reg.get("nome_arquivo_anotado") or derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(
        nome_original
    )
    reg["exibir_no_tutorial"] = versao
    reg["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    mapa[nome_original] = reg
    novo[CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS] = mapa
    return novo


def mesclar_remocao_anotacao_imagem_tutorial_transcribrothers(
    steps_json: dict[str, Any],
    nome_original: str,
) -> dict[str, Any]:
    novo = dict(steps_json)
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(novo)
    mapa.pop(nome_original, None)
    if mapa:
        novo[CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS] = mapa
    else:
        novo.pop(CHAVE_STEPS_JSON_ANOTACOES_IMAGENS_TUTORIAL_ASSETS_PNG_TRANSCRIBROTHERS, None)
    return novo


def substituir_referencia_asset_png_no_markdown_por_nome_arquivo_transcribrothers(
    markdown: str,
    nome_original: str,
    nome_destino: str,
) -> str:
    """Substitui `![](assets/nome_original)` por `![](assets/nome_destino)` (uma ocorrência por vez, todas)."""
    href_antigo = f"assets/{nome_original}"
    href_novo = f"assets/{nome_destino}"
    saida = markdown.replace(f"]({href_antigo})", f"]({href_novo})")
    saida = saida.replace(f"](<{href_antigo}>)", f"](<{href_novo}>)")
    return saida
