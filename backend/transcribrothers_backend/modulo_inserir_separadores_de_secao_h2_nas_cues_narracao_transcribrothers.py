"""Marca a seção ## de cada cue e insere intercalário antes de cada H2, menos o primeiro."""

from __future__ import annotations

import re
from typing import Any

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    substituir_campos_da_cue_narracao_com_janela_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_util_partir_texto_plano_em_frases_para_legendas_transcribrothers import (
    partir_texto_plano_em_frases_para_legendas_transcribrothers,
)

DURACAO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS = 2.0
DURACAO_MINIMA_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS = 0.5
DURACAO_MAXIMA_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS = 8.0
EFEITO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO = "linhas-que-desenham-o-lugar"
PRESENCA_PADRAO_IMAGEM_TRANSICAO_SECAO = 60
_MAX_CHARS_TITULO_CARTAO_SEPARADOR_SECAO = 40
_RE_PARENTESES_TITULO_SEPARADOR = re.compile(r"\s*\([^)]*\)")


def _normalizar_frase_para_casamento_transcribrothers(texto: str) -> str:
    return " ".join((texto or "").replace("\r\n", "\n").replace("\r", "\n").split())


def _normalizar_titulo_para_comparar_duplicata_transcribrothers(texto: str) -> str:
    bruto = _normalizar_frase_para_casamento_transcribrothers(texto).casefold()
    return " ".join(bruto.replace(".", " ").split())


def encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(
    titulo: str,
) -> str:
    """Título curto para o cartão e a fala da vinheta (sem parênteses, ~40 caracteres)."""
    original = _normalizar_frase_para_casamento_transcribrothers(titulo)
    sem_parenteses = _RE_PARENTESES_TITULO_SEPARADOR.sub("", original)
    s = _normalizar_frase_para_casamento_transcribrothers(sem_parenteses).strip(" -:;,.")
    if not s:
        s = original
    if len(s) <= _MAX_CHARS_TITULO_CARTAO_SEPARADOR_SECAO:
        return s
    palavras = s.split()
    escolhidas: list[str] = []
    for palavra in palavras:
        candidato = " ".join(escolhidas + [palavra])
        if escolhidas and len(candidato) > _MAX_CHARS_TITULO_CARTAO_SEPARADOR_SECAO:
            break
        escolhidas.append(palavra)
    return " ".join(escolhidas) if escolhidas else s[:_MAX_CHARS_TITULO_CARTAO_SEPARADOR_SECAO]


def _arredondar_duracao_vinheta_para_meio_segundo_transcribrothers(segundos: float) -> float:
    """A API de vinhetas só aceita 0,5 / 1 / 1,5 … 8 s."""
    limitado = min(
        DURACAO_MAXIMA_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS,
        max(DURACAO_MINIMA_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS, float(segundos)),
    )
    return round(limitado * 2.0) / 2.0


def duracao_alvo_do_separador_secao_com_fala_tts_transcribrothers(
    *,
    duracao_pedida_segundos: float,
    duracao_fala_segundos: float,
) -> float:
    """A vinheta dura o pedido ou a fala, o que for maior, em meios de segundo."""
    bruto = max(
        DURACAO_MINIMA_TRANSICAO_SECAO_VIDEO_NARRADO_SEGUNDOS,
        float(duracao_pedida_segundos),
        float(duracao_fala_segundos),
    )
    return _arredondar_duracao_vinheta_para_meio_segundo_transcribrothers(bruto)


def _cue_repete_so_o_titulo_da_secao_transcribrothers(
    cue: CueNarracaoComJanelaVideoTranscribrothers,
    titulo: str,
) -> bool:
    texto = _normalizar_titulo_para_comparar_duplicata_transcribrothers(cue.texto)
    if not texto:
        return False
    alvo = _normalizar_titulo_para_comparar_duplicata_transcribrothers(titulo)
    curto = _normalizar_titulo_para_comparar_duplicata_transcribrothers(
        encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(titulo)
    )
    return bool(alvo) and (texto == alvo or texto == curto)


def aplicar_titulo_curto_nas_cues_separador_apos_limpeza_legendas_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    """Garante título curto no texto e na receita do cartão depois da IA."""
    saida: list[CueNarracaoComJanelaVideoTranscribrothers] = []
    for cue in cues:
        if not bool(getattr(cue, "eh_separador_secao", False)):
            saida.append(cue)
            continue
        curto = encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(
            cue.texto or str(getattr(cue, "titulo_secao_heading", "") or "")
        )
        receita: dict[str, Any] = dict(getattr(cue, "receita_vinheta_separador", None) or {})
        receita["titulo"] = curto
        saida.append(
            substituir_campos_da_cue_narracao_com_janela_transcribrothers(
                cue,
                texto=curto,
                receita_vinheta_separador=receita,
            )
        )
    return saida


