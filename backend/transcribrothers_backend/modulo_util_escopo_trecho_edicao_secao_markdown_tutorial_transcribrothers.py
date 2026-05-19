"""Localização de trecho colado e fatiamento do corpo da seção para edição com escopo limitado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    SecaoMarkdownNivel2TutorialTranscribrothers,
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
)

ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers = Literal[
    "secao_inteira",
    "trecho_local",
    "a_partir_de",
]

ROTULO_REGIAO_PREFACIO_INTRODUCAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS = (
    "(Introdução — antes das seções ##)"
)


@dataclass(frozen=True)
class RegiaoEdicaoMarkdownTutorialTranscribrothers:
    """Região editável: uma seção «##» ou o prefácio antes da primeira «##»."""

    eh_prefacio: bool
    secao: SecaoMarkdownNivel2TutorialTranscribrothers | None
    inicio_caractere: int
    fim_caractere: int
    rotulo_regiao: str


@dataclass(frozen=True)
class PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers:
    regiao: RegiaoEdicaoMarkdownTutorialTranscribrothers
    corpo_regiao: str
    fatia: "FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers"


@dataclass(frozen=True)
class FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers:
    prefixo_imutavel: str
    zona_editavel: str
    sufixo_imutavel: str
    trecho_ancora_resolvido: str
    inicio_zona_no_corpo_secao: int
    fim_zona_no_corpo_secao: int


def _normalizar_quebras_linha_texto_markdown_transcribrothers(s: str) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n")


def localizar_intervalo_trecho_ancora_no_texto_transcribrothers(
    texto: str,
    trecho_ancora: str,
) -> tuple[int, int, str]:
    """Retorna (inicio, fim, trecho_canonico_encontrado). Erro se ausente ou ambíguo."""
    ancora_raw = (trecho_ancora or "").strip()
    if not ancora_raw:
        raise ValueError("Informe o trecho de referência (cole o texto do tutorial).")
    if len(ancora_raw) < 8:
        raise ValueError("O trecho colado é curto demais; inclua mais linhas para localizar com segurança.")

    texto_n = _normalizar_quebras_linha_texto_markdown_transcribrothers(texto)
    ancora_n = _normalizar_quebras_linha_texto_markdown_transcribrothers(ancora_raw)

    candidatos: list[tuple[int, int, str]] = []

    def _registrar(inicio: int, trecho_encontrado: str) -> None:
        fim = inicio + len(trecho_encontrado)
        candidatos.append((inicio, fim, trecho_encontrado))

    if ancora_n in texto_n:
        inicio = 0
        while True:
            idx = texto_n.find(ancora_n, inicio)
            if idx < 0:
                break
            _registrar(idx, ancora_n)
            inicio = idx + 1

    if not candidatos:
        linhas_ancora = [ln for ln in ancora_n.splitlines() if ln.strip()]
        if len(linhas_ancora) >= 1:
            primeira = linhas_ancora[0].strip()
            inicio_busca = 0
            while True:
                idx_linha = texto_n.find(primeira, inicio_busca)
                if idx_linha < 0:
                    break
                trecho_cand = texto_n[idx_linha : idx_linha + len(ancora_n)]
                if trecho_cand == ancora_n:
                    _registrar(idx_linha, ancora_n)
                elif len(linhas_ancora) > 1:
                    fim_busca = idx_linha + max(len(ancora_n) * 3, 4000)
                    bloco = texto_n[idx_linha:fim_busca]
                    if all(ln.strip() in bloco for ln in linhas_ancora[1:]):
                        fim_est = idx_linha + len(ancora_n)
                        for ln in reversed(linhas_ancora):
                            pos = bloco.rfind(ln.strip())
                            if pos >= 0:
                                fim_est = idx_linha + pos + len(ln.strip())
                                break
                        _registrar(idx_linha, texto_n[idx_linha:fim_est])
                inicio_busca = idx_linha + 1

    if not candidatos:
        raise ValueError(
            "Não foi possível localizar o trecho colado no tutorial. "
            "Copie o texto exatamente como aparece (incluindo títulos e quebras de linha)."
        )
    if len(candidatos) > 1:
        raise ValueError(
            "O trecho colado aparece mais de uma vez no texto. "
            "Inclua mais linhas no colado para desambiguar."
        )
    return candidatos[0]


