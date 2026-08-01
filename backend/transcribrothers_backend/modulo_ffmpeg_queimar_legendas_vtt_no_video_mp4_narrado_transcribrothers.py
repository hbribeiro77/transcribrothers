"""Queima (burn-in) legendas WebVTT no MP4 narrado — reencode sob demanda para download."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    executar_ffmpeg_com_argumentos,
    executar_ffmpeg_com_argumentos_e_progresso_percentual_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    _argumentos_encoder_video_transcribrothers,
    resolver_encoder_video_montagem_narrado_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
    montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)
from transcribrothers_backend.modulo_util_converter_webvtt_em_arquivo_ass_legendas_queimadas_playres_1080_transcribrothers import (
    gravar_arquivo_ass_a_partir_webvtt_legendas_queimadas_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)

# Sufixo _v3: ASS com PlayRes + scale antes da queima (invalida cache v2/force_style).
NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS = (
    "video_com_narracao_tts_com_legendas_queimadas_v3.mp4"
)
# Encode escreve aqui e só promove para o nome final no fim (evita download incompleto).
NOME_ARQUIVO_MP4_TEMPORARIO_QUEIMA_LEGENDAS_TRANSCRIBROTHERS = (
    "_video_com_narracao_tts_com_legendas_queimadas_em_encode_transcribrothers.mp4"
)
# Nome ASCII simples no cwd do ffmpeg — evita escape de drive letter no Windows.
NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS = (
    "_legendas_para_queimar_temporario_transcribrothers.ass"
)
# Mantido para testes/legado de escape de path (VTT antigo).
NOME_ARQUIVO_VTT_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS = (
    "_legendas_para_queimar_temporario_transcribrothers.vtt"
)


def escapar_texto_caminho_posix_para_filtro_subtitles_ffmpeg_transcribrothers(texto_posix: str) -> str:
    """
    Escapa caminho POSIX para `-vf subtitles=` / `ass=`.
    No Windows, o ':' do drive precisa de barra dupla no argv (`D\\\\:/...`).
    """
    texto = texto_posix.replace("\\", "/")
    if len(texto) >= 2 and texto[1] == ":":
        texto = f"{texto[0]}\\\\:{texto[2:]}"
    else:
        texto = texto.replace(":", "\\:")
    texto = texto.replace("'", "\\'")
    texto = texto.replace("[", "\\[")
    texto = texto.replace("]", "\\]")
    texto = texto.replace(",", "\\,")
    texto = texto.replace(";", "\\;")
    return texto


def escapar_caminho_para_filtro_subtitles_ffmpeg_transcribrothers(caminho: Path) -> str:
    """Escapa caminho absoluto para uso em filtro de legendas do ffmpeg."""
    return escapar_texto_caminho_posix_para_filtro_subtitles_ffmpeg_transcribrothers(
        caminho.resolve().as_posix()
    )


def video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
    *,
    caminho_video_mp4: Path,
    caminho_vtt: Path,
    caminho_saida: Path,
) -> bool:
    if not caminho_saida.is_file():
        return False
    if not caminho_video_mp4.is_file() or not caminho_vtt.is_file():
        return False
    mtime_saida = caminho_saida.stat().st_mtime
    return mtime_saida >= max(
        caminho_video_mp4.stat().st_mtime,
        caminho_vtt.stat().st_mtime,
    )


def montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers(
    caminho_ou_nome_ass: Path | str,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    """
    Monta o `-vf`: scale/fps primeiro, depois `ass=` (PlayRes do ASS = resolução do encode).
    Prefira nome relativo simples (arquivo no cwd do ffmpeg).
    """
    if isinstance(caminho_ou_nome_ass, Path):
        nome_ou_escapado = escapar_caminho_para_filtro_subtitles_ffmpeg_transcribrothers(
            caminho_ou_nome_ass
        )
    else:
        nome_ou_escapado = str(caminho_ou_nome_ass).strip()
        if not nome_ou_escapado or "/" in nome_ou_escapado or "\\" in nome_ou_escapado:
            raise ValueError(
                "Nome relativo do ASS para queima deve ser só o arquivo (sem pastas)."
            )
    prefs = preferencias_encode or preferencias_encode_video_narrado_padrao_transcribrothers()
    escala_fps = montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(prefs)
    return f"{escala_fps},ass={nome_ou_escapado}"


# Alias de compatibilidade para imports/testes antigos.
def montar_filtro_vf_subtitles_vtt_queimadas_transcribrothers(
    caminho_ou_nome_ass: Path | str,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
) -> str:
    return montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers(
        caminho_ou_nome_ass,
        preferencias_encode,
    )


async def queimar_legendas_vtt_no_video_mp4_via_ffmpeg_transcribrothers(
    *,
    caminho_video_mp4: Path,
    caminho_vtt: Path,
    caminho_saida: Path,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
    on_percentual_progresso: Callable[[float], Awaitable[None]] | None = None,
) -> Path:
    """
    Reencode o vídeo desenhando legendas nos pixels; copia o áudio AAC.
    Converte VTT → ASS (PlayRes do encode), aplica scale e só então queima com `ass=`.
    """
    if not caminho_video_mp4.is_file():
        raise FileNotFoundError(f"Arquivo de vídeo narrado não encontrado: {caminho_video_mp4}")
    if not caminho_vtt.is_file():
        raise FileNotFoundError(f"Arquivo de legendas VTT não encontrado: {caminho_vtt}")

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    diretorio_trabalho = caminho_saida.parent.resolve()
    caminho_saida_tmp = (
        diretorio_trabalho / NOME_ARQUIVO_MP4_TEMPORARIO_QUEIMA_LEGENDAS_TRANSCRIBROTHERS
    )
    if caminho_saida_tmp.is_file():
        caminho_saida_tmp.unlink()

    ass_temporario = diretorio_trabalho / NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS
    gravar_arquivo_ass_a_partir_webvtt_legendas_queimadas_transcribrothers(
        caminho_vtt,
        ass_temporario,
        preferencias=preferencias_encode,
    )

    filtro = montar_filtro_vf_ass_legendas_queimadas_apos_scale_transcribrothers(
        NOME_ARQUIVO_ASS_TEMPORARIO_PARA_QUEIMAR_TRANSCRIBROTHERS,
        preferencias_encode=preferencias_encode,
    )
    encoder = resolver_encoder_video_montagem_narrado_transcribrothers()
    duracao_entrada = 0.0
    if on_percentual_progresso is not None:
        try:
            duracao_entrada = float(await obter_duracao_video_segundos_via_ffprobe(caminho_video_mp4))
        except Exception:
            duracao_entrada = 0.0

    async def _rodar(args: list[str]) -> None:
        if on_percentual_progresso is not None and duracao_entrada > 0:
            await executar_ffmpeg_com_argumentos_e_progresso_percentual_transcribrothers(
                args,
                cwd=diretorio_trabalho,
                duracao_entrada_segundos=duracao_entrada,
                on_percentual=on_percentual_progresso,
            )
        else:
            await executar_ffmpeg_com_argumentos(args, cwd=diretorio_trabalho)

    base = [
        "-y",
        "-i",
        str(caminho_video_mp4.resolve()),
        "-vf",
        filtro,
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        *_argumentos_encoder_video_transcribrothers(encoder),
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(caminho_saida_tmp.resolve()),
    ]
    try:
        try:
            await _rodar(base)
        except Exception:
            if encoder != "h264_nvenc":
                raise
            if caminho_saida_tmp.is_file():
                caminho_saida_tmp.unlink()
            base_cpu = [
                "-y",
                "-i",
                str(caminho_video_mp4.resolve()),
                "-vf",
                filtro,
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                *_argumentos_encoder_video_transcribrothers("libx264"),
                "-c:a",
                "copy",
                "-movflags",
                "+faststart",
                str(caminho_saida_tmp.resolve()),
            ]
            await _rodar(base_cpu)

        if not caminho_saida_tmp.is_file():
            raise RuntimeError("ffmpeg concluiu sem gerar o MP4 com legendas queimadas.")
        if caminho_saida.is_file():
            caminho_saida.unlink()
        caminho_saida_tmp.replace(caminho_saida)
    finally:
        if ass_temporario.is_file():
            try:
                ass_temporario.unlink()
            except OSError:
                pass
        if caminho_saida_tmp.is_file():
            try:
                caminho_saida_tmp.unlink()
            except OSError:
                pass

    if not caminho_saida.is_file():
        raise RuntimeError("ffmpeg concluiu sem gerar o MP4 com legendas queimadas.")
    return caminho_saida


async def obter_ou_gerar_video_narrado_com_legendas_queimadas_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    diretorio_assets: Path,
    forcar_regenerar: bool = False,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
    on_percentual_progresso: Callable[[float], Awaitable[None]] | None = None,
) -> Path:
    """
    Devolve o MP4 com legendas queimadas, regenerando só se o cache estiver velho
    em relação ao MP4 narrado ou ao VTT.
    """
    caminho_video = (
        diretorio_trabalho_job / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    )
    caminho_vtt = diretorio_assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    caminho_saida = (
        diretorio_trabalho_job / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS
    )

    if not forcar_regenerar and video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
        caminho_video_mp4=caminho_video,
        caminho_vtt=caminho_vtt,
        caminho_saida=caminho_saida,
    ):
        return caminho_saida

    return await queimar_legendas_vtt_no_video_mp4_via_ffmpeg_transcribrothers(
        caminho_video_mp4=caminho_video,
        caminho_vtt=caminho_vtt,
        caminho_saida=caminho_saida,
        preferencias_encode=preferencias_encode,
        on_percentual_progresso=on_percentual_progresso,
    )