def _titulo_visivel_do_heading_h2_transcribrothers(linha_heading: str) -> str:
    s = (linha_heading or "").strip()
    if s.startswith("##"):
        s = s[2:].strip()
    return s


def listar_frases_com_titulo_secao_h2_do_markdown_transcribrothers(
    markdown: str,
) -> list[tuple[str, str]]:
    md = markdown or ""
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
    pares: list[tuple[str, str]] = []
    inicio_primeiro_h2 = secoes[0].inicio_caractere if secoes else len(md)
    preambulo = md[:inicio_primeiro_h2]
    for frase in partir_texto_plano_em_frases_para_legendas_transcribrothers(
        extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(preambulo)
    ):
        pares.append((frase, ""))
    for secao in secoes:
        titulo = _titulo_visivel_do_heading_h2_transcribrothers(secao.linha_heading)
        corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(md, secao)
        for frase in partir_texto_plano_em_frases_para_legendas_transcribrothers(
            extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(corpo)
        ):
            pares.append((frase, titulo))
    return pares


def carimbar_titulo_secao_h2_nas_cues_narracao_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    markdown: str,
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    frases_por_titulo: dict[str, set[str]] = {}
    ordem_titulos: list[str] = []
    for frase, titulo in listar_frases_com_titulo_secao_h2_do_markdown_transcribrothers(markdown):
        if titulo not in frases_por_titulo:
            frases_por_titulo[titulo] = set()
            ordem_titulos.append(titulo)
        frases_por_titulo[titulo].add(_normalizar_frase_para_casamento_transcribrothers(frase))
    ultimo = ""
    saida: list[CueNarracaoComJanelaVideoTranscribrothers] = []
    for cue in cues:
        alvo = _normalizar_frase_para_casamento_transcribrothers(cue.texto)
        candidatos = [titulo for titulo in ordem_titulos if alvo in frases_por_titulo[titulo]]
        if len(candidatos) == 1:
            ultimo = candidatos[0]
        elif len(candidatos) > 1 and ultimo not in candidatos:
            ultimo = candidatos[0]
        saida.append(
            substituir_campos_da_cue_narracao_com_janela_transcribrothers(
                cue,
                titulo_secao_heading=ultimo,
            )
        )
    return saida


def _montar_receita_vinheta_do_separador_transcribrothers(
    *,
    titulo: str,
    efeito: str,
    duracao_segundos: float,
    vinheta_id: str | None = None,
) -> dict[str, object]:
    vinheta_ok = (vinheta_id or "").strip() or None
    receita: dict[str, object] = {
        "titulo": titulo,
        "efeito": efeito,
        "vinheta_id": vinheta_ok,
        "duracao_segundos": float(duracao_segundos),
    }
    if vinheta_ok is None:
        receita["presenca_da_imagem"] = PRESENCA_PADRAO_IMAGEM_TRANSICAO_SECAO
    return receita


def inserir_separadores_de_secao_h2_nas_cues_narracao_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    *,
    efeito: str,
    duracao_segundos: float,
    vinheta_id: str | None = None,
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    duracao = max(0.5, float(duracao_segundos))
    efeito_ok = (efeito or "").strip() or EFEITO_PADRAO_TRANSICAO_SECAO_VIDEO_NARRADO
    vinheta_ok = (vinheta_id or "").strip() or None
    saida: list[CueNarracaoComJanelaVideoTranscribrothers] = []
    primeira_secao: str | None = None
    for cue in cues:
        titulo = str(getattr(cue, "titulo_secao_heading", "") or "").strip()
        inseriu_separador = False
        if titulo:
            if primeira_secao is None:
                primeira_secao = titulo
            elif titulo != primeira_secao and (
                not saida or str(getattr(saida[-1], "titulo_secao_heading", "") or "") != titulo
            ):
                titulo_curto = encurtar_titulo_para_cartao_e_fala_do_separador_de_secao_transcribrothers(
                    titulo
                )
                receita = _montar_receita_vinheta_do_separador_transcribrothers(
                    titulo=titulo_curto,
                    efeito=efeito_ok,
                    duracao_segundos=duracao,
                    vinheta_id=vinheta_ok,
                )
                saida.append(
                    CueNarracaoComJanelaVideoTranscribrothers(
                        texto=titulo_curto,
                        inicio_video_segundos=0.0,
                        fim_video_segundos=duracao,
                        origem_ancora="separador_secao",
                        casado=True,
                        sem_narracao=False,
                        titulo_secao_heading=titulo,
                        eh_separador_secao=True,
                        receita_vinheta_separador=receita,
                    )
                )
                primeira_secao = titulo
                inseriu_separador = True
        if inseriu_separador and _cue_repete_so_o_titulo_da_secao_transcribrothers(cue, titulo):
            continue
        saida.append(cue)
    return saida
