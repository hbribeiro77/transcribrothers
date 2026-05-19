"""Extrai caminhos relativos `assets/*.png` citados em Markdown (tutorial), em ordem de primeira ocorrência."""

from __future__ import annotations

import re

_RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"!\[[^\]]*\]\(\s*([^)]+?)\s*\)")


def normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(raw: str) -> str | None:
    """Aceita `assets/foo.png`, `./assets/foo.png` ou URL com fragmento; devolve `assets/foo.png` ou None."""
    s = (raw or "").strip().strip('"').strip("'")
    if not s:
        return None
    if "?" in s:
        s = s.split("?", 1)[0].strip()
    s = s.replace("\\", "/")
    if "#" in s:
        s = s.split("#", 1)[0].strip()
    if s.lower().startswith(("http://", "https://", "data:")):
        return None
    s = s.lstrip("./")
    if not s.lower().endswith(".png"):
        return None
    if s.startswith("assets/"):
        return s
    idx = s.find("assets/")
    if idx >= 0:
        return s[idx:]
    return None


def listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(
    markdown: str,
) -> list[str]:
    """Lista única por caminho, preservando ordem da primeira aparição no texto."""
    if not (markdown or "").strip():
        return []
    vistos: set[str] = set()
    saida: list[str] = []
    for m in _RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.finditer(markdown):
        norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(m.group(1))
        if norm is None:
            continue
        if norm not in vistos:
            vistos.add(norm)
            saida.append(norm)
    return saida


_RE_ASSETS_PNG_SOLTO_NO_TEXTO_TRANSCRIBROTHERS = re.compile(
    r"(?i)\bassets/[^\s)\]\"'<>]+\.png\b",
)
_RE_FIGURA_OU_IMAGEM_NUMERO_NO_TEXTO_TRANSCRIBROTHERS = re.compile(
    r"(?i)\b(figura|imagem|img)\s*[#:]?\s*(\d{1,3})\b",
)


def montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
    *,
    markdown: str,
    instrucoes_revisao_humana: str | None,
    rels_completos_com_tempos: list[tuple[float, str]],
) -> list[tuple[float, str]]:
    """Imagens a anexar ao LiteLLM na regeneração: as do Markdown + as citadas nas instruções.

    - Ordem: primeiro a ordem de primeira aparição no Markdown; depois extras únicos vindos das instruções.
    - Nas instruções aceita: ``Figura 2``, ``imagem #3``, ``assets/foo.png`` (só se existir no snapshot).
    - ``Figura N`` usa a mesma numeração da lista abaixo (1 = primeira imagem do tutorial na ordem do .md).
    """
    nome_para_par: dict[str, tuple[float, str]] = {}
    for t, rel in rels_completos_com_tempos:
        nome = rel.strip().replace("\\", "/").split("/")[-1]
        if nome:
            nome_para_par[nome] = (float(t), rel if rel.startswith("assets/") else f"assets/{nome}")

    ordem_md = listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(markdown)

    def _append(
        saida: list[tuple[float, str]],
        visto: set[str],
        par: tuple[float, str],
    ) -> None:
        nome = par[1].strip().replace("\\", "/").split("/")[-1]
        if nome not in visto:
            visto.add(nome)
            saida.append(par)

    saida: list[tuple[float, str]] = []
    visto: set[str] = set()
    for rel_md in ordem_md:
        nome = rel_md.split("/")[-1]
        if nome in nome_para_par:
            _append(saida, visto, nome_para_par[nome])

    inst = (instrucoes_revisao_humana or "").strip()
    if inst:
        for m in _RE_FIGURA_OU_IMAGEM_NUMERO_NO_TEXTO_TRANSCRIBROTHERS.finditer(inst):
            try:
                idx = int(m.group(2))
            except ValueError:
                continue
            if 1 <= idx <= len(ordem_md):
                nome = ordem_md[idx - 1].split("/")[-1]
                if nome in nome_para_par:
                    _append(saida, visto, nome_para_par[nome])
        for m in _RE_ASSETS_PNG_SOLTO_NO_TEXTO_TRANSCRIBROTHERS.finditer(inst):
            norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(m.group(0))
            if norm is None:
                continue
            nome = norm.split("/")[-1]
            if nome in nome_para_par:
                _append(saida, visto, nome_para_par[nome])
    return saida


