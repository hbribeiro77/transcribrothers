"""Verificação pós-regeneração de seção: redundância com outras seções ``##`` do tutorial."""

from __future__ import annotations

import json
from datetime import datetime, timezone
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
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    SecaoMarkdownNivel2TutorialTranscribrothers,
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
)

_LIMITE_CHARS_RESULTADO_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS = 48_000

SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS = """\
Você é um auditor de redundância em tutoriais Markdown com várias seções (##).

Tarefa: comparar a **seção editada (proposta)** com as **outras seções** do mesmo documento e detectar se a proposta repete temas, passos ou explicações que já estão bem cobertos noutro sítio.

Regras:
1) Responda APENAS com um único objeto JSON (sem Markdown à volta).
2) `redundancia` = a proposta reexplica de forma substancial algo que outra seção já cobre (mesmo passo, mesmo fluxo, mesma UI, mesmo contexto introdutório).
3) `atencao` = possível sobreposição leve ou reintrodução parcial de contexto; não é grave.
4) `ok` = a proposta foca no escopo da sua seção sem duplicar outras.
5) Não penalize referências curtas necessárias (ex.: «como na secção anterior») se o corpo não repetir o passo a passo.
6) Liste no máximo 12 itens em `itens`; se estiver bem, `itens` pode ser [].
7) Campos na raiz: `classificacao_global`, `mensagem_resumo`, `itens`.
8) Cada item: `tema`, `classificacao` (ok|atencao|redundancia), `secao_ja_cobre` (heading ## exato ou vazio), `trecho_ou_resumo_na_proposta`, `justificativa_curta`.
9) Use português do Brasil em `mensagem_resumo` e `justificativa_curta`.
"""


class ItemVerificacaoRedundanciaSecaoJsonTranscribrothers(BaseModel):
    tema: str = Field(default="", max_length=2000)
    classificacao: Literal["ok", "atencao", "redundancia"] = "atencao"
    secao_ja_cobre: str = Field(default="", max_length=500)
    trecho_ou_resumo_na_proposta: str = Field(default="", max_length=3000)
    justificativa_curta: str = Field(default="", max_length=3000)


class ResultadoVerificacaoRedundanciaSecaoJsonTranscribrothers(BaseModel):
    classificacao_global: Literal["ok", "atencao", "redundancia"] = "atencao"
    mensagem_resumo: str = Field(default="", max_length=8000)
    itens: list[ItemVerificacaoRedundanciaSecaoJsonTranscribrothers] = Field(default_factory=list)

    @field_validator("itens")
    @classmethod
    def _limitar_itens(cls, v: list[ItemVerificacaoRedundanciaSecaoJsonTranscribrothers]) -> list:
        return v[:12]


def _truncar_texto_transcribrothers(texto: str, max_chars: int) -> tuple[str, bool]:
    s = texto or ""
    if len(s) <= max_chars:
        return s, False
    return s[: max_chars - 40] + "\n\n…[texto truncado para análise]…\n", True


def montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers(
    markdown_completo: str,
    secao_em_edicao: SecaoMarkdownNivel2TutorialTranscribrothers,
    *,
    max_chars_por_secao: int,
    max_secoes: int,
) -> tuple[list[dict[str, str]], bool]:
    """
    Devolve lista de {heading, markdown} das outras seções.
    Prioriza vizinhas (índice ±1) e depois as restantes, até max_secoes.
    """
    todas = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown_completo)
    outras = [s for s in todas if s.indice != secao_em_edicao.indice]
    if not outras:
        return [], False

    def _ordem_prioridade(s: SecaoMarkdownNivel2TutorialTranscribrothers) -> tuple[int, int]:
        dist = abs(s.indice - secao_em_edicao.indice)
        return (dist, s.indice)

    outras.sort(key=_ordem_prioridade)
    outras = outras[: max(1, int(max_secoes))]

    algum_truncado = False
    saida: list[dict[str, str]] = []
    for s in outras:
        corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(markdown_completo, s)
        corpo_cortado, trunc = _truncar_texto_transcribrothers(corpo, max_chars_por_secao)
        algum_truncado = algum_truncado or trunc
        saida.append({"heading": s.linha_heading, "markdown": corpo_cortado})
    return saida, algum_truncado


