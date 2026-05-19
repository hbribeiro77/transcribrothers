"""Lista, extrai e substitui seções de tutorial Markdown delimitadas por headings ``##`` (nível 2)."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

_RE_HEADING_NIVEL2_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"^## [^#].*$", re.MULTILINE)

_STOPWORDS_TITULO_SECAO_MARKDOWN_PT_BR_TRANSCRIBROTHERS = frozenset(
    {"de", "da", "do", "das", "dos", "e", "em", "na", "no", "nas", "nos", "a", "o", "as", "os", "um", "uma"}
)


@dataclass(frozen=True)
class SecaoMarkdownNivel2TutorialTranscribrothers:
    indice: int
    linha_heading: str
    titulo_normalizado: str
    inicio_caractere: int
    fim_caractere: int


def normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(linha_heading: str) -> str:
    s = (linha_heading or "").strip()
    if s.startswith("##"):
        s = s[2:].strip()
    return " ".join(s.lower().split())


def listar_secoes_markdown_nivel2_tutorial_transcribrothers(
    markdown: str,
) -> list[SecaoMarkdownNivel2TutorialTranscribrothers]:
    """Cada seção vai do ``## Título`` até o caractere antes do próximo ``##`` (ou fim do arquivo)."""
    md = markdown or ""
    matches = list(_RE_HEADING_NIVEL2_MARKDOWN_TRANSCRIBROTHERS.finditer(md))
    saida: list[SecaoMarkdownNivel2TutorialTranscribrothers] = []
    for i, m in enumerate(matches):
        inicio = m.start()
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        linha = m.group(0).strip()
        saida.append(
            SecaoMarkdownNivel2TutorialTranscribrothers(
                indice=i,
                linha_heading=linha,
                titulo_normalizado=normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(linha),
                inicio_caractere=inicio,
                fim_caractere=fim,
            )
        )
    return saida


def extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(
    markdown: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
) -> str:
    return (markdown or "")[secao.inicio_caractere : secao.fim_caractere].rstrip()


def _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers(norm: str) -> set[str]:
    return {
        w
        for w in (norm or "").split()
        if w and w not in _STOPWORDS_TITULO_SECAO_MARKDOWN_PT_BR_TRANSCRIBROTHERS
    }


def pontuar_similaridade_titulo_secao_markdown_nivel2_transcribrothers(
    titulo_secao_heading: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
) -> float:
    """Pontua 0..1 a proximidade entre um heading pedido e uma seção «##» do tutorial."""
    norm_alvo = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(titulo_secao_heading)
    norm_secao = secao.titulo_normalizado
    if not norm_alvo or not norm_secao:
        return 0.0
    if norm_alvo == norm_secao:
        return 1.0
    if norm_alvo in norm_secao or norm_secao in norm_alvo:
        return 0.92
    ratio = difflib.SequenceMatcher(None, norm_alvo, norm_secao).ratio()
    tok_a = _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers(norm_alvo)
    tok_s = _tokens_significativos_titulo_secao_normalizado_markdown_transcribrothers(norm_secao)
    if tok_a and tok_s:
        cobertura_alvo = len(tok_a & tok_s) / len(tok_a)
        ratio = max(ratio, cobertura_alvo * 0.95)
    return ratio


def listar_secoes_candidatas_por_titulo_heading_aproximado_markdown_nivel2_transcribrothers(
    secoes: list[SecaoMarkdownNivel2TutorialTranscribrothers],
    titulo_secao_heading: str,
    *,
    limiar_similaridade: float = 0.62,
) -> list[tuple[SecaoMarkdownNivel2TutorialTranscribrothers, float]]:
    alvo = (titulo_secao_heading or "").strip()
    if not alvo or not secoes:
        return []
    pontuadas: list[tuple[SecaoMarkdownNivel2TutorialTranscribrothers, float]] = []
    for s in secoes:
        p = pontuar_similaridade_titulo_secao_markdown_nivel2_transcribrothers(alvo, s)
        if p >= limiar_similaridade:
            pontuadas.append((s, p))
    pontuadas.sort(key=lambda item: item[1], reverse=True)
    return pontuadas