_MAX_FRAMES_VISAO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = 5
_MIN_FRAMES_VISAO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS = 3
_MARGEM_JANELA_TEMPORAL_FRAMES_EDICAO_SECAO_SEGUNDOS = 120.0

_RE_PEDIDO_MENCIONA_IMAGEM_OU_FIGURA_TRANSCRIBROTHERS = re.compile(
    r"(?i)\b(imagem|imagens|figura|figuras|screenshot|screenshots|captura|print|tela|"
    r"inclu[a-z]*|adicione|adicione|coloque|mostre|ilustr)\b",
)


def _catalogo_json_frames_extraidos_disponiveis_transcribrothers(
    rels_completos_com_tempos: list[tuple[float, str]],
) -> list[dict[str, object]]:
    ordenados = sorted(rels_completos_com_tempos, key=lambda par: float(par[0]))
    return [
        {
            "indice_catalogo": i + 1,
            "t_segundos": float(t),
            "arquivo_relativo_markdown": rel,
        }
        for i, (t, rel) in enumerate(ordenados)
    ]


def _janela_temporal_segundos_para_escopo_edicao_secao_transcribrothers(
    timestamps_escopo_segundos: list[float],
    rels_completos_com_tempos: list[tuple[float, str]],
) -> tuple[float, float] | None:
    if timestamps_escopo_segundos:
        return (
            min(timestamps_escopo_segundos) - _MARGEM_JANELA_TEMPORAL_FRAMES_EDICAO_SECAO_SEGUNDOS,
            max(timestamps_escopo_segundos) + _MARGEM_JANELA_TEMPORAL_FRAMES_EDICAO_SECAO_SEGUNDOS,
        )
    if rels_completos_com_tempos:
        tempos = [float(t) for t, _ in rels_completos_com_tempos]
        return (min(tempos), max(tempos))
    return None


