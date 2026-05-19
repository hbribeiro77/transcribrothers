"""Interpreta pedido do usuário em linguagem natural → modo de escopo, trecho âncora e instruções."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    extrair_primeiro_objeto_json_de_texto_llm_transcribrothers,
)
from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
    ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    localizar_intervalo_trecho_ancora_no_texto_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers,
)

SYSTEM_PROMPT_INTERPRETACAO_PEDIDO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = """\
Você analisa pedidos de edição em tutoriais Markdown e devolve JSON estruturado.

O tutorial pode ter:
- Uma introdução ANTES da primeira «## » (título «# » e parágrafos iniciais) — use trecho_local ou a_partir_de nessa área.
- Seções «## » depois — use trecho_local, a_partir_de ou secao_inteira.

O usuário escreve em português do Brasil, de forma orgânica. Exemplos:
- «Nessa parte aqui: [texto] — faça uma intro mais detalhada» → modo trecho_local; trecho_ancora = cópia literal do tutorial.
- «Detalhe melhor a partir de "Dinâmica do Processo"» → modo a_partir_de; trecho_ancora = texto que marca o início no tutorial.
- «Reescreva a seção Personalização da Lista de Pastas com tom mais didático» → modo secao_inteira; titulo_secao_heading = «## …» exato.

