"""Monta Markdown, transcrição e catálogo de frames para o contexto do chat Ask."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
)

LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS = 95_000
LIMITE_CARACTERES_TRANSCRICAO_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS = 8_000

_RECORTE_INICIAL_MARKDOWN_LONGO_CHAT_ASK_TRANSCRIBROTHERS = 4_000
_RECORTE_INICIAL_TEXTO_TRANSCRICAO_LONGA_CHAT_ASK_TRANSCRIBROTHERS = 4_000

_RE_OFFSET_MS_NOME_PNG_CHAT_ASK_TRANSCRIBROTHERS = re.compile(r"offset_ms_(\d+)", re.IGNORECASE)
_RE_TOKEN_PERGUNTA_CHAT_ASK_TRANSCRIBROTHERS = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True)
class FrameCatalogoChatAskTranscribrothers:
    caminho_relativo: str
    instante_segundos: float


@dataclass(frozen=True)
class ContextoChatAskDocumentoJobTranscribrothers:
    markdown_para_prompt: str
    transcricao_para_prompt: str
    catalogo_frames: list[FrameCatalogoChatAskTranscribrothers]
    tem_markdown: bool
    tem_transcricao: bool


def instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers(nome: str) -> float | None:
    m = _RE_OFFSET_MS_NOME_PNG_CHAT_ASK_TRANSCRIBROTHERS.search(nome or "")
    if not m:
        return None
    return int(m.group(1)) / 1000.0


def _tokens_pergunta_chat_ask_transcribrothers(pergunta: str) -> list[str]:
    return [
        t.casefold()
        for t in _RE_TOKEN_PERGUNTA_CHAT_ASK_TRANSCRIBROTHERS.findall(pergunta or "")
        if len(t) >= 4
    ]


def _instante_de_caminho_png_chat_ask_transcribrothers(caminho_relativo: str) -> float | None:
    return instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers(Path(caminho_relativo).name)


def montar_catalogo_frames_chat_ask_transcribrothers(
    *,
    caminhos_frames_rel_job: list[tuple[float, str]],
    steps_json: dict | None,
) -> list[FrameCatalogoChatAskTranscribrothers]:
    por_caminho: dict[str, list[float]] = {}

    def _registrar(caminho: str, instante: float) -> None:
        rel = (caminho or "").strip().replace("\\", "/")
        if not rel:
            return
        por_caminho.setdefault(rel, []).append(float(instante))

    for instante, caminho in caminhos_frames_rel_job or []:
        _registrar(caminho, instante)
        off = _instante_de_caminho_png_chat_ask_transcribrothers(caminho)
        if off is not None:
            _registrar(caminho, off)

    for reg in listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(steps_json):
        caminho = reg.get("caminho_relativo")
        if not isinstance(caminho, str) or not caminho.strip():
            continue
        ts = reg.get("timestamp_segundos_efetivo")
        if isinstance(ts, (int, float)):
            _registrar(caminho, float(ts))
        off = _instante_de_caminho_png_chat_ask_transcribrothers(caminho)
        if off is not None:
            _registrar(caminho, off)

    saida: list[FrameCatalogoChatAskTranscribrothers] = []
    for caminho in sorted(por_caminho.keys()):
        instantes = por_caminho[caminho]
        escolhido = min(instantes, key=lambda t: abs(t))
        saida.append(
            FrameCatalogoChatAskTranscribrothers(
                caminho_relativo=caminho,
                instante_segundos=escolhido,
            )
        )
    return saida


def _montar_markdown_para_prompt_chat_ask_transcribrothers(markdown: str, pergunta: str) -> str:
    md = markdown or ""
    if len(md) <= LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS:
        return md

    tokens = _tokens_pergunta_chat_ask_transcribrothers(pergunta)
    secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)

    linhas_indice = ["## Índice de seções", ""]
    for sec in secoes:
        linhas_indice.append(sec.linha_heading)
    indice = "\n".join(linhas_indice).rstrip() + "\n\n"

    prefixo = md[:_RECORTE_INICIAL_MARKDOWN_LONGO_CHAT_ASK_TRANSCRIBROTHERS]

    blocos_secao: list[str] = []
    for sec in secoes:
        corpo = extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers(md, sec)
        haystack = (sec.linha_heading + "\n" + corpo).casefold()
        if not tokens or not any(tok in haystack for tok in tokens):
            continue
        blocos_secao.append(corpo.rstrip())

    partes = [indice, prefixo]
    if blocos_secao:
        partes.append("\n\n".join(blocos_secao))
    return "\n\n".join(p for p in partes if p)


def _formatar_segmento_transcricao_chat_ask_transcribrothers(seg: SegmentoTranscricaoComTempo) -> str:
    return f"[{seg.inicio_segundos:.3f}-{seg.fim_segundos:.3f}] {seg.texto}"


def _montar_transcricao_para_prompt_chat_ask_transcribrothers(
    transcricao: ResultadoTranscricaoComSegmentos | None,
    pergunta: str,
) -> tuple[str, bool]:
    if transcricao is None:
        return "", False
    texto = transcricao.texto_completo or ""
    if not texto.strip() and not transcricao.segmentos:
        return "", False

    if len(texto) <= LIMITE_CARACTERES_TRANSCRICAO_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS:
        return texto, True

    tokens = _tokens_pergunta_chat_ask_transcribrothers(pergunta)
    prefixo = texto[:_RECORTE_INICIAL_TEXTO_TRANSCRICAO_LONGA_CHAT_ASK_TRANSCRIBROTHERS]

    linhas_segmentos: list[str] = []
    for seg in transcricao.segmentos:
        if not tokens or not any(tok in (seg.texto or "").casefold() for tok in tokens):
            continue
        linhas_segmentos.append(_formatar_segmento_transcricao_chat_ask_transcribrothers(seg))

    partes = [prefixo]
    if linhas_segmentos:
        partes.append("\n".join(linhas_segmentos))
    return "\n\n".join(p for p in partes if p), True


def montar_contexto_chat_ask_documento_job_transcribrothers(
    *,
    markdown: str,
    transcricao: ResultadoTranscricaoComSegmentos | None,
    pergunta: str,
    caminhos_frames_rel_job: list[tuple[float, str]],
    steps_json: dict | None,
) -> ContextoChatAskDocumentoJobTranscribrothers:
    md = markdown or ""
    tem_markdown = bool(md.strip())
    markdown_prompt = _montar_markdown_para_prompt_chat_ask_transcribrothers(md, pergunta) if tem_markdown else ""
    transcricao_prompt, tem_transcricao = _montar_transcricao_para_prompt_chat_ask_transcribrothers(
        transcricao, pergunta
    )
    catalogo = montar_catalogo_frames_chat_ask_transcribrothers(
        caminhos_frames_rel_job=caminhos_frames_rel_job,
        steps_json=steps_json,
    )
    return ContextoChatAskDocumentoJobTranscribrothers(
        markdown_para_prompt=markdown_prompt,
        transcricao_para_prompt=transcricao_prompt,
        catalogo_frames=catalogo,
        tem_markdown=tem_markdown,
        tem_transcricao=tem_transcricao,
    )
