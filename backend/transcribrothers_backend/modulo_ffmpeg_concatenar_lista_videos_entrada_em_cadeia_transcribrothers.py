"""Concatena N vídeos de entrada: um stream copy se todos compatíveis, senão cadeia par a par."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers import (
    ResultadoConcatenacaoVideosEntradaTranscribrothers,
    concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers,
    obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers,
    perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
    executar_ffmpeg_com_argumentos,
)

_logger = logging.getLogger("transcribrothers.concat_lista_video_entrada")


def _escrever_lista_concat_demuxer(caminhos: list[Path], lista_txt: Path) -> None:
    linhas = []
    for p in caminhos:
        caminho_esc = str(p.resolve()).replace("\\", "/").replace("'", r"'\''")
        linhas.append(f"file '{caminho_esc}'")
    lista_txt.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")


async def _tentar_concat_n_stream_copy_transcribrothers(
    *,
    caminhos_videos: list[Path],
    caminho_saida: Path,
) -> bool:
    with tempfile.TemporaryDirectory(prefix="tb_concat_n_copy_") as tmp:
        lista = Path(tmp) / "lista_concat_n.txt"
        _escrever_lista_concat_demuxer(caminhos_videos, lista)
        args = [
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista),
            "-c",
            "copy",
            str(caminho_saida),
        ]
        await executar_ffmpeg_com_argumentos(args)
    return caminho_saida.is_file() and caminho_saida.stat().st_size > 0


async def concatenar_lista_videos_entrada_em_cadeia_via_ffmpeg_transcribrothers(
    *,
    caminhos_videos: list[Path],
    caminho_saida: Path,
) -> ResultadoConcatenacaoVideosEntradaTranscribrothers:
    if len(caminhos_videos) < 2:
        raise ValueError("É preciso ao menos dois vídeos para concatenar em cadeia.")
    for p in caminhos_videos:
        if not p.is_file():
            raise FileNotFoundError(f"Vídeo não encontrado: {p}")

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_saida.exists():
        caminho_saida.unlink()

    perfis = []
    for p in caminhos_videos:
        perfil = await obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers(p)
        perfis.append(perfil)

    mesma_ext = len({p.suffix.lower() for p in caminhos_videos}) == 1
    todos_compativeis = mesma_ext and all(p is not None for p in perfis)
    if todos_compativeis:
        assert perfis[0] is not None
        for outro in perfis[1:]:
            assert outro is not None
            if not perfis_streams_sao_compativeis_para_concat_stream_copy_transcribrothers(perfis[0], outro):
                todos_compativeis = False
                break

    if todos_compativeis:
        try:
            ok = await _tentar_concat_n_stream_copy_transcribrothers(
                caminhos_videos=caminhos_videos,
                caminho_saida=caminho_saida,
            )
            if ok:
                _logger.info(
                    "concat lista video_entrada modo=stream_copy n=%s saida=%s",
                    len(caminhos_videos),
                    caminho_saida.name,
                )
                return ResultadoConcatenacaoVideosEntradaTranscribrothers(
                    caminho_saida=caminho_saida,
                    modo="stream_copy",
                )
        except ErroFfmpegTranscribrothers as exc:
            _logger.warning("stream_copy N-vias falhou; cadeia par a par. erro=%s", exc)
            caminho_saida.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="tb_concat_cadeia_") as tmp:
        dir_tmp = Path(tmp)
        atual = caminhos_videos[0]
        modo_agregado: str = "stream_copy"
        for i, proximo in enumerate(caminhos_videos[1:]):
            parcial = dir_tmp / f"parcial_{i}{atual.suffix.lower() or '.mp4'}"
            resultado = await concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(
                caminho_video_a=atual,
                caminho_video_b=proximo,
                caminho_saida=parcial,
            )
            if resultado.modo == "reencode":
                modo_agregado = "reencode"
            atual = resultado.caminho_saida

        if caminho_saida.exists():
            caminho_saida.unlink()
        # Copia o parcial final para a saída pedida (pode mudar extensão no reencode).
        saida_efetiva = (
            caminho_saida
            if atual.suffix.lower() == caminho_saida.suffix.lower()
            else caminho_saida.with_suffix(atual.suffix.lower() or ".mp4")
        )
        if saida_efetiva.exists() and saida_efetiva.resolve() != atual.resolve():
            saida_efetiva.unlink()
        # shutil via read/write — Path.replace pode cruzar volumes; copy bytes simples:
        saida_efetiva.write_bytes(atual.read_bytes())
        _logger.info(
            "concat lista video_entrada modo=%s n=%s saida=%s",
            modo_agregado,
            len(caminhos_videos),
            saida_efetiva.name,
        )
        return ResultadoConcatenacaoVideosEntradaTranscribrothers(
            caminho_saida=saida_efetiva,
            modo="stream_copy" if modo_agregado == "stream_copy" else "reencode",
        )
