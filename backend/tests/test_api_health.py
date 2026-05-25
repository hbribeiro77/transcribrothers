from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_healthcheck_retorna_ok() -> None:
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "pipeline_identificador" in data
        assert len(str(data.get("pipeline_identificador") or "")) > 10
        assert "ffprobe_disponivel" in data
        assert "ffmpeg_disponivel" in data


def test_config_publica_transcribrothers_retorna_modelos() -> None:
    with TestClient(app) as client:
        r = client.get("/api/config/transcribrothers")
        assert r.status_code == 200
        data = r.json()
        assert "litellm_models" in data
        assert "litellm_model_default" in data
        assert "transcricao_backend" in data
        assert "litellm_http_verify_ssl" in data
        assert "litellm_ssl_ca_bundle_configurado" in data
        assert isinstance(data["litellm_models"], list)
        assert "transcricao_multimodal_janela_segundos" in data
        assert isinstance(data["transcricao_multimodal_janela_segundos"], int)
        assert "transcricao_multimodal_janelas_paralelas_maxima" in data
        assert isinstance(data["transcricao_multimodal_janelas_paralelas_maxima"], int)
        assert "transcricao_multimodal_overrides_runtime_sqlite_ativos" in data
        assert isinstance(data["transcricao_multimodal_overrides_runtime_sqlite_ativos"], bool)
        assert "transcricao_multimodal_formato_audio_inline" in data
        assert data["transcricao_multimodal_formato_audio_inline"] in ("wav", "mp3", "opus", "aac")
        assert "transcricao_multimodal_audio_bitrate_kbps" in data
        assert isinstance(data["transcricao_multimodal_audio_bitrate_kbps"], int)
        assert "transcricao_multimodal_audio_mono" in data
        assert isinstance(data["transcricao_multimodal_audio_mono"], bool)
        assert "verificacao_sustentacao_tutorial_habilitada_efetiva" in data
        assert isinstance(data["verificacao_sustentacao_tutorial_habilitada_efetiva"], bool)
        assert "verificacao_sustentacao_tutorial_habilitada_padrao_env" in data
        assert isinstance(data["verificacao_sustentacao_tutorial_habilitada_padrao_env"], bool)
        assert "verificacao_sustentacao_tutorial_preferencia_sqlite_definida" in data
        assert isinstance(data["verificacao_sustentacao_tutorial_preferencia_sqlite_definida"], bool)
        assert "gitlab_criar_issue_habilitado" in data
        assert isinstance(data["gitlab_criar_issue_habilitado"], bool)
        assert "ffprobe_disponivel" in data
        assert isinstance(data["ffprobe_disponivel"], bool)
        assert "ffmpeg_disponivel" in data
        assert isinstance(data["ffmpeg_disponivel"], bool)
