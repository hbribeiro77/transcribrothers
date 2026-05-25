"""Testes de pipeline/prompt de reprodução de bug sem JSON de cliques."""

from transcribrothers_backend.constante_texto_instrucao_reproducao_bug_sem_json_cliques_transcribrothers import (
    TEXTO_INSTRUCAO_REPRODUCAO_BUG_SEM_JSON_CLIQUES_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers import (
    montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_reproducao_bug_recbrothers_transcribrothers import (
    _montar_pseudo_cliques_a_partir_de_rels_transcribrothers,
)


def test_montar_pseudo_cliques_a_partir_de_rels() -> None:
    rels = [(1.5, "assets/frame_a.png"), (3.0, "assets/frame_b.png")]
    cliques = _montar_pseudo_cliques_a_partir_de_rels_transcribrothers(rels)
    assert cliques == [
        {"tRelativoMs": 1500, "origem": "inferido_pipeline"},
        {"tRelativoMs": 3000, "origem": "inferido_pipeline"},
    ]


def test_prefixo_litellm_inclui_bloco_sem_json_quando_solicitado() -> None:
    prefixo = montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers(
        sem_json_cliques_recbrothers=True,
    )
    assert TEXTO_INSTRUCAO_REPRODUCAO_BUG_SEM_JSON_CLIQUES_TRANSCRIBROTHERS in prefixo
