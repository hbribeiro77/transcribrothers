"""Nome amigável no Content-Disposition do MP4 narrado (sem path traversal)."""

from __future__ import annotations

CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TITULO_ARQUIVO_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_titulo_arquivo"
)

_CARACTERES_PROIBIDOS_NOME_ARQUIVO_DOWNLOAD = set('<>:"/\\|?*')


def sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
    nome: str | None,
    *,
    fallback: str = "video_narrado.mp4",
) -> str:
    bruto = str(nome or "").replace("\\", "/").strip()
    bruto = bruto.rsplit("/", 1)[-1].strip()
    if bruto in {".", ".."}:
        return fallback
    limpo_chars: list[str] = []
    for ch in bruto:
        if ch < " " or ch in _CARACTERES_PROIBIDOS_NOME_ARQUIVO_DOWNLOAD:
            continue
        limpo_chars.append(ch)
    limpo = " ".join("".join(limpo_chars).split()).strip(" .")
    if not limpo:
        return fallback
    if not limpo.lower().endswith(".mp4"):
        limpo = f"{limpo}.mp4"
    if len(limpo) > 180:
        limpo = f"{limpo[:-4][:176].rstrip(' .')}.mp4"
    return limpo


def resolver_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
    *,
    nome_arquivo_query: str | None,
    titulo_persistido: str | None,
    legendado: bool,
    fallback: str,
) -> str:
    query = (nome_arquivo_query or "").strip()
    if query:
        return sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            query,
            fallback=fallback,
        )
    titulo = (titulo_persistido or "").strip()
    if titulo:
        sufixo = " legendado.mp4" if legendado else ".mp4"
        return sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            f"{titulo}{sufixo}",
            fallback=fallback,
        )
    return fallback
