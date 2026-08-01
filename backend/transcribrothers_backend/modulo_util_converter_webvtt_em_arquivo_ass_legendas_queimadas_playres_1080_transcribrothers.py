"""
Converte WebVTT → ASS com PlayRes explícito (evita default 384×288 do libass).

Usado na queima de legendas no MP4: margens/fonte em pixels reais do encode.
"""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)
from transcribrothers_backend.modulo_util_parsear_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers import (
    parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers,
)

# (PlayResX, PlayResY, Fontsize, MarginL, MarginR, MarginV)
_METRICAS_POR_RESOLUCAO: dict[str, tuple[int, int, int, int, int, int]] = {
    "1080p": (1920, 1080, 48, 40, 40, 28),
    "720p": (1280, 720, 36, 28, 28, 22),
    "480p": (854, 480, 28, 20, 20, 16),
    "original": (1920, 1080, 48, 40, 40, 28),
}


def resolver_metricas_ass_legendas_queimadas_transcribrothers(
    preferencias: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> tuple[int, int, int, int, int, int]:
    prefs = preferencias or preferencias_encode_video_narrado_padrao_transcribrothers()
    return _METRICAS_POR_RESOLUCAO.get(
        prefs.resolucao,
        _METRICAS_POR_RESOLUCAO["1080p"],
    )


def formatar_timestamp_ass_centissegundos_transcribrothers(segundos: float) -> str:
    """Formato ASS `H:MM:SS.cc` (centésimos)."""
    total_cs = max(0, int(round(float(segundos) * 100.0)))
    h = total_cs // 360_000
    resto = total_cs % 360_000
    m = resto // 6_000
    resto = resto % 6_000
    s = resto // 100
    cs = resto % 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def escapar_texto_dialogue_ass_transcribrothers(texto: str) -> str:
    t = (texto or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    t = " ".join(t.split())
    t = t.replace("\\", "\\\\")
    t = t.replace("{", "\\{").replace("}", "\\}")
    return t


def converter_conteudo_webvtt_para_conteudo_ass_legendas_queimadas_transcribrothers(
    conteudo_vtt: str,
    *,
    preferencias: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    play_x, play_y, font_size, margin_l, margin_r, margin_v = (
        resolver_metricas_ass_legendas_queimadas_transcribrothers(preferencias)
    )
    cues = parsear_conteudo_webvtt_em_cues_texto_para_pipeline_narracao_transcribrothers(
        conteudo_vtt
    )
    linhas = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: None",
        f"PlayResX: {play_x}",
        f"PlayResY: {play_y}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        # Alignment=2 inferior centro; BorderStyle=3 caixa opaca.
        "Style: Default,Arial,"
        f"{font_size},&H00FFFFFF,&H000000FF,&H80000000,&H80000000,"
        f"0,0,0,0,100,100,0,0,3,1,0,2,{margin_l},{margin_r},{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for cue in cues:
        if cue.fim_segundos <= cue.inicio_segundos:
            continue
        texto = escapar_texto_dialogue_ass_transcribrothers(cue.texto)
        if not texto:
            continue
        inicio = formatar_timestamp_ass_centissegundos_transcribrothers(cue.inicio_segundos)
        fim = formatar_timestamp_ass_centissegundos_transcribrothers(cue.fim_segundos)
        linhas.append(f"Dialogue: 0,{inicio},{fim},Default,,0,0,0,,{texto}")
    linhas.append("")
    return "\n".join(linhas)


def gravar_arquivo_ass_a_partir_webvtt_legendas_queimadas_transcribrothers(
    caminho_vtt: Path,
    caminho_ass_saida: Path,
    *,
    preferencias: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> Path:
    conteudo_vtt = caminho_vtt.read_text(encoding="utf-8")
    ass = converter_conteudo_webvtt_para_conteudo_ass_legendas_queimadas_transcribrothers(
        conteudo_vtt,
        preferencias=preferencias,
    )
    caminho_ass_saida.parent.mkdir(parents=True, exist_ok=True)
    caminho_ass_saida.write_text(ass, encoding="utf-8")
    return caminho_ass_saida
