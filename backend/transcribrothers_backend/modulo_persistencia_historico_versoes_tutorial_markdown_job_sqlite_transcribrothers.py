from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    HistoricoVersaoTutorialMarkdownJobTranscribrothers,
)


def _criado_em_iso_utc_com_sufixo_z_para_api_transcribrothers(dt: datetime | None) -> str | None:
    """Garante sufixo de fuso (`Z`) para o front não tratar o instante como hora local sem UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    u = dt.astimezone(timezone.utc)
    s = u.isoformat(timespec="microseconds")
    return s.replace("+00:00", "Z")


async def apagar_todas_versoes_historico_tutorial_markdown_do_job_transcribrothers(
    session: AsyncSession,
    job_id: str,
) -> None:
    await session.execute(
        delete(HistoricoVersaoTutorialMarkdownJobTranscribrothers).where(
            HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id
        )
    )


async def obter_ultimo_conteudo_historico_tutorial_markdown_do_job_transcribrothers(
    session: AsyncSession,
    job_id: str,
) -> str | None:
    stmt = (
        select(HistoricoVersaoTutorialMarkdownJobTranscribrothers.conteudo_markdown)
        .where(HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id)
        .order_by(HistoricoVersaoTutorialMarkdownJobTranscribrothers.id.desc())
        .limit(1)
    )
    return (await session.scalar(stmt))


async def inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
    session: AsyncSession,
    *,
    job_id: str,
    conteudo_markdown: str,
    origem: str,
) -> int | None:
    texto = (conteudo_markdown or "").strip()
    if not texto:
        return None
    ultimo = await obter_ultimo_conteudo_historico_tutorial_markdown_do_job_transcribrothers(session, job_id)
    if ultimo is not None and ultimo.strip() == texto:
        return None
    row = HistoricoVersaoTutorialMarkdownJobTranscribrothers(
        job_id=job_id,
        criado_em=datetime.now(timezone.utc),
        origem=(origem or "desconhecido")[:72],
        conteudo_markdown=conteudo_markdown,
    )
    session.add(row)
    await session.flush()
    return int(row.id)


async def inserir_versao_historico_tutorial_markdown_se_conteudo_novo_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    job_id: str,
    conteudo_markdown: str,
    origem: str,
) -> int | None:
    """
    Grava snapshot se o texto for diferente do último snapshot (evita duplicar em retries idênticos).
    Devolve o `id` da linha inserida ou None se não inseriu.
    """
    async with session_factory() as session:
        rid = await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=conteudo_markdown,
            origem=origem,
        )
        if rid is None:
            return None
        await session.commit()
        return rid


async def listar_resumo_versoes_historico_tutorial_markdown_do_job_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    limite: int = 80,
) -> list[dict]:
    limite = max(1, min(200, int(limite)))
    async with session_factory() as session:
        stmt = (
            select(HistoricoVersaoTutorialMarkdownJobTranscribrothers)
            .where(HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id)
            .order_by(HistoricoVersaoTutorialMarkdownJobTranscribrothers.id.desc())
            .limit(limite)
        )
        rows = (await session.scalars(stmt)).all()
    out: list[dict] = []
    for r in rows:
        md = r.conteudo_markdown or ""
        preview = _preview_uma_linha_markdown_para_lista_historico_transcribrothers(md)
        out.append(
            {
                "id": r.id,
                "criado_em": _criado_em_iso_utc_com_sufixo_z_para_api_transcribrothers(r.criado_em),
                "origem": r.origem,
                "tamanho_caracteres": len(md),
                "preview_linha": preview,
            }
        )
    return out


def _preview_uma_linha_markdown_para_lista_historico_transcribrothers(md: str, max_len: int = 140) -> str:
    s = (md or "").strip().replace("\r\n", "\n")
    if not s:
        return ""
    primeira = s.split("\n", 1)[0].strip()
    if len(primeira) > max_len:
        return primeira[: max_len - 1] + "…"
    return primeira


async def obter_conteudo_versao_historico_tutorial_markdown_por_id_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    job_id: str,
    historico_id: int,
) -> tuple[str, str, str] | None:
    """Devolve (conteudo, origem, criado_em_iso) ou None."""
    async with session_factory() as session:
        stmt = select(HistoricoVersaoTutorialMarkdownJobTranscribrothers).where(
            HistoricoVersaoTutorialMarkdownJobTranscribrothers.id == int(historico_id),
            HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id,
        )
        row = (await session.scalars(stmt)).first()
        if row is None:
            return None
        return (
            row.conteudo_markdown,
            row.origem,
            _criado_em_iso_utc_com_sufixo_z_para_api_transcribrothers(row.criado_em) or "",
        )


async def obter_par_markdown_antes_depois_ultima_regeneracao_tutorial_no_historico_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
) -> tuple[str, str, str] | None:
    """
    Para jobs que concluíram regeneração com pipeline antigo (Markdown aplicado direto, sem preview).
    Devolve (markdown_antes, markdown_depois, origem_ultima_regeneracao) ou None.
    """
    from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
        ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_FAB_TRANSCRIBROTHERS,
        ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS,
    )

    origens_regeneracao = {
        ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_FAB_TRANSCRIBROTHERS,
        ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS,
    }
    async with session_factory() as session:
        stmt = (
            select(HistoricoVersaoTutorialMarkdownJobTranscribrothers)
            .where(HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id)
            .order_by(HistoricoVersaoTutorialMarkdownJobTranscribrothers.id.asc())
        )
        rows = (await session.scalars(stmt)).all()
    if len(rows) < 2:
        return None
    idx_regen: int | None = None
    for i in range(len(rows) - 1, -1, -1):
        if rows[i].origem in origens_regeneracao:
            idx_regen = i
            break
    if idx_regen is None or idx_regen < 1:
        return None
    depois = (rows[idx_regen].conteudo_markdown or "").strip()
    if not depois:
        return None
    antes_row = rows[idx_regen - 1]
    antes = (antes_row.conteudo_markdown or "").strip()
    if not antes or antes == depois:
        return None
    if antes_row.origem not in (
        ORIGEM_HISTORICO_TUTORIAL_PIPELINE_INICIAL_TRANSCRIBROTHERS,
        *origens_regeneracao,
    ):
        return None
    return antes, depois, str(rows[idx_regen].origem or "")


async def contar_versoes_historico_tutorial_markdown_do_job_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
) -> int:
    async with session_factory() as session:
        n = await session.scalar(
            select(func.count())
            .select_from(HistoricoVersaoTutorialMarkdownJobTranscribrothers)
            .where(HistoricoVersaoTutorialMarkdownJobTranscribrothers.job_id == job_id)
        )
    return int(n or 0)
