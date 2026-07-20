"""Verificação pós-geração: tutorial Markdown vs transcrição (LLM com saída JSON estruturada).

Não substitui revisão humana: sinaliza possíveis afirmações pouco sustentadas na transcrição.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    _serializar_segmentos,
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

_LIMITE_CHARS_RESULTADO_VERIFICACAO_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS = 72_000

SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS = """\
Você é um auditor de consistência factual (não é advogado nem juiz).

Tarefa: comparar o tutorial em Markdown com a transcrição fornecida em JSON (texto completo, segmentos com tempos e texto, e lista de frames referenciados).

Regras:
1) Responda APENAS com um único objeto JSON (sem Markdown à volta, sem comentários).
2) Procure afirmações concretas no tutorial (passos, nomes de botões, valores, sequências) que não tenham suporte claro na transcrição ou que pareçam invenção.
3) Não penalize texto genérico (“clique em Guardar”) se for plausível num tutorial; marque `nao_sustentado` só quando houver indício forte de invenção ou contradição com a transcrição.
4) `incerto` quando faltar contexto na transcrição para confirmar ou negar.
5) `classificacao_global`:
   - `ok`: nenhum item `nao_sustentado`; poucos ou zero `incerto`.
   - `atencao`: há `incerto` relevantes ou `nao_sustentado` leves.
   - `risco`: há pelo menos um `nao_sustentado` que indique facto ou passo inventado.
