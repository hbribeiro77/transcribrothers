import pytest

from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
    ROTULO_REGIAO_PREFACIO_INTRODUCAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
    localizar_intervalo_trecho_ancora_no_texto_transcribrothers,
    mesclar_corpo_regiao_editada_no_markdown_completo_tutorial_transcribrothers,
    mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers,
    preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
)

MD_WHATSAPP = """\
# Integração de Atendimento Remoto via WhatsApp

Este tutorial descreve a implementação do fluxo de atendimento remoto utilizando o WhatsApp Flow, integrando o portal da Defensoria com a plataforma Indigo.

## Visão geral e processo

Visão Geral do Fluxo
A estratégia central utiliza o WhatsApp Flow para validar a disponibilidade do assistido, eliminando a necessidade de negociação de horários. O fluxo prioriza a eficiência operacional, tratando o agendamento como um compromisso firme desde a sua criação no portal da Defensoria.

Dinâmica do Processo
Definição do Horário: O usuário do portal identifica um horário disponível e realiza o agendamento imediato, sem criar registros provisórios.
Solicitação de Comparecimento: Após o registro, o usuário dispara uma solicitação via WhatsApp Flow.

## Premissas

Impessoalidade: O sistema busca uma confirmação binária (sim/não).
"""

MD_RELATORIOS = """\
# Relatórios SEEU e Visualização de Pastas

Este tutorial apresenta as recentes atualizações no portal da Defensoria, focando na integração dos relatórios do SEEU nas árvores de navegação e nas novas opções de personalização da lista de pastas.

## Personalização da lista

Conteúdo da primeira seção.
"""


def test_trecho_local_preserva_prefixo_e_sufixo():
    prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
        MD_WHATSAPP,
        modo="trecho_local",
        trecho_ancora="""Visão Geral do Fluxo
A estratégia central utiliza o WhatsApp Flow""",
    )
    assert prep.regiao.secao is not None
    assert "Dinâmica do Processo" in prep.fatia.sufixo_imutavel
    assert prep.fatia.prefixo_imutavel.startswith("## Visão geral")
    novo_corpo = mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers(
        prep.fatia,
        "Visão Geral do Fluxo\n\nIntrodução bem mais detalhada sobre o fluxo.",
    )
    assert "Introdução bem mais detalhada" in novo_corpo
    assert "Dinâmica do Processo" in novo_corpo


def test_a_partir_de_mantem_prefixo():
    prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
        MD_WHATSAPP,
        modo="a_partir_de",
        trecho_ancora="Dinâmica do Processo",
    )
    assert "Visão Geral do Fluxo" in prep.fatia.prefixo_imutavel
    assert prep.fatia.zona_editavel.startswith("Dinâmica do Processo")


def test_detecta_secao_pelo_trecho_sem_heading_explicito():
    prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
        MD_WHATSAPP,
        modo="trecho_local",
        trecho_ancora="Impessoalidade: O sistema busca uma confirmação binária",
    )
    assert prep.regiao.secao is not None
    assert prep.regiao.secao.linha_heading == "## Premissas"


def test_prefacio_intro_antes_da_primeira_secao():
    trecho = (
        "Este tutorial apresenta as recentes atualizações no portal da Defensoria, "
        "focando na integração dos relatórios do SEEU nas árvores de navegação "
        "e nas novas opções de personalização da lista de pastas."
    )
    prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
        MD_RELATORIOS,
        modo="trecho_local",
        trecho_ancora=trecho,
    )
    assert prep.regiao.eh_prefacio
    assert prep.regiao.rotulo_regiao == ROTULO_REGIAO_PREFACIO_INTRODUCAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS
    assert trecho in prep.corpo_regiao
    assert "# Relatórios SEEU" in prep.fatia.prefixo_imutavel
    novo_prefacio = mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers(
        prep.fatia,
        "Este tutorial apresenta as atualizações com muito mais detalhe e contexto para o usuário.",
    )
    md_novo = mesclar_corpo_regiao_editada_no_markdown_completo_tutorial_transcribrothers(
        MD_RELATORIOS,
        prep.regiao,
        novo_prefacio,
    )
    assert "muito mais detalhe" in md_novo
    assert "## Personalização da lista" in md_novo


def test_reservar_heading_fora_da_zona_quando_ancora_comeca_no_titulo():
    md = "## Personalização da Lista de Pastas\n\nTexto intro.\n\nBloco alvo\n\nFim.\n"
    prep = preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
        md,
        modo="a_partir_de",
        trecho_ancora="## Personalização da Lista de Pastas",
    )
    assert prep.regiao.secao is not None
    assert prep.fatia.prefixo_imutavel.strip().startswith("## Personalização")
    mesclado = mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers(
        prep.fatia,
        "##\n\nTexto reescrito com mais detalhe.",
        linha_heading_secao=prep.regiao.secao.linha_heading,
    )
    assert mesclado.splitlines()[0].strip() == "## Personalização da Lista de Pastas"


def test_trecho_ambiguo_rejeita():
    md = "## A\n\nparagrafo repetido aqui no texto\n\n## B\n\nparagrafo repetido aqui no texto\n"
    with pytest.raises(ValueError, match="mais de uma vez"):
        localizar_intervalo_trecho_ancora_no_texto_transcribrothers(md, "paragrafo repetido aqui no texto")
