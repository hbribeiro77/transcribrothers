"""Handlers habilitados e snapshot completo de pipeline custom no job."""

from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_util_handlers_pipeline_custom_habilitados_job_steps_transcribrothers import (
    handler_pipeline_custom_habilitado_no_job_transcribrothers,
    job_usa_snapshot_pipeline_custom_transcribrothers,
)


def test_handler_habilitado_sem_custom_sempre_true_transcribrothers() -> None:
    assert handler_pipeline_custom_habilitado_no_job_transcribrothers({}, "auditor_sustentacao_tutorial") is True
    assert handler_pipeline_custom_habilitado_no_job_transcribrothers(None, "gerador_tutorial_markdown") is True


def test_handler_habilitado_com_custom_somente_handlers_do_snapshot_transcribrothers() -> None:
    steps = {
        "pipeline_custom_id": "uuid",
        "pipeline_custom_agentes": {
            "gerador_tutorial_markdown": {"prompts": []},
            "preparacao_transcricao": {"prompts": []},
        },
    }
    assert job_usa_snapshot_pipeline_custom_transcribrothers(steps) is True
    assert handler_pipeline_custom_habilitado_no_job_transcribrothers(steps, "gerador_tutorial_markdown") is True
    assert handler_pipeline_custom_habilitado_no_job_transcribrothers(steps, "verificacao_imagens_duplicadas") is False
    assert handler_pipeline_custom_habilitado_no_job_transcribrothers(steps, "auditor_sustentacao_tutorial") is False


def test_montar_snapshot_completo_inclui_titulo_e_passos_transcribrothers() -> None:
    class _Pipeline:
        id = "pipe-1"
        copiado_de = "pipeline_inicial_tutorial"
        titulo = "Minha pipeline"
        descricao = "Desc custom"
        passos_json = [
            {"id": "gerador", "agente_id": "a1", "rotulo": "Gerador", "descricao": "Gera MD"},
        ]

    class _Agente:
        id = "a1"
        handler_chave = "gerador_tutorial_markdown"
        prompts_json = [{"chave": "instrucao_tutorial_sem_imagens", "texto": "x", "tipo": "instrucao", "rotulo": "t"}]
        modelo_litellm = None

    snap = montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers(_Pipeline(), [_Agente()])
    assert snap["pipeline_custom_titulo"] == "Minha pipeline"
    assert snap["pipeline_custom_descricao"] == "Desc custom"
    assert len(snap["pipeline_custom_passos"]) == 1
    assert snap["pipeline_custom_passos"][0]["handler_chave"] == "gerador_tutorial_markdown"
    assert "gerador_tutorial_markdown" in snap["pipeline_custom_agentes"]