def _centro_temporal_escopo_edicao_secao_transcribrothers(
    timestamps_escopo_segundos: list[float],
    rels_completos_com_tempos: list[tuple[float, str]],
) -> float:
    if timestamps_escopo_segundos:
        return sum(timestamps_escopo_segundos) / len(timestamps_escopo_segundos)
    if rels_completos_com_tempos:
        return float(rels_completos_com_tempos[len(rels_completos_com_tempos) // 2][0])
    return 0.0


def _distancia_segundos_frame_a_timestamps_escopo_edicao_secao_transcribrothers(
    t_segundos: float,
    timestamps_escopo_segundos: list[float],
    *,
    centro_fallback: float,
) -> float:
    if timestamps_escopo_segundos:
        return min(abs(t_segundos - ts) for ts in timestamps_escopo_segundos)
    return abs(t_segundos - centro_fallback)


def _nome_arquivo_png_relativo_transcribrothers(rel: str) -> str:
    return rel.strip().replace("\\", "/").split("/")[-1]


def montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
    *,
    markdown_tutorial_completo: str,
    markdown_escopo_edicao: str,
    instrucoes_revisor: str,
    rels_completos_com_tempos: list[tuple[float, str]],
    timestamps_escopo_segundos: list[float] | None = None,
    max_frames_visao: int = _MAX_FRAMES_VISAO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    min_frames_visao_quando_pedido_imagem: int = _MIN_FRAMES_VISAO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    margem_janela_temporal_segundos: float = _MARGEM_JANELA_TEMPORAL_FRAMES_EDICAO_SECAO_SEGUNDOS,
) -> tuple[list[tuple[float, str]], list[dict[str, object]]]:
    """Catálogo textual de todos os frames do job + 3–5 candidatos anexados com visão ao LiteLLM."""
    catalogo = _catalogo_json_frames_extraidos_disponiveis_transcribrothers(rels_completos_com_tempos)
    if not rels_completos_com_tempos:
        return [], catalogo

    ts_escopo = list(timestamps_escopo_segundos or [])
    if not ts_escopo:
        ts_escopo = extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers(
            markdown_escopo_edicao
        )

    limite_visao = max(1, int(max_frames_visao))
    alvo_min_imagem = max(1, min(int(min_frames_visao_quando_pedido_imagem), limite_visao))

    visao: list[tuple[float, str]] = []
    visto: set[str] = set()

    def _anexar(par: tuple[float, str]) -> bool:
        nome = _nome_arquivo_png_relativo_transcribrothers(par[1])
        if not nome or nome in visto or len(visao) >= limite_visao:
            return False
        visto.add(nome)
        visao.append((float(par[0]), par[1]))
        return True

    centro = _centro_temporal_escopo_edicao_secao_transcribrothers(ts_escopo, rels_completos_com_tempos)

    def _distancia(par: tuple[float, str]) -> float:
        return _distancia_segundos_frame_a_timestamps_escopo_edicao_secao_transcribrothers(
            float(par[0]),
            ts_escopo,
            centro_fallback=centro,
        )

    md_completo = (markdown_tutorial_completo or "").strip() or markdown_escopo_edicao
    for par in montar_rels_png_anexo_regeneracao_tutorial_markdown_mais_instrucoes_revisor_transcribrothers(
        markdown=md_completo,
        instrucoes_revisao_humana=instrucoes_revisor,
        rels_completos_com_tempos=rels_completos_com_tempos,
    ):
        _anexar(par)

    for par in montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers(
        markdown=markdown_escopo_edicao,
        rels_completos_com_tempos=rels_completos_com_tempos,
    ):
        _anexar(par)

    janela = _janela_temporal_segundos_para_escopo_edicao_secao_transcribrothers(
        ts_escopo, rels_completos_com_tempos
    )
    if janela is not None:
        tmin, tmax = janela
        pool_janela = [
            (float(t), rel)
            for t, rel in rels_completos_com_tempos
            if tmin <= float(t) <= tmax
        ]
    else:
        pool_janela = [(float(t), rel) for t, rel in rels_completos_com_tempos]

    candidatos_janela = sorted(
        [par for par in pool_janela if _nome_arquivo_png_relativo_transcribrothers(par[1]) not in visto],
        key=_distancia,
    )
    for par in candidatos_janela:
        if len(visao) >= limite_visao:
            break
        _anexar(par)

    pedido_cita_imagem = bool(_RE_PEDIDO_MENCIONA_IMAGEM_OU_FIGURA_TRANSCRIBROTHERS.search(instrucoes_revisor or ""))
    if pedido_cita_imagem:
        alvo = min(alvo_min_imagem, limite_visao, len(rels_completos_com_tempos))
        if len(visao) < alvo:
            for par in sorted(rels_completos_com_tempos, key=_distancia):
                if len(visao) >= alvo:
                    break
                _anexar((float(par[0]), par[1]))

    if not visao:
        for par in sorted(rels_completos_com_tempos, key=_distancia)[:limite_visao]:
            _anexar((float(par[0]), par[1]))

    return visao[:limite_visao], catalogo


def extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers(
    markdown: str,
) -> list[float]:
    """Extrai segundos de links `?t=` no Markdown (reutilizado na edição por seção)."""
    out: list[float] = []
    for m in re.finditer(r"\?t=(\d+(?:\.\d+)?)", markdown or ""):
        try:
            out.append(float(m.group(1)))
        except ValueError:
            continue
    return out


def montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers(
    *,
    markdown: str,
    rels_completos_com_tempos: list[tuple[float, str]],
) -> list[tuple[float, str]]:
    """Junta ordem do Markdown com `t_segundos` do snapshot quando o nome do ficheiro coincide."""
    ordem_paths = listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(
        markdown
    )
    if not ordem_paths:
        return []
    nome_para_par: dict[str, tuple[float, str]] = {}
    for t, rel in rels_completos_com_tempos:
        nome = rel.strip().replace("\\", "/").split("/")[-1]
        if nome:
            nome_para_par[nome] = (float(t), rel if rel.startswith("assets/") else f"assets/{nome}")
    saida: list[tuple[float, str]] = []
    for rel_md in ordem_paths:
        nome = rel_md.split("/")[-1]
        if nome in nome_para_par:
            saida.append(nome_para_par[nome])
    return saida