def obter_intervalo_prefacio_antes_primeira_secao_nivel2_markdown_transcribrothers(
    markdown: str,
) -> tuple[int, int]:
    """Do início do arquivo até o caractere antes do primeiro «## » (pode incluir «# » título)."""
    md = markdown or ""
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
    if not secoes:
        return 0, len(md)
    return 0, int(secoes[0].inicio_caractere)


def resolver_regiao_edicao_markdown_com_trecho_ancora_transcribrothers(
    markdown: str,
    trecho_ancora: str,
    *,
    titulo_secao_heading: str | None = None,
    indice_secao: int | None = None,
) -> tuple[RegiaoEdicaoMarkdownTutorialTranscribrothers, int, int]:
    """Resolve região (prefácio ou seção ##) e intervalo da âncora relativo ao corpo da região."""
    md = markdown or ""
    inicio_md, fim_md, _ = localizar_intervalo_trecho_ancora_no_texto_transcribrothers(md, trecho_ancora)
    ini_pref, fim_pref = obter_intervalo_prefacio_antes_primeira_secao_nivel2_markdown_transcribrothers(md)

    if titulo_secao_heading is not None and str(titulo_secao_heading).strip():
        secao = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
            md,
            titulo_secao_heading=titulo_secao_heading,
            indice_secao=None,
        )
    elif indice_secao is not None:
        secao = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
            md,
            titulo_secao_heading=None,
            indice_secao=indice_secao,
        )
    else:
        secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
        contendo = [s for s in secoes if s.inicio_caractere <= inicio_md < s.fim_caractere]
        if contendo:
            secao = contendo[0]
        elif fim_pref > ini_pref and ini_pref <= inicio_md < fim_pref:
            regiao = RegiaoEdicaoMarkdownTutorialTranscribrothers(
                eh_prefacio=True,
                secao=None,
                inicio_caractere=ini_pref,
                fim_caractere=fim_pref,
                rotulo_regiao=ROTULO_REGIAO_PREFACIO_INTRODUCAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
            )
            inicio_corpo = inicio_md - ini_pref
            fim_corpo = fim_md - ini_pref
            return regiao, inicio_corpo, fim_corpo
        elif not secoes:
            regiao = RegiaoEdicaoMarkdownTutorialTranscribrothers(
                eh_prefacio=True,
                secao=None,
                inicio_caractere=0,
                fim_caractere=len(md),
                rotulo_regiao=ROTULO_REGIAO_PREFACIO_INTRODUCAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
            )
            return regiao, inicio_md, fim_md
        else:
            raise ValueError(
                "O trecho colado não está dentro de nenhuma seção «##» nem na introdução do documento "
                "(texto antes da primeira «##»). Cole um trecho do corpo certo ou escolha a seção manualmente."
            )

    if not (secao.inicio_caractere <= inicio_md < secao.fim_caractere):
        raise ValueError(
            f"O trecho colado não pertence à seção {secao.linha_heading!r}. "
            "Ajuste o colado ou escolha outra seção."
        )
    regiao = RegiaoEdicaoMarkdownTutorialTranscribrothers(
        eh_prefacio=False,
        secao=secao,
        inicio_caractere=secao.inicio_caractere,
        fim_caractere=secao.fim_caractere,
        rotulo_regiao=secao.linha_heading,
    )
    inicio_corpo = inicio_md - secao.inicio_caractere
    fim_corpo = fim_md - secao.inicio_caractere
    return regiao, inicio_corpo, fim_corpo


def resolver_secao_markdown_nivel2_para_edicao_com_trecho_ancora_transcribrothers(
    markdown: str,
    trecho_ancora: str,
    *,
    titulo_secao_heading: str | None = None,
    indice_secao: int | None = None,
) -> tuple[SecaoMarkdownNivel2TutorialTranscribrothers, int, int]:
    """Compatibilidade: só quando a região é uma seção «##»."""
    regiao, inicio_corpo, fim_corpo = resolver_regiao_edicao_markdown_com_trecho_ancora_transcribrothers(
        markdown,
        trecho_ancora,
        titulo_secao_heading=titulo_secao_heading,
        indice_secao=indice_secao,
    )
    if regiao.eh_prefacio or regiao.secao is None:
        raise ValueError(
            "O trecho está na introdução do documento (antes da primeira «##»), não numa seção «##»."
        )
    return regiao.secao, inicio_corpo, fim_corpo


