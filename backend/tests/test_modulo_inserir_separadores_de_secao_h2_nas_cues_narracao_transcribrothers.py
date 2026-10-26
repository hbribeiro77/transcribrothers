"""Inserção de intercalários de seção ## (menos o primeiro) nas cues da narração."""

from transcribrothers_backend.modulo_inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers import (
    aplicar_titulo_curto_nas_cues_separador_apos_limpeza_legendas_transcribrothers,
    carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers,
    duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers,
    encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers,
    inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers,
)

_MD_DUAS_SECOES = """# Tutorial

Abertura do curso. [tela](?t=1)

## Pré-requisito

Instale o Python. [tela](?t=5)

## Nova funcionalidade

Neste tutorial você cria um job. [tela](?t=12)
"""

_MD_TITULO_LONGO = """# Tutorial

Intro. [tela](?t=1)

## Primeira

Corpo um. [tela](?t=4)

## Passo 2: Associar ao Workspace de Legado (Transcrições Antigas)

Corpo dois. [tela](?t=10)
"""

_MD_UMA_SECAO = """# Tutorial

Intro. [tela](?t=1)

## Só uma

Texto da seção. [tela](?t=4)
"""


def test_carimba_preambulo_vazio_e_titulo_de_cada_h2() -> None:
    cues = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        _MD_DUAS_SECOES,
        duracao_video_segundos=20.0,
    ).cues
    carimbadas = carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(cues, _MD_DUAS_SECOES)
    titulos = [c.titulo_secao_heading for c in carimbadas]
    assert "" in titulos
    assert "Pré-requisito" in titulos
    assert "Nova funcionalidade" in titulos
    assert titulos.index("") < titulos.index("Pré-requisito") < titulos.index("Nova funcionalidade")


def test_encurta_titulo_longo_tira_parenteses_e_cabe_no_cartao() -> None:
    longo = "Passo 2: Associar ao Workspace de Legado (Transcrições Antigas)"
    curto = encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(longo)
    assert "(" not in curto
    assert len(curto) <= 40
    assert curto.startswith("Passo 2:")
    assert encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(
        "Nova funcionalidade"
    ) == "Nova funcionalidade"


def test_duracao_alvo_do_separador_e_o_maior_entre_pedida_e_fala() -> None:
    assert duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers(
        duracao_pedida_segundos=2.0,
        duracao_fala_segundos=1.2,
    ) == 2.0
    assert duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers(
        duracao_pedida_segundos=2.0,
        duracao_fala_segundos=3.5,
    ) == 3.5
    # A API de vinhetas só aceita meios de segundo («Escolha uma velocidade»).
    assert duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers(
        duracao_pedida_segundos=2.0,
        duracao_fala_segundos=2.18,
    ) == 2.0
    assert duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers(
        duracao_pedida_segundos=2.0,
        duracao_fala_segundos=2.3,
    ) == 2.5


def test_insere_separador_so_antes_do_segundo_h2() -> None:
    cues = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        _MD_DUAS_SECOES,
        duracao_video_segundos=20.0,
    ).cues
    carimbadas = carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(cues, _MD_DUAS_SECOES)
    saida = inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers(
        carimbadas,
        efeito="linhas-que-desenham-o-lugar",
        duracao_segundos=2.0,
    )
    separadores = [c for c in saida if c.eh_separador_secao]
    assert [c.texto for c in separadores] == ["Nova funcionalidade"]
    sep = separadores[0]
    assert sep.sem_narracao is False
    assert sep.inicio_video_segundos == 0.0
    assert sep.fim_video_segundos == 2.0
    assert sep.receita_vinheta_separador["efeito"] == "linhas-que-desenham-o-lugar"
    assert sep.receita_vinheta_separador["vinheta_id"] is None
    assert sep.receita_vinheta_separador["presenca_da_imagem"] == 60
    assert sep.receita_vinheta_separador["titulo"] == "Nova funcionalidade"
    indice = saida.index(sep)
    assert saida[indice + 1].titulo_secao_heading == "Nova funcionalidade"
    assert saida[indice + 1].texto != "Nova funcionalidade"
    assert any(
        (not c.eh_separador_secao) and "Pré-requisito" in (c.texto, c.titulo_secao_heading)
        for c in saida
    )


def test_aplica_titulo_curto_da_ia_no_cartao_do_separador() -> None:
    sep = CueNarracaoComJanelaVideoTranscribrothers(
        texto="Passo 2: Associar ao workspace de legado e também às transcrições antigas",
        inicio_video_segundos=0.0,
        fim_video_segundos=2.0,
        origem_ancora="separador_secao",
        casado=True,
        eh_separador_secao=True,
        titulo_secao_heading="Passo 2: Associar ao Workspace de Legado",
        receita_vinheta_separador={
            "titulo": "Passo 2: Associar ao Workspace de Legado",
            "efeito": "linhas-que-desenham-o-lugar",
            "duracao_segundos": 2.0,
        },
    )
    corpo = CueNarracaoComJanelaVideoTranscribrothers(
        texto="Abra o workspace.",
        inicio_video_segundos=10.0,
        fim_video_segundos=14.0,
        origem_ancora="markdown_t",
        casado=True,
        titulo_secao_heading="Passo 2: Associar ao Workspace de Legado",
    )
    saida = aplicar_titulo_curto_nas_cues_separador_apos_limpeza_legendas_transcribrothers(
        [sep, corpo]
    )
    assert saida[0].eh_separador_secao is True
    assert "(" not in saida[0].texto
    assert len(saida[0].texto) <= 40
    assert saida[0].receita_vinheta_separador["titulo"] == saida[0].texto
    assert saida[1].texto == "Abra o workspace."


def test_separador_de_h2_longo_fica_curto_e_sem_parenteses() -> None:
    cues = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        _MD_TITULO_LONGO,
        duracao_video_segundos=20.0,
    ).cues
    carimbadas = carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(cues, _MD_TITULO_LONGO)
    saida = inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers(
        carimbadas,
        efeito="linhas-que-desenham-o-lugar",
        duracao_segundos=2.0,
    )
    sep = next(c for c in saida if c.eh_separador_secao)
    assert "(" not in sep.texto
    assert len(sep.texto) <= 40
    assert sep.texto.startswith("Passo 2:")
    assert sep.sem_narracao is False
    assert sep.receita_vinheta_separador["titulo"] == sep.texto


def test_uma_secao_h2_nao_insere_separador() -> None:
    cues = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        _MD_UMA_SECAO,
        duracao_video_segundos=20.0,
    ).cues
    carimbadas = carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(cues, _MD_UMA_SECAO)
    saida = inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers(
        carimbadas,
        efeito="linhas-que-desenham-o-lugar",
        duracao_segundos=2.0,
    )
    assert all(not c.eh_separador_secao for c in saida)
    assert len(saida) == len(carimbadas)


def test_receita_do_separador_carrega_vinheta_salva() -> None:
    cues = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        _MD_DUAS_SECOES,
        duracao_video_segundos=20.0,
    ).cues
    carimbadas = carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(cues, _MD_DUAS_SECOES)
    saida = inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers(
        carimbadas,
        efeito="barras-que-se-cruzam",
        duracao_segundos=2.0,
        vinheta_id="abc-salva",
    )
    sep = next(c for c in saida if c.eh_separador_secao)
    assert sep.receita_vinheta_separador["vinheta_id"] == "abc-salva"
    assert sep.receita_vinheta_separador["efeito"] == "barras-que-se-cruzam"
    assert sep.receita_vinheta_separador.get("presenca_da_imagem") is None
    assert "cores" not in sep.receita_vinheta_separador
