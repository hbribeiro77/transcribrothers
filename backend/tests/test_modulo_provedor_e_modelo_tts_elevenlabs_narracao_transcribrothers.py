"""Provedor TTS (LiteLLM vs ElevenLabs) e modelo Eleven v4."""

from transcribrothers_backend.modulo_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers import (
    MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
    MODELO_TTS_ELEVENLABS_V4_TURBO_TRANSCRIBROTHERS,
    PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
    PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
    extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers,
    listar_modelos_tts_elevenlabs_para_interface_transcribrothers,
    normalizar_modelo_tts_elevenlabs_transcribrothers,
    normalizar_provedor_tts_narracao_transcribrothers,
    provedor_tts_parece_elevenlabs_pelo_modelo_transcribrothers,
    tem_chave_elevenlabs_configurada_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)


def test_provedor_padrao_e_litellm_e_aceita_elevenlabs() -> None:
    assert (
        normalizar_provedor_tts_narracao_transcribrothers(None)
        == PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS
    )
    assert (
        normalizar_provedor_tts_narracao_transcribrothers("ELEVENLABS")
        == PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS
    )


def test_modelo_elevenlabs_padrao_e_v4_e_rejeita_turbo() -> None:
    assert (
        normalizar_modelo_tts_elevenlabs_transcribrothers(None)
        == MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    )
    assert (
        normalizar_modelo_tts_elevenlabs_transcribrothers("eleven_v4")
        == MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    )
    try:
        normalizar_modelo_tts_elevenlabs_transcribrothers(
            MODELO_TTS_ELEVENLABS_V4_TURBO_TRANSCRIBROTHERS
        )
    except ValueError as exc:
        assert "turbo" in str(exc).lower()
    else:
        raise AssertionError("turbo deveria ser rejeitado")


def test_lista_modelos_elevenlabs_so_tem_v4() -> None:
    assert listar_modelos_tts_elevenlabs_para_interface_transcribrothers() == [
        MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS
    ]


def test_modelo_eleven_v4_identifica_provedor_elevenlabs() -> None:
    assert provedor_tts_parece_elevenlabs_pelo_modelo_transcribrothers("eleven_v4") is True
    assert (
        provedor_tts_parece_elevenlabs_pelo_modelo_transcribrothers(
            "gemini/gemini-2.5-flash-preview-tts"
        )
        is False
    )


def test_extrai_vozes_com_idioma_sotaque_e_pt_br_na_frente() -> None:
    itens = extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers(
        {
            "voices": [
                {
                    "voice_id": "en1",
                    "name": "Roger",
                    "labels": {"language": "en", "accent": "american"},
                },
                {
                    "voice_id": "br1",
                    "name": "1berto",
                    "labels": {"language": "pt", "accent": "brazilian"},
                    "verified_languages": [
                        {"language": "pt", "locale": "pt-BR", "accent": "brazilian"},
                    ],
                },
                {
                    "voice_id": "ptpt",
                    "name": "Lisboa",
                    "labels": {"language": "pt", "accent": "lisbon"},
                },
            ]
        }
    )
    assert [v["id"] for v in itens] == ["br1", "ptpt", "en1"]
    assert itens[0]["pt_br"] is True
    assert itens[0]["locale"] == "pt-BR"
    assert itens[0]["idioma"] == "pt"
    assert itens[0]["sotaque"] == "brazilian"
    assert itens[1]["pt_br"] is False
    assert itens[2]["pt_br"] is False


def test_extrai_vozes_get_voices_com_nome_como_estilo() -> None:
    itens = extrair_vozes_elevenlabs_da_resposta_get_voices_transcribrothers(
        {
            "voices": [
                {"voice_id": "abc123", "name": "Rachel"},
                {"voice_id": "  ", "name": "Ignorar"},
                {"voice_id": "def456", "name": "George"},
            ]
        }
    )
    assert [v["id"] for v in itens] == ["def456", "abc123"]
    assert itens[0]["estilo"] == "George"
    assert itens[1]["estilo"] == "Rachel"
    assert itens[0]["pt_br"] is False
    assert itens[1]["pt_br"] is False


def test_chave_elevenlabs_configurada_nao_expoe_segredo() -> None:
    assert (
        tem_chave_elevenlabs_configurada_transcribrothers(
            ConfiguracaoAmbienteTranscribrothers(elevenlabs_api_key="sk-teste")
        )
        is True
    )
    assert (
        tem_chave_elevenlabs_configurada_transcribrothers(
            ConfiguracaoAmbienteTranscribrothers(elevenlabs_api_key="  ")
        )
        is False
    )
