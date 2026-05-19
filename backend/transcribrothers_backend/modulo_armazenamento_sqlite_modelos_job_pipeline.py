from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import JSON, DateTime, Index, String, Text, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class StatusJobTranscribrothers(str, enum.Enum):
    pending = "pending"
    downloading = "downloading"
    extracting_audio = "extracting_audio"
    transcribing = "transcribing"
    capturing_frames = "capturing_frames"
    generating_tutorial = "generating_tutorial"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class OrigemEntradaJobTranscribrothers:
    drive = "drive"
    upload_local = "upload_local"


class RegistroRuntimeConfigValorTranscribrothers(Base):
    """Chave/valor para parâmetros editáveis pela UI (ex.: transcrição multimodal)."""

    __tablename__ = "runtime_config_valores_transcribrothers"

    chave: Mapped[str] = mapped_column(String(128), primary_key=True)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class HistoricoVersaoTutorialMarkdownJobTranscribrothers(Base):
    """Snapshots do `result_markdown` por job (lista compacta na UI + preview na coluna larga)."""

    __tablename__ = "historico_versoes_tutorial_markdown_job_transcribrothers"
    __table_args__ = (Index("ix_hist_tutorial_job_id_criado_desc", "job_id", "criado_em"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    origem: Mapped[str] = mapped_column(String(72), nullable=False)
    conteudo_markdown: Mapped[str] = mapped_column(Text, nullable=False)


class JobPipelineTranscribrothers(Base):
    __tablename__ = "jobs_pipeline_transcribrothers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), index=True, default=StatusJobTranscribrothers.pending.value)
    source_kind: Mapped[str] = mapped_column(
        String(32),
        default=OrigemEntradaJobTranscribrothers.drive,
        nullable=False,
    )
    drive_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_id: Mapped[str] = mapped_column(String(128), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


def novo_id_job() -> str:
    return str(uuid.uuid4())


def criar_engine_sqlite_async(url: str):
    return create_async_engine(url, future=True)


def criar_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def migrar_schema_sqlite_jobs_adicionar_source_kind_se_faltar(engine) -> None:
    async with engine.begin() as conn:
        r = await conn.execute(text("PRAGMA table_info(jobs_pipeline_transcribrothers)"))
        cols = [row[1] for row in r.fetchall()]
        if "source_kind" not in cols:
            await conn.execute(
                text(
                    "ALTER TABLE jobs_pipeline_transcribrothers "
                    "ADD COLUMN source_kind VARCHAR(32) DEFAULT 'drive'"
                )
            )


async def inicializar_banco(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await migrar_schema_sqlite_jobs_adicionar_source_kind_se_faltar(engine)