def fatiar_corpo_secao_markdown_por_modo_escopo_edicao_transcribrothers(
    corpo_secao: str,
    *,
    modo: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    inicio_ancora_no_corpo: int,
    fim_ancora_no_corpo: int,
    trecho_ancora_resolvido: str,
) -> FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers:
    corpo = corpo_secao or ""
    n = len(corpo)
    ini = max(0, min(int(inicio_ancora_no_corpo), n))
    fim = max(ini, min(int(fim_ancora_no_corpo), n))

    if modo == "secao_inteira":
        return FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers(
            prefixo_imutavel="",
            zona_editavel=corpo,
            sufixo_imutavel="",
            trecho_ancora_resolvido="",
            inicio_zona_no_corpo_secao=0,
            fim_zona_no_corpo_secao=n,
        )

    trecho_res = trecho_ancora_resolvido or corpo[ini:fim]

    if modo == "trecho_local":
        return FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers(
            prefixo_imutavel=corpo[:ini],
            zona_editavel=corpo[ini:fim],
            sufixo_imutavel=corpo[fim:],
            trecho_ancora_resolvido=trecho_res,
            inicio_zona_no_corpo_secao=ini,
            fim_zona_no_corpo_secao=fim,
        )

    if modo == "a_partir_de":
        return FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers(
            prefixo_imutavel=corpo[:ini],
            zona_editavel=corpo[ini:],
            sufixo_imutavel="",
            trecho_ancora_resolvido=trecho_res,
            inicio_zona_no_corpo_secao=ini,
            fim_zona_no_corpo_secao=n,
        )

    raise ValueError(f"modo_escopo_edicao inválido: {modo!r}")


def preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
    markdown: str,
    *,
    modo: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    trecho_ancora: str | None = None,
    titulo_secao_heading: str | None = None,
    indice_secao: int | None = None,
) -> PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers:
    md = markdown or ""
    if modo == "secao_inteira":
        secao = resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
            md,
            titulo_secao_heading=titulo_secao_heading,
            indice_secao=indice_secao,
        )
        regiao = RegiaoEdicaoMarkdownTutorialTranscribrothers(
            eh_prefacio=False,
            secao=secao,
            inicio_caractere=secao.inicio_caractere,
            fim_caractere=secao.fim_caractere,
            rotulo_regiao=secao.linha_heading,
        )
        corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(md, secao)
        fatia = fatiar_corpo_secao_markdown_por_modo_escopo_edicao_transcribrothers(
            corpo,
            modo=modo,
            inicio_ancora_no_corpo=0,
            fim_ancora_no_corpo=len(corpo),
            trecho_ancora_resolvido="",
        )
        return PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers(
            regiao=regiao,
            corpo_regiao=corpo,
            fatia=fatia,
        )

    if not (trecho_ancora or "").strip():
        raise ValueError("Informe o trecho de referência para este modo de edição.")

    _, _, trecho_res = localizar_intervalo_trecho_ancora_no_texto_transcribrothers(md, trecho_ancora)
    regiao, ini_corpo, fim_corpo = resolver_regiao_edicao_markdown_com_trecho_ancora_transcribrothers(
        md,
        trecho_ancora,
        titulo_secao_heading=titulo_secao_heading,
        indice_secao=indice_secao,
    )
    corpo = md[regiao.inicio_caractere : regiao.fim_caractere]
    fatia = fatiar_corpo_secao_markdown_por_modo_escopo_edicao_transcribrothers(
        corpo,
        modo=modo,
        inicio_ancora_no_corpo=ini_corpo,
        fim_ancora_no_corpo=fim_corpo,
        trecho_ancora_resolvido=trecho_res,
    )
    if not fatia.zona_editavel.strip():
        raise ValueError("A zona editável ficou vazia; revise o trecho colado.")
    if regiao.eh_prefacio:
        fatia = reservar_heading_h1_documento_fora_da_zona_editavel_transcribrothers(corpo, fatia)
    elif regiao.secao is not None:
        fatia = reservar_heading_secao_nivel2_fora_da_zona_editavel_transcribrothers(corpo, regiao.secao, fatia)
    if not fatia.zona_editavel.strip():
        raise ValueError("A zona editável ficou vazia após reservar títulos imutáveis.")
    return PreparacaoEscopoEdicaoMarkdownTutorialTranscribrothers(
        regiao=regiao,
        corpo_regiao=corpo,
        fatia=fatia,
    )


