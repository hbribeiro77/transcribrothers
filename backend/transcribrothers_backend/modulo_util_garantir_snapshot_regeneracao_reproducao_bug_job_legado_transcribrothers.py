"""Garante `regeneracao_tutorial_snapshot` em jobs `reproducao_bug` concluídos antes do backfill automático."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    _montar_snapshot_regeneracao_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_util_job_steps_indicam_reproducao_bug_transcribrothers import (
    job_steps_indicam_reproducao_bug_transcribrothers,
)

_RE_OFFSET_MS_NOME_PNG_REPRODUCAO_BUG = re.compile(r"offset_ms_(\d+)", re.IGNORECASE)
_PREFIXO_PNG_REPRODUCAO_BUG = "screenshot_reproducao_bug"


def montar_rels_snapshot_a_partir_de_pngs_assets_reproducao_bug_transcribrothers(
    assets_dir: Path,
) -> list[tuple[float, str]]:
    if not assets_dir.is_dir():
        return []
    candidatos: list[tuple[float, str]] = []
    for png in sorted(assets_dir.glob("*.png")):
        nome = png.name
        if _PREFIXO_PNG_REPRODUCAO_BUG not in nome.lower():
            continue
        m = _RE_OFFSET_MS_NOME_PNG_REPRODUCAO_BUG.search(nome)
        if not m:
            continue
        segundos = int(m.group(1)) / 1000.0
        candidatos.append((segundos, f"assets/{nome}"))
    candidatos.sort(key=lambda par: (par[0], par[1]))
    return candidatos


async def garantir_snapshot_regeneracao_em_job_reproducao_bug_legado_se_ausente_transcribrothers(
    session: AsyncSession,
    row: JobPipelineTranscribrothers,
    work: Path,
) -> bool:
    """
    Preenche snapshot a partir dos PNGs em assets/ (jobs concluídos antes de gravar snapshot no pipeline).
    Retorna True se gravou snapshot.
    """
    steps = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    if not job_steps_indicam_reproducao_bug_transcribrothers(steps):
        return False
    if isinstance(steps.get("regeneracao_tutorial_snapshot"), dict):
        return False
    if row.status not in ("completed", "failed"):
        return False
    if not (row.result_markdown or "").strip():
        return False

    assets_dir = work / "assets_exportados_para_markdown"
    rels = montar_rels_snapshot_a_partir_de_pngs_assets_reproducao_bug_transcribrothers(assets_dir)
    if not rels:
        return False

    transcricao_vazia = ResultadoTranscricaoComSegmentos(
        texto_completo="",
        segmentos=[],
        idioma_detectado=None,
    )
    steps["regeneracao_tutorial_snapshot"] = _montar_snapshot_regeneracao_tutorial_transcribrothers(
        transcricao_vazia,
        rels,
    )
    steps["regeneracao_tutorial_snapshot_backfill_reproducao_bug_em"] = datetime.now(
        timezone.utc
    ).isoformat()
    row.steps_json = steps
    flag_modified(row, "steps_json")
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(row)
    return True
