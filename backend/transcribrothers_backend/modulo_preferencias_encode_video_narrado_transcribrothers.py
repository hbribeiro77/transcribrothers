"""Preferências de encode do vídeo narrado: resolução alvo + FPS (aplicadas no mux)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ResolucaoEncodeVideoNarradoTranscribrothers = Literal[
    "original",
    "1080p",
    "720p",
    "480p",
]

RESOLUCOES_ENCODE_VIDEO_NARRADO_VALIDAS_TRANSCRIBROTHERS: tuple[
    ResolucaoEncodeVideoNarradoTranscribrothers, ...
] = ("original", "1080p", "720p", "480p")

# Altura máxima por preset (não faz upscale se a fonte for menor).
_ALTURA_MAXIMA_POR_RESOLUCAO: dict[ResolucaoEncodeVideoNarradoTranscribrothers, int | None] = {
    "original": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
}

FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS = 30
RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS: ResolucaoEncodeVideoNarradoTranscribrothers = (
    "1080p"
)


@dataclass(frozen=True, slots=True)
class PreferenciasEncodeVideoNarradoTranscribrothers:
    resolucao: ResolucaoEncodeVideoNarradoTranscribrothers = (
        RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS
    )
    fps: int = FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS

    def chave_cache_transcribrothers(self) -> str:
        return f"{self.resolucao}|fps={int(self.fps)}"


def preferencias_encode_video_narrado_padrao_transcribrothers() -> (
    PreferenciasEncodeVideoNarradoTranscribrothers
):
    return PreferenciasEncodeVideoNarradoTranscribrothers()


def normalizar_resolucao_encode_video_narrado_transcribrothers(
    valor: object,
) -> ResolucaoEncodeVideoNarradoTranscribrothers:
    s = str(valor or "").strip().lower()
    if s in RESOLUCOES_ENCODE_VIDEO_NARRADO_VALIDAS_TRANSCRIBROTHERS:
        return s  # type: ignore[return-value]
    raise ValueError(
        "Resolução de encode inválida. Use: original, 1080p, 720p ou 480p."
    )


def normalizar_fps_encode_video_narrado_transcribrothers(valor: object) -> int:
    try:
        n = int(valor)  # type: ignore[arg-type]
    except (TypeError, ValueError) as e:
        raise ValueError("FPS de encode inválido.") from e
    if n < 1 or n > 120:
        raise ValueError("FPS de encode deve estar entre 1 e 120.")
    return n


def montar_preferencias_encode_video_narrado_transcribrothers(
    *,
    resolucao: object = RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
    fps: object = FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
) -> PreferenciasEncodeVideoNarradoTranscribrothers:
    return PreferenciasEncodeVideoNarradoTranscribrothers(
        resolucao=normalizar_resolucao_encode_video_narrado_transcribrothers(resolucao),
        fps=normalizar_fps_encode_video_narrado_transcribrothers(fps),
    )


def montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(
    prefs: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    """
    Fragmento de filtro ffmpeg (sem colchetes): scale (+altura máx.) + fps + yuv420p.
    Não faz upscale: se ih <= alvo, só garante dimensões pares.
    """
    p = prefs or preferencias_encode_video_narrado_padrao_transcribrothers()
    altura = _ALTURA_MAXIMA_POR_RESOLUCAO.get(p.resolucao)
    if altura is None:
        scale = "scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=fast_bilinear"
    else:
        # min(altura_alvo, ih) e largura par proporcional; sem upscale.
        scale = (
            f"scale=w=trunc(iw*min(1\\,{altura}/ih)/2)*2:"
            f"h=trunc(min(ih\\,{altura})/2)*2:flags=fast_bilinear"
        )
    fps = max(1, int(p.fps))
    return f"{scale},fps={fps},format=yuv420p"
