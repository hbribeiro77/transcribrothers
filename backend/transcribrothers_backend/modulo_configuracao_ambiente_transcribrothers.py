from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PACOTE_BACKEND_TRANSCRIBROTHERS = Path(__file__).resolve().parent


def listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers(
    diretorio_pacote_transcribrothers_backend: Path,
) -> tuple[str, ...]:
    """Carrega `.env` na raiz do repositório e em `backend/.env`; o último arquivo vence em chaves repetidas.

    Evita que `uvicorn` iniciado na raiz do monorepo ignore `backend/.env` (comportamento de `env_file='.env'` só no cwd).
    """
    backend = diretorio_pacote_transcribrothers_backend.parent
    raiz = backend.parent
    caminhos: list[str] = []
    p_raiz = raiz / ".env"
    p_backend = backend / ".env"
    if p_raiz.is_file():
        caminhos.append(str(p_raiz.resolve()))
    if p_backend.is_file():
        caminhos.append(str(p_backend.resolve()))
    if caminhos:
        return tuple(caminhos)
    return (".env",)


_ARQUIVOS_DOT_ENV_SETTINGS = listar_caminhos_arquivos_dot_env_ordem_carregamento_para_settings_transcribrothers(
    _PACOTE_BACKEND_TRANSCRIBROTHERS
)


