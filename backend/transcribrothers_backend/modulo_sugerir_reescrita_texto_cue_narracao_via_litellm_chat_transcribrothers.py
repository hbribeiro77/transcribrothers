"""Núcleo: sugere reescrita de texto de cue via chat LiteLLM (não aplica no manifesto)."""

from __future__ import annotations

import re
from typing import Any

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)

PROMPT_SISTEMA_REESCRITA_TEXTO_CUE_NARRACAO_TRANSCRIBROTHERS = (
    "Você reescreve trechos curtos para narração TTS em português do Brasil. "
    "Devolva APENAS o texto reescrito, sem aspas, sem markdown e sem explicação. "
    "Mantenha o sentido. Prefira frases faláveis, serenas e claras. "
    "Evite títulos densos, jargão empilhado, markdown, âncoras ?t= e comandos ao modelo."
)

_RE_CERCA_CODIGO = re.compile(r"^```(?:\w+)?\s*|\s*```$", re.MULTILINE)


def limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers(bruto: str) -> str:
    texto = (bruto or "").strip()
    if not texto:
        return ""
    texto = _RE_CERCA_CODIGO.sub("", texto).strip()
    linhas = [ln.strip() for ln in texto.replace("\r\n", "\n").split("\n") if ln.strip()]
    if not linhas:
        return ""
    if len(linhas) == 1:
        return " ".join(linhas[0].split())
    candidato = linhas[-1]
    if candidato.lower().startswith(("sugestão:", "sugestao:", "reescrita:", "texto:")):
        candidato = candidato.split(":", 1)[-1].strip()
    return " ".join(candidato.split())


async def sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    texto: str,
    indice: int = 0,
    litellm_model_chat: str | None = None,
    modelo_chat_fallback_steps: str | None = None,
    log_etapa: str = "sugerir_reescrita_texto_cue_narracao",
) -> dict[str, Any]:
    """
    Gera sugestão de reescrita via chat. Não altera steps nem manifesto.
    """
    texto_norm = " ".join((texto or "").split())
    if not texto_norm:
        raise ValueError("Informe o texto da cue para sugerir reescrita.")

    try:
        modelo = resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers(
            configuracao,
            (litellm_model_chat or "").strip()
            or (modelo_chat_fallback_steps or "").strip()
            or None,
        )
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(
        configuracao
    )
    mensagens = [
        {"role": "system", "content": PROMPT_SISTEMA_REESCRITA_TEXTO_CUE_NARRACAO_TRANSCRIBROTHERS},
        {
            "role": "user",
            "content": (
                "Reescreva o trecho abaixo para narração TTS (uma única versão):\n\n"
                f"{texto_norm}"
            ),
        },
    ]
    try:
        bruto = await litellm_chat_completions_texto_simples_transcribrothers(
            modelo=modelo,
            api_key=api_key,
            api_base=api_base,
            httpx_verify=httpx_verify,
            mensagens=mensagens,
            temperature=0.3,
            httpx_timeout_connect_segundos=30.0,
            httpx_timeout_read_segundos=90.0,
            log_etapa=log_etapa,
            log_resumo_pedido=f"indice={indice} chars={len(texto_norm)}",
        )
    except Exception as exc:
        raise RuntimeError(f"Falha ao pedir sugestão à IA: {exc}") from exc

    sugestao = limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers(bruto)
    if not sugestao:
        return {
            "ok": False,
            "mensagem": "A IA não devolveu uma sugestão utilizável.",
            "indice": int(indice),
            "sugestao": "",
            "modelo": modelo,
            "texto_original": texto_norm,
        }
    return {
        "ok": True,
        "mensagem": "Sugestão pronta — revise antes de usar.",
        "indice": int(indice),
        "sugestao": sugestao,
        "modelo": modelo,
        "texto_original": texto_norm,
    }
