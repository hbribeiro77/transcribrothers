"""Modo tutorial passo a passo de software: detecção, prompts densos e limites de captura."""

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
    parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers,
)
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS,
    mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers,
    obter_pipeline_catalogo_sistema_por_id_transcribrothers,
)
from transcribrothers_backend.modulo_orquestrar_reprocessamento_pos_transcricao_com_novo_destino_job_transcribrothers import (
    DESTINOS_GERAR_OUTRO_FORMATO_VALIDOS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_parametros_modo_tutorial_passo_a_passo_software_captura_densa_transcribrothers import (
    ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
    ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
    job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers,
    resolver_parametros_captura_tutorial_markdown_transcribrothers,
)


def test_job_steps_indicam_tutorial_passo_a_passo_pelo_destino_ou_pipeline_custom_transcribrothers() -> None:
    assert job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(None) is False
    assert job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(
        {"destino_apos_transcricao": "gerar_tutorial"}
    ) is False
    assert job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(
        {"destino_apos_transcricao": ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS}
    ) is True
    assert job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(
        {
            "destino_apos_transcricao": "gerar_tutorial",
            "pipeline_custom_copiado_de": ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
        }
    ) is True


def test_parametros_tutorial_esparso_nao_mudam_prompts_nem_limites_padrao_transcribrothers() -> None:
    params = resolver_parametros_captura_tutorial_markdown_transcribrothers(
        {"destino_apos_transcricao": "gerar_tutorial"}
    )
    assert params.denso is False
    assert (
        params.instrucao_rascunho_sem_imagens
        == INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS
    )
    assert (
        params.system_planejamento_instantes
        == SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS
    )
    assert params.handler_rascunho == "rascunho_tutorial_sob_demanda"
    assert params.handler_plano == "plano_capturas_tutorial"
    assert params.handler_gerador == "gerador_tutorial_markdown"
    assert params.max_frames_per_minute_override is None
    assert params.tutorial_max_frames_total_override is None
    assert params.margem_minima_segundos_entre_links_override is None
    assert params.max_instantes_planejamento == 64


def test_parametros_tutorial_passo_a_passo_sao_densos_e_independentes_do_tutorial_esparso_transcribrothers() -> None:
    params = resolver_parametros_captura_tutorial_markdown_transcribrothers(
        {"destino_apos_transcricao": ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS}
    )
    assert params.denso is True
    assert (
        params.instrucao_rascunho_sem_imagens
        != INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS
    )
    assert "um screenshot" in params.instrucao_rascunho_sem_imagens.lower() or "cada procedimento" in (
        params.instrucao_rascunho_sem_imagens.lower()
    )
    assert "?t=" in params.instrucao_rascunho_sem_imagens
    assert (
        params.system_planejamento_instantes
        != SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS
    )
    assert "prefira menos capturas" not in params.system_planejamento_instantes.lower()
    assert params.handler_rascunho == "rascunho_tutorial_passo_a_passo_software"
    assert params.handler_plano == "plano_capturas_tutorial_passo_a_passo_software"
    assert params.handler_gerador == "gerador_tutorial_passo_a_passo_software"
    assert params.max_frames_per_minute_override == 30
    assert params.tutorial_max_frames_total_override == 192
    assert params.margem_minima_segundos_entre_links_override == 0.5
    assert params.max_instantes_planejamento == 192
    assert "uma imagem por procedimento" in params.instrucao_incorporar_frames.lower()


def test_parsear_plano_captura_respeita_teto_de_instantes_denso_acima_de_64_transcribrothers() -> None:
    instantes = list(range(80))
    texto = '{"instantes_segundos_para_capturar": %s, "mensagem_resumo": "denso"}' % instantes
    parsed_esparso = parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers(texto)
    assert len(parsed_esparso.instantes_segundos_para_capturar) == 64
    parsed_denso = parsear_resultado_planejamento_instantes_captura_de_texto_llm_transcribrothers(
        texto,
        max_instantes=192,
    )
    assert len(parsed_denso.instantes_segundos_para_capturar) == 80


def test_catalogo_mapeia_pipeline_passo_a_passo_software_como_executavel_de_upload_transcribrothers() -> None:
    assert (
        ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
        in PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS
    )
    assert (
        mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(
            ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
        )
        == ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
    )
    pipeline = obter_pipeline_catalogo_sistema_por_id_transcribrothers(
        ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
    )
    assert pipeline is not None
    assert pipeline.executavel is True
    assert pipeline.entradas_aceitas == ["video"]
    agentes = {passo.agente_id for passo in pipeline.passos}
    assert "rascunho_tutorial_passo_a_passo_software" in agentes
    assert "gerador_tutorial_passo_a_passo_software" in agentes
    assert "rascunho_tutorial_sob_demanda" not in agentes
    assert (
        ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
        in DESTINOS_GERAR_OUTRO_FORMATO_VALIDOS_TRANSCRIBROTHERS
    )
