from transcribrothers_backend.modulo_normalizar_voz_tts_efetiva_cue_gemini_ou_elevenlabs_transcribrothers import (
    normalizar_voz_tts_efetiva_para_cue_transcribrothers,
)


def test_preserva_voice_id_elevenlabs_em_vez_de_cair_em_kore() -> None:
    assert (
        normalizar_voz_tts_efetiva_para_cue_transcribrothers(
            "nPczCjzI2devNBz1zQrb",
            "Kore",
        )
        == "nPczCjzI2devNBz1zQrb"
    )


def test_ainda_normaliza_voz_gemini() -> None:
    assert normalizar_voz_tts_efetiva_para_cue_transcribrothers("aoede", "Kore") == "Aoede"
