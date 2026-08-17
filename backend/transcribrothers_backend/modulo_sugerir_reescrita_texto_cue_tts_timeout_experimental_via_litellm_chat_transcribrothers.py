"""Sugere reescrita de cue com timeout TTS experimental — wrapper sobre o núcleo genérico."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_diagnostico_tts_perfil_experimental_voz_transcribrothers import (
    FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
    PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
    normalizar_perfil_tts_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers import (
    ler_cues_pendentes_timeout_dos_steps_transcribrothers,
)
from transcribrothers_backend.modulo_sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers import (
    limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers,
    sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers,
)

# Reexport para testes/importadores antigos.
__all__ = [
    "limpar_sugestao_reescrita_cue_tts_da_resposta_ia_transcribrothers",
    "sugerir_reescrita_texto_cue_tts_pendente_timeout_experimental_transcribrothers",
]


async def sugerir_reescrita_texto_cue_tts_pendente_timeout_experimental_transcribrothers(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    indice: int,
    texto: str,
    litellm_model_chat: str | None = None,
) -> dict[str, Any]:
    """
    Valida fase experimental + cue pendente; delega a sugestão ao núcleo genérico.
    """
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise ValueError("Job não encontrado.")
        steps = dict(row.steps_json or {})
        fase = str(steps.get("pipeline_fase") or "")
        if fase != FASE_VIDEO_NARRADO_AGUARDANDO_RESOLUCAO_TTS_TIMEOUT_TRANSCRIBROTHERS:
            raise ValueError(
                "Este job não está aguardando resolução de timeout TTS experimental."
            )
        perfil = normalizar_perfil_tts_narracao_transcribrothers(
            steps.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS)
        )
        if perfil != PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS:
            raise ValueError("Sugestão de reescrita só no perfil experimental_voz.")
        pendentes = ler_cues_pendentes_timeout_dos_steps_transcribrothers(steps)
        if not any(int(p["indice"]) == int(indice) for p in pendentes):
            raise ValueError(f"Cue índice {indice} não está na lista de pendentes.")
        modelo_steps = str(steps.get("pipeline_video_narrado_modelo_chat_limpeza") or "").strip()

    return await sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers(
        configuracao=configuracao,
        texto=texto,
        indice=indice,
        litellm_model_chat=litellm_model_chat,
        modelo_chat_fallback_steps=modelo_steps,
        log_etapa="sugerir_reescrita_cue_tts_timeout",
    )
