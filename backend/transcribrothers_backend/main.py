from __future__ import annotations

import io
import re
import shutil
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Body, Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_controle_cancelamento_pipeline_jobs_transcribrothers import (
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers,
    marcar_cancelamento_pipeline_solicitado_para_job_transcribrothers,
)
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    OrigemEntradaJobTranscribrothers,
    StatusJobTranscribrothers,
    criar_engine_sqlite_async,
    criar_session_factory,
    inicializar_banco,
    novo_id_job,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
    obter_configuracao,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_metadados_google_drive_publico_arquivo_por_id import (
    media_type_para_video_por_extensao,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    ffmpeg_disponivel_transcribrothers,
    ffprobe_disponivel_transcribrothers,
    obter_diagnostico_ffmpeg_ffprobe_transcribrothers,
)
from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_RESUMO_PLANO_PARA_EDITOR_FINAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_transcricao_multimodal_sqlite_transcribrothers import (
    gravar_overrides_transcricao_multimodal_runtime_no_sqlite_transcribrothers,
    obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers,
    overrides_transcricao_multimodal_sqlite_tem_alguma_chave_preenchida_transcribrothers,
    resolver_janela_paralelas_formato_bitrate_mono_efetivos_com_overrides_sqlite_transcribrothers,
    resolver_tutorial_margem_e_planejamento_captura_efetivos_com_overrides_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_verificacao_redundancia_secao_markdown_sqlite_transcribrothers import (
    PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_HABILITADA,
    PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_INCLUIR_CLASSIFICACAO_ATENCAO,
    apagar_override_verificacao_redundancia_secao_markdown_runtime_sqlite_transcribrothers,
    gravar_preferencias_runtime_redundancia_secao_markdown_sqlite_transcribrothers,
    resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers,
    verificacao_redundancia_secao_markdown_desativada_efetiva_e_flag_override_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_verificacao_sustentacao_tutorial_sqlite_transcribrothers import (
    apagar_override_verificacao_sustentacao_tutorial_runtime_sqlite_transcribrothers,
    gravar_verificacao_sustentacao_tutorial_desativada_runtime_sqlite_transcribrothers,
    verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers,
)
from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
    agendar_pipeline_job_em_task_assincrona,
    agendar_regeneracao_apenas_tutorial_markdown_em_task_assincrona,
)
from transcribrothers_backend.modulo_pipeline_regeneracao_markdown_reproducao_bug_transcribrothers import (
    agendar_regeneracao_markdown_reproducao_bug_em_task_assincrona,
)
from transcribrothers_backend.modulo_pipeline_regeneracao_markdown_notas_proposta_funcionalidade_transcribrothers import (
    agendar_regeneracao_markdown_notas_proposta_funcionalidade_em_task_assincrona,
)
from transcribrothers_backend.modulo_pipeline_regeneracao_secao_markdown_tutorial_transcribrothers import (
    CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    agendar_regeneracao_secao_markdown_tutorial_em_task_assincrona,
)
from transcribrothers_backend.modulo_util_job_steps_indicam_notas_proposta_funcionalidade_transcribrothers import (
    job_steps_indicam_notas_proposta_funcionalidade_transcribrothers,
)
from transcribrothers_backend.modulo_util_job_steps_indicam_reproducao_bug_transcribrothers import (
    job_steps_indicam_reproducao_bug_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_extrair_e_substituir_secao_markdown_tutorial_por_heading_nivel2_transcribrothers import (
    extrair_corpo_secao_markdown_nivel2_tutorial_transcribrothers,
    listar_secoes_markdown_nivel2_tutorial_transcribrothers,
    resolver_secao_markdown_nivel2_por_linha_heading_ou_indice_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    listar_modelos_litellm_provisionados_para_interface,
    normalizar_backend_transcricao_audio_configurado,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
    tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy,
    tem_credencial_para_transcricao_no_pipeline,
    validar_e_resolver_modelo_litellm_solicitado_pelo_cliente,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_gitlab_criar_issue_portal_defensoria_gateway_transcribrothers import (
    criar_issue_gitlab_portal_defensoria_gateway_transcribrothers,
    gitlab_criar_issue_configurado_no_ambiente_transcribrothers,
    normalizar_titulo_issue_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_gitlab_comentar_issue_existente_transcribrothers import (
    LIMITE_CARACTERES_CORPO_NOTA_ISSUE_GITLAB_TRANSCRIBROTHERS,
    comentar_issue_gitlab_existente_transcribrothers,
    extrair_destino_issue_gitlab_a_partir_url_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_gitlab_wiki_documentacao_projeto_transcribrothers import (
    criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers,
    gitlab_criar_wiki_configurado_no_ambiente_transcribrothers,
    montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers,
    montar_slug_filho_pagina_wiki_gitlab_transcribrothers,
    montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers,
    montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers,
    pagina_wiki_gitlab_existe_no_projeto_transcribrothers,
    resolver_prefixo_pasta_wiki_gitlab_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers import (
    extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
)
from transcribrothers_backend.modulo_util_listar_nomes_arquivo_png_original_pasta_assets_tutorial_transcribrothers import (
    listar_nomes_arquivo_png_original_na_pasta_assets_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
    mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers,
    proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_salvar_imagem_anexo_contexto_fab_para_assets_markdown_tutorial_job_transcribrothers import (
    salvar_imagem_anexo_contexto_fab_para_assets_markdown_tutorial_job_transcribrothers,
)
from transcribrothers_backend.modulo_salvar_imagem_colada_clipboard_para_assets_markdown_tutorial_job_transcribrothers import (
    mesclar_registro_imagem_colada_clipboard_no_steps_json_transcribrothers,
    salvar_imagem_colada_clipboard_para_assets_markdown_tutorial_job_transcribrothers,
)
from transcribrothers_backend.modulo_util_nomenclatura_e_metadados_anotacao_imagens_tutorial_assets_png_transcribrothers import (
    derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers,
    mesclar_registro_anotacao_apos_gravar_png_anotado_transcribrothers,
    mesclar_registro_exibicao_imagem_tutorial_transcribrothers,
    mesclar_remocao_anotacao_imagem_tutorial_transcribrothers,
    nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers,
    obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers,
    registro_anotacao_imagem_para_resposta_api_transcribrothers,
    substituir_referencia_asset_png_no_markdown_por_nome_arquivo_transcribrothers,
)
from transcribrothers_backend.modulo_staging_video_importacao_recbrothers_transcribrothers import (
    consumir_staging_video_para_destino_job,
    obter_metadados_extras_staging_recbrothers,
    obter_metadados_staging_video_ou_erro_http,
    resolver_caminho_video_staging,
    salvar_upload_video_em_staging_recbrothers_transcribrothers,
)
from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_video_upload_local import (
    ErroExtensaoVideoUploadTranscribrothers,
    extrair_extensao_video_sanitizada_para_upload_local,
)
from transcribrothers_backend.modulo_constante_markdown_inicial_projeto_em_branco_transcribrothers import (
    MARKDOWN_INICIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
    ORIGEM_HISTORICO_TUTORIAL_EDICAO_MANUAL_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_TUTORIAL_EXCLUSAO_ASSET_IMAGEM_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_TUTORIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    ORIGEM_HISTORICO_TUTORIAL_RESTAURACAO_VERSAO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_remover_referencia_imagem_asset_markdown_tutorial_transcribrothers import (
    markdown_tutorial_referencia_imagem_asset_transcribrothers,
    remover_referencia_imagem_asset_do_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
    apagar_todas_versoes_historico_tutorial_markdown_do_job_transcribrothers,
    inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers,
    listar_resumo_versoes_historico_tutorial_markdown_do_job_transcribrothers,
    obter_conteudo_versao_historico_tutorial_markdown_por_id_transcribrothers,
)


class CorpoRegenerarSomenteTutorialMarkdownTranscribrothers(BaseModel):
    instrucoes_revisao_humana: str | None = None
    litellm_model: str | None = None
    revisao_profunda_multifase: bool = False
    caminhos_assets_png_contexto_fab: list[str] | None = None
    textos_contexto_fab: list[str] | None = None


class CorpoRegenerarReproducaoBugMarkdownTranscribrothers(BaseModel):
    instrucoes_revisao_humana: str | None = None
    litellm_model: str | None = None
    documento_autonomo_sem_video: bool = False


class CorpoRegenerarNotasPropostaMarkdownTranscribrothers(BaseModel):
    instrucoes_revisao_humana: str | None = None
    litellm_model: str | None = None
    documento_autonomo_sem_video: bool = False


class CorpoPatchResultMarkdownJobTranscribrothers(BaseModel):
    result_markdown: str


class ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers(BaseModel):
    indice: int
    linha_heading: str


class CorpoRegenerarSecaoMarkdownTutorialTranscribrothers(BaseModel):
    titulo_secao_heading: str | None = None
    indice_secao: int | None = Field(default=None, ge=0)
    instrucoes_revisor: str = Field(..., min_length=1, max_length=16_000)
    litellm_model: str | None = None
    modo_escopo_edicao: Literal["secao_inteira", "trecho_local", "a_partir_de"] = "trecho_local"
    trecho_ancora: str | None = Field(default=None, max_length=32_000)
    interpretar_escopo_automaticamente: bool = True
    caminhos_assets_png_contexto_fab: list[str] | None = None
    textos_contexto_fab: list[str] | None = None


class RespostaUploadImagemAnexoContextoFabProjetoEmBrancoTranscribrothers(BaseModel):
    nome_arquivo: str
    caminho_relativo: str
    job: RespostaJobTranscribrothers


class RespostaExtrairDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers(BaseModel):
    nome_arquivo: str
    texto: str
    truncado: bool = False


class ResumoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers(BaseModel):
    id: int
    criado_em: str | None
    origem: str
    tamanho_caracteres: int
    preview_linha: str


class RespostaConteudoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers(BaseModel):
    markdown: str
    origem: str
    criado_em: str


_LIMITE_BYTES_RESULT_MARKDOWN_JOB_EDICAO_MANUAL_TRANSCRIBROTHERS = 8 * 1024 * 1024


class RespostaJobTranscribrothers(BaseModel):
    id: str
    status: str
    source_kind: str = OrigemEntradaJobTranscribrothers.drive
    drive_url: str
    file_id: str
    error_message: str | None = None
    result_markdown: str | None = None
    steps_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RespostaStagingVideoRecbrothersTranscribrothers(BaseModel):
    staging_id: str
    filename: str
    size_bytes: int
    modo_recbrothers: str | None = None
    cliques_json_presente: bool = False
    total_cliques: int = 0


class RespostaMetadadosStagingVideoRecbrothersTranscribrothers(BaseModel):
    staging_id: str
    filename: str
    size_bytes: int
    ext: str
    created_at: str
    expires_at: str
    modo_recbrothers: str | None = None
    cliques_json_presente: bool = False
    total_cliques: int = 0


def _job_para_resposta(row: JobPipelineTranscribrothers) -> RespostaJobTranscribrothers:
    return RespostaJobTranscribrothers(
        id=row.id,
        status=row.status,
        source_kind=getattr(row, "source_kind", None) or OrigemEntradaJobTranscribrothers.drive,
        drive_url=row.drive_url,
        file_id=row.file_id,
        error_message=row.error_message,
        result_markdown=row.result_markdown,
        steps_json=row.steps_json or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class ResumoJobListaPipelineTranscribrothers(BaseModel):
    """Lista leve para a UI (sem `result_markdown` nem `steps_json`)."""

    id: str
    status: str
    source_kind: str = OrigemEntradaJobTranscribrothers.drive
    drive_url: str
    file_id: str
    tem_resultado_markdown: bool
    titulo_tutorial_markdown_h1: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


def _resumo_job_para_lista(row: JobPipelineTranscribrothers) -> ResumoJobListaPipelineTranscribrothers:
    md = row.result_markdown
    tem_md = isinstance(md, str) and bool(md.strip())
    titulo_h1 = extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers(md) if tem_md else None
    return ResumoJobListaPipelineTranscribrothers(
        id=row.id,
        status=row.status,
        source_kind=getattr(row, "source_kind", None) or OrigemEntradaJobTranscribrothers.drive,
        drive_url=row.drive_url,
        file_id=row.file_id,
        tem_resultado_markdown=tem_md,
        titulo_tutorial_markdown_h1=titulo_h1,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def _diretorio_assets_png_exportados_markdown_do_job(data_dir: Path, job_id: str) -> Path:
    return _diretorio_trabalho_job(data_dir, job_id) / "assets_exportados_para_markdown"


_LIMITE_BYTES_UPLOAD_PNG_ANOTADO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = 12 * 1024 * 1024


def _localizar_arquivo_video_entrada_no_diretorio_job(work: Path) -> Path | None:
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in sorted(work.glob(pattern)):
            if p.is_file():
                return p
    return None


_ASSET_NAME_OK = re.compile(r"^[a-zA-Z0-9._-]+$")


class RespostaConfigPublicaTranscribrothers(BaseModel):
    litellm_models: list[str]
    litellm_model_default: str
    litellm_usa_endpoint_customizado: bool
    litellm_http_verify_ssl: bool
    litellm_ssl_ca_bundle_configurado: bool
    transcricao_backend: str
    transcricao_modelo_multimodal_padrao: str | None = None
    transcricao_multimodal_janela_segundos: int
    transcricao_multimodal_janelas_paralelas_maxima: int
    transcricao_multimodal_formato_audio_inline: str
    transcricao_multimodal_audio_bitrate_kbps: int
    transcricao_multimodal_audio_mono: bool
    transcricao_multimodal_overrides_runtime_sqlite_ativos: bool = False
    tutorial_margem_minima_segundos_entre_links_temporais_captura: float
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado: bool
    tutorial_max_frames_total: int
    tutorial_frame_max_width_px: int
    verificacao_sustentacao_tutorial_habilitada_efetiva: bool = True
    verificacao_sustentacao_tutorial_habilitada_padrao_env: bool = True
    verificacao_sustentacao_tutorial_preferencia_sqlite_definida: bool = False
    verificacao_redundancia_secao_markdown_habilitada_efetiva: bool = True
    verificacao_redundancia_secao_markdown_habilitada_padrao_env: bool = True
    verificacao_redundancia_secao_markdown_preferencia_sqlite_definida: bool = False
    verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva: bool = True
    verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app: bool = True
    verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva: bool = False
    verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app: bool = False
    verificacao_redundancia_secao_correcao_automatica_preferencia_sqlite_definida: bool = False
    gitlab_criar_issue_habilitado: bool = False
    gitlab_create_issue_project_path: str = ""
    gitlab_criar_wiki_habilitado: bool = False
    gitlab_wiki_project_path: str = ""
    gitlab_wiki_slug_prefixo_pasta: str = "workshop"
    ffmpeg_disponivel: bool = False
    ffprobe_disponivel: bool = False


class CorpoCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers(BaseModel):
    """Título + Markdown (description ou job_id no servidor). Imagens exigem job_id."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    job_id: str | None = None
    incluir_imagens_png_markdown: bool = True

    @field_validator("title", mode="before")
    @classmethod
    def _remover_espacos_titulo_issue_gitlab(cls, v: object) -> str:
        return str(v or "").strip()

    @field_validator("description", "job_id", mode="before")
    @classmethod
    def _normalizar_campos_opcionais_corpo_issue_gitlab(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @model_validator(mode="after")
    def _exigir_descricao_ou_job_id(self) -> CorpoCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers:
        if not self.description and not self.job_id:
            raise ValueError("Informe description ou job_id.")
        if self.incluir_imagens_png_markdown and not self.job_id:
            raise ValueError("Para incluir imagens PNG no GitLab, informe job_id.")
        return self


class RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers(BaseModel):
    ok: bool = True
    iid: int
    web_url: str
    issue_url: str
    project: str
    labels: str
    imagens_png_enviadas_gitlab: int = 0
    imagens_png_ignoradas_gitlab: int = 0


class CorpoComentarIssueGitlabDocumentoMarkdownTranscribrothers(BaseModel):
    """URL de issue + Markdown (description ou job_id no servidor). Imagens exigem job_id."""

    issue_url: str = Field(min_length=1)
    description: str | None = None
    job_id: str | None = None
    incluir_imagens_png_markdown: bool = True

    @field_validator("issue_url", mode="before")
    @classmethod
    def _remover_espacos_url_issue_gitlab(cls, v: object) -> str:
        return str(v or "").strip()

    @field_validator("description", "job_id", mode="before")
    @classmethod
    def _normalizar_campos_opcionais_corpo_comentario_gitlab(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @model_validator(mode="after")
    def _exigir_descricao_ou_job_id(self) -> CorpoComentarIssueGitlabDocumentoMarkdownTranscribrothers:
        if not self.description and not self.job_id:
            raise ValueError("Informe description ou job_id.")
        if self.incluir_imagens_png_markdown and not self.job_id:
            raise ValueError("Para incluir imagens PNG no GitLab, informe job_id.")
        return self


class RespostaComentarIssueGitlabDocumentoMarkdownTranscribrothers(BaseModel):
    ok: bool = True
    note_id: int
    note_url: str
    issue_url: str
    project: str
    issue_iid: int
    imagens_png_enviadas_gitlab: int = 0
    imagens_png_ignoradas_gitlab: int = 0


class CorpoCriarPaginaWikiGitlabDocumentacaoTranscribrothers(BaseModel):
    """Título + Markdown (content ou job_id no servidor). Imagens exigem job_id."""

    title: str = Field(min_length=1, max_length=255)
    content: str | None = None
    job_id: str | None = None
    incluir_imagens_png_markdown: bool = True
    prefixo_pasta_wiki: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _remover_espacos_titulo_wiki_gitlab(cls, v: object) -> str:
        return str(v or "").strip()

    @field_validator("content", "job_id", "prefixo_pasta_wiki", mode="before")
    @classmethod
    def _normalizar_campos_opcionais_corpo_wiki_gitlab(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @model_validator(mode="after")
    def _exigir_content_ou_job_id(self) -> CorpoCriarPaginaWikiGitlabDocumentacaoTranscribrothers:
        if not self.content and not self.job_id:
            raise ValueError("Informe content ou job_id.")
        if self.incluir_imagens_png_markdown and not self.job_id:
            raise ValueError("Para incluir imagens PNG no GitLab, informe job_id.")
        return self


class RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers(BaseModel):
    ok: bool = True
    web_url: str
    wiki_url: str
    project: str
    slug: str
    titulo: str
    atualizada: bool = False
    link_adicionado_no_indice_pasta: bool = False
    imagens_png_enviadas_gitlab: int = 0
    imagens_png_ignoradas_gitlab: int = 0


class RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers(BaseModel):
    slug: str
    web_url: str
    wiki_url: str
    project: str
    prefixo_pasta_wiki: str
    web_url_indice_workshop: str
    pagina_destino_ja_existe_no_gitlab: bool


class RespostaInstrucoesPadraoTutorialLitellmTextoUsuarioTranscribrothers(BaseModel):
    """Textos padrão do preâmbulo antes do JSON na mensagem `user` ao LiteLLM (tutorial Markdown)."""

    instrucao_sem_imagens: str
    instrucao_com_imagens: str
    instrucao_sem_imagens_documento_autonomo_sem_video: str
    instrucao_com_imagens_documento_autonomo_sem_video: str


class RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialTranscribrothers(BaseModel):
    """System prompts e instruções fixas no código (somente leitura) para transparência na UI."""

    pipeline_identificador: str = ""
    system_verificacao_sustentacao_tutorial_markdown_vs_transcricao: str
    system_verificacao_redundancia_secao_markdown_entre_secoes: str
    system_revisao_profunda_analista_plano_tutorial: str
    system_revisao_profunda_worker_item_plano_tutorial: str
    system_revisao_profunda_resumo_plano_para_editor_final: str
    instrucao_editor_final_revisao_profunda_consolidacao_markdown: str


class CorpoPatchTranscricaoMultimodalRuntimeTranscribrothers(BaseModel):
    transcricao_multimodal_janela_segundos: int = Field(ge=0, le=86400)
    transcricao_multimodal_janelas_paralelas_maxima: int = Field(ge=1, le=32)
    transcricao_multimodal_formato_audio_inline: Literal["wav", "mp3", "opus", "aac"]
    transcricao_multimodal_audio_bitrate_kbps: int = Field(ge=16, le=320)
    transcricao_multimodal_audio_mono: bool
    tutorial_margem_minima_segundos_entre_links_temporais_captura: float = Field(ge=0.5, le=120.0)
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado: bool


class CorpoPatchVerificacaoSustentacaoTutorialRuntimeTranscribrothers(BaseModel):
    """Persiste na base se o passo Auditor (verificação) deve executar após gerar o tutorial."""

    verificacao_sustentacao_tutorial_habilitada: bool


class CorpoPatchVerificacaoRedundanciaSecaoMarkdownRuntimeTranscribrothers(BaseModel):
    """Persiste na base preferências de redundância na edição por seção (auditor e correção automática)."""

    verificacao_redundancia_secao_markdown_habilitada: bool
    verificacao_redundancia_secao_correcao_automatica_habilitada: bool
    verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao: bool


def _resolver_modelo_litellm_para_job_ou_erro_http_400(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    modelo_solicitado: str | None,
) -> str:
    try:
        return validar_e_resolver_modelo_litellm_solicitado_pelo_cliente(cfg, modelo_solicitado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@asynccontextmanager
async def lifespan_transcribrothers_app(app: FastAPI):
    cfg = obter_configuracao()
    data_dir = cfg.transcribrothers_data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "transcribrothers.sqlite3"
    url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    engine = criar_engine_sqlite_async(url)
    await inicializar_banco(engine)
    session_factory = criar_session_factory(engine)
    app.state.cfg = cfg
    app.state.session_factory = session_factory
    app.state.data_dir = data_dir
    yield
    await engine.dispose()


app = FastAPI(title="Transcribrothers API", lifespan=lifespan_transcribrothers_app)


@app.middleware("http")
async def adicionar_cabecalhos_seguranca_minimos(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


def _registrar_cors(cfg: ConfiguracaoAmbienteTranscribrothers) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins_list(),
        allow_origin_regex=r"^chrome-extension://.*$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


_cfg_inicial = obter_configuracao()
_registrar_cors(_cfg_inicial)


def obter_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def obter_data_dir(request: Request) -> Path:
    return request.app.state.data_dir


def obter_cfg(request: Request) -> ConfiguracaoAmbienteTranscribrothers:
    return request.app.state.cfg


SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(obter_session_factory)]
DataDirDep = Annotated[Path, Depends(obter_data_dir)]


async def _montar_resposta_config_publica_transcribrothers(
    request: Request,
) -> RespostaConfigPublicaTranscribrothers:
    cfg = obter_cfg(request)
    session_factory = obter_session_factory(request)
    async with session_factory() as session:
        overrides = await obter_overrides_transcricao_multimodal_runtime_do_sqlite_transcribrothers(session)
        desativada_efetiva, sqlite_verif = (
            await verificacao_sustentacao_tutorial_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
                session,
                cfg,
            )
        )
        desativada_redundancia_efetiva, sqlite_redundancia = (
            await verificacao_redundancia_secao_markdown_desativada_efetiva_e_flag_override_sqlite_transcribrothers(
                session,
                cfg,
            )
        )
        prefs_redundancia = await resolver_preferencias_efetivas_runtime_redundancia_secao_markdown_transcribrothers(
            session,
            cfg,
        )
    janela_ef, paralelas_ef, formato_ef, bitrate_ef, mono_ef = (
        resolver_janela_paralelas_formato_bitrate_mono_efetivos_com_overrides_sqlite_transcribrothers(
            int(cfg.transcricao_multimodal_janela_segundos),
            int(cfg.transcricao_multimodal_janelas_paralelas_maxima),
            str(cfg.transcricao_multimodal_formato_audio_inline),
            int(cfg.transcricao_multimodal_audio_bitrate_kbps),
            bool(cfg.transcricao_multimodal_audio_mono),
            overrides,
        )
    )
    margem_links_ef, planejamento_captura_ef = (
        resolver_tutorial_margem_e_planejamento_captura_efetivos_com_overrides_sqlite_transcribrothers(
            float(cfg.tutorial_margem_minima_segundos_entre_links_temporais_captura),
            bool(cfg.tutorial_planejamento_instantes_captura_frames_litellm_habilitado),
            overrides,
        )
    )
    modelos = listar_modelos_litellm_provisionados_para_interface(cfg)
    if not modelos and (cfg.litellm_model or "").strip():
        modelos = [(cfg.litellm_model or "").strip()]
    mm = resolver_modelo_para_transcricao_litellm_multimodal_audio(cfg) or None
    cfg_gitlab = obter_configuracao()
    return RespostaConfigPublicaTranscribrothers(
        litellm_models=modelos,
        litellm_model_default=(cfg.litellm_model or "").strip() or (modelos[0] if modelos else ""),
        litellm_usa_endpoint_customizado=bool((cfg.litellm_endpoint or "").strip()),
        litellm_http_verify_ssl=bool(cfg.litellm_http_verify_ssl),
        litellm_ssl_ca_bundle_configurado=bool((cfg.litellm_ssl_ca_bundle or "").strip()),
        transcricao_backend=normalizar_backend_transcricao_audio_configurado(cfg),
        transcricao_modelo_multimodal_padrao=mm,
        transcricao_multimodal_janela_segundos=janela_ef,
        transcricao_multimodal_janelas_paralelas_maxima=paralelas_ef,
        transcricao_multimodal_formato_audio_inline=formato_ef,
        transcricao_multimodal_audio_bitrate_kbps=int(bitrate_ef),
        transcricao_multimodal_audio_mono=bool(mono_ef),
        transcricao_multimodal_overrides_runtime_sqlite_ativos=overrides_transcricao_multimodal_sqlite_tem_alguma_chave_preenchida_transcribrothers(
            overrides
        ),
        tutorial_margem_minima_segundos_entre_links_temporais_captura=float(margem_links_ef),
        tutorial_planejamento_instantes_captura_frames_litellm_habilitado=bool(planejamento_captura_ef),
        tutorial_max_frames_total=int(cfg.tutorial_max_frames_total),
        tutorial_frame_max_width_px=int(cfg.tutorial_frame_max_width_px),
        verificacao_sustentacao_tutorial_habilitada_efetiva=not bool(desativada_efetiva),
        verificacao_sustentacao_tutorial_habilitada_padrao_env=not bool(
            cfg.verificacao_sustentacao_tutorial_desativada
        ),
        verificacao_sustentacao_tutorial_preferencia_sqlite_definida=bool(sqlite_verif),
        verificacao_redundancia_secao_markdown_habilitada_efetiva=not bool(desativada_redundancia_efetiva),
        verificacao_redundancia_secao_markdown_habilitada_padrao_env=not bool(
            cfg.verificacao_redundancia_secao_markdown_desativada
        ),
        verificacao_redundancia_secao_markdown_preferencia_sqlite_definida=bool(sqlite_redundancia),
        verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva=bool(
            prefs_redundancia.correcao_automatica_habilitada
        ),
        verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app=bool(
            PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_HABILITADA
        ),
        verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva=bool(
            prefs_redundancia.correcao_automatica_incluir_classificacao_atencao
        ),
        verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app=bool(
            PADRAO_APP_CORRECAO_AUTOMATICA_REDUNDANCIA_SECAO_INCLUIR_CLASSIFICACAO_ATENCAO
        ),
        verificacao_redundancia_secao_correcao_automatica_preferencia_sqlite_definida=bool(
            prefs_redundancia.preferencia_sqlite_correcao_habilitada_definida
            or prefs_redundancia.preferencia_sqlite_correcao_incluir_atencao_definida
        ),
        gitlab_criar_issue_habilitado=gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg_gitlab),
        gitlab_create_issue_project_path=(cfg_gitlab.gitlab_create_issue_project_path or "").strip(),
        gitlab_criar_wiki_habilitado=gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(cfg_gitlab),
        gitlab_wiki_project_path=(cfg_gitlab.gitlab_wiki_project_path or "").strip(),
        gitlab_wiki_slug_prefixo_pasta=(cfg_gitlab.gitlab_wiki_slug_prefixo_pasta or "workshop").strip()
        or "workshop",
        ffmpeg_disponivel=ffmpeg_disponivel_transcribrothers(cfg),
        ffprobe_disponivel=ffprobe_disponivel_transcribrothers(cfg),
    )


@app.post(
    "/api/gitlab/issues/create-in-project",
    response_model=RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers,
)
async def criar_issue_gitlab_portal_defensoria_gateway_api_transcribrothers(
    corpo: CorpoCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers:
    from transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers import (
        preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers,
    )

    cfg = obter_configuracao()
    if not gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "GitLab não configurado no servidor. Defina GITLAB_BASE_URL e GITLAB_TOKEN "
                "(por exemplo em env.local na raiz do repositório) e reinicie o uvicorn."
            ),
        )
    try:
        titulo = normalizar_titulo_issue_gitlab_transcribrothers(corpo.title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    steps_json: dict | None = None
    markdown_fonte: str
    if corpo.job_id:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, corpo.job_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Job não encontrado.")
            markdown_fonte = (row.result_markdown or "").strip()
            steps_json = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    else:
        markdown_fonte = (corpo.description or "").strip()

    if not markdown_fonte:
        raise HTTPException(status_code=400, detail="Markdown do documento vazio.")

    imagens_enviadas = 0
    imagens_ignoradas = 0
    descricao = markdown_fonte
    if corpo.incluir_imagens_png_markdown and corpo.job_id:
        assets_dir = _diretorio_assets_png_exportados_markdown_do_job(data_dir, corpo.job_id)
        try:
            descricao, imagens_enviadas, imagens_ignoradas = (
                await preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers(
                    cfg,
                    markdown_fonte,
                    assets_dir,
                    steps_json,
                    incluir_imagens_png_markdown=True,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

    try:
        issue = await criar_issue_gitlab_portal_defensoria_gateway_transcribrothers(
            cfg,
            titulo=titulo,
            descricao_markdown=descricao,
            timeout_segundos=120.0 if imagens_enviadas > 0 else 60.0,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    web_url = str(issue.get("web_url") or "").strip()
    if not web_url:
        raise HTTPException(status_code=502, detail="GitLab não devolveu web_url da issue criada.")
    iid_raw = issue.get("iid")
    try:
        iid = int(iid_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise HTTPException(status_code=502, detail="GitLab não devolveu iid válido da issue criada.") from None

    labels = (cfg.gitlab_create_issue_default_labels or "squad::bravo").strip() or "squad::bravo"
    project = (cfg.gitlab_create_issue_project_path or "").strip()
    return RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers(
        ok=True,
        iid=iid,
        web_url=web_url,
        issue_url=web_url,
        project=project,
        labels=labels,
        imagens_png_enviadas_gitlab=imagens_enviadas,
        imagens_png_ignoradas_gitlab=imagens_ignoradas,
    )


@app.post(
    "/api/gitlab/issues/comment-in-existing-issue",
    response_model=RespostaComentarIssueGitlabDocumentoMarkdownTranscribrothers,
)
async def comentar_issue_gitlab_documento_markdown_api_transcribrothers(
    corpo: CorpoComentarIssueGitlabDocumentoMarkdownTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaComentarIssueGitlabDocumentoMarkdownTranscribrothers:
    from transcribrothers_backend.modulo_util_reescrever_markdown_tutorial_assets_png_com_urls_upload_gitlab_transcribrothers import (
        preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers,
    )

    cfg = obter_configuracao()
    if not gitlab_criar_issue_configurado_no_ambiente_transcribrothers(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "GitLab não configurado no servidor. Defina GITLAB_BASE_URL e GITLAB_TOKEN "
                "(por exemplo em env.local na raiz do repositório) e reinicie o uvicorn."
            ),
        )
    try:
        destino = extrair_destino_issue_gitlab_a_partir_url_transcribrothers(cfg, corpo.issue_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    steps_json: dict | None = None
    markdown_fonte: str
    if corpo.job_id:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, corpo.job_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Job não encontrado.")
            markdown_fonte = (row.result_markdown or "").strip()
            steps_json = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    else:
        markdown_fonte = (corpo.description or "").strip()

    if not markdown_fonte:
        raise HTTPException(status_code=400, detail="Markdown do documento vazio.")
    if len(markdown_fonte) > LIMITE_CARACTERES_CORPO_NOTA_ISSUE_GITLAB_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail="Markdown do documento excede o limite de 1.000.000 caracteres do GitLab.",
        )

    imagens_enviadas = 0
    imagens_ignoradas = 0
    descricao = markdown_fonte
    if corpo.incluir_imagens_png_markdown and corpo.job_id:
        assets_dir = _diretorio_assets_png_exportados_markdown_do_job(data_dir, corpo.job_id)
        try:
            descricao, imagens_enviadas, imagens_ignoradas = (
                await preparar_descricao_markdown_issue_gitlab_com_upload_imagens_assets_png_transcribrothers(
                    cfg,
                    markdown_fonte,
                    assets_dir,
                    steps_json,
                    incluir_imagens_png_markdown=True,
                    project_path_gitlab=destino.project_path,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

    try:
        note = await comentar_issue_gitlab_existente_transcribrothers(
            cfg,
            issue_url=destino.issue_url,
            corpo_markdown=descricao,
            timeout_segundos=120.0 if imagens_enviadas > 0 else 60.0,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    note_id_raw = note.get("id")
    try:
        note_id = int(note_id_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise HTTPException(status_code=502, detail="GitLab não devolveu id válido do comentário.") from None
    note_url = str(note.get("url") or "").strip() or f"{destino.issue_url}#note_{note_id}"

    return RespostaComentarIssueGitlabDocumentoMarkdownTranscribrothers(
        ok=True,
        note_id=note_id,
        note_url=note_url,
        issue_url=destino.issue_url,
        project=destino.project_path,
        issue_iid=destino.issue_iid,
        imagens_png_enviadas_gitlab=imagens_enviadas,
        imagens_png_ignoradas_gitlab=imagens_ignoradas,
    )


@app.get(
    "/api/gitlab/wikis/preview-create-page-url",
    response_model=RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers,
)
async def preview_url_pagina_wiki_gitlab_documentacao_api_transcribrothers(
    title: str,
    job_id: str,
    prefixo_pasta_wiki: str | None = None,
) -> RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers:
    """URL prevista {pasta}/… e se a subpágina já existe no GitLab (somente leitura)."""
    cfg = obter_configuracao()
    if not gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "GitLab wiki não configurado no servidor. Defina GITLAB_BASE_URL, GITLAB_TOKEN e "
                "GITLAB_WIKI_PROJECT_PATH (por exemplo em env.local na raiz do repositório) e reinicie o uvicorn."
            ),
        )
    job_id_norm = (job_id or "").strip()
    if not job_id_norm:
        raise HTTPException(status_code=400, detail="job_id obrigatório.")
    try:
        titulo = normalizar_titulo_issue_gitlab_transcribrothers(title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    try:
        prefixo = resolver_prefixo_pasta_wiki_gitlab_transcribrothers(cfg, prefixo_pasta_wiki)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    slug_filho = montar_slug_filho_pagina_wiki_gitlab_transcribrothers(titulo)
    slug_api = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(
        cfg, titulo, prefixo_pasta=prefixo
    )
    web_url = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
        cfg, slug_filho, prefixo_pasta=prefixo
    )
    web_indice = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(
        cfg, prefixo_pasta=prefixo
    )
    existe = await pagina_wiki_gitlab_existe_no_projeto_transcribrothers(cfg, slug_api)
    project = (cfg.gitlab_wiki_project_path or "").strip()
    return RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers(
        slug=slug_filho,
        web_url=web_url,
        wiki_url=web_url,
        project=project,
        prefixo_pasta_wiki=prefixo,
        web_url_indice_workshop=web_indice,
        pagina_destino_ja_existe_no_gitlab=existe,
    )


@app.post(
    "/api/gitlab/wikis/create-page-in-project",
    response_model=RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers,
)
async def criar_pagina_wiki_gitlab_documentacao_api_transcribrothers(
    corpo: CorpoCriarPaginaWikiGitlabDocumentacaoTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers:
    from transcribrothers_backend.modulo_util_preparar_markdown_pagina_wiki_gitlab_com_upload_imagens_assets_png_transcribrothers import (
        preparar_conteudo_markdown_pagina_wiki_gitlab_com_upload_imagens_assets_png_transcribrothers,
    )

    cfg = obter_configuracao()
    if not gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "GitLab wiki não configurado no servidor. Defina GITLAB_BASE_URL, GITLAB_TOKEN e "
                "GITLAB_WIKI_PROJECT_PATH (por exemplo em env.local na raiz do repositório) e reinicie o uvicorn."
            ),
        )
    try:
        titulo = normalizar_titulo_issue_gitlab_transcribrothers(corpo.title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    steps_json: dict | None = None
    markdown_fonte: str
    if corpo.job_id:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, corpo.job_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Job não encontrado.")
            markdown_fonte = (row.result_markdown or "").strip()
            steps_json = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    else:
        markdown_fonte = (corpo.content or "").strip()

    if not markdown_fonte:
        raise HTTPException(status_code=400, detail="Markdown do documento vazio.")

    imagens_enviadas = 0
    imagens_ignoradas = 0
    conteudo = markdown_fonte
    if corpo.incluir_imagens_png_markdown and corpo.job_id:
        assets_dir = _diretorio_assets_png_exportados_markdown_do_job(data_dir, corpo.job_id)
        try:
            conteudo, imagens_enviadas, imagens_ignoradas = (
                await preparar_conteudo_markdown_pagina_wiki_gitlab_com_upload_imagens_assets_png_transcribrothers(
                    cfg,
                    markdown_fonte,
                    assets_dir,
                    steps_json,
                    incluir_imagens_png_markdown=True,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

    if not corpo.job_id:
        raise HTTPException(
            status_code=400,
            detail="job_id obrigatório para exportar para a wiki (slug {pasta}/… e imagens em assets/).",
        )
    try:
        prefixo = resolver_prefixo_pasta_wiki_gitlab_transcribrothers(cfg, corpo.prefixo_pasta_wiki)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    slug_destino = montar_slug_api_completo_pagina_wiki_gitlab_transcribrothers(
        cfg, titulo, prefixo_pasta=prefixo
    )
    try:
        wiki = await criar_ou_atualizar_pagina_wiki_gitlab_documentacao_transcribrothers(
            cfg,
            titulo=titulo,
            conteudo_markdown=conteudo,
            slug_completo=slug_destino,
            timeout_segundos=120.0 if imagens_enviadas > 0 else 60.0,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    slug_filho_resposta = str(
        wiki.get("slug_filho") or montar_slug_filho_pagina_wiki_gitlab_transcribrothers(titulo)
    ).strip()
    slug_resposta = str(wiki.get("slug") or slug_destino).strip() or slug_destino
    web_url = montar_web_url_pagina_wiki_gitlab_documentacao_transcribrothers(
        cfg, slug_filho_resposta, prefixo_pasta=prefixo
    )
    project = (cfg.gitlab_wiki_project_path or "").strip()
    return RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers(
        ok=True,
        web_url=web_url,
        wiki_url=web_url,
        project=project,
        slug=slug_filho_resposta,
        titulo=titulo,
        atualizada=bool(wiki.get("atualizada")),
        link_adicionado_no_indice_pasta=bool(wiki.get("link_adicionado_no_indice_pasta")),
        imagens_png_enviadas_gitlab=imagens_enviadas,
        imagens_png_ignoradas_gitlab=imagens_ignoradas,
    )


@app.get("/api/config/transcribrothers", response_model=RespostaConfigPublicaTranscribrothers)
async def obter_configuracao_publica_para_interface_transcribrothers(
    request: Request,
) -> RespostaConfigPublicaTranscribrothers:
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.get(
    "/api/config/transcribrothers/tutorial-litellm-instrucoes-padrao",
    response_model=RespostaInstrucoesPadraoTutorialLitellmTextoUsuarioTranscribrothers,
)
async def obter_textos_padrao_instrucao_prefixo_litellm_tutorial_markdown_transcribrothers() -> (
    RespostaInstrucoesPadraoTutorialLitellmTextoUsuarioTranscribrothers
):
    return RespostaInstrucoesPadraoTutorialLitellmTextoUsuarioTranscribrothers(
        instrucao_sem_imagens=INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
        instrucao_com_imagens=INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
        instrucao_sem_imagens_documento_autonomo_sem_video=(
            INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS
        ),
        instrucao_com_imagens_documento_autonomo_sem_video=(
            INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS
        ),
    )


@app.get(
    "/api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial",
    response_model=RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialTranscribrothers,
)
async def obter_prompts_fixos_revisao_profunda_e_verificacao_sustentacao_tutorial_transcribrothers() -> (
    RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialTranscribrothers
):
    """Textos fixos no código-fonte do backend (transparência; não expõe segredos nem dados de jobs)."""
    return RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialTranscribrothers(
        pipeline_identificador=IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
        system_verificacao_sustentacao_tutorial_markdown_vs_transcricao=(
            SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS
        ),
        system_verificacao_redundancia_secao_markdown_entre_secoes=(
            SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS
        ),
        system_revisao_profunda_analista_plano_tutorial=SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
        system_revisao_profunda_worker_item_plano_tutorial=(
            SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS
        ),
        system_revisao_profunda_resumo_plano_para_editor_final=(
            SYSTEM_PROMPT_RESUMO_PLANO_PARA_EDITOR_FINAL_TRANSCRIBROTHERS
        ),
        instrucao_editor_final_revisao_profunda_consolidacao_markdown=(
            INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS
        ),
    )


@app.patch("/api/config/transcribrothers/transcricao-multimodal-runtime", response_model=RespostaConfigPublicaTranscribrothers)
async def atualizar_configuracao_runtime_transcricao_multimodal_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchTranscricaoMultimodalRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await gravar_overrides_transcricao_multimodal_runtime_no_sqlite_transcribrothers(
            session,
            transcricao_multimodal_janela_segundos=int(body.transcricao_multimodal_janela_segundos),
            transcricao_multimodal_janelas_paralelas_maxima=int(
                body.transcricao_multimodal_janelas_paralelas_maxima
            ),
            transcricao_multimodal_formato_audio_inline=str(body.transcricao_multimodal_formato_audio_inline),
            transcricao_multimodal_audio_bitrate_kbps=int(body.transcricao_multimodal_audio_bitrate_kbps),
            transcricao_multimodal_audio_mono=bool(body.transcricao_multimodal_audio_mono),
            tutorial_margem_minima_segundos_entre_links_temporais_captura=float(
                body.tutorial_margem_minima_segundos_entre_links_temporais_captura
            ),
            tutorial_planejamento_instantes_captura_frames_litellm_habilitado=bool(
                body.tutorial_planejamento_instantes_captura_frames_litellm_habilitado
            ),
        )
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.patch(
    "/api/config/transcribrothers/verificacao-sustentacao-tutorial-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def atualizar_preferencia_runtime_verificacao_sustentacao_tutorial_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchVerificacaoSustentacaoTutorialRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await gravar_verificacao_sustentacao_tutorial_desativada_runtime_sqlite_transcribrothers(
            session,
            desativada=not bool(body.verificacao_sustentacao_tutorial_habilitada),
        )
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.delete(
    "/api/config/transcribrothers/verificacao-sustentacao-tutorial-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def apagar_preferencia_runtime_verificacao_sustentacao_tutorial_volta_ao_env_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await apagar_override_verificacao_sustentacao_tutorial_runtime_sqlite_transcribrothers(session)
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.patch(
    "/api/config/transcribrothers/verificacao-redundancia-secao-markdown-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def atualizar_preferencia_runtime_verificacao_redundancia_secao_markdown_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchVerificacaoRedundanciaSecaoMarkdownRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await gravar_preferencias_runtime_redundancia_secao_markdown_sqlite_transcribrothers(
            session,
            verificacao_desativada=not bool(body.verificacao_redundancia_secao_markdown_habilitada),
            correcao_automatica_habilitada=bool(
                body.verificacao_redundancia_secao_correcao_automatica_habilitada
            ),
            correcao_automatica_incluir_classificacao_atencao=bool(
                body.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao
            ),
        )
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.delete(
    "/api/config/transcribrothers/verificacao-redundancia-secao-markdown-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def apagar_preferencia_runtime_verificacao_redundancia_secao_markdown_volta_ao_env_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await apagar_override_verificacao_redundancia_secao_markdown_runtime_sqlite_transcribrothers(session)
    return await _montar_resposta_config_publica_transcribrothers(request)


_DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS = frozenset(
    {"gerar_tutorial", "reproducao_bug", "notas_proposta_funcionalidade"},
)


@app.post("/api/staging/upload", response_model=RespostaStagingVideoRecbrothersTranscribrothers)
async def criar_staging_video_importacao_recbrothers_transcribrothers(
    request: Request,
    data_dir: DataDirDep,
    video: UploadFile = File(..., description="Vídeo temporário (ex.: gravação RecBrothers)"),
    cliques_json: Annotated[UploadFile | None, File(description="JSON de cliques (modo demonstrar bug)")] = None,
    modo_recbrothers: Annotated[str | None, Form()] = None,
) -> RespostaStagingVideoRecbrothersTranscribrothers:
    cfg = obter_cfg(request)
    meta, extras = await salvar_upload_video_em_staging_recbrothers_transcribrothers(
        data_dir=data_dir,
        video=video,
        max_video_bytes=int(cfg.max_video_bytes),
        ttl_horas=float(cfg.staging_video_ttl_horas),
        cliques_json=cliques_json,
        modo_recbrothers=modo_recbrothers,
    )
    return RespostaStagingVideoRecbrothersTranscribrothers(
        staging_id=meta.staging_id,
        filename=meta.filename,
        size_bytes=meta.size_bytes,
        modo_recbrothers=extras.get("modo_recbrothers"),
        cliques_json_presente=bool(extras.get("cliques_json_presente")),
        total_cliques=int(extras.get("total_cliques") or 0),
    )


@app.get(
    "/api/staging/{staging_id}",
    response_model=RespostaMetadadosStagingVideoRecbrothersTranscribrothers,
)
async def obter_metadados_staging_video_importacao_recbrothers_transcribrothers(
    staging_id: str,
    data_dir: DataDirDep,
) -> RespostaMetadadosStagingVideoRecbrothersTranscribrothers:
    meta = obter_metadados_staging_video_ou_erro_http(data_dir, staging_id)
    extras = obter_metadados_extras_staging_recbrothers(data_dir, staging_id)
    return RespostaMetadadosStagingVideoRecbrothersTranscribrothers(
        staging_id=meta.staging_id,
        filename=meta.filename,
        size_bytes=meta.size_bytes,
        ext=meta.ext,
        created_at=meta.created_at,
        expires_at=meta.expires_at,
        modo_recbrothers=extras.get("modo_recbrothers"),
        cliques_json_presente=bool(extras.get("cliques_json_presente")),
        total_cliques=int(extras.get("total_cliques") or 0),
    )


@app.get("/api/staging/{staging_id}/video")
async def obter_arquivo_video_staging_importacao_recbrothers_transcribrothers(
    staging_id: str,
    data_dir: DataDirDep,
) -> FileResponse:
    meta, caminho = resolver_caminho_video_staging(data_dir, staging_id)
    media = media_type_para_video_por_extensao(meta.ext)
    return FileResponse(
        path=caminho,
        media_type=media,
        filename=meta.filename,
    )


@app.post("/api/jobs/upload", response_model=RespostaJobTranscribrothers)
async def criar_novo_job_pipeline_a_partir_de_upload_video_arquivo_local(
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    video: Annotated[UploadFile | None, File(description="Arquivo de vídeo do seu computador")] = None,
    staging_id: Annotated[str | None, Form()] = None,
    litellm_model: Annotated[str | None, Form()] = None,
    tutorial_litellm_instrucao_prefixo: Annotated[str | None, Form()] = None,
    destino_apos_transcricao: Annotated[str | None, Form()] = None,
    cliques_json: Annotated[
        UploadFile | None,
        File(description="JSON opcional de cliques (reproducao_bug)"),
    ] = None,
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_para_transcricao_no_pipeline(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Transcrição: configure o proxy LiteLLM com LITELLM_API_KEY e LITELLM_ENDPOINT. "
                "Modo openai_whisper exige POST /v1/audio/transcriptions no gateway. "
                "Modo litellm_multimodal_audio exige POST /v1/chat/completions e um modelo gemini/ "
                "(TRANSCRICAO_LITELLM_MODELO ou LITELLM_MODELOS_PROVISIONADOS / LITELLM_MODEL)."
            ),
        )
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "O job inclui geração do tutorial no proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                "(POST /v1/chat/completions). Não há fluxo sem proxy neste projeto."
            ),
        )
    staging_id_norm = (staging_id or "").strip()
    nome_arquivo_video = (video.filename or "").strip() if video is not None else ""
    tem_staging = bool(staging_id_norm)
    tem_video = bool(nome_arquivo_video)
    if tem_staging and tem_video:
        raise HTTPException(
            status_code=400,
            detail="Informe apenas video ou staging_id, não ambos.",
        )
    if not tem_staging and not tem_video:
        raise HTTPException(
            status_code=400,
            detail="Envie o arquivo video ou um staging_id de importação RecBrothers.",
        )

    modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, litellm_model)

    try:
        instr_norm = normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers(
            tutorial_litellm_instrucao_prefixo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    destino_pipeline = (destino_apos_transcricao or "gerar_tutorial").strip()
    if destino_pipeline not in _DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"destino_apos_transcricao inválido: {destino_pipeline!r}. "
                f"Valores aceitos: {', '.join(sorted(_DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS))}."
            ),
        )

    nome_cliques_json = (cliques_json.filename or "").strip() if cliques_json is not None else ""
    if nome_cliques_json and destino_pipeline != "reproducao_bug":
        raise HTTPException(
            status_code=400,
            detail="JSON de cliques só pode ser enviado com destino_apos_transcricao=reproducao_bug.",
        )

    job_id = novo_id_job()
    work = _diretorio_trabalho_job(data_dir, job_id)
    work.mkdir(parents=True, exist_ok=True)

    importado_recbrothers_staging_id: str | None = None
    extras_staging: dict = {}
    total_cliques_reproducao_bug = 0
    if tem_staging:
        meta_staging = obter_metadados_staging_video_ou_erro_http(data_dir, staging_id_norm)
        destino_video = work / f"video_entrada_arquivo_local{meta_staging.ext}"
        nome_original, total, ext, extras_staging = consumir_staging_video_para_destino_job(
            data_dir,
            staging_id_norm,
            destino_video,
        )
        importado_recbrothers_staging_id = staging_id_norm
        total_cliques_reproducao_bug = int(extras_staging.get("total_cliques") or 0)
    else:
        nome_original = video.filename or "video.mp4"  # type: ignore[union-attr]
        try:
            ext = extrair_extensao_video_sanitizada_para_upload_local(nome_original)
        except ErroExtensaoVideoUploadTranscribrothers as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        destino_video = work / f"video_entrada_arquivo_local{ext}"
        max_b = int(cfg.max_video_bytes)
        chunk_size = 1024 * 1024
        total = 0
        try:
            with destino_video.open("wb") as f:
                while True:
                    bloco = await video.read(chunk_size)  # type: ignore[union-attr]
                    if not bloco:
                        break
                    total += len(bloco)
                    if total > max_b:
                        destino_video.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=413,
                            detail=f"Arquivo excede o limite de {max_b} bytes.",
                        )
                    f.write(bloco)
        finally:
            await video.close()  # type: ignore[union-attr]
        if cliques_json is not None and nome_cliques_json:
            from transcribrothers_backend.modulo_util_validar_e_gravar_json_cliques_reproducao_bug_job_transcribrothers import (
                validar_e_gravar_upload_cliques_json_reproducao_bug_job_transcribrothers,
            )

            total_cliques_reproducao_bug = (
                await validar_e_gravar_upload_cliques_json_reproducao_bug_job_transcribrothers(
                    work,
                    cliques_json,
                )
            )

    duracao_video_segundos_ffprobe = await obter_duracao_video_segundos_via_ffprobe(destino_video)

    async with session_factory() as session:
        steps_json = {
            "source": OrigemEntradaJobTranscribrothers.upload_local,
            "original_filename": nome_original,
            "saved_as": destino_video.name,
            "bytes_written": total,
            "litellm_model": modelo_litellm,
            "destino_apos_transcricao": destino_pipeline,
        }
        if duracao_video_segundos_ffprobe > 0:
            steps_json["duracao_video_segundos"] = round(float(duracao_video_segundos_ffprobe), 3)
        if instr_norm is not None:
            steps_json["tutorial_litellm_instrucao_prefixo_custom"] = instr_norm
        if importado_recbrothers_staging_id:
            steps_json["importado_recbrothers_staging_id"] = importado_recbrothers_staging_id
        if destino_pipeline == "reproducao_bug":
            steps_json["reproducao_bug_total_cliques"] = total_cliques_reproducao_bug
            if total_cliques_reproducao_bug <= 0:
                steps_json["reproducao_bug_sem_json_cliques"] = True
            steps_json["modo_recbrothers"] = extras_staging.get("modo_recbrothers")
        row = JobPipelineTranscribrothers(
            id=job_id,
            status=StatusJobTranscribrothers.pending.value,
            source_kind=OrigemEntradaJobTranscribrothers.upload_local,
            drive_url=f"Arquivo local: {nome_original}",
            file_id="-",
            error_message=None,
            result_markdown=None,
            steps_json=steps_json,
        )
        session.add(row)
        await session.commit()

    agendar_pipeline_job_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
    )

    async with session_factory() as session:
        created = await session.get(JobPipelineTranscribrothers, job_id)
        assert created is not None
        return _job_para_resposta(created)


@app.post("/api/jobs/projeto-em-branco", response_model=RespostaJobTranscribrothers)
async def criar_job_projeto_em_branco_sem_video_nem_pipeline_transcribrothers(
    data_dir: DataDirDep,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    """Cria projeto concluído com Markdown inicial, pasta de assets e sem transcrição."""
    job_id = novo_id_job()
    work = _diretorio_trabalho_job(data_dir, job_id)
    work.mkdir(parents=True, exist_ok=True)
    _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id).mkdir(parents=True, exist_ok=True)

    markdown_inicial = MARKDOWN_INICIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS
    caminho_md = work / "tutorial_gerado_transcribrothers.md"
    caminho_md.write_text(markdown_inicial, encoding="utf-8")

    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        montar_snapshot_regeneracao_tutorial_minimo_projeto_em_branco_transcribrothers,
    )

    steps_json = {
        "source": OrigemEntradaJobTranscribrothers.projeto_em_branco,
        "destino_apos_transcricao": "projeto_em_branco",
        "projeto_em_branco": True,
        "regeneracao_tutorial_snapshot": (
            montar_snapshot_regeneracao_tutorial_minimo_projeto_em_branco_transcribrothers()
        ),
    }

    async with session_factory() as session:
        row = JobPipelineTranscribrothers(
            id=job_id,
            status=StatusJobTranscribrothers.completed.value,
            source_kind=OrigemEntradaJobTranscribrothers.projeto_em_branco,
            drive_url="Projeto em branco",
            file_id="-",
            error_message=None,
            result_markdown=markdown_inicial,
            steps_json=steps_json,
        )
        session.add(row)
        await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=markdown_inicial,
            origem=ORIGEM_HISTORICO_TUTORIAL_PROJETO_EM_BRANCO_TRANSCRIBROTHERS,
        )
        await session.commit()

    async with session_factory() as session:
        created = await session.get(JobPipelineTranscribrothers, job_id)
        assert created is not None
        return _job_para_resposta(created)


@app.get("/api/jobs", response_model=list[ResumoJobListaPipelineTranscribrothers])
async def listar_jobs_recentes_do_pipeline_transcribrothers(
    session_factory: SessionFactoryDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 40,
) -> list[ResumoJobListaPipelineTranscribrothers]:
    async with session_factory() as session:
        stmt = (
            select(JobPipelineTranscribrothers)
            .order_by(JobPipelineTranscribrothers.updated_at.desc())
            .limit(int(limit))
        )
        rows = (await session.scalars(stmt)).all()
    return [_resumo_job_para_lista(r) for r in rows]


@app.delete("/api/jobs/{job_id}")
async def apagar_job_e_pasta_trabalho_no_disco_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, bool]:
    """Remove o registro na base e a pasta `data/jobs/{id}/`.

    Jobs em andamento: solicita cancelamento cooperativo do pipeline (se ainda estiver
    rodando no mesmo processo) e apaga de qualquer forma — útil para jobs travados ou
    após reinício do servidor.
    """
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
            StatusJobTranscribrothers.cancelled.value,
        ):
            marcar_cancelamento_pipeline_solicitado_para_job_transcribrothers(job_id)
        await apagar_todas_versoes_historico_tutorial_markdown_do_job_transcribrothers(session, job_id)
        await session.delete(row)
        await session.commit()
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
    work = _diretorio_trabalho_job(data_dir, job_id)
    if work.is_dir():
        shutil.rmtree(work, ignore_errors=True)
    return {"ok": True}


_FASES_REGENERACAO_AGENDADA_ORFA_TRANSCRIBROTHERS = frozenset(
    {
        "regenerando_somente_tutorial_litellm_agendado",
        "regenerando_markdown_reproducao_bug_litellm_agendado",
        "regenerando_markdown_notas_proposta_litellm_agendado",
    }
)


async def _reconciliar_job_regeneracao_agendada_orfa_travada_em_generating_tutorial_transcribrothers(
    session: AsyncSession,
    row: JobPipelineTranscribrothers,
) -> None:
    """Se o servidor reiniciou após agendar regeneração, o job pode ficar preso em *_agendado."""
    if row.status != StatusJobTranscribrothers.generating_tutorial.value:
        return
    steps = dict(row.steps_json or {})
    fase = steps.get("pipeline_fase")
    if fase not in _FASES_REGENERACAO_AGENDADA_ORFA_TRANSCRIBROTHERS:
        return
    if not (row.result_markdown or "").strip():
        return
    atualizado = row.updated_at
    if atualizado is None:
        return
    agora = datetime.now(timezone.utc)
    if atualizado.tzinfo is None:
        atualizado = atualizado.replace(tzinfo=timezone.utc)
    if (agora - atualizado).total_seconds() < 45:
        return
    steps["regeneracao_agendada_orfa_reconciliada_em"] = agora.isoformat()
    destino = steps.get("destino_apos_transcricao")
    if destino == "reproducao_bug":
        steps["pipeline_fase"] = "reproducao_bug_concluida"
    elif destino == "notas_proposta_funcionalidade":
        steps["pipeline_fase"] = "notas_proposta_concluida"
    else:
        steps["pipeline_fase"] = "regeneracao_tutorial_concluida"
    steps.pop("regeneracao_apenas_markdown", None)
    steps.pop("regeneracao_reproducao_bug", None)
    steps.pop("regeneracao_notas_proposta", None)
    row.status = StatusJobTranscribrothers.completed.value
    row.error_message = None
    row.steps_json = steps
    flag_modified(row, "steps_json")
    row.updated_at = agora
    await session.commit()
    await session.refresh(row)


@app.get("/api/jobs/{job_id}", response_model=RespostaJobTranscribrothers)
async def obter_status_e_resultado_do_job_pipeline(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        await _resolver_duracao_video_segundos_do_job_com_cache_ffprobe_transcribrothers(
            session,
            row,
            work,
        )
        await _reconciliar_job_regeneracao_agendada_orfa_travada_em_generating_tutorial_transcribrothers(
            session,
            row,
        )
        from transcribrothers_backend.modulo_util_garantir_snapshot_regeneracao_reproducao_bug_job_legado_transcribrothers import (
            garantir_snapshot_regeneracao_em_job_reproducao_bug_legado_se_ausente_transcribrothers,
        )

        await garantir_snapshot_regeneracao_em_job_reproducao_bug_legado_se_ausente_transcribrothers(
            session,
            row,
            work,
        )
        await session.refresh(row)
        return _job_para_resposta(row)


@app.post("/api/jobs/{job_id}/cancel", response_model=RespostaJobTranscribrothers)
async def solicitar_cancelamento_do_job_pipeline_em_execucao_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
            StatusJobTranscribrothers.cancelled.value,
        ):
            raise HTTPException(
                status_code=400,
                detail="Este job já terminou; não é possível cancelar.",
            )
    marcar_cancelamento_pipeline_solicitado_para_job_transcribrothers(job_id)
    async with session_factory() as session:
        row2 = await session.get(JobPipelineTranscribrothers, job_id)
        assert row2 is not None
        return _job_para_resposta(row2)


@app.post("/api/jobs/{job_id}/retry", response_model=RespostaJobTranscribrothers)
async def repetir_job_pipeline_apos_falha_ou_cancelamento_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.failed.value,
            StatusJobTranscribrothers.cancelled.value,
        ):
            raise HTTPException(
                status_code=400,
                detail="Só é possível repetir jobs com status failed ou cancelled.",
            )
        steps = dict(row.steps_json or {})
        for k in ("error_traceback", "error_type", "error_repr"):
            steps.pop(k, None)
        steps["pipeline_fase"] = "retry_retomando_pipeline_reutilizando_artefatos"
        row.status = StatusJobTranscribrothers.pending.value
        row.error_message = None
        row.result_markdown = None
        row.steps_json = steps
        await session.commit()

    agendar_pipeline_job_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
    )

    async with session_factory() as session:
        criado = await session.get(JobPipelineTranscribrothers, job_id)
        assert criado is not None
        return _job_para_resposta(criado)


@app.post("/api/jobs/{job_id}/regenerate-tutorial", response_model=RespostaJobTranscribrothers)
async def regenerar_somente_markdown_tutorial_reaproveitando_transcricao_e_frames_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoRegenerarSomenteTutorialMarkdownTranscribrothers | None = Body(default=None),
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Regeneração usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                "(POST /v1/chat/completions)."
            ),
        )
    payload = body or CorpoRegenerarSomenteTutorialMarkdownTranscribrothers()
    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers,
        job_steps_indicam_projeto_em_branco_transcribrothers,
    )

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers(
            dict(row.steps_json or {})
        )
        row.steps_json = steps
        _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps)
        if payload.revisao_profunda_multifase and job_steps_indicam_projeto_em_branco_transcribrothers(steps):
            raise HTTPException(
                status_code=400,
                detail="Revisão profunda não está disponível em projeto em branco (sem transcrição de vídeo).",
            )
        if not isinstance(steps.get("regeneracao_tutorial_snapshot"), dict):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Snapshot de regeneração indisponível. É necessário um job que tenha concluído "
                    "a captura de telas (ou falhado depois disso com snapshot salvo)."
                ),
            )
        if row.status == StatusJobTranscribrothers.generating_tutorial.value:
            raise HTTPException(
                status_code=409,
                detail="Tutorial já em geração; aguarde concluir antes de regenerar.",
            )
        if row.status in (
            StatusJobTranscribrothers.pending.value,
            StatusJobTranscribrothers.downloading.value,
            StatusJobTranscribrothers.extracting_audio.value,
            StatusJobTranscribrothers.transcribing.value,
            StatusJobTranscribrothers.capturing_frames.value,
        ):
            raise HTTPException(
                status_code=409,
                detail="Aguarde o pipeline terminar a captura de telas antes de regenerar só o Markdown.",
            )

        modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, payload.litellm_model)

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps = _mesclar_contexto_fab_pedido_em_steps_json_transcribrothers(
            steps,
            caminhos_assets_png_contexto_fab=payload.caminhos_assets_png_contexto_fab,
            textos_contexto_fab=payload.textos_contexto_fab,
            exigir_projeto_em_branco=True,
        )
        steps["regeneracao_apenas_markdown"] = True
        steps["pipeline_fase"] = "regenerando_somente_tutorial_litellm_agendado"
        steps["litellm_model"] = modelo_litellm
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        await session.commit()

    agendar_regeneracao_apenas_tutorial_markdown_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        instrucoes_revisao_humana=payload.instrucoes_revisao_humana,
        modelo_litellm=modelo_litellm,
        revisao_profunda_multifase=bool(payload.revisao_profunda_multifase),
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/regenerate-reproducao-bug",
    response_model=RespostaJobTranscribrothers,
)
async def regenerar_markdown_reproducao_bug_reaproveitando_cliques_e_frames_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    body: CorpoRegenerarReproducaoBugMarkdownTranscribrothers | None = Body(default=None),
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Regeneração usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                "(POST /v1/chat/completions)."
            ),
        )
    payload = body or CorpoRegenerarReproducaoBugMarkdownTranscribrothers()

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        from transcribrothers_backend.modulo_util_garantir_snapshot_regeneracao_reproducao_bug_job_legado_transcribrothers import (
            garantir_snapshot_regeneracao_em_job_reproducao_bug_legado_se_ausente_transcribrothers,
        )

        await garantir_snapshot_regeneracao_em_job_reproducao_bug_legado_se_ausente_transcribrothers(
            session,
            row,
            work,
        )
        await session.refresh(row)
        steps = dict(row.steps_json or {})
        if not job_steps_indicam_reproducao_bug_transcribrothers(steps):
            raise HTTPException(
                status_code=400,
                detail="Regeneração de reprodução de bug só está disponível para jobs com destino reproducao_bug.",
            )
        _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps)
        if not isinstance(steps.get("regeneracao_tutorial_snapshot"), dict):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Snapshot de regeneração indisponível. Conclua o pipeline de reprodução de bug "
                    "antes de regenerar o Markdown."
                ),
            )
        if row.status == StatusJobTranscribrothers.generating_tutorial.value:
            raise HTTPException(
                status_code=409,
                detail="Geração em andamento; aguarde concluir antes de regenerar.",
            )
        if row.status in (
            StatusJobTranscribrothers.pending.value,
            StatusJobTranscribrothers.downloading.value,
            StatusJobTranscribrothers.extracting_audio.value,
            StatusJobTranscribrothers.transcribing.value,
            StatusJobTranscribrothers.capturing_frames.value,
        ):
            raise HTTPException(
                status_code=409,
                detail="Aguarde o pipeline concluir antes de regenerar o Markdown.",
            )

        modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, payload.litellm_model)

        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps["regeneracao_apenas_markdown"] = True
        steps["regeneracao_reproducao_bug"] = True
        steps["pipeline_fase"] = "regenerando_markdown_reproducao_bug_litellm_agendado"
        steps["litellm_model"] = modelo_litellm
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        await session.commit()

    agendar_regeneracao_markdown_reproducao_bug_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        instrucoes_revisao_humana=payload.instrucoes_revisao_humana,
        modelo_litellm=modelo_litellm,
        documento_autonomo_sem_video=bool(payload.documento_autonomo_sem_video),
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/regenerate-notas-proposta",
    response_model=RespostaJobTranscribrothers,
)
async def regenerar_markdown_notas_proposta_reaproveitando_transcricao_e_frames_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    body: CorpoRegenerarNotasPropostaMarkdownTranscribrothers | None = Body(default=None),
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Regeneração usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                "(POST /v1/chat/completions)."
            ),
        )
    payload = body or CorpoRegenerarNotasPropostaMarkdownTranscribrothers()

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        if not job_steps_indicam_notas_proposta_funcionalidade_transcribrothers(steps):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Regeneração de notas de proposta só está disponível para jobs com destino "
                    "notas_proposta_funcionalidade."
                ),
            )
        _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps)
        if not isinstance(steps.get("regeneracao_tutorial_snapshot"), dict):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Snapshot de regeneração indisponível. Conclua o pipeline de notas de proposta "
                    "antes de regenerar o Markdown."
                ),
            )
        if row.status == StatusJobTranscribrothers.generating_tutorial.value:
            raise HTTPException(
                status_code=409,
                detail="Geração em andamento; aguarde concluir antes de regenerar.",
            )
        if row.status in (
            StatusJobTranscribrothers.pending.value,
            StatusJobTranscribrothers.downloading.value,
            StatusJobTranscribrothers.extracting_audio.value,
            StatusJobTranscribrothers.transcribing.value,
            StatusJobTranscribrothers.capturing_frames.value,
        ):
            raise HTTPException(
                status_code=409,
                detail="Aguarde o pipeline concluir antes de regenerar o Markdown.",
            )

        modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, payload.litellm_model)

        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps["regeneracao_apenas_markdown"] = True
        steps["regeneracao_notas_proposta"] = True
        steps["pipeline_fase"] = "regenerando_markdown_notas_proposta_litellm_agendado"
        steps["litellm_model"] = modelo_litellm
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        await session.commit()

    agendar_regeneracao_markdown_notas_proposta_funcionalidade_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        instrucoes_revisao_humana=payload.instrucoes_revisao_humana,
        modelo_litellm=modelo_litellm,
        documento_autonomo_sem_video=bool(payload.documento_autonomo_sem_video),
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/regenerate-tutorial/aplicar",
    response_model=RespostaJobTranscribrothers,
)
async def aplicar_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
        CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
    )
    from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
        ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_FAB_TRANSCRIBROTHERS,
        ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS,
    )
    from transcribrothers_backend.modulo_pipeline_job_transcricao_tutorial import (
        _diretorio_trabalho_job,
    )

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        preview = steps.get(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS)
        if not isinstance(preview, dict):
            raise HTTPException(
                status_code=400,
                detail="Não há pré-visualização da regeneração do tutorial pendente para aplicar.",
            )
        md = str(preview.get("markdown_completo_proposto") or preview.get("markdown_depois") or "").strip()
        if not md:
            raise HTTPException(status_code=400, detail="Pré-visualização inválida (Markdown vazio).")
        revisao_profunda = bool(preview.get("revisao_profunda_multifase"))

    work = _diretorio_trabalho_job(data_dir, job_id)
    if work.is_dir():
        md_path = work / "tutorial_gerado_transcribrothers.md"
        md_path.write_text(md, encoding="utf-8", newline="\n")

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        assert row is not None
        row.result_markdown = md
        row.updated_at = datetime.now(timezone.utc)
        steps = dict(row.steps_json or {})
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps["regeneracao_tutorial_aplicada_em"] = datetime.now(timezone.utc).isoformat()
        steps["tutorial_ok"] = True
        steps["pipeline_fase"] = "regeneracao_tutorial_concluida"
        row.steps_json = steps
        origem = (
            ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS
            if revisao_profunda
            else ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_FAB_TRANSCRIBROTHERS
        )
        await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=md,
            origem=origem,
        )
        await session.commit()

    async with session_factory() as session:
        atualizado = await session.get(JobPipelineTranscribrothers, job_id)
        assert atualizado is not None
        return _job_para_resposta(atualizado)


@app.post(
    "/api/jobs/{job_id}/regenerate-tutorial/recuperar-preview-do-historico",
    response_model=RespostaJobTranscribrothers,
)
async def recuperar_preview_regeneracao_tutorial_markdown_de_historico_versoes_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    """
    Reconstrói preview pendente quando a regeneração gravou o Markdown direto (pipeline antigo em memória)
    mas o histórico de versões tem «antes» e «depois».
    """
    from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
        CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
    )
    from transcribrothers_backend.modulo_constante_origem_historico_versao_tutorial_markdown_job_transcribrothers import (
        ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS,
    )
    from transcribrothers_backend.modulo_persistencia_historico_versoes_tutorial_markdown_job_sqlite_transcribrothers import (
        obter_par_markdown_antes_depois_ultima_regeneracao_tutorial_no_historico_transcribrothers,
    )

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        if CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS in steps:
            raise HTTPException(status_code=409, detail="Já existe pré-visualização pendente neste job.")
        if not steps.get("regeneracao_apenas_markdown"):
            raise HTTPException(
                status_code=400,
                detail="Só é possível recuperar preview após uma regeneração do tutorial (fluxo 2).",
            )
        if steps.get("regeneracao_tutorial_aplicada_em"):
            raise HTTPException(
                status_code=409,
                detail=(
                    "A regeneração deste tutorial já foi aplicada ao documento. "
                    "Não é possível reabrir a pré-visualização pendente."
                ),
            )

    par = await obter_par_markdown_antes_depois_ultima_regeneracao_tutorial_no_historico_transcribrothers(
        session_factory,
        job_id,
    )
    if par is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Não foi possível reconstruir a pré-visualização: o histórico precisa de pelo menos duas "
                "versões (tutorial inicial + regeneração)."
            ),
        )
    markdown_antes, markdown_depois, origem_regen = par
    revisao_profunda = origem_regen == ORIGEM_HISTORICO_TUTORIAL_REVISAO_PROFUNDA_TRANSCRIBROTHERS

    ver_sust = steps.get("verificacao_sustentacao_tutorial")
    preview_blob: dict[str, Any] = {
        "markdown_antes": markdown_antes,
        "markdown_depois": markdown_depois,
        "markdown_completo_proposto": markdown_depois,
        "instrucoes_usadas": "",
        "criado_em": datetime.now(timezone.utc).isoformat(),
        "revisao_profunda_multifase": revisao_profunda,
        "recuperado_de_historico_versoes": True,
    }
    if isinstance(ver_sust, dict):
        preview_blob["verificacao_sustentacao_tutorial"] = ver_sust

    steps[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS] = (
        preview_blob
    )
    steps["pipeline_fase"] = FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        assert row is not None
        row.result_markdown = markdown_antes
        row.steps_json = steps
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return _job_para_resposta(row)


@app.post(
    "/api/jobs/{job_id}/regenerate-tutorial/descartar",
    response_model=RespostaJobTranscribrothers,
)
async def descartar_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
        CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS,
    )

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        if CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS not in steps:
            raise HTTPException(status_code=400, detail="Não há pré-visualização pendente.")
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        if steps.get("pipeline_fase") == FASE_PIPELINE_REGENERACAO_TUTORIAL_MARKDOWN_PREVIEW_PRONTA_TRANSCRIBROTHERS:
            steps.pop("pipeline_fase", None)
        row.steps_json = steps
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return _job_para_resposta(row)


def _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps: dict) -> None:
    from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
        CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
    )
    from transcribrothers_backend.modulo_pipeline_regeneracao_secao_markdown_tutorial_transcribrothers import (
        CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    )

    if CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS in steps:
        raise HTTPException(
            status_code=409,
            detail=(
                "Há pré-visualização de edição parcial pendente. Aplique ou descarte no editor "
                "antes de regenerar o documento inteiro."
            ),
        )
    if CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS in steps:
        raise HTTPException(
            status_code=409,
            detail=(
                "Há pré-visualização da regeneração do tutorial pendente. Aplique ou descarte "
                "antes de iniciar outra operação."
            ),
        )


def _mesclar_contexto_fab_pedido_em_steps_json_transcribrothers(
    steps: dict,
    *,
    caminhos_assets_png_contexto_fab: list[str] | None,
    textos_contexto_fab: list[str] | None,
    exigir_projeto_em_branco: bool,
) -> dict:
    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        job_steps_indicam_projeto_em_branco_transcribrothers,
    )
    from transcribrothers_backend.modulo_util_validar_e_normalizar_contexto_anexos_fab_pedido_transcribrothers import (
        normalizar_caminhos_assets_png_contexto_fab_pedido_transcribrothers,
        normalizar_textos_contexto_fab_pedido_transcribrothers,
    )

    tem_pedido = bool(caminhos_assets_png_contexto_fab) or bool(textos_contexto_fab)
    if tem_pedido and exigir_projeto_em_branco and not job_steps_indicam_projeto_em_branco_transcribrothers(steps):
        raise HTTPException(
            status_code=400,
            detail="Anexos de contexto no FAB só estão disponíveis em projeto em branco.",
        )
    if not job_steps_indicam_projeto_em_branco_transcribrothers(steps):
        return dict(steps)

    out = dict(steps)
    caminhos = normalizar_caminhos_assets_png_contexto_fab_pedido_transcribrothers(
        caminhos_assets_png_contexto_fab
    )
    textos = normalizar_textos_contexto_fab_pedido_transcribrothers(textos_contexto_fab)
    if caminhos:
        out["regeneracao_fab_contexto_caminhos_assets_png"] = caminhos
    else:
        out.pop("regeneracao_fab_contexto_caminhos_assets_png", None)
    if textos:
        out["regeneracao_fab_contexto_textos"] = textos
    else:
        out.pop("regeneracao_fab_contexto_textos", None)
    return out


def _validar_job_pode_regenerar_markdown_secao_transcribrothers(row: JobPipelineTranscribrothers) -> None:
    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers,
    )

    steps = garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers(
        dict(row.steps_json or {})
    )
    row.steps_json = steps
    _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps)
    if not isinstance(steps.get("regeneracao_tutorial_snapshot"), dict):
        raise HTTPException(
            status_code=400,
            detail="Snapshot de regeneração indisponível para este job.",
        )
    if row.status == StatusJobTranscribrothers.generating_tutorial.value:
        raise HTTPException(
            status_code=409,
            detail="Há geração ou regeneração em curso; aguarde antes de editar por seção.",
        )
    if row.status not in (
        StatusJobTranscribrothers.completed.value,
        StatusJobTranscribrothers.failed.value,
    ):
        raise HTTPException(
            status_code=409,
            detail="Edição por seção só está disponível com o job concluído ou falhou.",
        )
    if not (row.result_markdown or "").strip():
        raise HTTPException(status_code=400, detail="Tutorial vazio.")


@app.get(
    "/api/jobs/{job_id}/tutorial-markdown/secoes-nivel-2",
    response_model=list[ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers],
)
async def listar_secoes_nivel2_do_tutorial_markdown_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> list[ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        md = (row.result_markdown or "").strip()
    if not md:
        return []
    try:
        secoes = listar_secoes_markdown_nivel2_tutorial_transcribrothers(md)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return [
        ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers(
            indice=s.indice,
            linha_heading=s.linha_heading,
        )
        for s in secoes
    ]


@app.post("/api/jobs/{job_id}/regenerate-markdown-section", response_model=RespostaJobTranscribrothers)
async def pedir_regeneracao_markdown_de_uma_secao_tutorial_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoRegenerarSecaoMarkdownTutorialTranscribrothers,
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail="Defina LITELLM_API_KEY e LITELLM_ENDPOINT para regenerar seções.",
        )
    modo_escopo = body.modo_escopo_edicao
    trecho = (body.trecho_ancora or "").strip() or None
    interpretar_auto = bool(body.interpretar_escopo_automaticamente) and not trecho
    if not interpretar_auto:
        if modo_escopo == "secao_inteira":
            if not body.titulo_secao_heading and body.indice_secao is None:
                raise HTTPException(
                    status_code=400,
                    detail="Informe titulo_secao_heading ou indice_secao.",
                )
        elif not trecho:
            raise HTTPException(
                status_code=400,
                detail="Informe trecho_ancora ou use a interpretação automática do escopo.",
            )
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        _validar_job_pode_regenerar_markdown_secao_transcribrothers(row)
        md = (row.result_markdown or "").strip()
        if not interpretar_auto:
            try:
                from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
                    preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers,
                )

                preparar_fatia_escopo_edicao_secao_markdown_tutorial_transcribrothers(
                    md,
                    modo=modo_escopo,
                    trecho_ancora=trecho,
                    titulo_secao_heading=body.titulo_secao_heading,
                    indice_secao=body.indice_secao,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
        modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, body.litellm_model)
        steps = dict(row.steps_json or {})
        _levantar_se_preview_markdown_pendente_no_job_transcribrothers(steps)
        from transcribrothers_backend.modulo_constante_chave_steps_json_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers import (
            CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS,
        )

        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS, None)
        steps = _mesclar_contexto_fab_pedido_em_steps_json_transcribrothers(
            steps,
            caminhos_assets_png_contexto_fab=body.caminhos_assets_png_contexto_fab,
            textos_contexto_fab=body.textos_contexto_fab,
            exigir_projeto_em_branco=True,
        )
        steps["pipeline_fase"] = "regenerando_secao_markdown_litellm_agendado"
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        await session.commit()

    agendar_regeneracao_secao_markdown_tutorial_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        titulo_secao_heading=body.titulo_secao_heading,
        indice_secao=body.indice_secao,
        instrucoes_revisor=body.instrucoes_revisor.strip(),
        modelo_litellm=modelo_litellm,
        modo_escopo_edicao=modo_escopo,
        trecho_ancora=trecho,
        interpretar_escopo_automaticamente=interpretar_auto,
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/regenerate-markdown-section/aplicar",
    response_model=RespostaJobTranscribrothers,
)
async def aplicar_preview_regeneracao_secao_markdown_tutorial_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        preview = steps.get(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS)
        if not isinstance(preview, dict):
            raise HTTPException(
                status_code=400,
                detail="Não há pré-visualização de seção pendente para aplicar.",
            )
        md = str(preview.get("markdown_completo_proposto") or "").strip()
        if not md:
            raise HTTPException(status_code=400, detail="Pré-visualização inválida (Markdown vazio).")

    work = _diretorio_trabalho_job(data_dir, job_id)
    if work.is_dir():
        md_path = work / "tutorial_gerado_transcribrothers.md"
        md_path.write_text(md, encoding="utf-8", newline="\n")

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        assert row is not None
        row.result_markdown = md
        row.updated_at = datetime.now(timezone.utc)
        steps = dict(row.steps_json or {})
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        steps["regeneracao_secao_aplicada_em"] = datetime.now(timezone.utc).isoformat()
        if steps.get("pipeline_fase") == "regeneracao_secao_markdown_preview_pronta":
            steps.pop("pipeline_fase", None)
        row.steps_json = steps
        await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=md,
            origem=ORIGEM_HISTORICO_TUTORIAL_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
        )
        await session.commit()

    async with session_factory() as session:
        atualizado = await session.get(JobPipelineTranscribrothers, job_id)
        assert atualizado is not None
        return _job_para_resposta(atualizado)


@app.post(
    "/api/jobs/{job_id}/regenerate-markdown-section/descartar",
    response_model=RespostaJobTranscribrothers,
)
async def descartar_preview_regeneracao_secao_markdown_tutorial_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        if CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS not in steps:
            raise HTTPException(status_code=400, detail="Não há pré-visualização pendente.")
        steps.pop(CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS, None)
        if steps.get("pipeline_fase") == "regeneracao_secao_markdown_preview_pronta":
            steps.pop("pipeline_fase", None)
        row.steps_json = steps
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return _job_para_resposta(row)


@app.patch("/api/jobs/{job_id}/result-markdown", response_model=RespostaJobTranscribrothers)
async def atualizar_result_markdown_manual_apos_job_parar_transcribrothers(
    job_id: str,
    body: CorpoPatchResultMarkdownJobTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Persiste edição manual do tutorial (SQLite + ficheiro para o ZIP exportar o mesmo conteúdo)."""
    raw = body.result_markdown
    if len(raw.encode("utf-8")) > _LIMITE_BYTES_RESULT_MARKDOWN_JOB_EDICAO_MANUAL_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Markdown muito grande para esta operação (limite "
                f"{_LIMITE_BYTES_RESULT_MARKDOWN_JOB_EDICAO_MANUAL_TRANSCRIBROTHERS // (1024 * 1024)} MiB)."
            ),
        )
    work = _diretorio_trabalho_job(data_dir, job_id)
    if not work.is_dir():
        raise HTTPException(status_code=404, detail="Diretório do job não encontrado.")
    md_path = work / "tutorial_gerado_transcribrothers.md"
    try:
        md_path.write_text(raw, encoding="utf-8", newline="\n")
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Não foi possível gravar o ficheiro do tutorial no disco: {e}",
        ) from e

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
        ):
            raise HTTPException(
                status_code=400,
                detail="Só é possível gravar edição manual do tutorial quando o job está concluído ou falhou.",
            )
        row.result_markdown = raw
        row.updated_at = datetime.now(timezone.utc)
        steps = dict(row.steps_json or {})
        steps["tutorial_editado_manual_ui_em"] = datetime.now(timezone.utc).isoformat()
        row.steps_json = steps
        await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=raw,
            origem=ORIGEM_HISTORICO_TUTORIAL_EDICAO_MANUAL_TRANSCRIBROTHERS,
        )
        await session.commit()

    async with session_factory() as session:
        atualizado = await session.get(JobPipelineTranscribrothers, job_id)
        assert atualizado is not None
        return _job_para_resposta(atualizado)


@app.get(
    "/api/jobs/{job_id}/tutorial-markdown/historico-versoes",
    response_model=list[ResumoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers],
)
async def listar_historico_versoes_tutorial_markdown_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
) -> list[ResumoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    itens = await listar_resumo_versoes_historico_tutorial_markdown_do_job_transcribrothers(
        session_factory,
        job_id,
    )
    return [ResumoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers(**d) for d in itens]


@app.get(
    "/api/jobs/{job_id}/tutorial-markdown/historico-versoes/{historico_id}",
    response_model=RespostaConteudoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers,
)
async def obter_conteudo_versao_historico_tutorial_markdown_do_job_transcribrothers(
    job_id: str,
    historico_id: int,
    session_factory: SessionFactoryDep,
) -> RespostaConteudoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    tupla = await obter_conteudo_versao_historico_tutorial_markdown_por_id_transcribrothers(
        session_factory,
        job_id=job_id,
        historico_id=historico_id,
    )
    if tupla is None:
        raise HTTPException(status_code=404, detail="Versão de histórico não encontrada para este job.")
    conteudo, origem, criado_em = tupla
    return RespostaConteudoVersaoHistoricoTutorialMarkdownJobApiTranscribrothers(
        markdown=conteudo,
        origem=origem,
        criado_em=criado_em,
    )


@app.post(
    "/api/jobs/{job_id}/tutorial-markdown/historico-versoes/{historico_id}/restaurar",
    response_model=RespostaJobTranscribrothers,
)
async def restaurar_versao_historico_tutorial_markdown_no_job_transcribrothers(
    job_id: str,
    historico_id: int,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    tupla = await obter_conteudo_versao_historico_tutorial_markdown_por_id_transcribrothers(
        session_factory,
        job_id=job_id,
        historico_id=historico_id,
    )
    if tupla is None:
        raise HTTPException(status_code=404, detail="Versão de histórico não encontrada para este job.")
    raw, _origem_hist, _criado_hist = tupla
    if len(raw.encode("utf-8")) > _LIMITE_BYTES_RESULT_MARKDOWN_JOB_EDICAO_MANUAL_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Markdown muito grande para esta operação (limite "
                f"{_LIMITE_BYTES_RESULT_MARKDOWN_JOB_EDICAO_MANUAL_TRANSCRIBROTHERS // (1024 * 1024)} MiB)."
            ),
        )
    work = _diretorio_trabalho_job(data_dir, job_id)
    if not work.is_dir():
        raise HTTPException(status_code=404, detail="Diretório do job não encontrado.")
    md_path = work / "tutorial_gerado_transcribrothers.md"
    try:
        md_path.write_text(raw, encoding="utf-8", newline="\n")
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Não foi possível gravar o ficheiro do tutorial no disco: {e}",
        ) from e

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
        ):
            raise HTTPException(
                status_code=400,
                detail="Só é possível restaurar o tutorial quando o job está concluído ou falhou.",
            )
        row.result_markdown = raw
        row.updated_at = datetime.now(timezone.utc)
        steps = dict(row.steps_json or {})
        steps["tutorial_restaurado_de_historico_em"] = datetime.now(timezone.utc).isoformat()
        steps["tutorial_restaurado_de_historico_id"] = int(historico_id)
        row.steps_json = steps
        await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
            session,
            job_id=job_id,
            conteudo_markdown=raw,
            origem=ORIGEM_HISTORICO_TUTORIAL_RESTAURACAO_VERSAO_TRANSCRIBROTHERS,
        )
        await session.commit()

    async with session_factory() as session:
        atualizado = await session.get(JobPipelineTranscribrothers, job_id)
        assert atualizado is not None
        return _job_para_resposta(atualizado)


class RespostaMetadataVideoJobTranscribrothers(BaseModel):
    duracao_segundos: float = Field(ge=0)
    ffprobe_disponivel: bool = False


async def _resolver_duracao_video_segundos_do_job_com_cache_ffprobe_transcribrothers(
    session: AsyncSession,
    row: JobPipelineTranscribrothers,
    work: Path,
) -> float:
    steps = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    em_cache = steps.get("duracao_video_segundos")
    if isinstance(em_cache, (int, float)) and float(em_cache) > 0:
        return float(em_cache)
    caminho = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if caminho is None or not caminho.is_file():
        return 0.0
    dur = await obter_duracao_video_segundos_via_ffprobe(caminho)
    if dur > 0:
        steps["duracao_video_segundos"] = round(dur, 3)
        row.steps_json = steps
        flag_modified(row, "steps_json")
        await session.commit()
        await session.refresh(row)
    return dur


@app.get(
    "/api/jobs/{job_id}/video/metadata",
    response_model=RespostaMetadataVideoJobTranscribrothers,
)
async def obter_metadata_video_job_duracao_ffprobe_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaMetadataVideoJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        dur = await _resolver_duracao_video_segundos_do_job_com_cache_ffprobe_transcribrothers(
            session,
            row,
            work,
        )
    return RespostaMetadataVideoJobTranscribrothers(
        duracao_segundos=max(0.0, float(dur)),
        ffprobe_disponivel=ffprobe_disponivel_transcribrothers(),
    )


@app.get("/api/jobs/{job_id}/video")
async def servir_arquivo_video_original_do_job_para_player_html5(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if video is None or not video.is_file():
        raise HTTPException(status_code=404, detail="Vídeo ainda não disponível ou não encontrado.")
    ext = video.suffix.lstrip(".") or "mp4"
    return FileResponse(
        path=str(video),
        media_type=media_type_para_video_por_extensao(ext),
        filename=video.name,
    )


class CorpoDefinirExibicaoImagemTutorialAnotadaTranscribrothers(BaseModel):
    versao: Literal["original", "anotado"]


class RespostaListaAnotacoesImagensTutorialJobApiTranscribrothers(BaseModel):
    por_arquivo: dict[str, dict[str, Any]]


class ItemListaAssetImagemTutorialJobApiTranscribrothers(BaseModel):
    nome_arquivo_original: str
    referenciado_no_markdown: bool
    nome_arquivo_anotado: str
    exibir_no_tutorial: Literal["original", "anotado"]
    tem_arquivo_anotado: bool
    atualizado_em: str | None = None


class RespostaListaAssetsImagensTutorialJobApiTranscribrothers(BaseModel):
    itens: list[ItemListaAssetImagemTutorialJobApiTranscribrothers]


class CorpoCapturarFrameManualVideoTutorialTranscribrothers(BaseModel):
    timestamp_segundos: float = Field(..., ge=0, le=86400 * 48)


class RespostaCapturarFrameManualVideoTutorialTranscribrothers(BaseModel):
    nome_arquivo: str
    caminho_relativo: str
    snippet_markdown: str
    timestamp_segundos_solicitado: float
    timestamp_segundos_efetivo: float
    job: RespostaJobTranscribrothers


@app.post("/api/jobs/{job_id}/capturar-frame-manual-video-tutorial")
async def capturar_frame_manual_do_video_para_assets_e_snippet_markdown(
    job_id: str,
    corpo: CorpoCapturarFrameManualVideoTutorialTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaCapturarFrameManualVideoTutorialTranscribrothers:
    """Extrai PNG no instante do vídeo, grava em assets e devolve snippet para colar no Markdown."""
    cfg = obter_configuracao()
    largura = (
        int(cfg.tutorial_frame_max_width_px) if cfg.tutorial_frame_max_width_px > 0 else None
    )
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        if video is None or not video.is_file():
            raise HTTPException(
                status_code=409,
                detail="Vídeo do job ainda não está disponível para captura de frame.",
            )
        indice = proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers(row.steps_json)
        try:
            t_efetivo, nome_arquivo, caminho_rel, snippet = (
                await capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers(
                    caminho_video=video,
                    diretorio_trabalho_job=work,
                    timestamp_segundos_solicitado=corpo.timestamp_segundos,
                    indice_nome_arquivo=indice,
                    largura_maxima_saida_pixeis=largura,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao capturar frame no vídeo: {exc}",
            ) from exc
        row.steps_json = mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers(
            dict(row.steps_json or {}),
            timestamp_segundos_solicitado=corpo.timestamp_segundos,
            timestamp_segundos_efetivo=t_efetivo,
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_rel,
        )
        await session.commit()
        await session.refresh(row)
        return RespostaCapturarFrameManualVideoTutorialTranscribrothers(
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_rel,
            snippet_markdown=snippet,
            timestamp_segundos_solicitado=corpo.timestamp_segundos,
            timestamp_segundos_efetivo=t_efetivo,
            job=_job_para_resposta(row),
        )


class RespostaColarImagemClipboardMarkdownTutorialTranscribrothers(BaseModel):
    nome_arquivo: str
    caminho_relativo: str
    snippet_markdown: str
    job: RespostaJobTranscribrothers


@app.post(
    "/api/jobs/{job_id}/fab-anexos-contexto-imagem",
    response_model=RespostaUploadImagemAnexoContextoFabProjetoEmBrancoTranscribrothers,
)
async def upload_imagem_anexo_contexto_fab_projeto_em_branco_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    imagem: UploadFile = File(..., description="PNG/JPEG/WebP anexado ao pedido FAB"),
) -> RespostaUploadImagemAnexoContextoFabProjetoEmBrancoTranscribrothers:
    """Grava imagem de contexto do FAB em assets/ (só projeto em branco)."""
    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers,
        job_steps_indicam_projeto_em_branco_transcribrothers,
    )

    cfg = obter_configuracao()
    largura = (
        int(cfg.tutorial_frame_max_width_px) if cfg.tutorial_frame_max_width_px > 0 else None
    )
    tipo_mime = (imagem.content_type or "image/png").strip()
    if not tipo_mime.lower().startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem.")
    conteudo = await imagem.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Imagem vazia.")

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers(
            dict(row.steps_json or {})
        )
        if not job_steps_indicam_projeto_em_branco_transcribrothers(steps):
            raise HTTPException(
                status_code=400,
                detail="Anexos de contexto no FAB só estão disponíveis em projeto em branco.",
            )
        work = _diretorio_trabalho_job(data_dir, job_id)
        try:
            nome_arquivo, caminho_rel = (
                await salvar_imagem_anexo_contexto_fab_para_assets_markdown_tutorial_job_transcribrothers(
                    diretorio_trabalho_job=work,
                    conteudo_bytes=conteudo,
                    tipo_mime=tipo_mime,
                    largura_maxima_saida_pixeis=largura,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao gravar anexo de imagem: {exc}",
            ) from exc
        row.steps_json = steps
        await session.commit()
        await session.refresh(row)
        return RespostaUploadImagemAnexoContextoFabProjetoEmBrancoTranscribrothers(
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_rel,
            job=_job_para_resposta(row),
        )


@app.post(
    "/api/jobs/{job_id}/fab-anexos-contexto-documento",
    response_model=RespostaExtrairDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers,
)
async def extrair_documento_anexo_contexto_fab_projeto_em_branco_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    documento: UploadFile = File(..., description="PDF, Markdown ou texto para contexto do pedido FAB"),
) -> RespostaExtrairDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers:
    """Extrai texto de .pdf, .md ou .txt para anexar ao pedido (só projeto em branco)."""
    from transcribrothers_backend.modulo_util_extrair_texto_documento_anexo_contexto_fab_projeto_em_branco_transcribrothers import (
        extrair_texto_documento_anexo_contexto_fab_transcribrothers,
        truncar_texto_documento_para_limite_anexo_fab_transcribrothers,
    )
    from transcribrothers_backend.modulo_util_snapshot_regeneracao_tutorial_projeto_em_branco_transcribrothers import (
        garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers,
        job_steps_indicam_projeto_em_branco_transcribrothers,
    )

    nome = (documento.filename or "documento").strip() or "documento"
    conteudo = await documento.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = garantir_snapshot_regeneracao_em_steps_para_job_projeto_em_branco_transcribrothers(
            dict(row.steps_json or {})
        )
        if not job_steps_indicam_projeto_em_branco_transcribrothers(steps):
            raise HTTPException(
                status_code=400,
                detail="Anexos de contexto no FAB só estão disponíveis em projeto em branco.",
            )
        try:
            texto_bruto = extrair_texto_documento_anexo_contexto_fab_transcribrothers(
                nome_arquivo=nome,
                conteudo_bytes=conteudo,
                tipo_mime=documento.content_type,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    texto, truncado = truncar_texto_documento_para_limite_anexo_fab_transcribrothers(texto_bruto)
    return RespostaExtrairDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers(
        nome_arquivo=nome,
        texto=texto,
        truncado=truncado,
    )


@app.post("/api/jobs/{job_id}/colar-imagem-clipboard-markdown-tutorial")
async def colar_imagem_clipboard_markdown_tutorial_para_assets_e_snippet(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    imagem: UploadFile = File(..., description="PNG/JPEG/WebP colado da área de transferência"),
) -> RespostaColarImagemClipboardMarkdownTutorialTranscribrothers:
    """Grava imagem colada em assets/ do job e devolve snippet Markdown para inserir no editor."""
    cfg = obter_configuracao()
    largura = (
        int(cfg.tutorial_frame_max_width_px) if cfg.tutorial_frame_max_width_px > 0 else None
    )
    tipo_mime = (imagem.content_type or "image/png").strip()
    if not tipo_mime.lower().startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem.")
    conteudo = await imagem.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Imagem vazia.")

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        indice = proximo_indice_nome_arquivo_frame_manual_video_tutorial_transcribrothers(row.steps_json)
        try:
            nome_arquivo, caminho_rel, snippet = (
                await salvar_imagem_colada_clipboard_para_assets_markdown_tutorial_job_transcribrothers(
                    diretorio_trabalho_job=work,
                    conteudo_bytes=conteudo,
                    tipo_mime=tipo_mime,
                    indice_nome_arquivo=indice,
                    largura_maxima_saida_pixeis=largura,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao gravar imagem colada: {exc}",
            ) from exc
        row.steps_json = mesclar_registro_imagem_colada_clipboard_no_steps_json_transcribrothers(
            dict(row.steps_json or {}),
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_rel,
        )
        await session.commit()
        await session.refresh(row)
        return RespostaColarImagemClipboardMarkdownTutorialTranscribrothers(
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_rel,
            snippet_markdown=snippet,
            job=_job_para_resposta(row),
        )


@app.get("/api/jobs/{job_id}/imagens-tutorial/anotacoes")
async def listar_metadados_anotacoes_imagens_tutorial_do_job(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaListaAnotacoesImagensTutorialJobApiTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(row.steps_json)
    por_arquivo: dict[str, dict[str, Any]] = {}
    for nome_original, reg in mapa.items():
        if not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome_original):
            continue
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original)
        except ValueError:
            continue
        existe = (assets / nome_anotado).is_file()
        por_arquivo[nome_original] = registro_anotacao_imagem_para_resposta_api_transcribrothers(
            nome_original,
            reg,
            existe,
        )
    return RespostaListaAnotacoesImagensTutorialJobApiTranscribrothers(por_arquivo=por_arquivo)


@app.get(
    "/api/jobs/{job_id}/imagens-tutorial/lista-assets",
    response_model=RespostaListaAssetsImagensTutorialJobApiTranscribrothers,
)
async def listar_assets_imagens_png_tutorial_do_job(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaListaAssetsImagensTutorialJobApiTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    nomes_disco = listar_nomes_arquivo_png_original_na_pasta_assets_tutorial_transcribrothers(assets)
    mapa = obter_mapa_anotacoes_imagens_do_steps_json_transcribrothers(row.steps_json)
    md = row.result_markdown or ""
    referenciados: set[str] = set()
    for caminho in listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(md):
        nome = caminho.rsplit("/", 1)[-1]
        if nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome):
            referenciados.add(nome)
        elif nome.lower().endswith(".png"):
            # Referência direta a `.anotado.png` no Markdown: galeria usa o original correspondente.
            if ".anotado.png" in nome.lower():
                base = nome[: -len(".anotado.png")] + ".png"
                if nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(base):
                    referenciados.add(base)
    todos_nomes = sorted(set(nomes_disco) | referenciados, key=str.lower)
    itens: list[ItemListaAssetImagemTutorialJobApiTranscribrothers] = []
    for nome_original in todos_nomes:
        reg = mapa.get(nome_original, {})
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_original)
        except ValueError:
            continue
        existe_anotado = (assets / nome_anotado).is_file()
        api_reg = registro_anotacao_imagem_para_resposta_api_transcribrothers(
            nome_original,
            reg if isinstance(reg, dict) else {},
            existe_anotado,
        )
        itens.append(
            ItemListaAssetImagemTutorialJobApiTranscribrothers(
                nome_arquivo_original=nome_original,
                referenciado_no_markdown=nome_original in referenciados,
                nome_arquivo_anotado=str(api_reg["nome_arquivo_anotado"]),
                exibir_no_tutorial=api_reg["exibir_no_tutorial"],
                tem_arquivo_anotado=bool(api_reg["tem_arquivo_anotado"]),
                atualizado_em=api_reg.get("atualizado_em") if isinstance(api_reg.get("atualizado_em"), str) else None,
            )
        )
    return RespostaListaAssetsImagensTutorialJobApiTranscribrothers(itens=itens)


@app.put("/api/jobs/{job_id}/assets/{nome_arquivo}/anotacao")
async def gravar_png_anotado_de_screenshot_tutorial_do_job(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    arquivo_png: UploadFile = File(...),
) -> RespostaJobTranscribrothers:
    if not _ASSET_NAME_OK.match(nome_arquivo) or not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(
        nome_arquivo
    ):
        raise HTTPException(status_code=400, detail="Nome de arquivo PNG original inválido.")
    if arquivo_png.content_type and not arquivo_png.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Envie um arquivo de imagem PNG.")
    conteudo = await arquivo_png.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(conteudo) > _LIMITE_BYTES_UPLOAD_PNG_ANOTADO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS:
        raise HTTPException(status_code=413, detail="Imagem anotada excede o tamanho máximo permitido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        original = assets / nome_arquivo
        if not original.is_file():
            raise HTTPException(status_code=404, detail="Screenshot original não encontrado.")
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_arquivo)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        assets.mkdir(parents=True, exist_ok=True)
        (assets / nome_anotado).write_bytes(conteudo)
        steps = mesclar_registro_anotacao_apos_gravar_png_anotado_transcribrothers(
            dict(row.steps_json or {}),
            nome_arquivo,
            exibir_no_tutorial="anotado",
        )
        row.steps_json = steps
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.patch("/api/jobs/{job_id}/assets/{nome_arquivo}/exibicao-imagem")
async def definir_versao_exibicao_screenshot_tutorial_no_preview(
    job_id: str,
    nome_arquivo: str,
    corpo: CorpoDefinirExibicaoImagemTutorialAnotadaTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    if not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome_arquivo):
        raise HTTPException(status_code=400, detail="Nome de arquivo PNG original inválido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if corpo.versao == "anotado":
            assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
            try:
                nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_arquivo)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            if not (assets / nome_anotado).is_file():
                raise HTTPException(
                    status_code=409,
                    detail="Não há versão anotada salva para esta imagem.",
                )
        try:
            steps = mesclar_registro_exibicao_imagem_tutorial_transcribrothers(
                dict(row.steps_json or {}),
                nome_arquivo,
                corpo.versao,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        row.steps_json = steps
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.delete("/api/jobs/{job_id}/assets/{nome_arquivo}/anotacao")
async def remover_png_anotado_de_screenshot_tutorial_do_job(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    if not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome_arquivo):
        raise HTTPException(status_code=400, detail="Nome de arquivo PNG original inválido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_arquivo)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        path_anotado = assets / nome_anotado
        if path_anotado.is_file():
            path_anotado.unlink()
        row.steps_json = mesclar_remocao_anotacao_imagem_tutorial_transcribrothers(
            dict(row.steps_json or {}),
            nome_arquivo,
        )
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.post("/api/jobs/{job_id}/assets/{nome_arquivo}/sincronizar-markdown-com-versao-anotada")
async def atualizar_markdown_job_para_referenciar_png_anotado_no_tutorial(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Substitui `![](assets/original.png)` por `![](assets/original.anotado.png)` no `result_markdown`."""
    if not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome_arquivo):
        raise HTTPException(status_code=400, detail="Nome de arquivo PNG original inválido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_arquivo)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not (assets / nome_anotado).is_file():
            raise HTTPException(status_code=409, detail="Salve a versão anotada antes de atualizar o Markdown.")
        md = row.result_markdown or ""
        if not md.strip():
            raise HTTPException(status_code=409, detail="Job não possui tutorial Markdown.")
        row.result_markdown = substituir_referencia_asset_png_no_markdown_por_nome_arquivo_transcribrothers(
            md,
            nome_arquivo,
            nome_anotado,
        )
        row.steps_json = mesclar_registro_exibicao_imagem_tutorial_transcribrothers(
            dict(row.steps_json or {}),
            nome_arquivo,
            "anotado",
        )
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.delete("/api/jobs/{job_id}/assets/{nome_arquivo}")
async def excluir_asset_png_original_e_anotado_do_tutorial_do_job(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    if not _ASSET_NAME_OK.match(nome_arquivo) or not nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(
        nome_arquivo
    ):
        raise HTTPException(status_code=400, detail="Nome de arquivo PNG original inválido.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    if not work.is_dir():
        raise HTTPException(status_code=404, detail="Diretório do job não encontrado.")
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    try:
        nome_anotado = derivar_nome_arquivo_png_anotado_a_partir_do_original_transcribrothers(nome_arquivo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    path_original = assets / nome_arquivo
    path_anotado = assets / nome_anotado
    tinha_original = path_original.is_file()
    tinha_anotado = path_anotado.is_file()
    if not tinha_original and not tinha_anotado:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Job não encontrado.")
            md_atual = row.result_markdown or ""
            if not markdown_tutorial_referencia_imagem_asset_transcribrothers(md_atual, nome_arquivo):
                raise HTTPException(status_code=404, detail="Asset não encontrado.")
    if tinha_original:
        path_original.unlink()
    if tinha_anotado:
        path_anotado.unlink()

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
        ):
            raise HTTPException(
                status_code=400,
                detail="Só é possível excluir assets quando o job está concluído ou falhou.",
            )
        md_atual = row.result_markdown or ""
        referenciado = markdown_tutorial_referencia_imagem_asset_transcribrothers(md_atual, nome_arquivo)
        md_novo = md_atual
        if referenciado:
            md_novo = remover_referencia_imagem_asset_do_markdown_tutorial_transcribrothers(
                md_atual,
                nome_arquivo,
            )
        steps = mesclar_remocao_anotacao_imagem_tutorial_transcribrothers(
            dict(row.steps_json or {}),
            nome_arquivo,
        )
        row.steps_json = steps
        if referenciado and md_novo != md_atual:
            row.result_markdown = md_novo
            row.updated_at = datetime.now(timezone.utc)
            md_path = work / "tutorial_gerado_transcribrothers.md"
            if md_path.is_file():
                try:
                    md_path.write_text(md_novo, encoding="utf-8", newline="\n")
                except OSError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Não foi possível atualizar o ficheiro do tutorial: {e}",
                    ) from e
            await inserir_versao_historico_tutorial_markdown_na_sessao_sem_commit_transcribrothers(
                session,
                job_id=job_id,
                conteudo_markdown=md_novo,
                origem=ORIGEM_HISTORICO_TUTORIAL_EXCLUSAO_ASSET_IMAGEM_TRANSCRIBROTHERS,
            )
        else:
            row.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.get("/api/jobs/{job_id}/assets/{nome_arquivo}")
async def servir_asset_png_do_tutorial_do_job(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    if not _ASSET_NAME_OK.match(nome_arquivo) or ".." in nome_arquivo or "/" in nome_arquivo:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    path = assets / nome_arquivo
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Asset não encontrado.")
    return FileResponse(str(path), media_type="image/png")


@app.get("/api/jobs/{job_id}/export.zip")
async def baixar_pacote_zip_com_tutorial_markdown_e_assets_png(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> StreamingResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    md = work / "tutorial_gerado_transcribrothers.md"
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    if not md.is_file():
        raise HTTPException(status_code=404, detail="Tutorial ainda não gerado.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(md, arcname="tutorial.md")
        if assets.is_dir():
            for p in sorted(assets.iterdir()):
                if p.is_file() and p.suffix.lower() == ".png":
                    zf.write(p, arcname=f"assets/{p.name}")
    buf.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="transcribrothers-{job_id}.zip"'}
    return StreamingResponse(buf, media_type="application/zip", headers=headers)


@app.get("/api/health")
async def healthcheck_transcribrothers() -> dict[str, str | bool]:
    """Inclui `pipeline_identificador` para confirmar que o processo carregou o build esperado do pipeline."""
    diag_ffmpeg = obter_diagnostico_ffmpeg_ffprobe_transcribrothers()
    return {
        "status": "ok",
        "pipeline_identificador": IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
        "preview_regeneracao_tutorial_documento_inteiro_habilitado": True,
        "anotacao_imagens_tutorial_duas_versoes_habilitado": True,
        "captura_frame_manual_video_tutorial_habilitado": True,
        **diag_ffmpeg,
    }