def reservar_heading_h1_documento_fora_da_zona_editavel_transcribrothers(
    corpo_prefacio: str,
    fatia: FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
) -> FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers:
    """Mantém a linha «# Título» do documento fora da zona editável."""
    corpo = corpo_prefacio or ""
    primeira = corpo.lstrip().splitlines()[0].strip() if corpo.strip() else ""
    if not primeira.startswith("# ") or primeira.startswith("## "):
        return fatia
    pos_heading = corpo.find(primeira)
    if pos_heading < 0:
        return fatia
    pos_apos_heading = pos_heading + len(primeira)
    while pos_apos_heading < len(corpo) and corpo[pos_apos_heading] in "\r\n":
        pos_apos_heading += 1
    if fatia.inicio_zona_no_corpo_secao >= pos_apos_heading:
        return fatia
    new_prefix = corpo[:pos_apos_heading]
    if fatia.sufixo_imutavel:
        new_zona = corpo[pos_apos_heading : fatia.fim_zona_no_corpo_secao]
        new_fim = fatia.fim_zona_no_corpo_secao
    else:
        new_zona = corpo[pos_apos_heading:]
        new_fim = len(corpo)
    return FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers(
        prefixo_imutavel=new_prefix,
        zona_editavel=new_zona,
        sufixo_imutavel=fatia.sufixo_imutavel,
        trecho_ancora_resolvido=fatia.trecho_ancora_resolvido,
        inicio_zona_no_corpo_secao=pos_apos_heading,
        fim_zona_no_corpo_secao=new_fim,
    )


def mesclar_corpo_regiao_editada_no_markdown_completo_tutorial_transcribrothers(
    markdown: str,
    regiao: RegiaoEdicaoMarkdownTutorialTranscribrothers,
    corpo_regiao_atualizado: str,
) -> str:
    md = markdown or ""
    novo = (corpo_regiao_atualizado or "").strip()
    if not novo and regiao.fim_caractere > regiao.inicio_caractere:
        raise ValueError("A região editada ficou vazia.")
    antes = md[: regiao.inicio_caractere]
    depois = md[regiao.fim_caractere :]
    if antes and not antes.endswith("\n") and not novo.startswith("\n"):
        novo = "\n" + novo
    if depois and not novo.endswith("\n") and not depois.startswith("\n"):
        novo = novo + "\n"
    return antes + novo + depois


def secao_sintetica_para_verificacao_redundancia_prefacio_markdown_transcribrothers(
    fim_prefacio: int,
) -> SecaoMarkdownNivel2TutorialTranscribrothers:
    return SecaoMarkdownNivel2TutorialTranscribrothers(
        indice=-1,
        linha_heading="## (Introdução do documento)",
        titulo_normalizado="introducao documento",
        inicio_caractere=0,
        fim_caractere=max(0, int(fim_prefacio)),
    )


