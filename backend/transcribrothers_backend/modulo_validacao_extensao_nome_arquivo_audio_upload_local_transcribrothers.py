from __future__ import annotations

from pathlib import PurePath

EXTENSOES_AUDIO_PERMITIDAS_PARA_UPLOAD_LOCAL = frozenset(
    {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".opus"}
)


class ErroExtensaoAudioUploadTranscribrothers(ValueError):
    pass


def extrair_extensao_audio_sanitizada_para_upload_local(nome_original: str) -> str:
    suf = PurePath(nome_original or "").suffix.lower()
    if not suf or suf not in EXTENSOES_AUDIO_PERMITIDAS_PARA_UPLOAD_LOCAL:
        raise ErroExtensaoAudioUploadTranscribrothers(
            "Extensão não permitida. Use um arquivo de áudio comum "
            f"({', '.join(sorted(EXTENSOES_AUDIO_PERMITIDAS_PARA_UPLOAD_LOCAL))})."
        )
    return suf


def classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers(
    nome_original: str,
) -> str:
    """Devolve 'video' ou 'audio' conforme a extensão; ValueError se nenhuma."""
    from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_video_upload_local import (
        EXTENSOES_VIDEO_PERMITIDAS_PARA_UPLOAD_LOCAL,
        ErroExtensaoVideoUploadTranscribrothers,
        extrair_extensao_video_sanitizada_para_upload_local,
    )

    try:
        extrair_extensao_video_sanitizada_para_upload_local(nome_original)
        return "video"
    except ErroExtensaoVideoUploadTranscribrothers:
        pass
    try:
        extrair_extensao_audio_sanitizada_para_upload_local(nome_original)
        return "audio"
    except ErroExtensaoAudioUploadTranscribrothers as e:
        raise ValueError(
            "Extensão não permitida. Envie um vídeo "
            f"({', '.join(sorted(EXTENSOES_VIDEO_PERMITIDAS_PARA_UPLOAD_LOCAL))}) "
            "ou um áudio "
            f"({', '.join(sorted(EXTENSOES_AUDIO_PERMITIDAS_PARA_UPLOAD_LOCAL))})."
        ) from e
