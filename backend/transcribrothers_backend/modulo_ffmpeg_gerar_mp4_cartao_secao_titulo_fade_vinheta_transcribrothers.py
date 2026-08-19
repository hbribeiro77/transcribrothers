"""Gera MP4 de cartão de seção (vinheta) com título, fade in/out via ffmpeg."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    executar_ffmpeg_com_argumentos,
)
from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    ffmpeg_disponivel_transcribrothers,
)

DURACAO_PADRAO_CARTAO_SECAO_SEGUNDOS = 3.5
FADE_PADRAO_CARTAO_SECAO_SEGUNDOS = 0.4
LARGURA_PADRAO_CARTAO_SECAO = 1920
ALTURA_PADRAO_CARTAO_SECAO = 1080
# Azul-escuro sóbrio (portal / institucional).
COR_FUNDO_CARTAO_SECAO_HEX = "0B3D5C"
COR_TEXTO_CARTAO_SECAO = "white"
COR_SUBTITULO_CARTAO_SECAO = "D6E4F0"
SUBTITULO_PADRAO_CARTAO_SECAO = "Portal da Defensoria"


def escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(caminho: Path | str) -> str:
    """Escapa path para uso em filtros ffmpeg (Windows e Unix)."""
    bruto = str(caminho).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    return bruto


def truncar_titulo_cartao_secao_transcribrothers(titulo: str, *, max_chars: int = 72) -> str:
    limpo = " ".join((titulo or "").replace("\r", " ").replace("\n", " ").split())
    if not limpo:
        return "Nova funcionalidade"
    if len(limpo) <= max_chars:
        return limpo
    return limpo[: max(1, max_chars - 1)].rstrip() + "…"


def resolver_fonte_truetype_para_drawtext_cartao_secao_transcribrothers() -> Path | None:
    candidatos = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\calibri.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for c in candidatos:
        if c.is_file():
            return c
    return None


def montar_filtro_vf_cartao_secao_drawtext_fade_transcribrothers(
    *,
    caminho_arquivo_titulo: Path,
    caminho_arquivo_subtitulo: Path | None,
    caminho_fonte: Path | None,
    duracao_segundos: float,
    fade_segundos: float,
    fontsize_titulo: int = 64,
    fontsize_subtitulo: int = 32,
) -> str:
    dur = max(0.5, float(duracao_segundos))
    fade = max(0.05, min(float(fade_segundos), dur / 2.5))
    st_out = max(0.0, dur - fade)
    titulo_esc = escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(caminho_arquivo_titulo)
    partes: list[str] = [
        f"fade=t=in:st=0:d={fade:.3f}",
        f"fade=t=out:st={st_out:.3f}:d={fade:.3f}",
    ]
    base_draw = (
        f"drawtext=textfile='{titulo_esc}':reload=0:fontsize={int(fontsize_titulo)}:"
        f"fontcolor={COR_TEXTO_CARTAO_SECAO}:borderw=2:bordercolor=black@0.35:"
        f"x=(w-text_w)/2:y=(h-text_h)/2-24"
    )
    if caminho_fonte is not None and caminho_fonte.is_file():
        font_esc = escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(caminho_fonte)
        base_draw = (
            f"drawtext=fontfile='{font_esc}':textfile='{titulo_esc}':reload=0:"
            f"fontsize={int(fontsize_titulo)}:fontcolor={COR_TEXTO_CARTAO_SECAO}:"
            f"borderw=2:bordercolor=black@0.35:x=(w-text_w)/2:y=(h-text_h)/2-24"
        )
    partes.append(base_draw)
    if caminho_arquivo_subtitulo is not None and caminho_arquivo_subtitulo.is_file():
        sub_esc = escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(
            caminho_arquivo_subtitulo
        )
        if caminho_fonte is not None and caminho_fonte.is_file():
            font_esc = escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(caminho_fonte)
            partes.append(
                f"drawtext=fontfile='{font_esc}':textfile='{sub_esc}':reload=0:"
                f"fontsize={int(fontsize_subtitulo)}:fontcolor={COR_SUBTITULO_CARTAO_SECAO}:"
                f"x=(w-text_w)/2:y=(h-text_h)/2+56"
            )
        else:
            partes.append(
                f"drawtext=textfile='{sub_esc}':reload=0:fontsize={int(fontsize_subtitulo)}:"
                f"fontcolor={COR_SUBTITULO_CARTAO_SECAO}:x=(w-text_w)/2:y=(h-text_h)/2+56"
            )
    return ",".join(partes)


def _par_dimensao_par_transcribrothers(valor: int, padrao: int) -> int:
    n = int(valor) if valor and int(valor) > 0 else padrao
    n = max(320, min(3840, n))
    if n % 2:
        n -= 1
    return max(320, n)


async def gerar_mp4_cartao_secao_titulo_com_fade_via_ffmpeg_transcribrothers(
    *,
    caminho_saida: Path,
    titulo: str,
    subtitulo: str | None = SUBTITULO_PADRAO_CARTAO_SECAO,
    duracao_segundos: float = DURACAO_PADRAO_CARTAO_SECAO_SEGUNDOS,
    fade_segundos: float = FADE_PADRAO_CARTAO_SECAO_SEGUNDOS,
    largura: int = LARGURA_PADRAO_CARTAO_SECAO,
    altura: int = ALTURA_PADRAO_CARTAO_SECAO,
    cor_fundo_hex: str = COR_FUNDO_CARTAO_SECAO_HEX,
) -> Path:
    """Gera vídeo mudo (H.264) com fundo sólido, título central e fades."""
    if not ffmpeg_disponivel_transcribrothers():
        raise ErroFfmpegTranscribrothers(
            "ffmpeg não encontrado no PATH. Instale ffmpeg e reinicie o terminal."
        )
    dur = max(0.5, float(duracao_segundos))
    fade = max(0.05, min(float(fade_segundos), dur / 2.5))
    w = _par_dimensao_par_transcribrothers(largura, LARGURA_PADRAO_CARTAO_SECAO)
    h = _par_dimensao_par_transcribrothers(altura, ALTURA_PADRAO_CARTAO_SECAO)
    titulo_limpo = truncar_titulo_cartao_secao_transcribrothers(titulo)
    sub_limpo = " ".join((subtitulo or "").split()) if subtitulo else ""
    cor = re.sub(r"[^0-9A-Fa-f]", "", cor_fundo_hex or "") or COR_FUNDO_CARTAO_SECAO_HEX
    if len(cor) not in (6, 8):
        cor = COR_FUNDO_CARTAO_SECAO_HEX

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fonte = resolver_fonte_truetype_para_drawtext_cartao_secao_transcribrothers()

    with tempfile.TemporaryDirectory(prefix="tb_cartao_secao_") as tmp:
        tmp_path = Path(tmp)
        arq_titulo = tmp_path / "titulo.txt"
        arq_titulo.write_text(titulo_limpo + "\n", encoding="utf-8")
        arq_sub: Path | None = None
        if sub_limpo:
            arq_sub = tmp_path / "subtitulo.txt"
            arq_sub.write_text(sub_limpo + "\n", encoding="utf-8")
        vf = montar_filtro_vf_cartao_secao_drawtext_fade_transcribrothers(
            caminho_arquivo_titulo=arq_titulo,
            caminho_arquivo_subtitulo=arq_sub,
            caminho_fonte=fonte,
            duracao_segundos=dur,
            fade_segundos=fade,
        )
        # fontsize relativo à altura
        if h < 720:
            vf = montar_filtro_vf_cartao_secao_drawtext_fade_transcribrothers(
                caminho_arquivo_titulo=arq_titulo,
                caminho_arquivo_subtitulo=arq_sub,
                caminho_fonte=fonte,
                duracao_segundos=dur,
                fade_segundos=fade,
                fontsize_titulo=42,
                fontsize_subtitulo=22,
            )
        args = [
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x{cor}:s={w}x{h}:d={dur:.3f}:r=30",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(caminho_saida),
        ]
        await executar_ffmpeg_com_argumentos(args)

    if not caminho_saida.is_file() or caminho_saida.stat().st_size <= 0:
        raise ErroFfmpegTranscribrothers("Cartão de seção não foi gerado (arquivo vazio).")
    return caminho_saida
