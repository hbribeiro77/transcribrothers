"""Persiste janelas de vídeo por cue para regeneração parcial após edição do VTT."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)

NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS = (
    "manifest_cues_narracao_janelas_video.json"
)


@dataclass(frozen=True)
class ItemManifestCueNarracaoJanelaVideoTranscribrothers:
    texto: str
    inicio_video_segundos: float
    fim_video_segundos: float
    origem_ancora: str = "markdown_t"
    casado: bool = True
    sem_narracao: bool = False
    voz_tts: str = ""
    # Pronúncia para TTS; vazio = usar `texto` (legenda).
    texto_tts: str = ""


def normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto: str) -> str:
    return " ".join((texto or "").replace("\r\n", "\n").replace("\r", "\n").split())


def indices_cues_com_texto_diferente_do_manifest_transcribrothers(
    *,
    textos_manifest: list[str],
    textos_desejados: list[str],
) -> list[int]:
    if len(textos_manifest) != len(textos_desejados):
        raise ValueError(
            "Quantidade de cues do VTT não bate com o manifesto da narração "
            f"({len(textos_desejados)} != {len(textos_manifest)})."
        )
    sujos: list[int] = []
    for i, (a, b) in enumerate(zip(textos_manifest, textos_desejados, strict=True)):
        if normalizar_texto_cue_para_comparacao_narracao_transcribrothers(a) != (
            normalizar_texto_cue_para_comparacao_narracao_transcribrothers(b)
        ):
            sujos.append(i)
    return sujos


def _item_de_dict_transcribrothers(raw: dict[str, Any]) -> ItemManifestCueNarracaoJanelaVideoTranscribrothers:
    return ItemManifestCueNarracaoJanelaVideoTranscribrothers(
        texto=str(raw.get("texto") or ""),
        inicio_video_segundos=float(raw["inicio_video_segundos"]),
        fim_video_segundos=float(raw["fim_video_segundos"]),
        origem_ancora=str(raw.get("origem_ancora") or "markdown_t"),
        casado=bool(raw.get("casado", True)),
        sem_narracao=bool(raw.get("sem_narracao", False)),
        voz_tts=str(raw.get("voz_tts") or "").strip(),
        texto_tts=str(raw.get("texto_tts") or "").strip(),
    )


def gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
    *,
    work: Path,
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    payload = {
        "versao": 1,
        "quantidade_cues": len(cues),
        "cues": [
            {
                "texto": c.texto,
                "inicio_video_segundos": c.inicio_video_segundos,
                "fim_video_segundos": c.fim_video_segundos,
                "origem_ancora": c.origem_ancora,
                "casado": c.casado,
                "sem_narracao": bool(getattr(c, "sem_narracao", False)),
                "voz_tts": str(getattr(c, "voz_tts", "") or "").strip(),
                "texto_tts": str(getattr(c, "texto_tts", "") or "").strip(),
            }
            for c in cues
        ],
    }
    caminho = work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS
    caminho.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho


def carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(
    work: Path,
) -> list[ItemManifestCueNarracaoJanelaVideoTranscribrothers] | None:
    caminho = work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS
    if not caminho.is_file():
        return None
    try:
        raw = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    lista = raw.get("cues")
    if not isinstance(lista, list) or not lista:
        return None
    saida: list[ItemManifestCueNarracaoJanelaVideoTranscribrothers] = []
    for item in lista:
        if not isinstance(item, dict):
            return None
        try:
            saida.append(_item_de_dict_transcribrothers(item))
        except (KeyError, TypeError, ValueError):
            return None
    return saida


def cues_janela_a_partir_manifest_transcribrothers(
    items: list[ItemManifestCueNarracaoJanelaVideoTranscribrothers],
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    return [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=it.texto,
            inicio_video_segundos=it.inicio_video_segundos,
            fim_video_segundos=it.fim_video_segundos,
            origem_ancora=it.origem_ancora,
            casado=it.casado,
            sem_narracao=it.sem_narracao,
            voz_tts=it.voz_tts,
            texto_tts=it.texto_tts,
        )
        for it in items
    ]


def aplicar_textos_vtt_sobre_cues_janela_preservando_tempos_video_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    textos: list[str],
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    if len(cues) != len(textos):
        raise ValueError(
            "Quantidade de textos VTT não bate com as cues de janela "
            f"({len(textos)} != {len(cues)})."
        )
    return [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
            inicio_video_segundos=cue.inicio_video_segundos,
            fim_video_segundos=cue.fim_video_segundos,
            origem_ancora=cue.origem_ancora,
            casado=cue.casado,
            sem_narracao=cue.sem_narracao,
            voz_tts=cue.voz_tts,
            texto_tts=cue.texto_tts,
        )
        for cue, texto in zip(cues, textos, strict=True)
    ]


def carimbar_voz_tts_em_todas_as_cues_janela_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    voz_tts: str,
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    voz = str(voz_tts or "").strip()
    return [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=c.texto,
            inicio_video_segundos=c.inicio_video_segundos,
            fim_video_segundos=c.fim_video_segundos,
            origem_ancora=c.origem_ancora,
            casado=c.casado,
            sem_narracao=c.sem_narracao,
            voz_tts=voz,
            texto_tts=c.texto_tts,
        )
        for c in cues
    ]
