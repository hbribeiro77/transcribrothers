"""Resolve escopo da edição por seção: interpretação IA → validação no Markdown → refinamento até confirmar."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_interpretacao_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers import (
    InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers,
    _truncar_markdown_para_contexto_interpretacao_transcribrothers,
    interpretar_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers,
    parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers,
)
from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
    ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers,
    preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers,
)

MAX_TENTATIVAS_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = 2

SYSTEM_PROMPT_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = """\
Você corrige o JSON de escopo de uma edição parcial em tutorial Markdown.

O pedido anterior falhou na validação contra o tutorial real (trecho não encontrado, seção «##» errada, etc.).

Regras:
1) Responda APENAS um objeto JSON com os mesmos campos da interpretação anterior.
2) `trecho_ancora` deve ser substring COPIADA VERBATIM do tutorial_markdown (mesmas quebras de linha).
3) `titulo_secao_heading` deve ser uma linha da lista `secoes_nivel2` ou null.
4) Ajuste `modo_escopo_edicao` se necessário (trecho_local | a_partir_de | secao_inteira).
5) `confianca`: use "alta" só se o trecho/seção existir de fato no tutorial fornecido.
6) `explicacao_curta`: uma frase em pt-BR do escopo corrigido.
7) Não invente texto que não esteja no tutorial.
"""


@dataclass(frozen=True)
class EscopoEdicaoSecaoMarkdownResolvidoTranscribrothers:
    modo_escopo_edicao: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers
    trecho_ancora: str | None
    instrucoes_revisor: str
    titulo_secao_heading: str | None
    indice_secao: int | None
    preparacao: PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers
    interpretacao_blob: dict[str, Any]
    escopo_confirmado: bool
    tentativas_refinamento: int


def _escopo_confianca_aceita_para_geracao_transcribrothers(
    confianca: Literal["alta", "media", "baixa"],
) -> bool:
    return confianca in ("alta", "media")


def _validar_escopo_no_markdown_transcribrothers(
    markdown: str,
    *,
    modo: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    trecho_ancora: str | None,
    titulo_secao_heading: str | None,
    indice_secao: int | None,
) -> tuple[PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers | None, str | None]:
    if modo == "secao_inteira" and not (titulo_secao_heading or "").strip() and indice_secao is None:
        return None, (
            "Modo «seção inteira» exige titulo_secao_heading (linha «##») ou indice_secao."
        )
    if modo != "secao_inteira" and not (trecho_ancora or "").strip():
        return None, "Informe trecho_ancora copiado do tutorial para este modo."
    try:
        prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
            markdown,
            modo=modo,
            trecho_ancora=trecho_ancora,
            titulo_secao_heading=titulo_secao_heading,
            indice_secao=indice_secao,
        )
        return prep, None
    except ValueError as e:
        return None, str(e)


def _interpretacao_para_campos_escopo_transcribrothers(
    interpretado: InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers,
    blob: dict[str, Any],
) -> tuple[
    ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    str | None,
    str,
    str | None,
    Literal["alta", "media", "baixa"],
]:
    modo = interpretado.modo_escopo_edicao
    trecho = interpretado.trecho_ancora
    instrucoes = (interpretado.instrucoes_revisor_limpas or blob.get("instrucoes_revisor_limpas") or "").strip()
    titulo = (interpretado.titulo_secao_heading or blob.get("titulo_secao_heading") or "").strip() or None
    confianca = interpretado.confianca
    return modo, trecho, instrucoes, titulo, confianca


async def _refinar_interpretacao_escopo_edicao_secao_markdown_litellm_transcribrothers(
    *,
    pedido_usuario: str,
    markdown_tutorial: str,
    tentativa_anterior: dict[str, Any],
    motivo_falha_validacao: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> tuple[InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers, dict[str, Any]]:
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown_tutorial)
    headings = [s.linha_heading for s in secoes]
    payload_user = {
        "secoes_nivel2": headings,
        "pedido_usuario": pedido_usuario,
        "motivo_falha_validacao": motivo_falha_validacao,
        "interpretacao_anterior": tentativa_anterior,
        "tutorial_markdown": _truncar_markdown_para_contexto_interpretacao_transcribrothers(
            markdown_tutorial
        ),
    }
    texto = await litellm_chat_completions_texto_simples_transcribrothers(
        modelo=modelo_litellm,
        api_key=api_key_litellm,
        api_base=api_base_litellm,
        httpx_verify=http_verify_litellm,
        mensagens=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
            },
            {
                "role": "user",
                "content": "Corrija o escopo (JSON):\n"
                + json.dumps(payload_user, ensure_ascii=False, indent=2),
            },
        ],
        temperature=0.1,
        usar_response_format_json_object=True,
        httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
        httpx_timeout_read_segundos=min(
            180.0,
            max(60.0, float(configuracao.litellm_http_timeout_read_segundos) / 8),
        ),
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa="refino_escopo_edicao_secao",
        log_resumo_pedido=pedido_usuario[:300],
        log_metadados={"motivo_falha_validacao": motivo_falha_validacao[:500]},
    )
    parsed = parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers(texto)
    titulo = (parsed.titulo_secao_heading or "").strip() or None
    if titulo:
        titulo_rec = reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers(
            titulo, secoes
        )
        if titulo_rec:
            titulo = titulo_rec
    trecho = parsed.trecho_ancora if parsed.modo_escopo_edicao != "secao_inteira" else None
    blob: dict[str, Any] = {
        "pedido_usuario_original": pedido_usuario,
        "modo_escopo_edicao": parsed.modo_escopo_edicao,
        "trecho_ancora": trecho,
        "instrucoes_revisor_limpas": (parsed.instrucoes_revisor_limpas or "").strip() or pedido_usuario,
        "titulo_secao_heading": titulo,
        "confianca": parsed.confianca,
        "explicacao_curta": (parsed.explicacao_curta or "").strip(),
        "avisos": [],
        "refinamento": True,
        "motivo_falha_anterior": motivo_falha_validacao,
    }
    return (
        InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers(
            modo_escopo_edicao=parsed.modo_escopo_edicao,
            trecho_ancora=trecho,
            instrucoes_revisor_limpas=blob["instrucoes_revisor_limpas"],
            titulo_secao_heading=titulo,
            confianca=parsed.confianca,
            explicacao_curta=parsed.explicacao_curta,
        ),
        blob,
    )


async def resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers(
    *,
    pedido_usuario: str,
    markdown_tutorial: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    interpretar_escopo_automaticamente: bool,
    modo_escopo_edicao: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers = "trecho_local",
    trecho_ancora: str | None = None,
    titulo_secao_heading: str | None = None,
    indice_secao: int | None = None,
    on_atualizar_fase_pipeline: Callable[[str], Awaitable[None]] | None = None,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> EscopoEdicaoSecaoMarkdownResolvidoTranscribrothers:
    """
    Interpreta (se automático), valida no Markdown e refina com IA até escopo confirmado.
    Só retorna quando preparar_fatia tiver sucesso e confiança for alta ou média.
    """
    pedido = (pedido_usuario or "").strip()
    if not pedido:
        raise ValueError("Informe o pedido de edição.")

    historico_tentativas: list[dict[str, Any]] = []
    tentativas_refinamento = 0

    if interpretar_escopo_automaticamente:
        interpretado, blob = await interpretar_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers(
            pedido_usuario=pedido,
            markdown_tutorial=markdown_tutorial,
            configuracao=configuracao,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
            validar_ancora_no_markdown=False,
            steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        )
        historico_tentativas.append(dict(blob))
        modo, trecho, instrucoes, titulo, confianca = _interpretacao_para_campos_escopo_transcribrothers(
            interpretado, blob
        )
        indice_efetivo: int | None = None
    else:
        modo = modo_escopo_edicao
        trecho = (trecho_ancora or "").strip() or None
        instrucoes = pedido
        titulo = (titulo_secao_heading or "").strip() or None
        indice_efetivo = indice_secao
        confianca = "alta"
        blob = {
            "pedido_usuario_original": pedido,
            "modo_escopo_edicao": modo,
            "trecho_ancora": trecho,
            "instrucoes_revisor_limpas": instrucoes,
            "titulo_secao_heading": titulo,
            "confianca": confianca,
            "explicacao_curta": "Escopo definido manualmente pelo usuário.",
            "avisos": [],
            "escopo_manual": True,
        }
        interpretado = InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers(
            modo_escopo_edicao=modo,
            trecho_ancora=trecho,
            instrucoes_revisor_limpas=instrucoes,
            titulo_secao_heading=titulo,
            confianca="alta",
            explicacao_curta=blob["explicacao_curta"],
        )

    prep: PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers | None = None
    ultimo_erro: str | None = None

    if interpretar_escopo_automaticamente and on_atualizar_fase_pipeline is not None:
        await on_atualizar_fase_pipeline("validando_escopo_edicao_secao_markdown")

    for tentativa in range(MAX_TENTATIVAS_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS + 1):
        if (
            interpretar_escopo_automaticamente
            and tentativa > 0
            and on_atualizar_fase_pipeline is not None
        ):
            await on_atualizar_fase_pipeline("validando_escopo_edicao_secao_markdown")
        prep, ultimo_erro = _validar_escopo_no_markdown_transcribrothers(
            markdown_tutorial,
            modo=modo,
            trecho_ancora=trecho,
            titulo_secao_heading=titulo,
            indice_secao=indice_efetivo,
        )
        if prep is not None and _escopo_confianca_aceita_para_geracao_transcribrothers(confianca):
            break

        if prep is not None and confianca == "baixa" and interpretar_escopo_automaticamente:
            ultimo_erro = (
                "A interpretação do pedido ficou com confiança baixa; é necessário refinar o escopo."
            )
            prep = None

        if not interpretar_escopo_automaticamente or tentativa >= MAX_TENTATIVAS_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS:
            break

        tentativas_refinamento += 1
        if on_atualizar_fase_pipeline is not None:
            await on_atualizar_fase_pipeline(
                "refinando_escopo_pedido_edicao_secao_markdown_litellm"
            )
        motivo = ultimo_erro or "Escopo não validado no tutorial."
        interpretado, blob_refino = await _refinar_interpretacao_escopo_edicao_secao_markdown_litellm_transcribrothers(
            pedido_usuario=pedido,
            markdown_tutorial=markdown_tutorial,
            tentativa_anterior=historico_tentativas[-1],
            motivo_falha_validacao=motivo,
            configuracao=configuracao,
            modelo_litellm=modelo_litellm,
            api_key_litellm=api_key_litellm,
            api_base_litellm=api_base_litellm,
            http_verify_litellm=http_verify_litellm,
            steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        )
        historico_tentativas.append(dict(blob_refino))
        blob = blob_refino
        modo, trecho, instrucoes, titulo, confianca = _interpretacao_para_campos_escopo_transcribrothers(
            interpretado, blob
        )

    if prep is None:
        secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown_tutorial)
        sugestoes = ", ".join(s.linha_heading for s in secoes[:8])
        raise ValueError(
            f"Não foi possível localizar no tutorial o que você pediu para editar. {ultimo_erro or ''} "
            f"Tente citar o título «##» ou colar um trecho exato do texto. "
            f"Seções disponíveis: {sugestoes or '(nenhuma «##»)'}"
        )

    if not _escopo_confianca_aceita_para_geracao_transcribrothers(confianca):
        raise ValueError(
            "O escopo do pedido continua ambíguo (confiança baixa). "
            "Reformule o pedido citando a seção ou um trecho do tutorial, ou use «Ajustar escopo manualmente»."
        )

    regiao = prep.regiao
    blob_final: dict[str, Any] = {
        **blob,
        "escopo_confirmado": True,
        "regiao_rotulo": regiao.rotulo_regiao,
        "regiao_prefacio_introducao": regiao.eh_prefacio,
        "tentativas_refinamento": tentativas_refinamento,
        "historico_interpretacoes": historico_tentativas,
    }

    return EscopoEdicaoSecaoMarkdownResolvidoTranscribrothers(
        modo_escopo_edicao=modo,
        trecho_ancora=trecho,
        instrucoes_revisor=instrucoes,
        titulo_secao_heading=titulo,
        indice_secao=indice_efetivo,
        preparacao=prep,
        interpretacao_blob=blob_final,
        escopo_confirmado=True,
        tentativas_refinamento=tentativas_refinamento,
    )
