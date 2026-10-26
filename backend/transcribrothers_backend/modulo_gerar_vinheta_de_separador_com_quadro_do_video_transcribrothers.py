"""Gera a vinheta do separador com o quadro do vídeo e publica na biblioteca do job."""

from __future__ import annotations

import asyncio
import base64
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_cliente_api_vinhetas_para_separador_de_secao_transcribrothers import (
    baixar_mp4_renderizado_da_vinheta_com_debug,
    url_da_api_de_vinhetas,
)
from transcribrothers_backend.modulo_persistir_debug_ultima_geracao_vinheta_separador_transcribrothers import (
    gravar_debug_ultima_geracao_vinheta_separador_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    capturar_frames_png_do_video_nos_timestamps_segundos,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_biblioteca_midias_tela_job_transcribrothers import (
    alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers,
    confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
    calcular_dimensoes_pares_do_encode_video_narrado_transcribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)


def normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte(
    largura: int,
    altura: int,
) -> tuple[int, int]:
    def par(valor: int) -> int:
        n = int(valor)
        n = n - (n % 2)
        return max(2, n)

    return par(largura), par(altura)


_cache_dimensoes_do_video_fonte: dict[str, tuple[int, int]] = {}


def _chave_do_cache_de_dimensoes(origem: Path) -> str:
    try:
        stat = origem.stat()
        return f"{origem.resolve()}|{stat.st_mtime_ns}|{stat.st_size}"
    except OSError:
        return str(origem)


async def _dimensoes_do_canvas_da_vinheta_no_video_fonte(
    *origens: Path | None,
) -> tuple[int, int] | tuple[None, None]:
    for origem in origens:
        if origem is None or not origem.is_file():
            continue
        chave = _chave_do_cache_de_dimensoes(origem)
        cached = _cache_dimensoes_do_video_fonte.get(chave)
        if cached is not None:
            return cached
        perfil = await obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers(origem)
        if perfil is None:
            continue
        dimensoes = normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte(perfil.largura, perfil.altura)
        _cache_dimensoes_do_video_fonte[chave] = dimensoes
        return dimensoes
    return None, None


async def _png_do_instante(caminho_video: Path | None, instante: float | None, pasta: Path, nome: str) -> Path | None:
    if caminho_video is None or instante is None or not caminho_video.is_file():
        return None
    gerados = await capturar_frames_png_do_video_nos_timestamps_segundos(
        caminho_video=caminho_video,
        timestamps_segundos=[max(0.0, float(instante))],
        diretorio_saida_frames=pasta,
        prefixo_nome_arquivo_longo_descritivo=nome,
    )
    return gerados[0] if gerados else None


def _milissegundos_desde(inicio: float) -> int:
    return max(0, int(round((time.perf_counter() - inicio) * 1000)))


def _numero_ou_none(valor: Any) -> int | float | None:
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    return None


async def gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers(
    *,
    titulo: str,
    efeito: str | None,
    vinheta_id: str | None,
    caminho_video: Path | None,
    instante_quadro_seguinte: float | None,
    instante_quadro_anterior: float | None,
    duracao_segundos: float | None = None,
    presenca_da_imagem: int | None = None,
    cores: dict[str, str] | None = None,
    work: Path | None = None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> tuple[bytes, float]:
    with tempfile.TemporaryDirectory() as pasta_texto:
        pasta = Path(pasta_texto)
        inicio_total = time.perf_counter()
        marca = inicio_total
        quadro_seguinte, quadro_anterior = await asyncio.gather(
            _png_do_instante(caminho_video, instante_quadro_seguinte, pasta, "quadro_seguinte_da_vinheta"),
            _png_do_instante(caminho_video, instante_quadro_anterior, pasta, "quadro_anterior_da_vinheta"),
        )
        ms_capturas = _milissegundos_desde(marca)
        ms_seguinte = ms_capturas if quadro_seguinte is not None else 0
        ms_anterior = ms_capturas if quadro_anterior is not None else 0
        marca = time.perf_counter()
        largura_fonte, altura_fonte = await _dimensoes_do_canvas_da_vinheta_no_video_fonte(
            caminho_video,
            quadro_seguinte,
            quadro_anterior,
        )
        prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
        if largura_fonte is not None and altura_fonte is not None:
            largura, altura = calcular_dimensoes_pares_do_encode_video_narrado_transcribrothers(
                largura_fonte,
                altura_fonte,
                prefs,
            )
        else:
            largura, altura = None, None
        ms_dimensoes = _milissegundos_desde(marca)
        imagem_base64 = None
        if quadro_seguinte is not None:
            imagem_base64 = base64.b64encode(quadro_seguinte.read_bytes()).decode("ascii")
        imagem_anterior_base64 = None
        if quadro_anterior is not None:
            imagem_anterior_base64 = base64.b64encode(quadro_anterior.read_bytes()).decode("ascii")
        marca = time.perf_counter()
        conteudo, debug_vinhetas = await baixar_mp4_renderizado_da_vinheta_com_debug(
            titulo=titulo,
            efeito=efeito,
            vinheta_id=vinheta_id,
            imagem_de_fundo_base64=imagem_base64,
            imagem_quadro_anterior_base64=imagem_anterior_base64,
            duracao_segundos=duracao_segundos,
            presenca_da_imagem=presenca_da_imagem,
            cores=cores,
            largura=largura,
            altura=altura,
        )
        ms_render = _milissegundos_desde(marca)
        destino = pasta / "vinheta.mp4"
        destino.write_bytes(conteudo)
        if duracao_segundos and duracao_segundos > 0:
            duracao = float(duracao_segundos)
            ms_duracao = 0
        else:
            duracao = 5.0
            marca = time.perf_counter()
            try:
                medida = float(await obter_duracao_video_segundos_via_ffprobe(destino) or 0.0)
                if medida > 0:
                    duracao = medida
            except Exception:
                pass
            ms_duracao = _milissegundos_desde(marca)
        if not isinstance(debug_vinhetas, dict):
            debug_vinhetas = {}
        relatorio = {
            "gerado_em": datetime.now(timezone.utc).astimezone().isoformat(),
            "titulo": titulo,
            "efeito": efeito,
            "vinheta_id": vinheta_id,
            "largura": largura,
            "altura": altura,
            "largura_fonte": largura_fonte,
            "altura_fonte": altura_fonte,
            "resolucao_encode": prefs.resolucao,
            "duracao_pedida_segundos": duracao_segundos,
            "duracao_medida_segundos": duracao,
            "presenca_da_imagem": presenca_da_imagem,
            "tem_quadro_anterior": quadro_anterior is not None,
            "tem_quadro_seguinte": quadro_seguinte is not None,
            "bytes_mp4": len(conteudo),
            "fps": _numero_ou_none(debug_vinhetas.get("fps")),
            "quantidade_quadros": _numero_ou_none(debug_vinhetas.get("quantidade_quadros")),
            "dissolve_assada_nos_quadros": True,
            "url_api_vinhetas": url_da_api_de_vinhetas(),
            "tempos_ms": {
                "total": _milissegundos_desde(inicio_total),
                "captura_png_seguinte": ms_seguinte,
                "captura_png_anterior": ms_anterior,
                "sonda_dimensoes": ms_dimensoes,
                "render_vinhetas": ms_render,
                "sonda_duracao": ms_duracao,
                "amostragem_vite_node": _numero_ou_none(debug_vinhetas.get("amostragem_ms")),
                "desenho_pil": _numero_ou_none(debug_vinhetas.get("desenho_ms")),
                "encode_ffmpeg": _numero_ou_none(debug_vinhetas.get("encode_ms")),
            },
        }
        if work is not None:
            gravar_debug_ultima_geracao_vinheta_separador_transcribrothers(work, relatorio)
        return destino.read_bytes(), duracao


def nome_de_arquivo_da_vinheta_do_separador(titulo: str) -> str:
    bruto = re.sub(r"[^\w.\-]+", "_", (titulo or "vinheta").strip(), flags=re.UNICODE)[:40] or "vinheta"
    return f"vinheta_{bruto}.mp4"


async def publicar_vinheta_na_biblioteca_de_midias_do_job_transcribrothers(
    *,
    work: Path,
    job_id: str,
    titulo: str,
    efeito: str | None,
    vinheta_id: str | None,
    caminho_video: Path | None,
    instante_quadro_seguinte: float | None,
    instante_quadro_anterior: float | None,
    duracao_segundos: float | None = None,
    presenca_da_imagem: int | None = None,
    cores: dict[str, str] | None = None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> dict[str, object]:
    conteudo, duracao = await gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers(
        titulo=titulo,
        efeito=efeito,
        vinheta_id=vinheta_id,
        caminho_video=caminho_video,
        instante_quadro_seguinte=instante_quadro_seguinte,
        instante_quadro_anterior=instante_quadro_anterior,
        duracao_segundos=duracao_segundos,
        presenca_da_imagem=presenca_da_imagem,
        cores=cores,
        work=work,
        preferencias_encode=preferencias_encode,
    )
    item, destino = alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers(
        work=work,
        nome_original=nome_de_arquivo_da_vinheta_do_separador(titulo),
        extensao_com_ponto=".mp4",
    )
    try:
        destino.write_bytes(conteudo)
        confirmado = confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers(
            work=work,
            item=item,
            tamanho_bytes=destino.stat().st_size,
            duracao_segundos=duracao,
        )
    except Exception:
        if destino.is_file():
            destino.unlink()
        raise
    return {**confirmado.para_dict(job_id=job_id), "eh_entrada": False}
