import pytest

from transcribrothers_backend.modulo_resolver_escopo_edicao_secao_markdown_validacao_e_refinamento_litellm_transcribrothers import (
    _validar_escopo_no_markdown_transcribrothers,
    resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)

MD = """\
# Tutorial

Intro antes das seções.

## Configuração das Colunas

Corpo da seção sobre colunas.

## Outra seção

Fim.
"""


@pytest.mark.asyncio
async def test_resolver_manual_valida_trecho_local():
    prep, erro = _validar_escopo_no_markdown_transcribrothers(
        MD,
        modo="trecho_local",
        trecho_ancora="Corpo da seção sobre colunas",
        titulo_secao_heading=None,
        indice_secao=None,
    )
    assert erro is None
    assert prep is not None
    assert prep.regiao.secao is not None


@pytest.mark.asyncio
async def test_resolver_manual_heading_aproximado_secao_inteira():
    cfg = ConfiguracaoAmbienteTranscribrothers()
    resolvido = await resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers(
        pedido_usuario="Reescreva com mais detalhe.",
        markdown_tutorial=MD,
        configuracao=cfg,
        modelo_litellm="gpt-4o-mini",
        api_key_litellm=None,
        api_base_litellm=None,
        http_verify_litellm=True,
        interpretar_escopo_automaticamente=False,
        modo_escopo_edicao="secao_inteira",
        titulo_secao_heading="## Configuração de Colunas",
    )
    assert resolvido.escopo_confirmado
    assert resolvido.preparacao.regiao.secao is not None
    assert resolvido.preparacao.regiao.secao.linha_heading == "## Configuração das Colunas"


@pytest.mark.asyncio
async def test_resolver_manual_falha_trecho_inexistente():
    cfg = ConfiguracaoAmbienteTranscribrothers()
    with pytest.raises(ValueError, match="Não foi possível localizar"):
        await resolver_escopo_edicao_secao_markdown_tutorial_com_ia_e_validacao_transcribrothers(
            pedido_usuario="Melhore isso.",
            markdown_tutorial=MD,
            configuracao=cfg,
            modelo_litellm="gpt-4o-mini",
            api_key_litellm=None,
            api_base_litellm=None,
            http_verify_litellm=True,
            interpretar_escopo_automaticamente=False,
            modo_escopo_edicao="trecho_local",
            trecho_ancora="texto que não existe no tutorial",
        )