6) Liste no máximo 15 itens em `itens`; se estiver tudo bem, `itens` pode ser [].
7) Campos obrigatórios na raiz: `classificacao_global`, `mensagem_resumo`, `itens`.
8) Cada elemento de `itens` deve ter: `trecho_ou_tema`, `classificacao` (sustentado|incerto|nao_sustentado), `justificativa_curta`, `citacao_transcricao_opcional` (trecho da transcrição que apoia ou contradiz, ou string vazia).
9) Use português em `mensagem_resumo` e `justificativa_curta`.
"""


class ItemVerificacaoSustentacaoTutorialJsonTranscribrothers(BaseModel):
    trecho_ou_tema: str = Field(default="", max_length=2000)
    classificacao: Literal["sustentado", "incerto", "nao_sustentado"] = "incerto"
    justificativa_curta: str = Field(default="", max_length=3000)
    citacao_transcricao_opcional: str = Field(default="", max_length=4000)


class ResultadoVerificacaoSustentacaoTutorialJsonTranscribrothers(BaseModel):
    classificacao_global: Literal["ok", "atencao", "risco"] = "atencao"
    mensagem_resumo: str = Field(default="", max_length=8000)
    itens: list[ItemVerificacaoSustentacaoTutorialJsonTranscribrothers] = Field(default_factory=list)

    @field_validator("itens")
    @classmethod
    def _limitar_itens(cls, v: list[ItemVerificacaoSustentacaoTutorialJsonTranscribrothers]) -> list:
        return v[:15]


def montar_payload_json_transcricao_e_frames_para_verificacao_sustentacao_transcribrothers(
    transcricao: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
) -> dict[str, Any]:
    linhas_frames = [{"t_segundos": t, "arquivo_relativo_markdown": rel} for t, rel in rels]
    return {
        "texto_completo": transcricao.texto_completo,
        "idioma": transcricao.idioma_detectado,
        "segmentos": _serializar_segmentos(transcricao.segmentos),
        "frames": linhas_frames,
    }


def _encurtar_texto_segmentos_payload_verificacao_sustentacao_transcribrothers(
    payload: dict[str, Any],
    max_chars_por_texto_segmento: int,
) -> dict[str, Any]:
    out = dict(payload)
    segs = out.get("segmentos")
    if isinstance(segs, list):
        novos: list[dict[str, Any]] = []
        for s in segs:
            if not isinstance(s, dict):
                continue
            d = dict(s)
            tx = d.get("texto")
            if isinstance(tx, str) and len(tx) > max_chars_por_texto_segmento:
                d["texto"] = tx[: max_chars_por_texto_segmento - 1] + "…"
            novos.append(d)
        out["segmentos"] = novos
    tc = out.get("texto_completo")
    if isinstance(tc, str) and len(tc) > max_chars_por_texto_segmento * 4:
        out["texto_completo"] = tc[: max_chars_por_texto_segmento * 4 - 1] + "…"
    return out


def preparar_payload_e_markdown_truncados_para_verificacao_sustentacao_transcribrothers(
    *,
    transcricao: ResultadoTranscricaoComSegmentos,
    rels: list[tuple[float, str]],
    markdown_tutorial: str,
    max_chars_payload_json: int,
    max_chars_markdown: int,
) -> tuple[dict[str, Any], str, bool, bool]:
    """
    Devolve (payload, markdown_truncado, payload_foi_truncado, markdown_foi_truncado).
    Reduz tamanho dos textos dos segmentos até o JSON caber no limite (best-effort).
    """
    payload_base = montar_payload_json_transcricao_e_frames_para_verificacao_sustentacao_transcribrothers(
        transcricao,
        rels,
    )
    json_len_orig = len(json.dumps(payload_base, ensure_ascii=False))
    payload = payload_base
    trunc_payload = False
    if json_len_orig > max_chars_payload_json:
        trunc_payload = True
        for lim in (4000, 2000, 1000, 800, 600, 400, 300, 250, 200):
            payload = _encurtar_texto_segmentos_payload_verificacao_sustentacao_transcribrothers(
                montar_payload_json_transcricao_e_frames_para_verificacao_sustentacao_transcribrothers(
                    transcricao,
                    rels,
                ),
                lim,
            )
            if len(json.dumps(payload, ensure_ascii=False)) <= max_chars_payload_json:
                break

    md = markdown_tutorial or ""
    trunc_md = False
    if len(md) > max_chars_markdown:
        md = md[: max_chars_markdown - 80] + "\n\n…[tutorial truncado para análise no servidor]…\n"
        trunc_md = True
    return payload, md, trunc_payload, trunc_md


def parsear_resultado_verificacao_sustentacao_de_texto_resposta_llm_transcribrothers(
    texto_bruto: str,
) -> ResultadoVerificacaoSustentacaoTutorialJsonTranscribrothers:
    raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
    data = json.loads(raw_json)
    if not isinstance(data, dict):
        raise ValueError("JSON raiz deve ser um objeto.")
    return ResultadoVerificacaoSustentacaoTutorialJsonTranscribrothers.model_validate(data)


def serializar_resultado_verificacao_para_steps_json_transcribrothers(
    resultado: ResultadoVerificacaoSustentacaoTutorialJsonTranscribrothers,
    *,
    modelo_litellm: str,
    transcricao_json_truncada_para_prompt: bool,
    markdown_tutorial_truncado_para_prompt: bool,
) -> dict[str, Any]:
    blob: dict[str, Any] = {
        "sucesso": True,
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "modelo_litellm": modelo_litellm.strip(),
        "classificacao_global": resultado.classificacao_global,
        "mensagem_resumo": resultado.mensagem_resumo.strip(),
        "itens": [it.model_dump() for it in resultado.itens],
        "transcricao_json_truncada_para_prompt": transcricao_json_truncada_para_prompt,
        "markdown_tutorial_truncado_para_prompt": markdown_tutorial_truncado_para_prompt,
    }
    serial = json.dumps(blob, ensure_ascii=False)
    if len(serial) > _LIMITE_CHARS_RESULTADO_VERIFICACAO_PERSISTIDO_STEPS_JSON_TRANSCRIBROTHERS:
        blob["itens"] = blob["itens"][:8]
        blob["mensagem_resumo"] = (blob.get("mensagem_resumo") or "")[
            :8000
        ] + "…[mensagem truncada para persistência]"
        blob["truncado_para_limite_steps_json"] = True
    return blob


async def executar_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    markdown_tutorial: str,
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
    """
    Chama o LiteLLM e devolve dicionário pronto para `steps_json['verificacao_sustentacao_tutorial']`.
    Erros de rede/parse são devolvidos em `sucesso: false` (não levantam excepção).
    """
    if levantar_se_cancelado:
        levantar_se_cancelado()

    max_payload = max(10_000, int(configuracao.verificacao_sustentacao_tutorial_max_chars_payload_transcricao_json))
    max_md = max(5000, int(configuracao.verificacao_sustentacao_tutorial_max_chars_markdown_enviado))

    payload, md_cortado, trunc_p, trunc_m = preparar_payload_e_markdown_truncados_para_verificacao_sustentacao_transcribrothers(
        transcricao=transcricao_corta,
        rels=rels,
        markdown_tutorial=markdown_tutorial,
        max_chars_payload_json=max_payload,
        max_chars_markdown=max_md,
    )
    payload_txt = json.dumps(payload, ensure_ascii=False, indent=2)

    user = (
        "## Transcrição e frames (JSON — única fonte factual primária)\n"
        f"{payload_txt}\n\n"
        "---\n\n"
        "## Tutorial (Markdown)\n\n"
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
                        or SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS
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
            log_etapa="verificacao_sustentacao_tutorial",
            log_resumo_pedido="Auditor: tutorial vs transcrição",
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
        if steps_para_log_decisoes_ia is not None:
            from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
                registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            )

            n_itens = len(resultado.get("itens") or []) if isinstance(resultado.get("itens"), list) else 0
            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
                steps_para_log_decisoes_ia,
                etapa="verificacao_sustentacao_decisao",
                resumo=str(resultado.get("classificacao_global") or resultado.get("mensagem_resumo") or "Concluída")[
                    :500
                ],
                detalhe=str(resultado.get("mensagem_resumo") or "")[:2000] or None,
                modelo=modelo_litellm,
                metadados={"itens": n_itens},
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
            "erro": str(e).strip()[:12000],
            "erro_tipo": type(e).__name__,
            "transcricao_json_truncada_para_prompt": trunc_p,
            "markdown_tutorial_truncado_para_prompt": trunc_m,
        }


def blob_verificacao_sustentacao_omitida_por_configuracao_transcribrothers(
    *,
    motivo: str = "desativada_por_configuracao_ambiente",
) -> dict[str, Any]:
    return {
        "omitida": True,
        "motivo": motivo,
        "executado_em": datetime.now(timezone.utc).isoformat(),
    }
