"""Testes de slug/URL wiki — …/-/wikis/workshop/{slug_filho}."""

from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers,
    montar_slug_filho_pagina_wiki_gitlab_transcribrothers,
    montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers,
    montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers,
    montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers,
    slug_resposta_gitlab_wiki_corresponde_ao_slug_esperado_transcribrothers,
    slug_resposta_gitlab_wiki_esta_em_subpasta_prefixo_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def _cfg() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers(
        gitlab_base_url="https://gitlab.exemplo.defensoria",
        gitlab_wiki_project_path="portal-da-defensoria/documentacao",
        gitlab_wiki_slug_prefixo_pasta="workshop",
    )


def test_slug_filho_vem_só_do_titulo_sem_sufixo_job() -> None:
    filho = montar_slug_filho_pagina_wiki_gitlab_transcribrothers(
        "Review Sprint 10: Responsável indisponível nas tarefas e Melhorias na Triagem",
    )
    assert filho == "review-sprint-10-responsavel-indisponivel-nas-tarefas-e-melhorias-na-triagem"
    assert "ac9b7c2b" not in filho


def test_url_web_e_indice_workshop() -> None:
    cfg = _cfg()
    filho = "review-sprint-10-responsavel-indisponivel-nas-tarefas-e-melhorias-na-triagem"
    url_web = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(cfg, filho)
    assert (
        url_web
        == "https://gitlab.exemplo.defensoria/portal-da-defensoria/documentacao/-/wikis/workshop/review-sprint-10-responsavel-indisponivel-nas-tarefas-e-melhorias-na-triagem"
    )
    url_indice = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(cfg)
    assert url_indice.endswith("/-/wikis/workshop")
    assert "/workshop/" not in url_indice.replace("/-/wikis/workshop", "")


def test_slug_api_para_get_put_post() -> None:
    cfg = _cfg()
    titulo = "Review Sprint 10"
    slug_api = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(cfg, titulo)
    assert slug_api == "workshop/review-sprint-10"
    url_api = montar_url_api_wiki_pagina_gitlab_projeto_por_slug_transcribrothers(cfg, slug_api)
    assert "workshop%2Freview-sprint-10" in url_api


def test_normalizar_prefixo_pasta_wiki() -> None:
    from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
        normalizar_prefixo_pasta_wiki_gitlab_transcribrothers,
    )

    assert normalizar_prefixo_pasta_wiki_gitlab_transcribrothers("workshop") == "workshop"
    assert normalizar_prefixo_pasta_wiki_gitlab_transcribrothers("  Treinamentos  ") == "treinamentos"


def test_url_web_com_pasta_customizada() -> None:
    cfg = _cfg()
    filho = "meu-doc"
    url_web = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
        cfg, filho, prefixo_pasta="treinamentos"
    )
    assert url_web.endswith("/-/wikis/treinamentos/meu-doc")


def test_validacao_slug_resposta_subpasta_workshop() -> None:
    assert slug_resposta_gitlab_wiki_esta_em_subpasta_prefixo_transcribrothers(
        "workshop/meu-doc",
        "workshop",
    )
    assert not slug_resposta_gitlab_wiki_esta_em_subpasta_prefixo_transcribrothers("workshop", "workshop")
    assert slug_resposta_gitlab_wiki_corresponde_ao_slug_esperado_transcribrothers(
        "workshop/x",
        "workshop/x",
    )
