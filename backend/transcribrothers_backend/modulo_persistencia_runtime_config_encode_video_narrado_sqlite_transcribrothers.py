"""Persistência em SQLite: preferências de encode do vídeo narrado (resolução + FPS)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
    RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
    PreferenciasEncodeVideoNarradoTranscribrothers,
    montar_preferencias_encode_video_narrado_transcribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)

CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_RESOLUCAO = "encode_video_narrado_resolucao"
CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_FPS = "encode_video_narrado_fps"


async def obter_overrides_encode_video_narrado_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> dict[str, str]:
    out: dict[str, str] = {}
    for chave in (
        CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_RESOLUCAO,
        CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_FPS,
    ):
        row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
        if row is not None and (row.valor or "").strip():
            out[chave] = row.valor.strip()
    return out


async def resolver_preferencias_encode_video_narrado_efetivas_transcribrothers(
    session: AsyncSession,
) -> tuple[PreferenciasEncodeVideoNarradoTranscribrothers, bool]:
    """
    Devolve (prefs efetivas, existe_preferencia_sqlite).
    Sem override válido na base → padrão do app (1080p @ 30 fps).
    """
    ov = await obter_overrides_encode_video_narrado_do_sqlite_transcribrothers(session)
    if not ov:
        return preferencias_encode_video_narrado_padrao_transcribrothers(), False
    try:
        prefs = montar_preferencias_encode_video_narrado_transcribrothers(
            resolucao=ov.get(
                CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_RESOLUCAO,
                RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
            ),
            fps=ov.get(
                CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_FPS,
                str(FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS),
            ),
        )
    except ValueError:
        return preferencias_encode_video_narrado_padrao_transcribrothers(), False
    return prefs, True


async def gravar_preferencias_encode_video_narrado_runtime_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    resolucao: str,
    fps: int,
) -> PreferenciasEncodeVideoNarradoTranscribrothers:
    prefs = montar_preferencias_encode_video_narrado_transcribrothers(
        resolucao=resolucao,
        fps=fps,
    )
    agora = datetime.now(timezone.utc)
    pares = (
        (CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_RESOLUCAO, prefs.resolucao),
        (CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_FPS, str(int(prefs.fps))),
    )
    for chave, valor in pares:
        row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
        if row is None:
            session.add(
                RegistroRuntimeConfigValorTranscribrothers(
                    chave=chave, valor=valor, updated_at=agora
                )
            )
        else:
            row.valor = valor
            row.updated_at = agora
    await session.commit()
    return prefs


async def apagar_override_encode_video_narrado_runtime_sqlite_transcribrothers(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(RegistroRuntimeConfigValorTranscribrothers).where(
            RegistroRuntimeConfigValorTranscribrothers.chave.in_(
                [
                    CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_RESOLUCAO,
                    CHAVE_RUNTIME_ENCODE_VIDEO_NARRADO_FPS,
                ]
            )
        )
    )
    await session.commit()


async def carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers(
    session_factory: object,
) -> PreferenciasEncodeVideoNarradoTranscribrothers:
    """Convenience para pipelines em background (abre sessão, resolve, fecha)."""
    async with session_factory() as session:  # type: ignore[misc]
        prefs, _ = await resolver_preferencias_encode_video_narrado_efetivas_transcribrothers(
            session
        )
    return prefs
