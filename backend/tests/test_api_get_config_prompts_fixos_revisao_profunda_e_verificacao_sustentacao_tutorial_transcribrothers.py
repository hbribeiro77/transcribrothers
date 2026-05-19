"""GET /api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_get_prompts_fixos_revisao_e_verificacao_retorna_campos_esperados_transcribrothers() -> None:
    with TestClient(app) as client:
        r = client.get(
            "/api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial",
        )
        assert r.status_code == 200
        d = r.json()
        assert "pipeline_identificador" in d
        assert "system_verificacao_sustentacao_tutorial_markdown_vs_transcricao" in d
        assert "system_verificacao_redundancia_secao_markdown_entre_secoes" in d
        assert "system_revisao_profunda_analista_plano_tutorial" in d
        assert "system_revisao_profunda_worker_item_plano_tutorial" in d
        assert "system_revisao_profunda_resumo_plano_para_editor_final" in d
        assert "instrucao_editor_final_revisao_profunda_consolidacao_markdown" in d
        assert "Você é um auditor de consistência factual" in d["system_verificacao_sustentacao_tutorial_markdown_vs_transcricao"]
        assert "revisor técnico sénior" in d["system_revisao_profunda_analista_plano_tutorial"]
