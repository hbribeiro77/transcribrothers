"""Planejamento (LiteLLM, só texto): quais instantes `?t=` do rascunho merecem captura PNG antes do ffmpeg."""

from __future__ import annotations

import json
from typing import Any

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
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)

SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS = """\
Você escolhe quais instantes de uma gravação de reunião merecem screenshot para notas de proposta de funcionalidade.

Entrada: rascunho das notas (com links [MM:SS](?t=SEGUNDOS)), lista de candidatos (segundos exatos) e resumo da transcrição.

Regras:
1) Responda APENAS com um objeto JSON (sem Markdown à volta).
2) Priorize slides, mockups, demos na tela compartilhada e mudanças visuais mencionadas — não «botão do tutorial» passo a passo.
3) `instantes_segundos_para_capturar`: subconjunto dos candidatos (valores numéricos exatos da lista).
4) Evite capturas redundantes no mesmo slide ou tela estática.
5) Prefira menos capturas quando possível, sem perder evidências visuais importantes para a proposta.
6) Campos na raiz: `instantes_segundos_para_capturar` (lista de números), `mensagem_resumo` (pt-BR, curta).
"""

SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS = """\
Você escolhe quais instantes de um vídeo merecem screenshot para um tutorial Markdown.

Entrada: rascunho do tutorial (com links [MM:SS](?t=SEGUNDOS)), lista de candidatos (segundos exatos) e resumo da transcrição.

Regras:
1) Responda APENAS com um objeto JSON (sem Markdown à volta).
2) Nem todo link `?t=` precisa virar captura — prefira momentos em que a interface muda, surge diálogo novo, botão relevante ou tela distinta.
3) `instantes_segundos_para_capturar`: subconjunto dos candidatos (use os valores numéricos exatos da lista de candidatos).
4) Evite capturas redundantes no mesmo estado visual (mesma tela em segundos próximos).
5) Prefira menos capturas quando possível, sem perder passos visuais importantes.
6) Campos na raiz: `instantes_segundos_para_capturar` (lista de números), `mensagem_resumo` (pt-BR, curta).
"""


class ResultadoPlanejamentoInstantesCapturaFramesJsonTranscribrothers(BaseModel):
    instantes_segundos_para_capturar: list[float] = Field(default_factory=list)
    mensagem_resumo: str = Field(default="", max_length=8000)

    @field_validator("instantes_segundos_para_capturar")
    @classmethod
    def _limitar_instantes(cls, v: list[float]) -> list[float]:
        return [float(x) for x in v[:64]]


def parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers(
    texto_bruto: str,
) -> ResultadoPlanejamentoInstantesCapturaFramesJsonTranscribrothers:
    raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
    data = json.loads(raw_json)
    if not isinstance(data, dict):
        raise ValueError("JSON raiz deve ser um objeto.")
    return ResultadoPlanejamentoInstantesCapturaFramesJsonTranscribrothers.model_validate(data)


def alinhar_instantes_plano_litellm_aos_candidatos_transcribrothers(
    instantes_propostos: list[float],
    candidatos: list[float],
    *,
    tolerancia_segundos: float = 0.75,
) -> list[float]:
    """Mapeia valores devolvidos pelo modelo para os candidatos (ordem preservada, sem duplicar)."""
    if not candidatos:
        return []
    tol = max(0.05, float(tolerancia_segundos))
    saida: list[float] = []
    for prop in instantes_propostos:
        melhor: float | None = None
        melhor_dist = tol + 1.0
        for c in candidatos:
            d = abs(float(c) - float(prop))
            if d <= tol and d < melhor_dist:
                melhor = float(c)
                melhor_dist = d
        if melhor is not None and melhor not in saida:
            saida.append(melhor)
    return saida


def aplicar_resultado_planejamento_com_fallback_minimo_transcribrothers(
    instantes_alinhados: list[float],
    candidatos: list[float],
) -> list[float]:
    if instantes_alinhados:
        return instantes_alinhados
    if candidatos:
        return [float(candidatos[0])]
    return []


def _truncar_texto_transcribrothers(texto: str, max_chars: int) -> str:
    s = texto or ""
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 40] + "\n\n…[texto truncado]…\n"


def _resumir_transcricao_para_planejamento_captura_transcribrothers(
    transcricao: ResultadoTranscricaoComSegmentos,
    *,
    max_segmentos: int = 40,
) -> list[dict[str, object]]:
    segs = transcricao.segmentos[: max(1, int(max_segmentos))]
    return [
        {
            "inicio_segundos": round(float(s.inicio_segundos), 2),
            "fim_segundos": round(float(s.fim_segundos), 2),
            "texto": (s.texto or "")[:400],
        }
        for s in segs
    ]