def reservar_heading_secao_nivel2_fora_da_zona_editavel_transcribrothers(
    corpo_secao: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
    fatia: FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
) -> FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers:
    """Garante que a linha «## Título» da seção nunca entre na zona enviada ao modelo."""
    heading = secao.linha_heading.strip()
    corpo = corpo_secao or ""
    pos_heading = corpo.find(heading)
    if pos_heading < 0:
        return fatia

    pos_apos_heading = pos_heading + len(heading)
    while pos_apos_heading < len(corpo) and corpo[pos_apos_heading] in "\r\n":
        pos_apos_heading += 1

    if fatia.inicio_zona_no_corpo_secao >= pos_apos_heading:
        return fatia

    new_prefix = corpo[:pos_apos_heading]
    if fatia.sufixo_imutavel:
        new_zona = corpo[pos_apos_heading : fatia.fim_zona_no_corpo_secao]
        new_fim = fatia.fim_zona_no_corpo_secao
    else:
        new_zona = corpo[pos_apos_heading:]
        new_fim = len(corpo)
    return FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers(
        prefixo_imutavel=new_prefix,
        zona_editavel=new_zona,
        sufixo_imutavel=fatia.sufixo_imutavel,
        trecho_ancora_resolvido=fatia.trecho_ancora_resolvido,
        inicio_zona_no_corpo_secao=pos_apos_heading,
        fim_zona_no_corpo_secao=new_fim,
    )


def sanitizar_zona_markdown_resposta_llm_escopo_secao_transcribrothers(
    zona_markdown: str,
    *,
    linha_heading_secao: str,
) -> str:
    """Remove headings «## » que o modelo não deveria devolver na zona editável."""
    heading = linha_heading_secao.strip()
    linhas = (zona_markdown or "").strip().splitlines()
    while linhas:
        ln = linhas[0].strip()
        if not ln:
            linhas = linhas[1:]
            continue
        if ln.startswith("## ") and not ln.startswith("###"):
            linhas = linhas[1:]
            continue
        if ln == "##" or ln == heading:
            linhas = linhas[1:]
            continue
        break
    return "\n".join(linhas).strip()


def garantir_heading_secao_nivel2_no_inicio_corpo_mesclado_transcribrothers(
    corpo_secao: str,
    *,
    linha_heading_secao: str,
) -> str:
    heading = linha_heading_secao.strip()
    corpo = corpo_secao or ""
    if not corpo.strip():
        return heading + "\n"
    linhas = corpo.splitlines()
    primeira = linhas[0].strip() if linhas else ""
    if primeira == heading:
        return corpo
    if primeira in ("##", "## ") or (primeira.startswith("## ") and primeira != heading):
        linhas[0] = heading
        return "\n".join(linhas)
    if not primeira.startswith("## "):
        return heading + "\n\n" + corpo.lstrip()
    return corpo


def mesclar_zona_regenerada_no_corpo_secao_markdown_transcribrothers(
    fatia: FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    zona_markdown_regenerada: str,
    *,
    linha_heading_secao: str | None = None,
) -> str:
    zona = sanitizar_zona_markdown_resposta_llm_escopo_secao_transcribrothers(
        zona_markdown_regenerada,
        linha_heading_secao=linha_heading_secao or "",
    )
    if not zona:
        raise ValueError("A zona regenerada está vazia.")
    prefixo = fatia.prefixo_imutavel
    sufixo = fatia.sufixo_imutavel
    if prefixo and not prefixo.endswith("\n") and not zona.startswith("\n"):
        if not prefixo.endswith("\n\n"):
            zona = "\n" + zona
    if sufixo and not zona.endswith("\n") and not sufixo.startswith("\n"):
        zona = zona + "\n"
    mesclado = prefixo + zona + sufixo
    if (linha_heading_secao or "").strip():
        mesclado = garantir_heading_secao_nivel2_no_inicio_corpo_mesclado_transcribrothers(
            mesclado,
            linha_heading_secao=linha_heading_secao,
        )
    return mesclado


def validar_corpo_secao_apos_edicao_escopada_transcribrothers(
    corpo_secao: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
) -> None:
    linhas_n2 = [ln for ln in (corpo_secao or "").splitlines() if ln.startswith("## ") and not ln.startswith("###")]
    if len(linhas_n2) != 1:
        raise ValueError(
            "Após a edição, a seção deve manter exatamente um heading «## » no início."
        )
    primeira = (corpo_secao or "").lstrip().splitlines()[0].strip()
    if primeira != secao.linha_heading.strip():
        raise ValueError(
            f"O heading da seção foi alterado ({primeira!r}); o esperado é {secao.linha_heading!r}."
        )
