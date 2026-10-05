"""Sintetiza um trecho TTS via ElevenLabs v4 e devolve PCM16 mono 24 kHz."""

from __future__ import annotations

from transcribrothers_backend.modulo_cliente_elevenlabs_text_to_speech_e_vozes_transcribrothers import (
    sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_converter_mp3_bytes_para_pcm16_mono_24khz_transcribrothers import (
    converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    resolver_caminho_ffmpeg_transcribrothers,
)


async def sintetizar_pcm16_trecho_tts_elevenlabs_v4_transcribrothers(
    *,
    texto: str,
    voice_id: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo: str | None = None,
    ritmo: object = None,
) -> bytes:
    texto_narrar = montar_conteudo_mensagem_user_tts_pelo_perfil_narracao_transcribrothers(
        PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
        texto,
        ritmo=ritmo,
    )
    mp3 = await sintetizar_mp3_elevenlabs_text_to_speech_v4_transcribrothers(
        configuracao=configuracao,
        texto=texto_narrar,
        voice_id=voice_id,
        modelo=modelo,
    )
    ffmpeg = resolver_caminho_ffmpeg_transcribrothers(configuracao)
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg é necessário para usar ElevenLabs (converter MP3 em WAV PCM da narração)."
        )
    return converter_bytes_mp3_para_pcm16_mono_24khz_via_ffmpeg_transcribrothers(
        mp3,
        executavel_ffmpeg=ffmpeg,
    )