Regras:
1) Responda APENAS um objeto JSON (sem Markdown à volta).
2) `modo_escopo_edicao`: "trecho_local" | "a_partir_de" | "secao_inteira".
3) `trecho_ancora`: substring COPIADA VERBATIM do tutorial fornecido (mesmas quebras de linha). Obrigatório exceto em secao_inteira. Mínimo ~15 caracteres úteis; inclua título + início do parágrafo se ajudar a localizar.
4) `instrucoes_revisor_limpas`: só o pedido de edição, sem citações longas do tutorial.
5) `titulo_secao_heading`: copie da lista `secoes_nivel2` do JSON do usuário (linha «## …» exata). Se não tiver certeza, null — não invente variações do título.
6) `confianca`: "alta" | "media" | "baixa".
7) `explicacao_curta`: uma frase em pt-BR do que entendeu (para mostrar ao usuário).
8) Se o pedido for ambíguo, escolha o modo mais provável e confianca "baixa".
9) Não invente trechos que não existam no tutorial.
"""


class InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers(BaseModel):
    modo_escopo_edicao: Literal["trecho_local", "a_partir_de", "secao_inteira"]
    trecho_ancora: str | None = Field(default=None, max_length=16_000)
    instrucoes_revisor_limpas: str = Field(..., min_length=1, max_length=16_000)
    titulo_secao_heading: str | None = Field(default=None, max_length=500)
    confianca: Literal["alta", "media", "baixa"] = "media"
    explicacao_curta: str = Field(default="", max_length=2000)

    @field_validator("trecho_ancora", mode="before")
    @classmethod
    def _normalizar_trecho_opcional(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None


def parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers(
    texto_bruto: str,
) -> InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers:
    """Extrai JSON da resposta do modelo (string → objeto → validação Pydantic)."""
    raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
    try:
        data: object = json.loads(raw_json)
    except json.JSONDecodeError as e:
        trecho = (texto_bruto or "")[:1200]
        raise ValueError(
            "A interpretação do pedido não devolveu JSON válido. Tente de novo ou use escopo manual. "
            f"Detalhe: {e}. Trecho: {trecho!r}"
        ) from e
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(
                "A interpretação do pedido veio como texto JSON aninhado inválido."
            ) from e
    if not isinstance(data, dict):
        raise ValueError("JSON da interpretação do pedido deve ser um objeto na raiz.")
    return InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers.model_validate(data)


def _truncar_markdown_para_contexto_interpretacao_transcribrothers(md: str, max_chars: int = 95_000) -> str:
    t = md or ""
    if len(t) <= max_chars:
        return t
    metade = max_chars // 2
    return t[:metade] + "\n\n[… tutorial truncado para interpretação …]\n\n" + t[-metade:]


async def interpretar_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers(
    *,
    pedido_usuario: str,
    markdown_tutorial: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    validar_ancora_no_markdown: bool = True,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> tuple[InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers, dict[str, Any]]:
    pedido = (pedido_usuario or "").strip()
    if not pedido:
        raise ValueError("Informe o pedido de edição em linguagem natural.")

    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown_tutorial)
    headings = [s.linha_heading for s in secoes]
    payload_user = {
        "secoes_nivel2": headings,
        "pedido_usuario": pedido,
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
                "content": SYSTEM_PROMPT_INTERPRETACAO_PEDIDO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
            },
            {
                "role": "user",
                "content": "Dados (JSON):\n"
                + json.dumps(payload_user, ensure_ascii=False, indent=2),
            },
        ],
        temperature=0.15,
        usar_response_format_json_object=True,
        httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
        httpx_timeout_read_segundos=min(
            180.0,
            max(60.0, float(configuracao.litellm_http_timeout_read_segundos) / 8),
        ),
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa="interpretacao_escopo_edicao_secao",
        log_resumo_pedido=pedido[:300],
    )
    parsed = parsear_interpretacao_pedido_edicao_secao_markdown_de_texto_llm_transcribrothers(texto)

    instrucoes = (parsed.instrucoes_revisor_limpas or "").strip() or pedido
    modo: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers = parsed.modo_escopo_edicao
    trecho = parsed.trecho_ancora
    titulo = (parsed.titulo_secao_heading or "").strip() or None
    avisos: list[str] = []

    if titulo:
        titulo_reconciliado = reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers(
            titulo, secoes
        )
        if titulo_reconciliado:
            titulo = titulo_reconciliado
        elif titulo not in headings:
            avisos.append(
                f"O heading sugerido ({titulo!r}) não corresponde a nenhuma seção «##» listada."
            )
            if modo == "secao_inteira":
                titulo = None
    if modo != "secao_inteira":
        if not trecho:
            msg_sem_trecho = (
                "Não foi possível identificar um trecho do tutorial no seu pedido. "
                "Cole o trecho manualmente em «Ajustar escopo» ou seja mais explícito (ex.: «nessa parte: …»)."
            )
            if validar_ancora_no_markdown:
                raise ValueError(msg_sem_trecho)
            avisos.append(msg_sem_trecho)
        elif validar_ancora_no_markdown:
            try:
                localizar_intervalo_trecho_ancora_no_texto_transcribrothers(markdown_tutorial, trecho)
            except ValueError as e:
                avisos.append(str(e))
                raise ValueError(
                    f"A IA sugeriu um trecho que não bate com o tutorial: {e} "
                    "Tente reformular o pedido ou cole o trecho exato em «Ajustar escopo»."
                ) from e
        else:
            try:
                localizar_intervalo_trecho_ancora_no_texto_transcribrothers(markdown_tutorial, trecho)
            except ValueError as e:
                avisos.append(str(e))
    else:
        if not titulo and headings:
            avisos.append("Seção não identificada; será necessário escolher a seção ## manualmente.")
        trecho = None

    blob: dict[str, Any] = {
        "pedido_usuario_original": pedido,
        "modo_escopo_edicao": modo,
        "trecho_ancora": trecho,
        "instrucoes_revisor_limpas": instrucoes,
        "titulo_secao_heading": titulo,
        "confianca": parsed.confianca,
        "explicacao_curta": (parsed.explicacao_curta or "").strip(),
        "avisos": avisos,
    }
    return (
        InterpretacaoPedidoEdicaoSecaoMarkdownJsonTranscribrothers(
            modo_escopo_edicao=modo,
            trecho_ancora=trecho,
            instrucoes_revisor_limpas=instrucoes,
            titulo_secao_heading=titulo,
            confianca=parsed.confianca,
            explicacao_curta=parsed.explicacao_curta,
        ),
        blob,
    )
