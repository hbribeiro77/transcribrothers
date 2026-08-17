"""Gera WAV de amostra de uma voz Gemini TTS (frase fixa, sem job)."""

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

TEXTO_AMOSTRA_VOZ_TTS_NARRACAO_TRANSCRIBROTHERS = (
    "Esta é uma amostra da voz selecionada para a narração do vídeo."
)

_NOME_SUBPASTA_AMOSTRA = "tmp_preview_tts_amostra_voz_narracao"


@dataclass(frozen=True)
class ResultadoApiPreviewTtsAmostraVozNarracaoTranscribrothers:
    caminho_wav: Path
    modelo: str
    voz: str
    texto_caracteres: int


def caminho_preview_tts_amostra_voz_no_data_dir_transcribrothers(
    data_dir: Path,
    voz: str,
) -> Path:
    voz_safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in voz.strip()) or "voz"
    return data_dir / _NOME_SUBPASTA_AMOSTRA / f"amostra_{voz_safe}.wav"


async def gerar_arquivo_preview_tts_amostra_voz_narracao_transcribrothers(
    *,
    data_dir: Path,
    voz: str | None,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    litellm_model: str | None,
    perfil_tts: str | None = None,
    temperatura_tts: float | None = None,
    ritmo_tts: str | None = None,
) -> ResultadoApiPreviewTtsAmostraVozNarracaoTranscribrothers:
    try:
        voz_efetiva = normalizar_voz_tts_gemini_transcribrothers(
            voz or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
        )
    except ValueError as e:
        raise ValueError(str(e)) from e
    try:
        perfil_efetivo = normalizar_perfil_tts_narracao_transcribrothers(
            perfil_tts or PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
        )
    except ValueError as e:
        raise ValueError(str(e)) from e
    temperatura_efetiva = normalizar_temperatura_tts_narracao_transcribrothers(temperatura_tts)
    ritmo_efetivo = normalizar_ritmo_tts_narracao_transcribrothers(ritmo_tts)
    modelo = resolver_modelo_tts_para_narracao_documento_transcribrothers(
        configuracao,
        litellm_model,
    )
    caminho = caminho_preview_tts_amostra_voz_no_data_dir_transcribrothers(data_dir, voz_efetiva)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    resultado = await gerar_preview_tts_wav_de_uma_cue_via_litellm_transcribrothers(
        texto=TEXTO_AMOSTRA_VOZ_TTS_NARRACAO_TRANSCRIBROTHERS,
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
    return ResultadoApiPreviewTtsAmostraVozNarracaoTranscribrothers(
        caminho_wav=resultado.caminho_wav,
        modelo=resultado.modelo,
        voz=voz_efetiva,
        texto_caracteres=resultado.texto_caracteres,
    )