def parsear_resultado_verificacao_redundancia_secao_de_texto_llm_transcribrothers(
    texto_bruto: str,
) -> ResultadoVerificacaoRedundanciaSecaoJsonTranscribrothers:
    raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
    data = json.loads(raw_json)
    if not isinstance(data, dict):
        raise ValueError("JSON raiz deve ser um objeto.")
    return ResultadoVerificacaoRedundanciaSecaoJsonTranscribrothers.model_validate(data)


def serializar_resultado_verificacao_redundancia_para_steps_json_transcribrothers(
    resultado: ResultadoVerificacaoRedundanciaSecaoJsonTranscribrothers,
    *,
    modelo_litellm: str,
    outras_secoes_truncadas: bool,
) -> dict[str, Any]:
    blob: dict[str, Any] = {
        "sucesso": True,
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "modelo_litellm": modelo_litellm.strip(),
        "classificacao_global": resultado.classificacao_global,
        "mensagem_resumo": resultado.mensagem_resumo.strip(),
        "itens": [it.model_dump() for it in resultado.itens],
        "outras_secoes_truncadas_para_prompt": outras_secoes_truncadas,
    }
    serial = json.dumps(blob, ensure_ascii=False)
    if len(serial) > _LIMITE_CHARS_RESULTADO_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS:
        blob["itens"] = blob["itens"][:6]
        blob["mensagem_resumo"] = (blob.get("mensagem_resumo") or "")[:4000] + "…"
        blob["truncado_para_limite_steps_json"] = True
    return blob


SYSTEM_PROMPT_CORRECAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS = """\
Você é um editor técnico. Reescreve APENAS uma seção «##» de um tutorial para remover redundância com outras seções.

Regras obrigatórias:
1) Responda somente com o Markdown da seção — incluindo a mesma linha «## Título» (texto idêntico ao pedido).
2) Remova ou enxugue trechos que repetem passos, contexto ou explicações já cobertos nas outras seções indicadas no relatório do auditor.
3) Mantenha o foco exclusivo desta seção; não copie conteúdo integral de outras seções.
4) Preserve imagens `![](assets/….png)` e links temporais quando ainda fizerem sentido nesta seção.
5) Não invente factos novos; use a transcrição só para precisão factual.
6) Não envolva a resposta em blocos de código; só Markdown da seção.
"""


def deve_aplicar_correcao_automatica_redundancia_secao_transcribrothers(
    verificacao_blob: dict[str, Any],
    *,
    correcao_automatica_habilitada: bool,
    correcao_automatica_incluir_classificacao_atencao: bool,
) -> bool:
    if not bool(correcao_automatica_habilitada):
        return False
    if verificacao_blob.get("omitida"):
        return False
    if verificacao_blob.get("sucesso") is False:
        return False
    cls = str(verificacao_blob.get("classificacao_global") or "").strip().lower()
    if cls == "redundancia":
        return True
    if cls == "atencao" and bool(correcao_automatica_incluir_classificacao_atencao):
        return True
    return False


def _limpar_markdown_resposta_llm_secao_transcribrothers(texto: str) -> str:
    t = (texto or "").strip()
    if t.startswith("```"):
        linhas = t.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        t = "\n".join(linhas).strip()
    return t


async def corrigir_secao_markdown_apos_verificacao_redundancia_litellm_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    linha_heading_secao: str,
    secao_markdown_proposta: str,
    verificacao_redundancia_blob: dict[str, Any],
    outras_secoes_payload: list[dict[str, str]],
    instrucoes_revisor: str,
    transcricao_resumo_json: dict[str, Any],
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> str:
    payload = {
        "secao_heading": linha_heading_secao.strip(),
        "instrucoes_revisor": (instrucoes_revisor or "").strip(),
        "secao_proposta_com_redundancia": secao_markdown_proposta.strip(),
        "relatorio_auditor_redundancia": verificacao_redundancia_blob,
        "outras_secoes": outras_secoes_payload,
        "transcricao_contexto": transcricao_resumo_json,
    }
    user = (
        "Dados (JSON):\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Reescreva a seção eliminando a redundância apontada, mantendo o mesmo «##» no início."
    )
    texto = await litellm_chat_completions_texto_simples_transcribrothers(
        modelo=modelo_litellm,
        api_key=api_key_litellm,
        api_base=api_base_litellm,
        httpx_verify=http_verify_litellm,
        mensagens=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_CORRECAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
            },
            {"role": "user", "content": user},
        ],
        temperature=0.25,
        usar_response_format_json_object=False,
        httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
        httpx_timeout_read_segundos=min(
            600.0,
            max(90.0, float(configuracao.litellm_http_timeout_read_segundos) / 5),
        ),
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa="correcao_redundancia_secao_markdown",
        log_resumo_pedido=linha_heading_secao.strip()[:200],
    )
    out = _limpar_markdown_resposta_llm_secao_transcribrothers(texto)
    if not out:
        raise RuntimeError("Correção automática de redundância devolveu seção vazia.")
    return out


