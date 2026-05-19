"""Testes do PATCH de transcrição multimodal persistido em SQLite."""

from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_patch_transcricao_multimodal_runtime_altera_resposta_get() -> None:
    with TestClient(app) as client:
        r0 = client.get("/api/config/transcribrothers")
        assert r0.status_code == 200
        base = r0.json()
        novo_j = min(86400, int(base["transcricao_multimodal_janela_segundos"]) + 1)
        novo_p = min(32, max(1, int(base["transcricao_multimodal_janelas_paralelas_maxima"])))
        base_fmt = str(base.get("transcricao_multimodal_formato_audio_inline") or "wav")
        novo_fmt = "mp3" if base_fmt == "wav" else "wav"
        br = int(base.get("transcricao_multimodal_audio_bitrate_kbps") or 96)
        novo_br = min(320, max(16, br + (1 if br < 320 else -1)))
        mono = bool(base.get("transcricao_multimodal_audio_mono", True))
        r1 = client.patch(
            "/api/config/transcribrothers/transcricao-multimodal-runtime",
            json={
                "transcricao_multimodal_janela_segundos": novo_j,
                "transcricao_multimodal_janelas_paralelas_maxima": novo_p,
                "transcricao_multimodal_formato_audio_inline": novo_fmt,
                "transcricao_multimodal_audio_bitrate_kbps": novo_br,
                "transcricao_multimodal_audio_mono": mono,
                "tutorial_margem_minima_segundos_entre_links_temporais_captura": 3.0,
                "tutorial_planejamento_instantes_captura_frames_litellm_habilitado": True,
            },
        )
        assert r1.status_code == 200, r1.text
        d1 = r1.json()
        assert d1["transcricao_multimodal_janela_segundos"] == novo_j
        assert d1["transcricao_multimodal_janelas_paralelas_maxima"] == novo_p
        assert d1["transcricao_multimodal_formato_audio_inline"] == novo_fmt
        assert d1["transcricao_multimodal_audio_bitrate_kbps"] == novo_br
        assert d1["transcricao_multimodal_audio_mono"] is mono
        assert d1["tutorial_margem_minima_segundos_entre_links_temporais_captura"] == 3.0
        assert d1["tutorial_planejamento_instantes_captura_frames_litellm_habilitado"] is True
        assert d1["transcricao_multimodal_overrides_runtime_sqlite_ativos"] is True
        r2 = client.get("/api/config/transcribrothers")
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["transcricao_multimodal_janela_segundos"] == novo_j
        assert d2["transcricao_multimodal_formato_audio_inline"] == novo_fmt
        assert d2["transcricao_multimodal_overrides_runtime_sqlite_ativos"] is True


def test_patch_transcricao_multimodal_runtime_rejeita_fora_do_intervalo() -> None:
    with TestClient(app) as client:
        r = client.patch(
            "/api/config/transcribrothers/transcricao-multimodal-runtime",
            json={
                "transcricao_multimodal_janela_segundos": 90001,
                "transcricao_multimodal_janelas_paralelas_maxima": 5,
                "transcricao_multimodal_formato_audio_inline": "wav",
                "transcricao_multimodal_audio_bitrate_kbps": 96,
                "transcricao_multimodal_audio_mono": True,
                "tutorial_margem_minima_segundos_entre_links_temporais_captura": 2.0,
                "tutorial_planejamento_instantes_captura_frames_litellm_habilitado": True,
            },
        )
        assert r.status_code == 422
