from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
    CHAVE_STEPS_JSON_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS,
    registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
)


def test_registrar_decisao_ia_acumula_e_trunca_lista() -> None:
    steps: dict = {}
    for i in range(3):
        registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
            steps,
            etapa=f"etapa_{i}",
            resumo=f"resumo {i}",
        )
    lista = steps[CHAVE_STEPS_JSON_LOG_DECISOES_IA_PIPELINE_TRANSCRIBROTHERS]
    assert len(lista) == 3
    assert lista[0]["etapa"] == "etapa_0"
    assert lista[-1]["resumo"] == "resumo 2"
