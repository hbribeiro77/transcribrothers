"""Resolver de modelo e prompt para agentes custom no snapshot do job."""

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    resolver_modelo_agente_pipeline_custom_transcribrothers,
    resolver_prompt_agente_pipeline_custom_transcribrothers,
)


def _cfg_teste() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers.model_construct(
        litellm_model="modelo-default-servidor",
        litellm_modelos_provisionados="",
    )


def test_resolver_modelo_hierarquia_agente_job_default_transcribrothers() -> None:
    cfg = _cfg_teste()
    steps = {
        "pipeline_custom_agentes": {
            "gerador_tutorial_markdown": {
                "modelo_litellm": "modelo-do-agente",
                "prompts": [],
            }
        }
    }
    assert (
        resolver_modelo_agente_pipeline_custom_transcribrothers(
            "gerador_tutorial_markdown", steps, "modelo-do-job", cfg
        )
        == "modelo-do-agente"
    )
    steps_sem_modelo_agente = {
        "pipeline_custom_agentes": {
            "gerador_tutorial_markdown": {"modelo_litellm": None, "prompts": []}
        }
    }
    assert (
        resolver_modelo_agente_pipeline_custom_transcribrothers(
            "gerador_tutorial_markdown", steps_sem_modelo_agente, "modelo-do-job", cfg
        )
        == "modelo-do-job"
    )
    assert (
        resolver_modelo_agente_pipeline_custom_transcribrothers(
            "handler_desconhecido", {}, "", cfg
        )
        == "modelo-default-servidor"
    )


def test_resolver_prompt_fallback_quando_chave_ausente_transcribrothers() -> None:
    default = "texto padrao do sistema"
    steps = {
        "pipeline_custom_agentes": {
            "gerador_tutorial_markdown": {
                "prompts": [
                    {"chave": "instrucao_gerador", "texto": "  prompt custom  "},
                ]
            }
        }
    }
    assert (
        resolver_prompt_agente_pipeline_custom_transcribrothers(
            "gerador_tutorial_markdown", "instrucao_gerador", steps, default
        )
        == "prompt custom"
    )
    assert (
        resolver_prompt_agente_pipeline_custom_transcribrothers(
            "gerador_tutorial_markdown", "chave_inexistente", steps, default
        )
        == default
    )
    assert (
        resolver_prompt_agente_pipeline_custom_transcribrothers(
            "outro_handler", "instrucao_gerador", steps, default
        )
        == default
    )
