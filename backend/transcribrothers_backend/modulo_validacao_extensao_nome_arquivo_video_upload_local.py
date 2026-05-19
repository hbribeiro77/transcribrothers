from __future__ import annotations

from pathlib import PurePath

EXTENSOES_VIDEO_PERMITIDAS_PARA_UPLOAD_LOCAL = frozenset(
    {".mp4", ".webm", ".mov", ".mkv", ".mpeg", ".mpg", ".avi", ".m4v"}
)


class ErroExtensaoVideoUploadTranscribrothers(ValueError):
    pass


def extrair_extensao_video_sanitizada_para_upload_local(nome_original: str) -> str:
    suf = PurePath(nome_original or "").suffix.lower()
    if not suf or suf not in EXTENSOES_VIDEO_PERMITIDAS_PARA_UPLOAD_LOCAL:
        raise ErroExtensaoVideoUploadTranscribrothers(
            "Extensão não permitida. Use um arquivo de vídeo comum "
            f"({', '.join(sorted(EXTENSOES_VIDEO_PERMITIDAS_PARA_UPLOAD_LOCAL))})."
        )
    return suf
