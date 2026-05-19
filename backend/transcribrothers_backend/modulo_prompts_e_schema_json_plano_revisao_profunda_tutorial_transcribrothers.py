from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

_LIMITE_CHARS_PLANO_JSON_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS = 200_000


class EvidenciaTranscricaoItemPlanoRevisaoProfundaTranscribrothers(BaseModel):
    """Trecho da transcrição que sustenta uma lacuna."""

    citacao: str = Field(..., min_length=1, max_length=4000)
    inicio_segundos: float | None = None
    fim_segundos: float | None = None


class ItemTopicoPlanoRevisaoProfundaTranscribrothers(BaseModel):
    """Um tópico do tutorial a aprofundar."""

    id: str = Field(..., min_length=1, max_length=64)
    titulo_secao: str = Field(..., min_length=1, max_length=500)
    lacunas: list[str] = Field(default_factory=list)
    evidencias_transcricao: list[EvidenciaTranscricaoItemPlanoRevisaoProfundaTranscribrothers] = Field(
        default_factory=list
    )
    prioridade: int = Field(default=3, ge=1, le=9)

    @field_validator("lacunas")
    @classmethod
    def _limitar_tamanho_lacunas(cls, v: list[str]) -> list[str]:
        out: list[str] = []
        for s in v[:24]:
            t = (s or "").strip()
            if t and len(t) <= 2000:
                out.append(t)
        return out


class PlanoRevisaoProfundaTutorialTranscribrothers(BaseModel):
    """Plano devolvido pelo analista (JSON)."""

    topicos: list[ItemTopicoPlanoRevisaoProfundaTranscribrothers] = Field(default_factory=list)

    @field_validator("topicos")
    @classmethod
    def _limitar_quantidade_topicos(cls, v: list[ItemTopicoPlanoRevisaoProfundaTranscribrothers]) -> list:
        return v[:48]


SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS = """Você é um revisor técnico sénior. A sua única tarefa é analisar o tutorial em Markdown face à transcrição (JSON com segmentos temporais e texto) e listar lacunas por tópico.

Regras:
1) Responda APENAS com um único objeto JSON (sem Markdown à volta, sem comentários). O JSON deve obedecer ao schema indicado pelo utilizador.
2) Cada tópico deve corresponder a uma secção ou tema claro do tutorial (use titulo_secao próximo de um ## existente ou descreva o tema).
3) lacunas: frases curtas sobre o que falta ou está superficial face à transcrição.
4) evidencias_transcricao: citações curtas retiradas da transcrição (campo texto dos segmentos) que mostram conteúdo ainda não reflectado no tutorial; inclua inicio_segundos/fim_segundos do segmento quando souber.
5) prioridade: 1 = mais urgente (omissão grave), 9 = menor.
6) Não invente diálogos que não existam nos segmentos da transcrição.
7) Se o tutorial já estiver muito completo, devolva topicos como lista vazia."""


SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS = """Você é um editor técnico. Recebe o tutorial completo em Markdown, um item de plano (JSON) com lacunas e evidências da transcrição, e o JSON completo da transcrição+frames.

Tarefa:
- Corrija o tutorial para endereçar APENAS as lacunas desse item, mantendo o resto estável.
- Devolva o tutorial COMPLETO em Markdown (começando por # título), sem cercas de código.
- Não remova imagens ![](assets/...) existentes salvo se duplicadas por engano.
- Não contradiga a transcrição nem as evidências fornecidas.
- Use português claro, alinhado ao estilo do tutorial actual."""


SYSTEM_PROMPT_RESUMO_PLANO_PARA_EDITOR_FINAL_TRANSCRIBROTHERS = """Resumo estruturado do plano de revisão (tópicos e lacunas) em JSON compacto."""


INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS = """Revisão final (consolidação): harmonize voz, ritmo e terminologia em todo o tutorial; remova redundâncias introduzidas por revisões parciais; garanta que cabeçalhos ## e listas ficam coerentes; não apague conteúdo factual nem imagens úteis; não invente passos que não constem da transcrição ou do Markdown já produzido. O resultado deve ser o tutorial completo em Markdown."""


def extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto: str) -> str:
    """Remove cercas ```json ... ``` ou devolve o texto trimado."""
    s = (texto or "").strip()
    if not s:
        raise ValueError("Resposta vazia do modelo na fase de análise.")
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return s


def parsear_plano_revisao_profunda_de_texto_resposta_llm_transcribrothers(
    texto_bruto: str,
) -> tuple[PlanoRevisaoProfundaTutorialTranscribrothers, str]:
    """
    Valida e devolve (plano, json_serializado_truncado_para_persistência).
    Levanta ValueError com mensagem legível para UI.
    """
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data = json.loads(raw_json)
    except (json.JSONDecodeError, ValueError) as e:
        trecho = (texto_bruto or "")[:1200]
        raise ValueError(
            "O analista não devolveu JSON válido. Ajuste o modelo ou tente de novo. "
            f"Detalhe: {e}. Trecho: {trecho!r}"
        ) from e
    if not isinstance(data, dict):
        raise ValueError("JSON do analista deve ser um objecto na raiz.")
    try:
        plano = PlanoRevisaoProfundaTutorialTranscribrothers.model_validate(data)
    except Exception as e:  # noqa: BLE001
        raise ValueError(
            "JSON do analista não corresponde ao schema esperado (topicos, id, titulo_secao, …). "
            f"Detalhe: {e}"
        ) from e
    serial = json.dumps(plano.model_dump(), ensure_ascii=False)
    if len(serial) > _LIMITE_CHARS_PLANO_JSON_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS:
        serial = serial[:_LIMITE_CHARS_PLANO_JSON_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS] + "\n…[truncado]"
    return plano, serial


def montar_schema_json_exemplo_para_prompt_analista_transcribrothers() -> str:
    """Texto curto a incluir no user prompt ao analista."""
    exemplo: dict[str, Any] = {
        "topicos": [
            {
                "id": "exemplo_1",
                "titulo_secao": "## Exemplo de secção",
                "lacunas": ["Falta explicar o campo X mencionado na fala."],
                "evidencias_transcricao": [
                    {"citacao": "Trecho literal da transcrição.", "inicio_segundos": 12.5, "fim_segundos": 18.0}
                ],
                "prioridade": 2,
            }
        ]
    }
    return json.dumps(exemplo, ensure_ascii=False, indent=2)