def montar_mensagem_usuario_planejamento_instantes_captura_frames_transcribrothers(
    *,
    markdown_rascunho_tutorial: str,
    candidatos_segundos: list[float],
    transcricao: ResultadoTranscricaoComSegmentos,
    duracao_video_segundos: float,
    margem_minima_segundos_entre_links: float,
    max_capturas_apos_limites: int,
) -> str:
    payload = {
        "duracao_video_segundos": round(float(duracao_video_segundos), 2),
        "margem_minima_segundos_entre_links_temporais": round(float(margem_minima_segundos_entre_links), 2),
        "max_capturas_recomendado_apos_limites_pipeline": int(max_capturas_apos_limites),
        "candidatos_instantes_segundos": [round(float(t), 3) for t in candidatos_segundos],
        "transcricao_resumo_segmentos": _resumir_transcricao_para_planejamento_captura_transcribrothers(
            transcricao
        ),
        "markdown_rascunho_tutorial": _truncar_texto_transcribrothers(
            markdown_rascunho_tutorial,
            100_000,
        ),
    }
    return (
        "Escolha os instantes que merecem screenshot.\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
    )


async def planejar_instantes_captura_frames_tutorial_com_litellm_transcribrothers(
    *,
    markdown_rascunho_tutorial: str,
    candidatos_segundos: list[float],
    transcricao: ResultadoTranscricaoComSegmentos,
    duracao_video_segundos: float,
    margem_minima_segundos_entre_links: float,
    max_capturas_apos_limites: int,
    modelo_litellm: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    modo_notas_proposta_funcionalidade: bool = False,
) -> tuple[list[float], dict[str, Any]]:
    """
    Devolve instantes alinhados aos candidatos e metadados para `steps_json`.
    Em falha de parse ou HTTP, devolve todos os candidatos (comportamento conservador).
    """
    candidatos = list(candidatos_segundos)
    meta: dict[str, Any] = {
        "candidatos_total": len(candidatos),
        "planejamento_executado": False,
    }
    if not candidatos:
        return [], meta

    if not bool(configuracao.tutorial_planejamento_instantes_captura_frames_litellm_habilitado):
        meta["motivo_skip"] = "planejamento_desabilitado_config"
        return candidatos, meta

    mensagem_usuario = montar_mensagem_usuario_planejamento_instantes_captura_frames_transcribrothers(
        markdown_rascunho_tutorial=markdown_rascunho_tutorial,
        candidatos_segundos=candidatos,
        transcricao=transcricao,
        duracao_video_segundos=duracao_video_segundos,
        margem_minima_segundos_entre_links=margem_minima_segundos_entre_links,
        max_capturas_apos_limites=max_capturas_apos_limites,
    )
    try:
        texto = await litellm_chat_completions_texto_simples_transcribrothers(
            modelo=modelo_litellm,
            api_key=api_key,
            api_base=api_base,
            httpx_verify=httpx_verify,
            mensagens=[
                {
                    "role": "system",
                    "content": (
                        SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS
                        if modo_notas_proposta_funcionalidade
                        else SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS
                    ),
                },
                {"role": "user", "content": mensagem_usuario},
            ],
            temperature=0.2,
            usar_response_format_json_object=bool(
                configuracao.transcricao_litellm_chat_json_object_response_format
            ),
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
            log_etapa=(
                "planejamento_instantes_captura_notas_proposta"
                if modo_notas_proposta_funcionalidade
                else "planejamento_instantes_captura_frames_tutorial"
            ),
            log_resumo_pedido=f"{len(candidatos)} candidatos; teto {max_capturas_apos_limites}",
            log_metadados={"candidatos": len(candidatos)},
        )
        parsed = parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers(texto)
        alinhados = alinhar_instantes_plano_litellm_aos_candidatos_transcribrothers(
            parsed.instantes_segundos_para_capturar,
            candidatos,
        )
        escolhidos = aplicar_resultado_planejamento_com_fallback_minimo_transcribrothers(
            alinhados,
            candidatos,
        )
        meta.update(
            {
                "planejamento_executado": True,
                "instantes_escolhidos_total": len(escolhidos),
                "mensagem_resumo": parsed.mensagem_resumo.strip()[:2000],
            }
        )
        return escolhidos, meta
    except Exception as exc:  # noqa: BLE001 — fallback para captura de todos os candidatos
        meta.update(
            {
                "planejamento_executado": False,
                "erro": str(exc)[:2000],
                "fallback": "todos_candidatos",
            }
        )
        return candidatos, meta
