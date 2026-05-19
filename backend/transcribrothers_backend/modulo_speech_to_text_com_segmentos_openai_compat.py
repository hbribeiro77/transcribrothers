from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

import httpx
from openai import AsyncOpenAI


@dataclass(frozen=True)
class SegmentoTranscricaoComTempo:
    inicio_segundos: float
    fim_segundos: float
    texto: str


@dataclass(frozen=True)
class ResultadoTranscricaoComSegmentos:
    texto_completo: str
    segmentos: list[SegmentoTranscricaoComTempo]
    idioma_detectado: str | None


@runtime_checkable
class TranscriberComSegmentos(Protocol):
    async def transcrever_arquivo_audio_com_segmentos(
        self,
        caminho_audio: Path,
    ) -> ResultadoTranscricaoComSegmentos: ...


class TranscriberOpenAIWhisperComSegmentos:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        model: str = "whisper-1",
        httpx_verify: bool | str = True,
    ) -> None:
        if not api_key:
            raise ValueError("Chave API é obrigatória para transcrição (Whisper).")
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        if httpx_verify is not True:
            kwargs["http_client"] = httpx.AsyncClient(
                verify=httpx_verify,
                timeout=httpx.Timeout(600.0, connect=60.0),
            )
        self._client = AsyncOpenAI(**kwargs)
        self._model = model

    async def transcrever_arquivo_audio_com_segmentos(
        self,
        caminho_audio: Path,
    ) -> ResultadoTranscricaoComSegmentos:
        with caminho_audio.open("rb") as f:
            tr = await self._client.audio.transcriptions.create(
                file=f,
                model=self._model,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
        texto = getattr(tr, "text", None) or ""
        idioma = getattr(tr, "language", None)
        segmentos_raw = getattr(tr, "segments", None) or []
        segmentos: list[SegmentoTranscricaoComTempo] = []
        for s in segmentos_raw:
            start = float(getattr(s, "start", 0.0) or 0.0)
            end = float(getattr(s, "end", start) or start)
            st = str(getattr(s, "text", "") or "").strip()
            if st:
                segmentos.append(
                    SegmentoTranscricaoComTempo(
                        inicio_segundos=start,
                        fim_segundos=end,
                        texto=st,
                    )
                )
        if not segmentos and texto.strip():
            segmentos.append(
                SegmentoTranscricaoComTempo(
                    inicio_segundos=0.0,
                    fim_segundos=0.0,
                    texto=texto.strip(),
                )
            )
        return ResultadoTranscricaoComSegmentos(
            texto_completo=texto,
            segmentos=segmentos,
            idioma_detectado=idioma,
        )