def blob_verificacao_redundancia_secao_omitida_por_configuracao_transcribrothers(
    *,
    motivo: str = "desativada_por_configuracao",
) -> dict[str, Any]:
    return {
        "omitida": True,
        "motivo": motivo,
        "executado_em": datetime.now(timezone.utc).isoformat(),
    }


async def executar_verificacao_redundancia_secao_markdown_litellm_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    markdown_completo_atual: str,
    secao_em_edicao: SecaoMarkdownNivel2TutorialTranscribrothers,
    secao_markdown_proposta: str,
    instrucoes_revisor: str,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> dict[str, Any]:
    max_por_secao = max(
        800, int(configuracao.verificacao_redundancia_secao_max_chars_corpo_outra_secao)
    )
    max_secoes = max(1, min(24, int(configuracao.verificacao_redundancia_secao_max_outras_secoes)))

    outras, trunc_outras = montar_outras_secoes_markdown_para_verificacao_redundancia_transcribrothers(
        markdown_completo_atual,
        secao_em_edicao,
        max_chars_por_secao=max_por_secao,
        max_secoes=max_secoes,
    )

    payload = {
        "secao_em_edicao_heading": secao_em_edicao.linha_heading,
        "instrucoes_revisor": (instrucoes_revisor or "").strip(),
        "secao_proposta_markdown": secao_markdown_proposta.strip(),
        "outras_secoes": outras,
    }
    user = (
        "Dados (JSON):\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
    )

    try:
        texto = await litellm_chat_completions_texto_simples_transcribrothers(
            modelo=modelo_litellm,
            api_key=api_key_litellm,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            mensagens=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
                },
                {"role": "user", "content": user},
            ],
            temperature=0.15,
            usar_response_format_json_object=bool(
                configuracao.transcricao_litellm_chat_json_object_response_format
            ),
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=min(
                600.0,
                max(90.0, float(configuracao.litellm_http_timeout_read_segundos) / 6),
            ),
            steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
            log_etapa="verificacao_redundancia_secao_markdown",
            log_resumo_pedido=secao_em_edicao.linha_heading[:200],
        )
    except Exception as e:
        from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
            PipelineCanceladoPeloUsuarioTranscribrothers,
        )

        if isinstance(e, PipelineCanceladoPeloUsuarioTranscribrothers):
            raise
        return {
            "sucesso": False,
            "executado_em": datetime.now(timezone.utc).isoformat(),
            "modelo_litellm": modelo_litellm.strip(),
            "erro": str(e).strip()[:8000],
            "erro_tipo": type(e).__name__,
            "outras_secoes_truncadas_para_prompt": trunc_outras,
        }

    try:
        parsed = parsear_resultado_verificacao_redundancia_secao_de_texto_llm_transcribrothers(texto)
        resultado = serializar_resultado_verificacao_redundancia_para_steps_json_transcribrothers(
            parsed,
            modelo_litellm=modelo_litellm,
            outras_secoes_truncadas=trunc_outras,
        )
        if steps_para_log_decisoes_ia is not None:
            from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
                registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            )

            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
                steps_para_log_decisoes_ia,
                etapa="verificacao_redundancia_decisao",
                resumo=str(resultado.get("classificacao_global") or resultado.get("mensagem_resumo") or "Concluída")[
                    :500
                ],
                detalhe=str(resultado.get("mensagem_resumo") or "")[:2000] or None,
                modelo=modelo_litellm,
            )
        return resultado
    except Exception as e:
        from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
            PipelineCanceladoPeloUsuarioTranscribrothers,
        )

        if isinstance(e, PipelineCanceladoPeloUsuarioTranscribrothers):
            raise
        return {
            "sucesso": False,
            "executado_em": datetime.now(timezone.utc).isoformat(),
            "modelo_litellm": modelo_litellm.strip(),
            "erro": str(e).strip()[:8000],
            "erro_tipo": type(e).__name__,
            "outras_secoes_truncadas_para_prompt": trunc_outras,
        }
