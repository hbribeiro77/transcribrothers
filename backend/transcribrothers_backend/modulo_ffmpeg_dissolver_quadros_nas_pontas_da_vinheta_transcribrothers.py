"""Dissolve os quadros vizinhos nas pontas da vinheta, sem encurtar o clipe."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    executar_ffmpeg_com_argumentos,
)

DURACAO_DA_DISSOLUCAO_NAS_PONTAS_SEGUNDOS = 0.3
LARGURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA = 1920
ALTURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA = 1080


def _lado_par_do_canvas_da_dissolucao(valor: int, padrao: int) -> int:
    n = int(valor) if valor and int(valor) > 0 else padrao
    n = n - (n % 2)
    return max(2, n)


def filtro_de_dissolucao_dos_quadros_nas_pontas_da_vinheta(
    duracao_segundos: float,
    *,
    tem_quadro_anterior: bool,
    tem_quadro_seguinte: bool,
    largura: int = LARGURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA,
    altura: int = ALTURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA,
) -> tuple[str, str]:
    duracao = max(0.4, float(duracao_segundos))
    dissolucao = min(DURACAO_DA_DISSOLUCAO_NAS_PONTAS_SEGUNDOS, duracao / 2)
    inicio_do_fim = max(0.0, duracao - dissolucao)
    w = _lado_par_do_canvas_da_dissolucao(largura, LARGURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA)
    h = _lado_par_do_canvas_da_dissolucao(altura, ALTURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA)
    encaixe = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    )
    cadeia = "[0:v]format=yuv420p[base]"
    saida = "base"
    indice = 1
    if tem_quadro_anterior:
        cadeia += (
            f";[{indice}:v]{encaixe},format=rgba,fade=t=out:st=0:d={dissolucao:.3f}:alpha=1[quadro_anterior]"
            f";[{saida}][quadro_anterior]overlay=0:0:format=auto[com_anterior]"
        )
        saida = "com_anterior"
        indice += 1
    if tem_quadro_seguinte:
        cadeia += (
            f";[{indice}:v]{encaixe},format=rgba,fade=t=in:st={inicio_do_fim:.3f}:d={dissolucao:.3f}:alpha=1[quadro_seguinte]"
            f";[{saida}][quadro_seguinte]overlay=0:0:format=auto[com_seguinte]"
        )
        saida = "com_seguinte"
    return cadeia, saida


async def aplicar_dissolucao_dos_quadros_nas_pontas_da_vinheta(
    caminho_mp4: Path,
    *,
    duracao_segundos: float,
    quadro_anterior: Path | None = None,
    quadro_seguinte: Path | None = None,
    largura: int = LARGURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA,
    altura: int = ALTURA_PADRAO_DA_DISSOLUCAO_DA_VINHETA,
) -> None:
    tem_anterior = quadro_anterior is not None and quadro_anterior.is_file()
    tem_seguinte = quadro_seguinte is not None and quadro_seguinte.is_file()
    if not tem_anterior and not tem_seguinte:
        return
    filtro, saida = filtro_de_dissolucao_dos_quadros_nas_pontas_da_vinheta(
        duracao_segundos,
        tem_quadro_anterior=tem_anterior,
        tem_quadro_seguinte=tem_seguinte,
        largura=largura,
        altura=altura,
    )
    destino = caminho_mp4.with_name(f"{caminho_mp4.stem}-com-dissolucao.mp4")
    argumentos = ["-y", "-i", str(caminho_mp4)]
    if tem_anterior:
        argumentos.extend(["-loop", "1", "-i", str(quadro_anterior)])
    if tem_seguinte:
        argumentos.extend(["-loop", "1", "-i", str(quadro_seguinte)])
    argumentos.extend(
        [
            "-filter_complex",
            filtro,
            "-map",
            f"[{saida}]",
            "-an",
            "-t",
            f"{max(0.4, float(duracao_segundos)):.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(destino),
        ]
    )
    await executar_ffmpeg_com_argumentos(argumentos)
    destino.replace(caminho_mp4)
