"""Verificação pós-geração: notas de proposta vs transcrição (decisões e pendências)."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
    parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers,
    preparar_payload_e_markdown_truncados_para_verificacao_sustentacao_transcribrothers,
    serializar_resultado_verificacao_para_steps_json_transcribrothers,
)

SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS = """\
Você é um auditor de consistência factual em reuniões de produto.

Tarefa: comparar as **notas de proposta** em Markdown com a transcrição (JSON). Foque em **decisões tomadas**, \
**requisitos/escopo**, **próximos passos** e **action items** — não em tutorial passo a passo.

Regras:
1) Responda APENAS com um único objeto JSON (sem Markdown à volta).
2) Marque `nao_sustentado` quando uma decisão ou compromisso no documento não tiver suporte claro na transcrição \
ou parecer fechar uma pendência que na fala permaneceu em aberto.
3) `incerto` quando faltar contexto para confirmar.
4) `classificacao_global`: `ok`, `atencao` ou `risco` (mesmos critérios de auditoria factual).
5) Máximo 15 itens em `itens`; campos por item: `trecho_ou_tema`, `classificacao`, `justificativa_curta`, \
`citacao_transcricao_opcional`.
6) Português em `mensagem_resumo` e `justificativa_curta`.
"""


async def executar_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    markdown_notas: str,
    transcricao_corta: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    levantar_se_cancelado: Callable[[], None] | None = None,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    system_prompt_override: str | None = None,
) -> dict[str, Any]:
    """Devolve dicionário para `steps_json['verificacao_sustentacao_notas_proposta']`."""
    if levantar_se_cancelado:
        levantar_se_cancelado()

    max_payload = max(10_000, int(configuracao.verificacao_sustentacao_tutorial_max_chars_payload_transcricao_json))
    max_md = max(5000, int(configuracao.verificacao_sustentacao_tutorial_max_chars_markdown_enviado))

    payload, md_cortado, trunc_p, trunc_m = preparar_payload_e_markdown_truncados_para_verificacao_sustentacao_transcribrothers(
        transcricao=transcricao_corta,
        rels=rels,
        markdown_tutorial=markdown_notas,
        max_chars_payload_json=max_payload,
        max_chars_markdown=max_md,
    )
    payload_txt = json.dumps(payload, ensure_ascii=False, indent=2)

    user = (
        "## Transcrição e frames (JSON — fonte factual primária)\n"
        f"{payload_txt}\n\n"
        "---\n\n"
        "## Notas de proposta (Markdown)\n\n"
        f"{md_cortado}\n"
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
                    "content": (
                        (system_prompt_override or "").strip()
                        or SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS
                    ),
                },
                {"role": "user", "content": user},
            ],
            temperature=0.15,
            usar_response_format_json_object=bool(
                configuracao.transcricao_litellm_chat_json_object_response_format
            ),
            httpx_timeout_connect_segundos=float(configuracao.litellm_http_timeout_connect_segundos),
            httpx_timeout_read_segundos=min(
                900.0,
                max(120.0, float(configuracao.litellm_http_timeout_read_segundos) / 4),
            ),
            steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
            log_etapa="verificacao_sustentacao_notas_proposta",
            log_resumo_pedido="Auditor: notas de proposta vs transcrição",
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
            "erro": str(e).strip()[:12000],
            "erro_tipo": type(e).__name__,
            "tipo": "notas_proposta_funcionalidade",
            "transcricao_json_truncada_para_prompt": trunc_p,
            "markdown_tutorial_truncado_para_prompt": trunc_m,
        }

    if levantar_se_cancelado:
        levantar_se_cancelado()

    try:
        parsed = parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers(texto)
        resultado = serializar_resultado_verificacao_para_steps_json_transcribrothers(
            parsed,
            modelo_litellm=modelo_litellm,
            transcricao_json_truncada_para_prompt=trunc_p,
            markdown_tutorial_truncado_para_prompt=trunc_m,
        )
        resultado["tipo"] = "notas_proposta_funcionalidade"
        if steps_para_log_decisoes_ia is not None:
            from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
                registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            )

            n_itens = len(resultado.get("itens") or []) if isinstance(resultado.get("itens"), list) else 0
            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
                steps_para_log_decisoes_ia,
                etapa="verificacao_sustentacao_notas_proposta_decisao",
                resumo=str(resultado.get("classificacao_global") or resultado.get("mensagem_resumo") or "Concluída")[
                    :500
                ],
                detalhe=str(resultado.get("mensagem_resumo") or "")[:2000] or None,
                modelo=modelo_litellm,
                metadados={"itens": n_itens},
            )
        return resultado
    except Exception as e:
        return {
            "sucesso": False,
            "executado_em": datetime.now(timezone.utc).isoformat(),
            "modelo_litellm": modelo_litellm.strip(),
            "erro": str(e).strip()[:12000],
            "erro_tipo": type(e).__name__,
            "tipo": "notas_proposta_funcionalidade",
            "transcricao_json_truncada_para_prompt": trunc_p,
            "markdown_tutorial_truncado_para_prompt": trunc_m,
        }