class ConfiguracaoAmbienteTranscribrothers(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ARQUIVOS_DOT_ENV_SETTINGS,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_drive_api_key: str = ""
    openai_api_key: str = ""
    litellm_api_key: str = ""
    litellm_endpoint: str = ""
    litellm_http_verify_ssl: bool = True
    litellm_ssl_ca_bundle: str = ""
    # POST /v1/chat/completions (transcrição multimodal em janelas + tutorial): leitura longa para modelos lentos.
    litellm_http_timeout_connect_segundos: float = 120.0
    litellm_http_timeout_read_segundos: float = 7200.0
    litellm_model: str = "openai/gpt-4o-mini"
    litellm_modelos_provisionados: str = ""
    transcricao_backend: str = "openai_whisper"
    transcricao_litellm_modelo: str = ""
    # Tamanho de cada janela WAV enviada ao modelo multimodal (segundos). 0 = arquivo inteiro (não recomendado para vídeos longos).
    transcricao_multimodal_janela_segundos: int = 30
    # Quantas janelas transcrevem ao mesmo tempo (POST paralelos ao LiteLLM). 1 = sequencial. Máximo interno 32.
    transcricao_multimodal_janelas_paralelas_maxima: int = 5
    # Só transcrição multimodal LiteLLM: wav, mp3, opus (Ogg Opus), aac (M4A). Codecs dependem do ffmpeg.
    transcricao_multimodal_formato_audio_inline: str = "aac"
    # Bitrate (kbps) para mp3/opus/aac; ignorado para wav. Aceita também env antigo TRANSCRICAO_MULTIMODAL_MP3_BITRATE_KBPS.
    transcricao_multimodal_audio_bitrate_kbps: int = Field(
        default=32,
        validation_alias=AliasChoices(
            "TRANSCRICAO_MULTIMODAL_AUDIO_BITRATE_KBPS",
            "TRANSCRICAO_MULTIMODAL_MP3_BITRATE_KBPS",
        ),
    )
    # True = um canal (menor payload). False = estéreo ao extrair/codificar para o modelo.
    transcricao_multimodal_audio_mono: bool = True
    # POST /v1/chat/completions: pede saída JSON estrita (OpenAI-compatible). Se o proxy rejeitar, o cliente tenta de novo sem o campo.
    transcricao_litellm_chat_json_object_response_format: bool = True
    max_video_bytes: int = 524_288_000
    max_frames_per_minute: int = 12
    # 0 = sem teto extra (apenas max_frames_per_minute). >0 limita quantidade máxima de screenshots no tutorial.
    tutorial_max_frames_total: int = 0
    # True: rascunho Markdown com ?t= → captura só esses instantes → tutorial final com imagens.
    tutorial_captura_frames_sob_demanda: bool = True
    # Mínimo de segundos entre links `?t=` considerados distintos na deduplicação antes do ffmpeg.
    tutorial_margem_minima_segundos_entre_links_temporais_captura: float = 2.0
    # True: passo LiteLLM escolhe subconjunto dos candidatos `?t=` que merecem screenshot.
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado: bool = True
    # Largura máxima em px ao capturar frames (ffmpeg scale). 0 = mantém resolução original do frame.
    tutorial_frame_max_width_px: int = 1280
    # Revisão profunda (regeneração em fases analista+workers+editor): tecto de tópicos do plano (1–32).
    revisao_profunda_max_topicos: int = 8
    # Verificação pós-geração: comparar tutorial vs transcrição (LiteLLM, JSON). `true` desliga a etapa.
    verificacao_sustentacao_tutorial_desativada: bool = False
    # Visão em lotes de até 4 PNGs: remove imagens visualmente duplicadas no Markdown. `true` desliga.
    verificacao_imagens_duplicadas_tutorial_desativada: bool = False
    # Limites de caracteres enviados ao modelo de verificação (payload JSON da transcrição e corpo Markdown).
    verificacao_sustentacao_tutorial_max_chars_payload_transcricao_json: int = 90_000
    verificacao_sustentacao_tutorial_max_chars_markdown_enviado: int = 120_000
    # Edição por seção: auditor de redundância com outras seções ##. `true` desliga.
    verificacao_redundancia_secao_markdown_desativada: bool = False
    verificacao_redundancia_secao_max_chars_corpo_outra_secao: int = 3500
    verificacao_redundancia_secao_max_outras_secoes: int = 12
    cors_origins: str = "http://localhost:5173"
    transcribrothers_data_dir: Path = Path("./data")

    @field_validator("litellm_http_verify_ssl", mode="before")
    @classmethod
    def _parsear_litellm_http_verify_ssl_de_string_ambiente(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return True
        s = str(v).strip().lower()
        if s in ("0", "false", "no", "off"):
            return False
        return True

    @field_validator("transcricao_litellm_chat_json_object_response_format", mode="before")
    @classmethod
    def _parsear_transcricao_litellm_chat_json_object_response_format(
        cls, v: object
    ) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return True
        s = str(v).strip().lower()
        if s in ("0", "false", "no", "off"):
            return False
        return True

    @field_validator("transcricao_multimodal_janelas_paralelas_maxima", mode="before")
    @classmethod
    def _clamp_transcricao_multimodal_janelas_paralelas_maxima(cls, v: object) -> int:
        try:
            n = int(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 5
        return max(1, min(32, n))

    @field_validator("transcricao_multimodal_formato_audio_inline", mode="before")
    @classmethod
    def _normalizar_transcricao_multimodal_formato_audio_inline(cls, v: object) -> str:
        s = str(v or "aac").strip().lower()
        if s in ("wav", "mp3", "opus", "aac"):
            return s
        return "aac"

    @field_validator("transcricao_multimodal_audio_bitrate_kbps", mode="before")
    @classmethod
    def _clamp_transcricao_multimodal_audio_bitrate_kbps(cls, v: object) -> int:
        try:
            n = int(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 32
        return max(16, min(320, n))

    @field_validator("revisao_profunda_max_topicos", mode="before")
    @classmethod
    def _clamp_revisao_profunda_max_topicos(cls, v: object) -> int:
        try:
            n = int(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 8
        return max(1, min(32, n))

    @field_validator("verificacao_sustentacao_tutorial_desativada", mode="before")
    @classmethod
    def _parsear_verificacao_sustentacao_tutorial_desativada(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        if s in ("1", "true", "yes", "on"):
            return True
        return False

    @field_validator("verificacao_imagens_duplicadas_tutorial_desativada", mode="before")
    @classmethod
    def _parsear_verificacao_imagens_duplicadas_tutorial_desativada(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        if s in ("1", "true", "yes", "on"):
            return True
        return False

    @field_validator("verificacao_sustentacao_tutorial_max_chars_payload_transcricao_json", mode="before")
    @classmethod
    def _clamp_verificacao_payload_json(cls, v: object) -> int:
        try:
            n = int(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 90_000
        return max(8_000, min(500_000, n))

    @field_validator("verificacao_sustentacao_tutorial_max_chars_markdown_enviado", mode="before")
    @classmethod
    def _clamp_verificacao_markdown(cls, v: object) -> int:
        try:
            n = int(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 120_000
        return max(4_000, min(500_000, n))

    @field_validator("transcricao_multimodal_audio_mono", mode="before")
    @classmethod
    def _parsear_transcricao_multimodal_audio_mono(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return True
        s = str(v).strip().lower()
        if s in ("0", "false", "no", "off"):
            return False
        return True

    @field_validator("tutorial_margem_minima_segundos_entre_links_temporais_captura", mode="before")
    @classmethod
    def _clamp_tutorial_margem_minima_segundos_entre_links_temporais_captura(cls, v: object) -> float:
        try:
            n = float(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 2.0
        return max(0.5, min(120.0, n))

    @field_validator("tutorial_planejamento_instantes_captura_frames_litellm_habilitado", mode="before")
    @classmethod
    def _parsear_tutorial_planejamento_instantes_captura_frames_litellm_habilitado(
        cls, v: object
    ) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return True
        s = str(v).strip().lower()
        if s in ("0", "false", "no", "off"):
            return False
        return True

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def obter_configuracao() -> ConfiguracaoAmbienteTranscribrothers:
    return ConfiguracaoAmbienteTranscribrothers()
