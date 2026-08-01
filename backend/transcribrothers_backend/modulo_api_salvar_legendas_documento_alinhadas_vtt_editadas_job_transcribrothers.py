"""Valida cues editadas na UI e grava o VTT de legendas do documento no disco do job."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)


_TEXTO_PLACEHOLDER_CUE_SEM_NARRACAO_VTT = "(sem narração)"


@dataclass(frozen=True)
class CueLegendaEditadaEntradaApiTranscribrothers:
    inicio_segundos: float
    fim_segundos: float
    texto: str
    sem_narracao: bool = False
    # Só para regeneração TTS no modal; não entra no VTT.
    voz_tts: str = ""
    # Pronúncia para TTS; vazio = narrar `texto`. Não entra no VTT.
    texto_tts: str = ""
    # Força incluir a cue no TTS/promoção de prévia mesmo sem mudança de texto/voz.
    forcar_regenerar_tts: bool = False


@dataclass(frozen=True)
class ResultadoSalvarLegendasDocumentoAlinhadasVttEditadasTranscribrothers:
    nome_arquivo: str
    url_asset: str
    quantidade_cues: int
    steps_json_atualizado: dict[str, Any]


class ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(ValueError):
    """Payload de cues inválido para gravação do VTT."""


def validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(
    cues_brutas: list[Any],
) -> list[CueLegendaEditadaEntradaApiTranscribrothers]:
    if not isinstance(cues_brutas, list) or not cues_brutas:
        raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
            "Informe ao menos uma cue de legenda."
        )
    saida: list[CueLegendaEditadaEntradaApiTranscribrothers] = []
    for i, item in enumerate(cues_brutas, start=1):
        if not isinstance(item, dict):
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: formato inválido (esperado objeto)."
            )
        try:
            inicio = float(item.get("inicio_segundos"))
            fim = float(item.get("fim_segundos"))
        except (TypeError, ValueError) as exc:
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: tempos início/fim inválidos."
            ) from exc
        if not (inicio >= 0 and fim >= 0):
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: tempos não podem ser negativos."
            )
        if fim + 1e-9 < inicio:
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: fim ({fim}) é anterior ao início ({inicio})."
            )
        texto = item.get("texto")
        if not isinstance(texto, str):
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: texto deve ser string."
            )
        sem_narracao = bool(item.get("sem_narracao", False))
        voz_tts = str(item.get("voz_tts") or "").strip()
        texto_tts_bruto = item.get("texto_tts")
        if texto_tts_bruto is None:
            texto_tts_norm = ""
        elif not isinstance(texto_tts_bruto, str):
            raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                f"Cue {i}: texto_tts deve ser string."
            )
        else:
            texto_tts_norm = " ".join(
                texto_tts_bruto.replace("\r\n", "\n").replace("\r", "\n").split()
            )
        forcar_regenerar_tts = bool(item.get("forcar_regenerar_tts", False))
        texto_norm = " ".join(texto.replace("\r\n", "\n").replace("\r", "\n").split())
        if not texto_norm:
            if sem_narracao:
                texto_norm = _TEXTO_PLACEHOLDER_CUE_SEM_NARRACAO_VTT
            else:
                raise ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers(
                    f"Cue {i}: texto vazio após limpeza."
                )
        saida.append(
            CueLegendaEditadaEntradaApiTranscribrothers(
                inicio_segundos=inicio,
                fim_segundos=fim,
                texto=texto_norm,
                sem_narracao=sem_narracao,
                voz_tts=voz_tts,
                texto_tts=texto_tts_norm,
                forcar_regenerar_tts=forcar_regenerar_tts,
            )
        )
    return saida


def salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers(
    *,
    job_id: str,
    diretorio_assets: Path,
    steps_json: dict[str, Any] | None,
    cues_brutas: list[Any],
) -> ResultadoSalvarLegendasDocumentoAlinhadasVttEditadasTranscribrothers:
    cues = validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(cues_brutas)
    cues_gravacao = [
        CueLegendaAlinhadaTranscribrothers(
            texto=c.texto,
            inicio_segundos=c.inicio_segundos,
            fim_segundos=c.fim_segundos,
            casado=True,
        )
        for c in cues
    ]
    caminho = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
        diretorio_assets=diretorio_assets,
        cues=cues_gravacao,
        nome_arquivo=NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    )
    url_asset = f"/api/jobs/{job_id}/assets/{caminho.name}"
    agora = datetime.now(timezone.utc).isoformat()
    steps = dict(steps_json or {})
    blob_antigo = steps.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS)
    base: dict[str, Any] = dict(blob_antigo) if isinstance(blob_antigo, dict) else {}
    base.update(
        {
            "nome_arquivo": caminho.name,
            "url_asset": url_asset,
            "quantidade_cues": len(cues),
            "editado_em": agora,
            "timeline": base.get("timeline") or "narracao_tts",
        }
    )
    steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = base

    pipe = steps.get(CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS)
    if isinstance(pipe, dict):
        pipe_novo = dict(pipe)
        pipe_novo["nome_arquivo_vtt"] = caminho.name
        pipe_novo["url_asset_vtt"] = url_asset
        pipe_novo["quantidade_cues"] = len(cues)
        pipe_novo["legendas_editadas_em"] = agora
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = pipe_novo

    return ResultadoSalvarLegendasDocumentoAlinhadasVttEditadasTranscribrothers(
        nome_arquivo=caminho.name,
        url_asset=url_asset,
        quantidade_cues=len(cues),
        steps_json_atualizado=steps,
    )