def reconciliar_linha_heading_secao_interpretada_com_secoes_tutorial_transcribrothers(
    titulo_secao_heading: str | None,
    secoes: list[SecaoMarkdownNivel2TutorialTranscribrothers],
) -> str | None:
    """Mapeia heading sugerido pela IA para a linha «##» exata do tutorial, se possível."""
    alvo = (titulo_secao_heading or "").strip()
    if not alvo or not secoes:
        return None
    for s in secoes:
        if s.linha_heading.strip() == alvo:
            return s.linha_heading
    norm_alvo = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(alvo)
    for s in secoes:
        if s.titulo_normalizado == norm_alvo:
            return s.linha_heading
    candidatas = listar_secoes_candidatas_por_titulo_heading_aproximado_markdown_nivel2_transcribrothers(
        secoes, alvo
    )
    if not candidatas:
        return None
    if len(candidatas) == 1:
        return candidatas[0][0].linha_heading
    melhor, p_melhor = candidatas[0]
    _, p_segundo = candidatas[1]
    if p_melhor >= 0.78 or p_melhor - p_segundo >= 0.08:
        return melhor.linha_heading
    return None


def resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers(
    markdown: str,
    *,
    titulo_secao_heading: str | None = None,
    indice_secao: int | None = None,
) -> SecaoMarkdownNivel2TutorialTranscribrothers:
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(markdown)
    if not secoes:
        raise ValueError("O tutorial não tem seções de nível 2 (linhas que começam com «## »).")
    if titulo_secao_heading is not None and str(titulo_secao_heading).strip():
        alvo = str(titulo_secao_heading).strip()
        norm_alvo = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(alvo)
        for s in secoes:
            if s.linha_heading.strip() == alvo:
                return s
            if s.titulo_normalizado == norm_alvo:
                return s
        candidatas = listar_secoes_candidatas_por_titulo_heading_aproximado_markdown_nivel2_transcribrothers(
            secoes, alvo
        )
        if candidatas:
            melhor, p_melhor = candidatas[0]
            if len(candidatas) == 1 or (
                len(candidatas) > 1 and p_melhor - candidatas[1][1] >= 0.08
            ):
                return melhor
            ambiguos = ", ".join(s.linha_heading for s, _ in candidatas[:4])
            raise ValueError(
                f"O heading {alvo!r} é ambíguo (várias seções parecidas): {ambiguos}. "
                "Cite o título «##» exato ou cole um trecho do corpo da seção."
            )
        sugestoes = ", ".join(s.linha_heading for s in secoes[:10])
        raise ValueError(
            f"Seção não encontrada para o heading: {alvo!r}. "
            f"Seções «##» no tutorial: {sugestoes}."
        )
    if indice_secao is not None:
        idx = int(indice_secao)
        if idx < 0 or idx >= len(secoes):
            raise ValueError(f"indice_secao fora do intervalo (0..{len(secoes) - 1}).")
        return secoes[idx]
    raise ValueError("Informe titulo_secao_heading ou indice_secao.")


def substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers(
    markdown: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
    novo_corpo_secao: str,
) -> str:
    """Substitui só o intervalo da seção; ``novo_corpo_secao`` deve incluir a linha ``##`` inicial."""
    md = markdown or ""
    novo = (novo_corpo_secao or "").strip()
    if not novo:
        raise ValueError("O corpo da seção regenerada está vazio.")
    linhas_n2 = [ln for ln in novo.splitlines() if ln.startswith("## ") and not ln.startswith("###")]
    if len(linhas_n2) != 1:
        raise ValueError(
            "A seção regenerada deve conter exatamente uma linha de heading de nível 2 (## …)."
        )
    norm_esperado = secao.titulo_normalizado
    norm_novo = normalizar_titulo_heading_secao_markdown_nivel2_transcribrothers(linhas_n2[0])
    if norm_novo != norm_esperado:
        raise ValueError(
            f"O heading da seção regenerada ({linhas_n2[0]!r}) não corresponde à seção pedida "
            f"({secao.linha_heading!r})."
        )
    antes = md[: secao.inicio_caractere]
    depois = md[secao.fim_caractere :]
    meio = novo
    if antes and not antes.endswith("\n"):
        if not meio.startswith("\n"):
            meio = "\n" + meio
    if depois and not meio.endswith("\n"):
        meio = meio + "\n"
    return antes + meio + depois


def validar_resposta_llm_e_mesclar_secao_regenerada_no_markdown_tutorial_transcribrothers(
    markdown_original: str,
    secao: SecaoMarkdownNivel2TutorialTranscribrothers,
    markdown_secao_regenerada_pelo_modelo: str,
) -> str:
    return substituir_corpo_secao_markdown_nivel2_tutorial_transcribrothers(
        markdown_original,
        secao,
        markdown_secao_regenerada_pelo_modelo,
    )
