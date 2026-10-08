"""Schema OpenAI/LiteLLM das tools do Agente (edicao_parcial, revisao_profunda, sem_video)."""

from __future__ import annotations

from typing import Any

from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
    NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS,
    NOME_FERRAMENTA_SEM_VIDEO_CHAT_AGENTE_TRANSCRIBROTHERS,
)


def schema_tools_openai_chat_agente_documento_job_transcribrothers() -> list[dict[str, Any]]:
    propriedades_edicao = {
        "titulo_secao_heading": {
            "type": "string",
            "description": "Título da seção ## a alterar.",
        },
        "instrucoes": {
            "type": "string",
            "description": "O que mudar nesta seção; texto novo entre aspas simples.",
        },
                    "reescrever_secao": {
                        "type": "boolean",
                        "description": "true para reescrever a seção ## inteira (apagar trechos, legendas, timestamps).",
                    },
    }
    return [
        {
            "type": "function",
            "function": {
                "name": NOME_FERRAMENTA_EDICAO_PARCIAL_CHAT_AGENTE_TRANSCRIBROTHERS,
                "description": "Altera só uma seção ## do documento neste turno.",
                "parameters": {
                    "type": "object",
                    "properties": propriedades_edicao,
                    "required": ["titulo_secao_heading", "instrucoes"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": NOME_FERRAMENTA_REVISAO_PROFUNDA_CHAT_AGENTE_TRANSCRIBROTHERS,
                "description": "Revisão em etapas do documento inteiro contra a transcrição.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instrucoes": {"type": "string"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": NOME_FERRAMENTA_SEM_VIDEO_CHAT_AGENTE_TRANSCRIBROTHERS,
                "description": "Reescreve o documento para funcionar só com texto e imagens, sem vídeo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instrucoes": {"type": "string"},
                    },
                },
            },
        },
    ]
