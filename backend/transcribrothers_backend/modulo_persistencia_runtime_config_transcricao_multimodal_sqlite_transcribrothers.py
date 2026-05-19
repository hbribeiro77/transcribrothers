"""Persistência em SQLite: janela, paralelismo, formato, bitrate e mono da transcrição multimodal."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    RegistroRuntimeConfigValorTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELA_SEGUNDOS = "transcricao_multimodal_janela_segundos"
CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELAS_PARALELAS_MAXIMA = (
    "transcricao_multimodal_janelas_paralelas_maxima"
)
CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_FORMATO_AUDIO_INLINE = (
    "transcricao_multimodal_formato_audio_inline"
)
CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_BITRATE_KBPS = "transcricao_multimodal_audio_bitrate_kbps"
CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_MONO = "transcricao_multimodal_audio_mono"
CHAVE_RUNTIME_TUTORIAL_MARGEM_MINIMA_SEGUNDOS_ENTRE_LINKS_TEMPORAIS_CAPTURA = (
    "tutorial_margem_minima_segundos_entre_links_temporais_captura"
)
CHAVE_RUNTIME_TUTORIAL_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_LITELLM_HABILITADO = (
    "tutorial_planejamento_instantes_captura_frames_litellm_habilitado"
)


FORMATOS_AUDIO_INLINE_MULTIMODAL_SQLITE_TRANSCRIBROTHERS = frozenset({"wav", "mp3", "opus", "aac"})


@dataclass(frozen=True)
class OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers:
    janela_segundos: int | None = None
    janelas_paralelas_maxima: int | None = None
    formato_audio_inline: str | None = None
    audio_bitrate_kbps: int | None = None
    audio_mono: bool | None = None
    tutorial_margem_minima_segundos_entre_links_temporais_captura: float | None = None
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado: bool | None = None


def normalizar_formato_audio_inline_transcricao_multimodal(s: str) -> str | None:
    t = (s or "").strip().lower()
    if t in FORMATOS_AUDIO_INLINE_MULTIMODAL_SQLITE_TRANSCRIBROTHERS:
        return t
    return None


def normalizar_bool_mono_audio_transcricao_multimodal_sqlite(s: str) -> bool | None:
    v = (s or "").strip().lower()
    if v in ("1", "true", "yes", "on", "sim"):
        return True
    if v in ("0", "false", "no", "off", "nao", "não"):
        return False
    return None


async def obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(
    session: AsyncSession,
) -> OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers:
    janela: int | None = None
    paralelas: int | None = None
    formato: str | None = None
    bitrate: int | None = None
    mono: bool | None = None
    margem_links: float | None = None
    planejamento_captura: bool | None = None

    row_j = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELA_SEGUNDOS,
    )
    if row_j and (row_j.valor or "").strip():
        try:
            janela = int(row_j.valor.strip())
        except ValueError:
            pass

    row_p = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELAS_PARALELAS_MAXIMA,
    )
    if row_p and (row_p.valor or "").strip():
        try:
            paralelas = int(row_p.valor.strip())
        except ValueError:
            pass

    row_f = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_FORMATO_AUDIO_INLINE,
    )
    if row_f and (row_f.valor or "").strip():
        formato = normalizar_formato_audio_inline_transcricao_multimodal(row_f.valor)

    row_b = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_BITRATE_KBPS,
    )
    if row_b and (row_b.valor or "").strip():
        try:
            bitrate = int(row_b.valor.strip())
        except ValueError:
            pass

    row_m = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_MONO,
    )
    if row_m and (row_m.valor or "").strip():
        mono = normalizar_bool_mono_audio_transcricao_multimodal_sqlite(row_m.valor)

    row_ml = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TUTORIAL_MARGEM_MINIMA_SEGUNDOS_ENTRE_LINKS_TEMPORAIS_CAPTURA,
    )
    if row_ml and (row_ml.valor or "").strip():
        try:
            margem_links = max(0.5, min(120.0, float(row_ml.valor.strip())))
        except ValueError:
            pass

    row_pc = await session.get(
        RegistroRuntimeConfigValorTranscribrothers,
        CHAVE_RUNTIME_TUTORIAL_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_LITELLM_HABILITADO,
    )
    if row_pc and (row_pc.valor or "").strip():
        planejamento_captura = normalizar_bool_mono_audio_transcricao_multimodal_sqlite(row_pc.valor)

    return OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers(
        janela_segundos=janela,
        janelas_paralelas_maxima=paralelas,
        formato_audio_inline=formato,
        audio_bitrate_kbps=bitrate,
        audio_mono=mono,
        tutorial_margem_minima_segundos_entre_links_temporais_captura=margem_links,
        tutorial_planejamento_instantes_captura_frames_litellm_habilitado=planejamento_captura,
    )


async def gravar_overrides_transcricao_multimodal_runtime_no_sqlite_transcribrothers(
    session: AsyncSession,
    *,
    transcricao_multimodal_janela_segundos: int,
    transcricao_multimodal_janelas_paralelas_maxima: int,
    transcricao_multimodal_formato_audio_inline: str,
    transcricao_multimodal_audio_bitrate_kbps: int,
    transcricao_multimodal_audio_mono: bool,
    tutorial_margem_minima_segundos_entre_links_temporais_captura: float,
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado: bool,
) -> None:
    fmt = normalizar_formato_audio_inline_transcricao_multimodal(transcricao_multimodal_formato_audio_inline)
    if fmt is None:
        raise ValueError("transcricao_multimodal_formato_audio_inline inválido (use wav, mp3, opus ou aac).")
    br = max(16, min(320, int(transcricao_multimodal_audio_bitrate_kbps)))
    agora = datetime.now(timezone.utc)
    mono_str = "true" if bool(transcricao_multimodal_audio_mono) else "false"
    margem = max(0.5, min(120.0, float(tutorial_margem_minima_segundos_entre_links_temporais_captura)))
    planej_str = (
        "true"
        if bool(tutorial_planejamento_instantes_captura_frames_litellm_habilitado)
        else "false"
    )
    for chave, valor_str in (
        (
            CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELA_SEGUNDOS,
            str(int(transcricao_multimodal_janela_segundos)),
        ),
        (
            CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_JANELAS_PARALELAS_MAXIMA,
            str(int(transcricao_multimodal_janelas_paralelas_maxima)),
        ),
        (CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_FORMATO_AUDIO_INLINE, fmt),
        (CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_BITRATE_KBPS, str(br)),
        (CHAVE_RUNTIME_TRANSCRICAO_MULTIMODAL_AUDIO_MONO, mono_str),
        (
            CHAVE_RUNTIME_TUTORIAL_MARGEM_MINIMA_SEGUNDOS_ENTRE_LINKS_TEMPORAIS_CAPTURA,
            str(margem),
        ),
        (
            CHAVE_RUNTIME_TUTORIAL_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_LITELLM_HABILITADO,
            planej_str,
        ),
    ):
        row = await session.get(RegistroRuntimeConfigValorTranscribrothers, chave)
        if row is None:
            session.add(
                RegistroRuntimeConfigValorTranscribrothers(
                    chave=chave,
                    valor=valor_str,
                    updated_at=agora,
                )
            )
        else:
            row.valor = valor_str
            row.updated_at = agora
    await session.commit()


def overrides_transcricao_multimodal_sqlite_tem_alguma_chave_preenchida_transcribrothers(
    ov: OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers,
) -> bool:
    return (
        ov.janela_segundos is not None
        or ov.janelas_paralelas_maxima is not None
        or ov.formato_audio_inline is not None
        or ov.audio_bitrate_kbps is not None
        or ov.audio_mono is not None
        or ov.tutorial_margem_minima_segundos_entre_links_temporais_captura is not None
        or ov.tutorial_planejamento_instantes_captura_frames_litellm_habilitado is not None
    )


def resolver_tutorial_margem_e_planejamento_captura_efetivos_com_overrides_sqlite_transcribrothers(
    margem_base: float,
    planejamento_base: bool,
    overrides: OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers,
) -> tuple[float, bool]:
    margem_raw = (
        overrides.tutorial_margem_minima_segundos_entre_links_temporais_captura
        if overrides.tutorial_margem_minima_segundos_entre_links_temporais_captura is not None
        else margem_base
    )
    margem = max(0.5, min(120.0, float(margem_raw)))
    planej = (
        bool(overrides.tutorial_planejamento_instantes_captura_frames_litellm_habilitado)
        if overrides.tutorial_planejamento_instantes_captura_frames_litellm_habilitado is not None
        else bool(planejamento_base)
    )
    return margem, planej


def resolver_janela_paralelas_formato_bitrate_mono_efetivos_com_overrides_sqlite_transcribrothers(
    janela_base: int,
    paralelas_base: int,
    formato_base: str,
    bitrate_base: int,
    mono_base: bool,
    overrides: OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers,
) -> tuple[int, int, str, int, bool]:
    j = int(overrides.janela_segundos if overrides.janela_segundos is not None else janela_base)
    p = int(
        overrides.janelas_paralelas_maxima
        if overrides.janelas_paralelas_maxima is not None
        else paralelas_base
    )
    f_raw = overrides.formato_audio_inline if overrides.formato_audio_inline is not None else formato_base
    f = normalizar_formato_audio_inline_transcricao_multimodal(str(f_raw)) or "wav"
    br_raw = overrides.audio_bitrate_kbps if overrides.audio_bitrate_kbps is not None else bitrate_base
    br = max(16, min(320, int(br_raw)))
    mono = bool(overrides.audio_mono) if overrides.audio_mono is not None else bool(mono_base)
    return max(0, min(86400, j)), max(1, min(32, p)), f, br, mono


def aplicar_overrides_transcricao_multimodal_na_configuracao_transcribrothers(
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    overrides: OverridesTranscricaoMultimodalRuntimeSqliteTranscribrothers,
) -> ConfiguracaoAmbienteTranscribrothers:
    u: dict[str, object] = {}
    if overrides.janela_segundos is not None:
        u["transcricao_multimodal_janela_segundos"] = overrides.janela_segundos
    if overrides.janelas_paralelas_maxima is not None:
        u["transcricao_multimodal_janelas_paralelas_maxima"] = overrides.janelas_paralelas_maxima
    if overrides.formato_audio_inline is not None:
        u["transcricao_multimodal_formato_audio_inline"] = overrides.formato_audio_inline
    if overrides.audio_bitrate_kbps is not None:
        u["transcricao_multimodal_audio_bitrate_kbps"] = overrides.audio_bitrate_kbps
    if overrides.audio_mono is not None:
        u["transcricao_multimodal_audio_mono"] = overrides.audio_mono
    if overrides.tutorial_margem_minima_segundos_entre_links_temporais_captura is not None:
        u["tutorial_margem_minima_segundos_entre_links_temporais_captura"] = (
            overrides.tutorial_margem_minima_segundos_entre_links_temporais_captura
        )
    if overrides.tutorial_planejamento_instantes_captura_frames_litellm_habilitado is not None:
        u["tutorial_planejamento_instantes_captura_frames_litellm_habilitado"] = (
            overrides.tutorial_planejamento_instantes_captura_frames_litellm_habilitado
        )
    return configuracao.model_copy(update=u) if u else configuracao
