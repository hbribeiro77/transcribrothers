"""Gera WAV de prévia TTS para o texto atual de uma cue (sem alterar a narração definitiva)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    gerar_preview_tts_wav_de_uma_cue_via_litellm_transcribrothers,
    resolver_modelo_tts_para_narracao_documento_transcribrothers,
)
from transcribrothers_backend.modulo_promover_preview_tts_cue_validada_para_wav_definitivo_narracao_transcribrothers import (
    caminho_preview_tts_cue_narracao_no_work_transcribrothers,
    gravar_meta_preview_tts_cue_narracao_transcribrothers,
)


@dataclass(frozen=True)
class ResultadoApiPreviewTtsCueNarracaoTranscribrothers:
    caminho_wav: Path
    modelo: str
    texto_caracteres: int
    voz_tts: str = ""


async def gerar_arquivo_preview_tts_cue_narracao_job_transcribrothers(
    *,
    work: Path,
    indice: int,
    texto: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    litellm_model: str | None,
    voz: str | None = None,
    perfil_tts: str | None = None,
    temperatura_tts: float | None = None,
    ritmo_tts: str | None = None,
) -> ResultadoApiPreviewTtsCueNarracaoTranscribrothers:
    from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
        PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        normalizar_perfil_tts_narracao_transcribrothers,
        normalizar_ritmo_tts_narracao_transcribrothers,
        normalizar_temperatura_tts_narracao_transcribrothers,
    )
    from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
        VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
        normalizar_voz_tts_gemini_transcribrothers,
    )

    modelo = resolver_modelo_tts_para_narracao_documento_transcribrothers(
        configuracao,
        litellm_model,
    )
    try:
        voz_efetiva = normalizar_voz_tts_gemini_transcribrothers(
            voz or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
        )
    except ValueError:
        voz_efetiva = VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    try:
        perfil_efetivo = normalizar_perfil_tts_narracao_transcribrothers(
            perfil_tts or PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
        )
    except ValueError:
        perfil_efetivo = PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
    temperatura_efetiva = normalizar_temperatura_tts_narracao_transcribrothers(temperatura_tts)
    ritmo_efetivo = normalizar_ritmo_tts_narracao_transcribrothers(ritmo_tts)
    caminho = caminho_preview_tts_cue_narracao_no_work_transcribrothers(work, indice)
    resultado = await gerar_preview_tts_wav_de_uma_cue_via_litellm_transcribrothers(
        texto=texto,
        modelo=modelo,
        configuracao=configuracao,
        caminho_wav_saida=caminho,
        voz=voz_efetiva,
        perfil_tts=perfil_efetivo,
        temperatura=temperatura_efetiva,
        ritmo=ritmo_efetivo,
    )
    if not resultado.ok or resultado.caminho_wav is None:
        raise RuntimeError(resultado.mensagem)
    gravar_meta_preview_tts_cue_narracao_transcribrothers(
        work=work,
        indice_zero_based=indice,
        texto=texto,
        voz_tts=voz_efetiva,
        modelo=resultado.modelo,
    )
    return ResultadoApiPreviewTtsCueNarracaoTranscribrothers(
        caminho_wav=resultado.caminho_wav,
        modelo=resultado.modelo,
        texto_caracteres=resultado.texto_caracteres,
        voz_tts=voz_efetiva,
    )
