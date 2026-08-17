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
from transcribrothers_backend.modulo_log_diagnostico_upload_video_job_pipeline_transcribrothers import (
    configurar_logging_upload_video_job_pipeline_transcribrothers,
    gravar_arquivo_upload_video_com_limite_bytes_transcribrothers,
    log_erro_upload_video_job_transcribrothers,
    log_fim_gravacao_video_upload_job_transcribrothers,
    log_inicio_upload_video_job_transcribrothers,
    log_job_upload_registrado_e_pipeline_agendado_transcribrothers,
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
from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
    RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
    mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers,
    montar_resposta_catalogo_pipelines_disponiveis_documentacao_transcribrothers,
)
from transcribrothers_backend.modulo_editar_passos_internos_pipeline_custom_transcribrothers import (
    adicionar_passo_pipeline_custom_transcribrothers,
    reordenar_passos_pipeline_custom_transcribrothers,
    remover_passo_pipeline_custom_transcribrothers,
)
from transcribrothers_backend.modulo_montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers import (
    montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_pipelines_e_agentes_custom_sqlite_transcribrothers import (
    atualizar_agente_custom_transcribrothers,
    atualizar_pipeline_custom_transcribrothers,
    carregar_agentes_custom_da_pipeline_transcribrothers,
    criar_pipeline_custom_a_partir_de_molde_transcribrothers,
    duplicar_agente_catalogo_para_custom_transcribrothers,
    duplicar_pipeline_catalogo_para_custom_transcribrothers,
    excluir_agente_custom_transcribrothers,
    excluir_pipeline_custom_transcribrothers,
    obter_agente_custom_por_id_transcribrothers,
    obter_pipeline_custom_por_id_transcribrothers,
    pipeline_custom_e_executavel_upload_transcribrothers,
    reordenar_pipelines_custom_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_configuracao_agente_pipeline_custom_transcribrothers import (
    montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers,
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
from transcribrothers_backend.modulo_persistencia_runtime_config_encode_video_narrado_sqlite_transcribrothers import (
    apagar_override_encode_video_narrado_runtime_sqlite_transcribrothers,
    gravar_preferencias_encode_video_narrado_runtime_sqlite_transcribrothers,
    resolver_preferencias_encode_video_narrado_efetivas_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_voz_tts_narracao_sqlite_transcribrothers import (
    apagar_override_voz_tts_narracao_runtime_sqlite_transcribrothers,
    gravar_preferencias_voz_tts_narracao_runtime_sqlite_transcribrothers,
    resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
    listar_vozes_tts_gemini_disponiveis_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
    RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
    RESOLUCOES_ENCODE_VIDEO_NARRADO_VALIDAS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_pastas_wiki_gitlab_sqlite_transcribrothers import (
    apagar_override_pastas_wiki_gitlab_runtime_sqlite_transcribrothers,
    gravar_pastas_wiki_gitlab_runtime_sqlite_transcribrothers,
    pasta_wiki_esta_na_lista_permitida_transcribrothers,
    resolver_pastas_wiki_gitlab_efetivas_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_runtime_config_modelos_litellm_extras_sqlite_transcribrothers import (
    adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers,
    sincronizar_cache_modelos_litellm_extras_da_session_transcribrothers,
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
from transcribrothers_backend.modulo_orquestrar_reprocessamento_pos_transcricao_com_novo_destino_job_transcribrothers import (
    ErroGerarOutroFormatoJobTranscribrothers,
    aplicar_gerar_outro_formato_no_job_transcribrothers,
    job_pode_gerar_outro_formato_pos_transcricao_transcribrothers,
    resolver_snapshot_pipeline_custom_para_gerar_outro_formato_transcribrothers,
    validar_job_pode_gerar_outro_formato_transcribrothers,
)
from transcribrothers_backend.modulo_criar_job_a_partir_transcricao_importada_pronta_transcribrothers import (
    ErroImportarTranscricaoProntaTranscribrothers,
    criar_job_a_partir_transcricao_importada_pronta_transcribrothers,
)
from transcribrothers_backend.modulo_util_parsear_arquivo_ou_texto_transcricao_importada_srt_vtt_txt_transcribrothers import (
    ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers,
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
    listar_modelos_litellm_permitidos_efetivos_transcribrothers,
    normalizar_backend_transcricao_audio_configurado,
    resolver_modelo_para_transcricao_litellm_multimodal_audio,
    tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy,
    tem_credencial_para_transcricao_no_pipeline,
    validar_e_resolver_modelo_litellm_solicitado_pelo_cliente,
)
from transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers import (
    verificar_modelo_litellm_via_chat_completions_probe_transcribrothers,
)
from transcribrothers_backend.modulo_util_extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers import (
    extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers,
    resolver_modelo_tts_para_narracao_documento_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
    substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
    ErroVersaoVideoNarradoTranscribrothers,
    NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS,
    apagar_versao_video_narrado_transcribrothers,
    listar_versoes_video_narrado_do_work_transcribrothers,
    resolver_arquivo_versao_video_narrado_transcribrothers,
    tornar_versao_video_narrado_atual_transcribrothers,
)
from transcribrothers_backend.modulo_inventario_midia_fonte_e_cache_job_transcribrothers import (
    ErroMidiaFonteJobTranscribrothers,
    inventariar_midia_fonte_e_cache_do_work_transcribrothers,
    limpar_cache_regeneravel_job_transcribrothers,
    resolver_arquivo_midia_fonte_permitido_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_biblioteca_midias_tela_job_transcribrothers import (
    ErroBibliotecaMidiasTelaTranscribrothers,
    ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
    alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers,
    apagar_item_biblioteca_midias_tela_por_id_transcribrothers,
    confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers,
    listar_itens_biblioteca_midias_tela_do_work_transcribrothers,
    resolver_caminho_arquivo_biblioteca_midias_tela_por_id_transcribrothers,
)
from transcribrothers_backend.modulo_debug_cache_segmentos_video_narrado_job_transcribrothers import (
    montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers,
)
from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    FASE_VIDEO_NARRADO_AGENDADO,
    agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona,
    validar_pre_requisitos_pipeline_video_narrado_no_disco_transcribrothers,
)
from transcribrothers_backend.modulo_diretriz_conteudo_legendas_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS,
    normalizar_diretriz_conteudo_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_perfil_motor_sintese_tts_narracao_transcribrothers import (
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS,
    CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS,
    normalizar_paralelismo_tts_cues_experimental_transcribrothers,
    normalizar_perfil_tts_narracao_transcribrothers,
    normalizar_ritmo_tts_narracao_transcribrothers,
    normalizar_temperatura_tts_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_util_resolver_markdown_escopo_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_pipeline_atualizar_narracao_a_partir_legendas_vtt_editadas_job_transcribrothers import (
    FASE_VIDEO_NARRADO_ATUALIZANDO_LEGENDAS_EDITADAS,
    agendar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_task_assincrona,
    validar_pre_requisitos_atualizar_narracao_a_partir_vtt_editadas_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    FASE_VIDEO_NARRADO_GERANDO_COM_EDICOES_MODAL,
    agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona,
)
from transcribrothers_backend.modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers import (
    montar_resumo_janelas_video_e_wavs_do_job_transcribrothers,
    obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers,
    salvar_janelas_video_no_manifest_validando_sobreposicao_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    ErroValidacaoJanelasVideoCuesTranscribrothers,
)
from transcribrothers_backend.modulo_pipeline_remux_video_narrado_apos_edicao_janelas_video_job_transcribrothers import (
    FASE_VIDEO_NARRADO_REMUX_JANELAS_EDITADAS,
    agendar_remux_video_narrado_apos_edicao_janelas_em_task_assincrona,
    validar_pre_requisitos_remux_janelas_editadas_transcribrothers,
)
from transcribrothers_backend.modulo_api_preview_tts_amostra_voz_narracao_transcribrothers import (
    gerar_arquivo_preview_tts_amostra_voz_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_api_preview_tts_cue_narracao_texto_atual_job_transcribrothers import (
    gerar_arquivo_preview_tts_cue_narracao_job_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_cue_tts_pendente_timeout_experimental_e_continuar_mux_transcribrothers import (
    descartar_cue_tts_pendente_timeout_experimental_job_transcribrothers,
    resolver_cue_tts_pendente_timeout_experimental_job_transcribrothers,
)
from transcribrothers_backend.modulo_sugerir_reescrita_texto_cue_tts_timeout_experimental_via_litellm_chat_transcribrothers import (
    sugerir_reescrita_texto_cue_tts_pendente_timeout_experimental_transcribrothers,
)
from transcribrothers_backend.modulo_sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers import (
    sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers,
)
from transcribrothers_backend.modulo_api_salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers import (
    ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers,
    salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_queimar_legendas_vtt_no_video_mp4_narrado_transcribrothers import (
    NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS,
    video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_tarefa_gerar_video_narrado_com_legendas_queimadas_em_background_transcribrothers import (
    agendar_geracao_video_narrado_com_legendas_queimadas_transcribrothers,
    consultar_status_video_narrado_com_legendas_queimadas_transcribrothers,
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
    adicionar_markdown_na_descricao_issue_gitlab_existente_transcribrothers,
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
from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_audio_upload_local_transcribrothers import (
    classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers,
    extrair_extensao_audio_sanitizada_para_upload_local,
)
from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_video_upload_local import (
    ErroExtensaoVideoUploadTranscribrothers,
    extrair_extensao_video_sanitizada_para_upload_local,
)
from transcribrothers_backend.modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers import (
    ErroAnexarGravacaoComplementarTranscribrothers,
    aplicar_metadados_unificacao_nos_steps_json_transcribrothers,
    unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_preparar_video_entrada_unificado_a_partir_lista_clips_job_transcribrothers import (
    ErroPrepararVideoEntradaMultiploTranscribrothers,
    preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers,
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


class CorpoGerarOutroFormatoPosTranscricaoJobTranscribrothers(BaseModel):
    destino_apos_transcricao: str
    pipeline_custom_id: str | None = None
    litellm_model: str | None = None


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


# Pipelines de vídeo narrado / edições do modal: podem recomeçar após cancelamento.
_STATUS_JOB_PERMITE_REINICIAR_PIPELINE_VIDEO_NARRADO_TRANSCRIBROTHERS = frozenset(
    {
        StatusJobTranscribrothers.completed.value,
        StatusJobTranscribrothers.failed.value,
        StatusJobTranscribrothers.cancelled.value,
    }
)


def _garantir_job_permite_reiniciar_pipeline_video_narrado_transcribrothers(
    row: JobPipelineTranscribrothers,
    *,
    mensagem_se_bloqueado: str,
) -> None:
    if row.status in _STATUS_JOB_PERMITE_REINICIAR_PIPELINE_VIDEO_NARRADO_TRANSCRIBROTHERS:
        return
    raise HTTPException(
        status_code=400
        if row.status != StatusJobTranscribrothers.generating_tutorial.value
        else 409,
        detail=(
            "Já há uma geração em andamento; aguarde concluir."
            if row.status == StatusJobTranscribrothers.generating_tutorial.value
            else mensagem_se_bloqueado
        ),
    )


def _limpar_marcadores_cancelamento_ao_reiniciar_pipeline_video_narrado_transcribrothers(
    job_id: str,
    steps: dict[str, Any],
) -> None:
    limpar_marcacao_cancelamento_pipeline_job_transcribrothers(job_id)
    steps.pop("cancelamento_pipeline_solicitado", None)


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
    tamanho_bytes_disco: int = 0


def _resumo_job_para_lista(
    row: JobPipelineTranscribrothers,
    *,
    tamanho_bytes_disco: int = 0,
) -> ResumoJobListaPipelineTranscribrothers:
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
        tamanho_bytes_disco=max(0, int(tamanho_bytes_disco or 0)),
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
    gitlab_wiki_pastas_disponiveis: list[str] = Field(default_factory=lambda: ["workshop"])
    gitlab_wiki_pastas_preferencia_sqlite_definida: bool = False
    ffmpeg_disponivel: bool = False
    ffprobe_disponivel: bool = False
    encode_video_narrado_resolucao_efetiva: str = RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS
    encode_video_narrado_fps_efetivo: int = FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS
    encode_video_narrado_resolucao_padrao_app: str = RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS
    encode_video_narrado_fps_padrao_app: int = FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS
    encode_video_narrado_resolucoes_disponiveis: list[str] = Field(
        default_factory=lambda: list(RESOLUCOES_ENCODE_VIDEO_NARRADO_VALIDAS_TRANSCRIBROTHERS)
    )
    encode_video_narrado_preferencia_sqlite_definida: bool = False
    voz_tts_narracao_efetiva: str = VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    voz_tts_narracao_padrao_app: str = VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    voz_tts_narracao_preferencia_sqlite_definida: bool = False
    voz_tts_narracao_vozes_disponiveis: list[dict[str, str]] = Field(default_factory=list)


class CorpoPatchEncodeVideoNarradoRuntimeTranscribrothers(BaseModel):
    resolucao: str = Field(default=RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS)
    fps: int = Field(default=FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS, ge=1, le=120)


class CorpoPatchVozTtsNarracaoRuntimeTranscribrothers(BaseModel):
    voz: str = Field(default=VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS, min_length=1, max_length=64)


class CorpoPatchPastasWikiGitlabRuntimeTranscribrothers(BaseModel):
    pastas: list[str] = Field(..., min_length=1)
    pasta_padrao: str | None = None


class CorpoPatchModeloLitellmExtraRuntimeTranscribrothers(BaseModel):
    modelo: str = Field(..., min_length=1, max_length=256)


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


class RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers(BaseModel):
    ok: bool = True
    web_url: str
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


class CorpoVerificarModeloLitellmChatProbeTranscribrothers(BaseModel):
    """Identificador do modelo no proxy (mesmo slug usado no select da UI)."""

    model: str = Field(min_length=1)

    @field_validator("model")
    @classmethod
    def _modelo_nao_pode_ser_so_espacos(cls, v: str) -> str:
        s = (v or "").strip()
        if not s:
            raise ValueError("Informe o identificador do modelo LiteLLM.")
        return s


class RespostaVerificarModeloLitellmChatProbeTranscribrothers(BaseModel):
    """Resultado do probe barato de chat (não valida STT nem visão)."""

    ok: bool
    modelo: str
    mensagem: str


class CorpoGerarNarracaoTtsMarkdownJobTranscribrothers(BaseModel):
    """Modelo TTS opcional; se omitido, usa o primeiro provisionado com -tts."""

    litellm_model: str | None = None


class RespostaGerarNarracaoTtsMarkdownJobTranscribrothers(BaseModel):
    ok: bool
    mensagem: str
    nome_arquivo: str
    url_asset: str
    modelo: str
    texto_caracteres: int = 0
    texto_truncado: bool = False


class RespostaGerarVideoComNarracaoTtsJobTranscribrothers(BaseModel):
    ok: bool
    mensagem: str
    nome_arquivo: str
    url_download: str


class CorpoPipelineVideoNarradoAPartirDocumentoTranscribrothers(BaseModel):
    """`litellm_model` = TTS; `litellm_model_chat` = chat da UI para limpeza IA das legendas."""

    litellm_model: str | None = None
    litellm_model_chat: str | None = None
    # Markdown opcional (escopo parcial). Não altera result_markdown do job.
    markdown_narracao: str | None = None
    titulos_secoes_escopo: list[str] | None = None
    # Motor TTS: padrao (sagrado) | experimental_voz (isolado para testes de voz).
    perfil_tts: str | None = None
    # Cues TTS em paralelo (1–9; padrão 3) — vale para padrao e experimental_voz.
    # Nome histórico do campo (mantido por compatibilidade da API).
    paralelismo_tts_experimental: int | None = Field(default=None, ge=1, le=9)
    # Temperatura TTS (0.2–1.0, passo 0.1; padrão 0.4).
    temperatura_tts: float | None = Field(default=None, ge=0.2, le=1.0)
    # Ritmo via prompt: lento | normal | rapido | muito_rapido (padrão normal).
    ritmo_tts: str | None = None
    # Diretriz da limpeza IA: conservador | mais_falavel | mais_didatico | mais_descontraido.
    diretriz_conteudo_legendas: str | None = None


class CorpoAtualizarNarracaoAPartirLegendasVttEditadasTranscribrothers(BaseModel):
    """Regenera TTS só nas cues cujo texto no VTT mudou; remonta WAV+MP4."""

    litellm_model: str | None = None


class CorpoPreviewTtsCueNarracaoTextoAtualTranscribrothers(BaseModel):
    indice: int = Field(ge=0, le=50_000)
    texto: str = Field(min_length=1, max_length=16_000)
    litellm_model: str | None = None
    voz: str | None = None
    temperatura_tts: float | None = Field(default=None, ge=0.2, le=1.0)
    ritmo_tts: str | None = None


class CorpoResolverCueTtsPendenteTimeoutExperimentalTranscribrothers(BaseModel):
    """Reenvia uma cue com timeout no perfil experimental_voz (1 tentativa)."""

    indice: int = Field(ge=0, le=50_000)
    texto: str = Field(min_length=1, max_length=16_000)
    voz: str | None = None


class CorpoDescartarCueTtsPendenteTimeoutExperimentalTranscribrothers(BaseModel):
    """Mantém a cue sem narração (silêncio) e remove da lista de pendentes."""

    indice: int = Field(ge=0, le=50_000)


class CorpoSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers(BaseModel):
    """Pede sugestão de reescrita via chat; não altera o texto da cue até o usuário aceitar."""

    indice: int = Field(ge=0, le=50_000)
    texto: str = Field(min_length=1, max_length=16_000)
    litellm_model_chat: str | None = None


class RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers(BaseModel):
    ok: bool
    mensagem: str
    indice: int
    sugestao: str = ""
    modelo: str | None = None
    texto_original: str | None = None


class RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers(BaseModel):
    ok: bool
    mensagem: str
    indice: int
    pendentes_restantes: int = 0
    pipeline_continuada: bool = False
    pipeline_fase: str | None = None


class CorpoPreviewTtsAmostraVozNarracaoTranscribrothers(BaseModel):
    voz: str = Field(default=VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS, min_length=1, max_length=64)
    litellm_model: str | None = None
    perfil_tts: str | None = None
    temperatura_tts: float | None = Field(default=None, ge=0.2, le=1.0)
    ritmo_tts: str | None = None


class JanelaVideoCueEditadaApiTranscribrothers(BaseModel):
    inicio_video_segundos: float
    fim_video_segundos: float
    id_fonte_video: str = ""


class CorpoSalvarJanelasVideoCuesNarracaoJobTranscribrothers(BaseModel):
    janelas: list[JanelaVideoCueEditadaApiTranscribrothers]


class ResumoJanelaVideoCueApiRespostaTranscribrothers(BaseModel):
    indice: int
    texto: str
    inicio_video_segundos: float
    fim_video_segundos: float
    tem_wav: bool
    url_wav: str | None = None
    sem_narracao: bool = False
    voz_tts: str = ""
    # Pronúncia usada (ou a usar) no TTS; vazio = igual a `texto`.
    texto_tts: str = ""
    id_fonte_video: str = ""


class RespostaJanelasVideoCuesNarracaoJobTranscribrothers(BaseModel):
    ok: bool = True
    quantidade_cues: int
    cues: list[ResumoJanelaVideoCueApiRespostaTranscribrothers]
    voz_tts_padrao_job: str = VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS


class CueLegendaDocumentoAlinhadaEditadaApiTranscribrothers(BaseModel):
    inicio_segundos: float
    fim_segundos: float
    texto: str
    sem_narracao: bool = False
    voz_tts: str | None = None
    # Pronúncia para TTS; vazio/omitido = narrar `texto`. Não entra no VTT.
    texto_tts: str | None = None
    forcar_regenerar_tts: bool = False


class CorpoSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers(BaseModel):
    cues: list[CueLegendaDocumentoAlinhadaEditadaApiTranscribrothers]


class CorpoGerarVideoComEdicoesDoModalNarradoTranscribrothers(BaseModel):
    """Salva edições do modal, regenera TTS se preciso e remonta o MP4 na timeline VTT."""

    litellm_model: str | None = None
    temperatura_tts: float | None = Field(default=None, ge=0.2, le=1.0)
    ritmo_tts: str | None = None
    cues: list[CueLegendaDocumentoAlinhadaEditadaApiTranscribrothers]
    janelas: list[JanelaVideoCueEditadaApiTranscribrothers] | None = None


class CorpoSugerirReescritaTextoCueNarracaoTranscribrothers(BaseModel):
    """Sugestão IA de reescrita da legenda (modal editar); não aplica sozinha."""

    indice: int = Field(ge=0, le=50_000)
    texto: str = Field(min_length=1, max_length=16_000)
    litellm_model_chat: str | None = None


class RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers(BaseModel):
    ok: bool = True
    nome_arquivo: str
    url_asset: str
    quantidade_cues: int


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


class CorpoDuplicarFonteCatalogoCustomTranscribrothers(BaseModel):
    fonte_id: str


class CorpoCriarPipelineCustomTranscribrothers(BaseModel):
    fonte_id: str
    titulo: str | None = None
    descricao: str | None = None


class CorpoReordenarPipelinesCustomTranscribrothers(BaseModel):
    pipeline_ids_ordenados: list[str] = Field(..., min_length=0)


class CorpoPatchPipelineCustomTranscribrothers(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    entradas_aceitas: list[str] | None = None


class CorpoReordenarPassosPipelineCustomTranscribrothers(BaseModel):
    passo_ids_ordenados: list[str] = Field(..., min_length=1)


class CorpoAdicionarPassoPipelineCustomTranscribrothers(BaseModel):
    agente_fonte_id: str
    rotulo: str | None = None
    descricao: str | None = None


class PromptPatchAgenteCustomTranscribrothers(BaseModel):
    chave: str
    tipo: str
    rotulo: str
    texto: str = ""
    observacao: str | None = None


class CorpoPatchAgenteCustomTranscribrothers(BaseModel):
    rotulo: str | None = None
    descricao: str | None = None
    modelo_litellm: str | None = None
    prompts: list[PromptPatchAgenteCustomTranscribrothers] | None = None


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
    configurar_logging_upload_video_job_pipeline_transcribrothers()
    cfg = obter_configuracao()
    data_dir = cfg.transcribrothers_data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "transcribrothers.sqlite3"
    url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    engine = criar_engine_sqlite_async(url)
    await inicializar_banco(engine)
    session_factory = criar_session_factory(engine)
    async with session_factory() as session:
        await sincronizar_cache_modelos_litellm_extras_da_session_transcribrothers(session)
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
        pastas_wiki, pasta_wiki_padrao, pastas_wiki_sqlite = (
            await resolver_pastas_wiki_gitlab_efetivas_transcribrothers(session, obter_configuracao())
        )
        prefs_encode, encode_sqlite = (
            await resolver_preferencias_encode_video_narrado_efetivas_transcribrothers(session)
        )
        prefs_voz_tts, voz_tts_sqlite = (
            await resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(session)
        )
        await sincronizar_cache_modelos_litellm_extras_da_session_transcribrothers(session)
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
    modelos = listar_modelos_litellm_permitidos_efetivos_transcribrothers(cfg)
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
        gitlab_wiki_slug_prefixo_pasta=pasta_wiki_padrao,
        gitlab_wiki_pastas_disponiveis=pastas_wiki,
        gitlab_wiki_pastas_preferencia_sqlite_definida=bool(pastas_wiki_sqlite),
        ffmpeg_disponivel=ffmpeg_disponivel_transcribrothers(cfg),
        ffprobe_disponivel=ffprobe_disponivel_transcribrothers(cfg),
        encode_video_narrado_resolucao_efetiva=prefs_encode.resolucao,
        encode_video_narrado_fps_efetivo=int(prefs_encode.fps),
        encode_video_narrado_resolucao_padrao_app=RESOLUCAO_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
        encode_video_narrado_fps_padrao_app=FPS_ENCODE_VIDEO_NARRADO_PADRAO_TRANSCRIBROTHERS,
        encode_video_narrado_resolucoes_disponiveis=list(
            RESOLUCOES_ENCODE_VIDEO_NARRADO_VALIDAS_TRANSCRIBROTHERS
        ),
        encode_video_narrado_preferencia_sqlite_definida=bool(encode_sqlite),
        voz_tts_narracao_efetiva=prefs_voz_tts.voz,
        voz_tts_narracao_padrao_app=VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
        voz_tts_narracao_preferencia_sqlite_definida=bool(voz_tts_sqlite),
        voz_tts_narracao_vozes_disponiveis=listar_vozes_tts_gemini_disponiveis_transcribrothers(),
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


@app.post(
    "/api/gitlab/issues/append-to-existing-issue-description",
    response_model=RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers,
)
async def anexar_markdown_descricao_issue_gitlab_documento_api_transcribrothers(
    corpo: CorpoComentarIssueGitlabDocumentoMarkdownTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers:
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

    imagens_enviadas = 0
    imagens_ignoradas = 0
    descricao_anexada = markdown_fonte
    if corpo.incluir_imagens_png_markdown and corpo.job_id:
        assets_dir = _diretorio_assets_png_exportados_markdown_do_job(data_dir, corpo.job_id)
        try:
            descricao_anexada, imagens_enviadas, imagens_ignoradas = (
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
        issue = await adicionar_markdown_na_descricao_issue_gitlab_existente_transcribrothers(
            cfg,
            issue_url=destino.issue_url,
            markdown_documento=descricao_anexada,
            timeout_segundos=120.0 if imagens_enviadas > 0 else 60.0,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    web_url = str(issue.get("web_url") or destino.issue_url).strip() or destino.issue_url
    return RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers(
        ok=True,
        web_url=web_url,
        issue_url=web_url,
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
    session_factory: SessionFactoryDep,
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
    async with session_factory() as session:
        pastas_permitidas, _, _ = await resolver_pastas_wiki_gitlab_efetivas_transcribrothers(session, cfg)
    if not pasta_wiki_esta_na_lista_permitida_transcribrothers(prefixo, pastas_permitidas):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Pasta wiki {prefixo!r} não está na lista permitida. "
                f"Disponíveis: {', '.join(pastas_permitidas)}. "
                "Cadastre pastas em Configurações."
            ),
        )

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
    async with session_factory() as session:
        pastas_permitidas, _, _ = await resolver_pastas_wiki_gitlab_efetivas_transcribrothers(session, cfg)
    if not pasta_wiki_esta_na_lista_permitida_transcribrothers(prefixo, pastas_permitidas):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Pasta wiki {prefixo!r} não está na lista permitida. "
                f"Disponíveis: {', '.join(pastas_permitidas)}. "
                "Cadastre pastas em Configurações."
            ),
        )
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


@app.post(
    "/api/config/transcribrothers/verificar-modelo-litellm",
    response_model=RespostaVerificarModeloLitellmChatProbeTranscribrothers,
)
async def verificar_modelo_litellm_chat_completions_probe_na_configuracao_transcribrothers(
    request: Request,
    body: CorpoVerificarModeloLitellmChatProbeTranscribrothers,
) -> RespostaVerificarModeloLitellmChatProbeTranscribrothers:
    """Probe barato no proxy: confirma se o modelo aceita chat e devolve texto."""
    cfg = obter_cfg(request)
    resultado = await verificar_modelo_litellm_via_chat_completions_probe_transcribrothers(
        modelo=body.model,
        configuracao=cfg,
    )
    return RespostaVerificarModeloLitellmChatProbeTranscribrothers(
        ok=resultado.ok,
        modelo=resultado.modelo,
        mensagem=resultado.mensagem,
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


@app.get(
    "/api/pipelines/catalogo",
    response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
)
async def obter_catalogo_pipelines_disponiveis_documentacao_transcribrothers(
    session_factory: SessionFactoryDep,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    """Catálogo de pipelines (sistema + custom), passos e prompts."""
    async with session_factory() as session:
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.post("/api/pipelines/custom/duplicar", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def duplicar_pipeline_custom_a_partir_de_fonte_catalogo_transcribrothers(
    session_factory: SessionFactoryDep,
    body: CorpoDuplicarFonteCatalogoCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await duplicar_pipeline_catalogo_para_custom_transcribrothers(session, body.fonte_id.strip())
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.post("/api/pipelines/custom/criar", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def criar_pipeline_custom_a_partir_de_molde_catalogo_transcribrothers(
    session_factory: SessionFactoryDep,
    body: CorpoCriarPipelineCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await criar_pipeline_custom_a_partir_de_molde_transcribrothers(
                session,
                body.fonte_id.strip(),
                titulo=body.titulo,
                descricao=body.descricao,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.put("/api/pipelines/custom/ordem", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def reordenar_pipelines_custom_catalogo_transcribrothers(
    session_factory: SessionFactoryDep,
    body: CorpoReordenarPipelinesCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await reordenar_pipelines_custom_transcribrothers(session, body.pipeline_ids_ordenados)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.patch("/api/pipelines/custom/{pipeline_id}", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def atualizar_pipeline_custom_transcribrothers_api(
    pipeline_id: str,
    session_factory: SessionFactoryDep,
    body: CorpoPatchPipelineCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await atualizar_pipeline_custom_transcribrothers(
                session,
                pipeline_id,
                titulo=body.titulo,
                descricao=body.descricao,
                entradas_aceitas=body.entradas_aceitas,
            )
        except ValueError as e:
            msg = str(e)
            codigo = 404 if "não encontrada" in msg.lower() else 400
            raise HTTPException(status_code=codigo, detail=msg) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.put(
    "/api/pipelines/custom/{pipeline_id}/passos/ordem",
    response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
)
async def reordenar_passos_pipeline_custom_catalogo_transcribrothers(
    pipeline_id: str,
    session_factory: SessionFactoryDep,
    body: CorpoReordenarPassosPipelineCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await reordenar_passos_pipeline_custom_transcribrothers(
                session, pipeline_id, body.passo_ids_ordenados
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.post(
    "/api/pipelines/custom/{pipeline_id}/passos",
    response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
)
async def adicionar_passo_pipeline_custom_catalogo_transcribrothers(
    pipeline_id: str,
    session_factory: SessionFactoryDep,
    body: CorpoAdicionarPassoPipelineCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await adicionar_passo_pipeline_custom_transcribrothers(
                session,
                pipeline_id,
                agente_fonte_id=body.agente_fonte_id.strip(),
                rotulo=body.rotulo,
                descricao=body.descricao,
            )
        except ValueError as e:
            msg = str(e)
            status = 404 if "não encontrad" in msg.lower() else 400
            raise HTTPException(status_code=status, detail=msg) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.delete(
    "/api/pipelines/custom/{pipeline_id}/passos/{passo_id}",
    response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers,
)
async def remover_passo_pipeline_custom_catalogo_transcribrothers(
    pipeline_id: str,
    passo_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await remover_passo_pipeline_custom_transcribrothers(session, pipeline_id, passo_id)
        except ValueError as e:
            msg = str(e)
            status = 404 if "não encontrad" in msg.lower() else 400
            raise HTTPException(status_code=status, detail=msg) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.delete("/api/pipelines/custom/{pipeline_id}", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def excluir_pipeline_custom_transcribrothers_api(
    pipeline_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await excluir_pipeline_custom_transcribrothers(session, pipeline_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.post("/api/agentes/custom/duplicar", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def duplicar_agente_custom_a_partir_de_fonte_catalogo_transcribrothers(
    session_factory: SessionFactoryDep,
    body: CorpoDuplicarFonteCatalogoCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await duplicar_agente_catalogo_para_custom_transcribrothers(session, body.fonte_id.strip())
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.patch("/api/agentes/custom/{agente_id}", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def atualizar_agente_custom_transcribrothers_api(
    agente_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchAgenteCustomTranscribrothers,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    cfg = obter_cfg(request)
    modelo_norm: str | None | object = ...
    if "modelo_litellm" in body.model_fields_set:
        modelo_norm = (
            _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, body.modelo_litellm or None)
            if (body.modelo_litellm or "").strip()
            else None
        )
    prompts_json = None
    if body.prompts is not None:
        prompts_json = [p.model_dump() for p in body.prompts]
    async with session_factory() as session:
        try:
            await atualizar_agente_custom_transcribrothers(
                session,
                agente_id,
                rotulo=body.rotulo,
                descricao=body.descricao,
                prompts_json=prompts_json,
                modelo_litellm=modelo_norm,
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


@app.delete("/api/agentes/custom/{agente_id}", response_model=RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers)
async def excluir_agente_custom_transcribrothers_api(
    agente_id: str,
    session_factory: SessionFactoryDep,
) -> RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers:
    async with session_factory() as session:
        try:
            await excluir_agente_custom_transcribrothers(session, agente_id)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e
        return await montar_resposta_catalogo_pipelines_mesclado_sistema_e_custom_transcribrothers(session)


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


@app.patch(
    "/api/config/transcribrothers/encode-video-narrado-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def atualizar_preferencia_runtime_encode_video_narrado_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchEncodeVideoNarradoRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        try:
            await gravar_preferencias_encode_video_narrado_runtime_sqlite_transcribrothers(
                session,
                resolucao=body.resolucao,
                fps=int(body.fps),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.delete(
    "/api/config/transcribrothers/encode-video-narrado-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def apagar_preferencia_runtime_encode_video_narrado_volta_ao_padrao_app_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await apagar_override_encode_video_narrado_runtime_sqlite_transcribrothers(session)
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.patch(
    "/api/config/transcribrothers/voz-tts-narracao-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def atualizar_preferencia_runtime_voz_tts_narracao_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchVozTtsNarracaoRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        try:
            await gravar_preferencias_voz_tts_narracao_runtime_sqlite_transcribrothers(
                session,
                voz=body.voz,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.delete(
    "/api/config/transcribrothers/voz-tts-narracao-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def apagar_preferencia_runtime_voz_tts_narracao_volta_ao_padrao_app_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await apagar_override_voz_tts_narracao_runtime_sqlite_transcribrothers(session)
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.patch(
    "/api/config/transcribrothers/gitlab-wiki-pastas-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def atualizar_pastas_wiki_gitlab_runtime_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchPastasWikiGitlabRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        try:
            await gravar_pastas_wiki_gitlab_runtime_sqlite_transcribrothers(
                session,
                pastas=list(body.pastas),
                pasta_padrao=body.pasta_padrao,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.delete(
    "/api/config/transcribrothers/gitlab-wiki-pastas-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def apagar_pastas_wiki_gitlab_runtime_volta_ao_env_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaConfigPublicaTranscribrothers:
    async with session_factory() as session:
        await apagar_override_pastas_wiki_gitlab_runtime_sqlite_transcribrothers(session)
    return await _montar_resposta_config_publica_transcribrothers(request)


@app.patch(
    "/api/config/transcribrothers/modelos-litellm-extras-runtime",
    response_model=RespostaConfigPublicaTranscribrothers,
)
async def adicionar_modelo_litellm_extra_runtime_via_sqlite_transcribrothers(
    request: Request,
    session_factory: SessionFactoryDep,
    body: CorpoPatchModeloLitellmExtraRuntimeTranscribrothers,
) -> RespostaConfigPublicaTranscribrothers:
    """Inclui um slug na allowlist runtime (além de LITELLM_MODELOS_PROVISIONADOS)."""
    async with session_factory() as session:
        try:
            await adicionar_modelo_litellm_extra_runtime_sqlite_transcribrothers(
                session,
                modelo=body.modelo,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return await _montar_resposta_config_publica_transcribrothers(request)


class RespostaValidarPastaWikiGitlabIndiceTranscribrothers(BaseModel):
    pasta: str
    existe_no_gitlab: bool
    web_url_indice: str


@app.get(
    "/api/gitlab/wikis/validar-pasta-indice",
    response_model=RespostaValidarPastaWikiGitlabIndiceTranscribrothers,
)
async def validar_pasta_indice_wiki_gitlab_existe_api_transcribrothers(
    pasta: str,
) -> RespostaValidarPastaWikiGitlabIndiceTranscribrothers:
    """Confirma se a página índice da pasta existe no projeto wiki (somente leitura)."""
    cfg = obter_configuracao()
    if not gitlab_criar_wiki_configurado_no_ambiente_transcribrothers(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "GitLab wiki não configurado no servidor. Defina GITLAB_BASE_URL, GITLAB_TOKEN e "
                "GITLAB_WIKI_PROJECT_PATH."
            ),
        )
    try:
        pasta_norm = resolver_prefixo_pasta_wiki_gitlab_transcribrothers(cfg, pasta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    existe = await pagina_wiki_gitlab_existe_no_projeto_transcribrothers(cfg, pasta_norm)
    web_indice = montar_web_url_pagina_indice_pasta_wiki_gitlab_documentacao_transcribrothers(
        cfg, prefixo_pasta=pasta_norm
    )
    return RespostaValidarPastaWikiGitlabIndiceTranscribrothers(
        pasta=pasta_norm,
        existe_no_gitlab=bool(existe),
        web_url_indice=web_indice,
    )


_DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS = frozenset(
    {"gerar_tutorial", "reproducao_bug", "notas_proposta_funcionalidade", "so_transcricao"},
)

_DESTINOS_UPLOAD_SOMENTE_VIDEO_TRANSCRIBROTHERS = frozenset(
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


_MAX_PARTES_VIDEO_UPLOAD_MULTI_TRANSCRIBROTHERS = 12


@app.post("/api/jobs/upload", response_model=RespostaJobTranscribrothers)
async def criar_novo_job_pipeline_a_partir_de_upload_video_arquivo_local(
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    video: Annotated[UploadFile | None, File(description="Arquivo de vídeo do seu computador")] = None,
    videos: Annotated[
        list[UploadFile] | None,
        File(description="Um ou mais vídeos na ordem da timeline (unificados antes do pipeline)"),
    ] = None,
    staging_id: Annotated[str | None, Form()] = None,
    litellm_model: Annotated[str | None, Form()] = None,
    tutorial_litellm_instrucao_prefixo: Annotated[str | None, Form()] = None,
    destino_apos_transcricao: Annotated[str | None, Form()] = None,
    pipeline_custom_id: Annotated[str | None, Form()] = None,
    cliques_json: Annotated[
        UploadFile | None,
        File(description="JSON opcional de cliques (reproducao_bug)"),
    ] = None,
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    job_id = novo_id_job()
    try:
        return await _criar_novo_job_pipeline_a_partir_de_upload_video_arquivo_local_impl_transcribrothers(
            session_factory=session_factory,
            data_dir=data_dir,
            cfg=cfg,
            job_id=job_id,
            video=video,
            videos=videos,
            staging_id=staging_id,
            litellm_model=litellm_model,
            tutorial_litellm_instrucao_prefixo=tutorial_litellm_instrucao_prefixo,
            destino_apos_transcricao=destino_apos_transcricao,
            pipeline_custom_id=pipeline_custom_id,
            cliques_json=cliques_json,
        )
    except HTTPException:
        raise
    except Exception as e:
        log_erro_upload_video_job_transcribrothers(job_id=job_id, etapa="upload_nao_tratado", exc=e)
        raise


async def _criar_novo_job_pipeline_a_partir_de_upload_video_arquivo_local_impl_transcribrothers(
    *,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    cfg: ConfiguracaoAmbienteTranscribrothers,
    job_id: str,
    video: UploadFile | None,
    videos: list[UploadFile] | None,
    staging_id: str | None,
    litellm_model: str | None,
    tutorial_litellm_instrucao_prefixo: str | None,
    destino_apos_transcricao: str | None,
    pipeline_custom_id: str | None,
    cliques_json: UploadFile | None,
) -> RespostaJobTranscribrothers:
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
    staging_id_norm = (staging_id or "").strip()
    nome_arquivo_video = (video.filename or "").strip() if video is not None else ""
    partes_videos_lista = [
        u for u in (videos or []) if u is not None and (u.filename or "").strip()
    ]
    tem_staging = bool(staging_id_norm)
    tem_video_legado = bool(nome_arquivo_video)
    tem_videos_lista = bool(partes_videos_lista)
    if tem_staging and tem_video_legado and not tem_videos_lista:
        raise HTTPException(
            status_code=400,
            detail="Informe apenas video ou staging_id, não ambos. Para complementar o staging, use o campo videos.",
        )
    if not tem_staging and not tem_video_legado and not tem_videos_lista:
        raise HTTPException(
            status_code=400,
            detail="Envie o arquivo video (ou videos) ou um staging_id de importação RecBrothers.",
        )
    if len(partes_videos_lista) > _MAX_PARTES_VIDEO_UPLOAD_MULTI_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No máximo {_MAX_PARTES_VIDEO_UPLOAD_MULTI_TRANSCRIBROTHERS} vídeos por upload."
            ),
        )

    modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, litellm_model)

    try:
        instr_norm = normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers(
            tutorial_litellm_instrucao_prefixo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    destino_pipeline = (destino_apos_transcricao or "gerar_tutorial").strip()
    pipeline_custom_norm = (pipeline_custom_id or "").strip()
    snapshot_pipeline_custom: dict[str, Any] | None = None
    entradas_aceitas_efetivas: list[str] = ["video"]
    if pipeline_custom_norm:
        async with session_factory() as session:
            pipeline_row = await obter_pipeline_custom_por_id_transcribrothers(session, pipeline_custom_norm)
            if pipeline_row is None:
                raise HTTPException(status_code=400, detail=f"pipeline_custom_id inválido: {pipeline_custom_norm!r}.")
            copiado_de = str(pipeline_row.copiado_de or "")
            if not pipeline_custom_e_executavel_upload_transcribrothers(copiado_de):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Esta pipeline custom não pode ser usada no upload (fluxo 2). "
                        "Duplique um fluxo inicial (tutorial, notas, bug ou só transcrição)."
                    ),
                )
            destino_mapeado = mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(copiado_de)
            if not destino_mapeado:
                raise HTTPException(status_code=400, detail=f"Pipeline sem destino de upload mapeado: {copiado_de!r}.")
            destino_pipeline = destino_mapeado
            from transcribrothers_backend.modulo_catalogo_pipelines_disponiveis_documentacao_transcribrothers import (
                normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers,
                obter_pipeline_catalogo_sistema_por_id_transcribrothers,
            )

            molde = obter_pipeline_catalogo_sistema_por_id_transcribrothers(copiado_de)
            padrao_e = list(molde.entradas_aceitas) if molde else ["video"]
            entradas_aceitas_efetivas = list(
                normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
                    pipeline_row.entradas_aceitas_json,
                    padrao=padrao_e,  # type: ignore[arg-type]
                )
            )
            agentes_rows = await carregar_agentes_custom_da_pipeline_transcribrothers(session, pipeline_row)
            snapshot_pipeline_custom = montar_snapshot_completo_pipeline_custom_para_steps_json_transcribrothers(
                pipeline_row,
                agentes_rows,
            )
    else:
        if destino_pipeline == "so_transcricao":
            entradas_aceitas_efetivas = ["video", "audio"]
        else:
            entradas_aceitas_efetivas = ["video"]

    if destino_pipeline not in _DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"destino_apos_transcricao inválido: {destino_pipeline!r}. "
                f"Valores aceitos: {', '.join(sorted(_DESTINOS_APOS_TRANSCRICAO_UPLOAD_VALIDOS_TRANSCRIBROTHERS))}."
            ),
        )

    if destino_pipeline != "so_transcricao" and not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(
        cfg
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "O job inclui geração de documento no proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                "(POST /v1/chat/completions). Não há fluxo sem proxy neste projeto."
            ),
        )

    nome_cliques_json = (cliques_json.filename or "").strip() if cliques_json is not None else ""
    if nome_cliques_json and destino_pipeline != "reproducao_bug":
        raise HTTPException(
            status_code=400,
            detail="JSON de cliques só pode ser enviado com destino_apos_transcricao=reproducao_bug.",
        )

    partes_upload_ordenadas: list[UploadFile] = list(partes_videos_lista)
    if not partes_upload_ordenadas and tem_video_legado and video is not None:
        partes_upload_ordenadas = [video]

    nome_log_upload = (
        f"{len(partes_upload_ordenadas)} vídeos"
        if len(partes_upload_ordenadas) > 1
        else (nome_arquivo_video or staging_id_norm or "?")
    )
    log_inicio_upload_video_job_transcribrothers(
        job_id=job_id,
        destino_apos_transcricao=destino_pipeline,
        nome_arquivo=nome_log_upload,
        max_video_bytes=int(cfg.max_video_bytes),
        data_dir=data_dir.resolve(),
        via_staging=tem_staging,
    )

    work = _diretorio_trabalho_job(data_dir, job_id)
    work.mkdir(parents=True, exist_ok=True)

    importado_recbrothers_staging_id: str | None = None
    extras_staging: dict = {}
    total_cliques_reproducao_bug = 0
    tipo_entrada_midia = "video"
    destino_midia: Path
    nome_original: str
    total: int
    meta_unificacao_upload: dict[str, Any] | None = None

    caminhos_para_unificar: list[Path] = []
    nomes_originais_para_unificar: list[str] = []

    if tem_staging:
        meta_staging = obter_metadados_staging_video_ou_erro_http(data_dir, staging_id_norm)
        destino_staging = work / f"video_entrada_arquivo_local{meta_staging.ext}"
        nome_original, total, _ext, extras_staging = consumir_staging_video_para_destino_job(
            data_dir,
            staging_id_norm,
            destino_staging,
        )
        importado_recbrothers_staging_id = staging_id_norm
        total_cliques_reproducao_bug = int(extras_staging.get("total_cliques") or 0)
        tipo_entrada_midia = "video"
        destino_midia = destino_staging
        if partes_upload_ordenadas:
            caminhos_para_unificar.append(destino_staging)
            nomes_originais_para_unificar.append(nome_original)
    else:
        if not partes_upload_ordenadas:
            raise HTTPException(status_code=400, detail="Envie ao menos um arquivo de vídeo ou áudio.")
        nome_original = partes_upload_ordenadas[0].filename or "video.mp4"
        try:
            tipo_entrada_midia = classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers(nome_original)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if tipo_entrada_midia not in entradas_aceitas_efetivas:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Esta pipeline/destino não aceita entrada '{tipo_entrada_midia}'. "
                    f"Aceitas: {', '.join(entradas_aceitas_efetivas)}."
                ),
            )
        if tipo_entrada_midia == "audio" and destino_pipeline in _DESTINOS_UPLOAD_SOMENTE_VIDEO_TRANSCRIBROTHERS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Tutorial, notas e reprodução de bug exigem vídeo nesta versão. "
                    "Use «Só transcrição» para áudio."
                ),
            )
        if tipo_entrada_midia == "audio":
            if len(partes_upload_ordenadas) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Unificação de vários arquivos no upload só está disponível para vídeo.",
                )
            ext = extrair_extensao_audio_sanitizada_para_upload_local(nome_original)
            destino_midia = work / f"audio_entrada_arquivo_local{ext}"
            total = await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
                partes_upload_ordenadas[0],
                destino_midia,
                int(cfg.max_video_bytes),
                job_id=job_id,
            )
        elif len(partes_upload_ordenadas) == 1:
            try:
                ext = extrair_extensao_video_sanitizada_para_upload_local(nome_original)
            except ErroExtensaoVideoUploadTranscribrothers as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            destino_midia = work / f"video_entrada_arquivo_local{ext}"
            total = await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
                partes_upload_ordenadas[0],
                destino_midia,
                int(cfg.max_video_bytes),
                job_id=job_id,
            )
        else:
            # Vários vídeos: grava temporários e unifica antes do pipeline.
            for i, parte in enumerate(partes_upload_ordenadas):
                nome_parte = (parte.filename or f"parte_{i + 1}.mp4").strip()
                try:
                    tipo_parte = classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers(nome_parte)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e)) from e
                if tipo_parte != "video":
                    raise HTTPException(
                        status_code=400,
                        detail="Todos os arquivos em videos devem ser de vídeo para unificação.",
                    )
                try:
                    ext_parte = extrair_extensao_video_sanitizada_para_upload_local(nome_parte)
                except ErroExtensaoVideoUploadTranscribrothers as e:
                    raise HTTPException(status_code=400, detail=str(e)) from e
                dest_parte = work / f".upload_parte_video_{i + 1:03d}{ext_parte}"
                await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
                    parte,
                    dest_parte,
                    int(cfg.max_video_bytes),
                    job_id=job_id,
                )
                caminhos_para_unificar.append(dest_parte)
                nomes_originais_para_unificar.append(nome_parte)
            destino_midia = caminhos_para_unificar[0]
            total = sum(p.stat().st_size for p in caminhos_para_unificar)
            nome_original = " + ".join(Path(n).name for n in nomes_originais_para_unificar)

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

    if tem_staging and partes_upload_ordenadas:
        for i, parte in enumerate(partes_upload_ordenadas):
            nome_parte = (parte.filename or f"parte_extra_{i + 1}.mp4").strip()
            try:
                tipo_parte = classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers(nome_parte)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            if tipo_parte != "video":
                raise HTTPException(
                    status_code=400,
                    detail="Complementos do staging devem ser arquivos de vídeo.",
                )
            try:
                ext_parte = extrair_extensao_video_sanitizada_para_upload_local(nome_parte)
            except ErroExtensaoVideoUploadTranscribrothers as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            dest_parte = work / f".upload_parte_video_{i + 1:03d}{ext_parte}"
            await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
                parte,
                dest_parte,
                int(cfg.max_video_bytes),
                job_id=job_id,
            )
            caminhos_para_unificar.append(dest_parte)
            nomes_originais_para_unificar.append(nome_parte)
        nome_original = " + ".join(Path(n).name for n in nomes_originais_para_unificar)

    if tem_staging and tipo_entrada_midia not in entradas_aceitas_efetivas:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Esta pipeline/destino não aceita entrada '{tipo_entrada_midia}'. "
                f"Aceitas: {', '.join(entradas_aceitas_efetivas)}."
            ),
        )

    if len(caminhos_para_unificar) >= 2:
        try:
            meta_unificacao_upload = (
                await preparar_video_entrada_unificado_a_partir_lista_clips_no_work_transcribrothers(
                    work=work,
                    caminhos_clips_ordenados=caminhos_para_unificar,
                    nomes_originais_ordenados=nomes_originais_para_unificar,
                )
            )
        except ErroPrepararVideoEntradaMultiploTranscribrothers as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao unificar os vídeos do upload: {type(e).__name__}: {e}",
            ) from e
        destino_midia = Path(meta_unificacao_upload["caminho_video_entrada"])
        total = int(meta_unificacao_upload["bytes_written"])
        nome_original = " + ".join(meta_unificacao_upload.get("nomes_originais") or nomes_originais_para_unificar)

    duracao_video_segundos_ffprobe = await obter_duracao_video_segundos_via_ffprobe(destino_midia)
    if meta_unificacao_upload and meta_unificacao_upload.get("duracao_video_segundos"):
        duracao_video_segundos_ffprobe = float(meta_unificacao_upload["duracao_video_segundos"])
    log_fim_gravacao_video_upload_job_transcribrothers(
        job_id=job_id,
        destino_video=destino_midia,
        bytes_gravados=total,
        duracao_ffprobe_segundos=float(duracao_video_segundos_ffprobe),
    )

    async with session_factory() as session:
        steps_json = {
            "source": OrigemEntradaJobTranscribrothers.upload_local,
            "upload_ok": True,
            "original_filename": nome_original,
            "saved_as": destino_midia.name,
            "bytes_written": total,
            "litellm_model": modelo_litellm,
            "destino_apos_transcricao": destino_pipeline,
            "tipo_entrada_midia": tipo_entrada_midia,
        }
        if duracao_video_segundos_ffprobe > 0:
            steps_json["duracao_video_segundos"] = round(float(duracao_video_segundos_ffprobe), 3)
        if instr_norm is not None:
            steps_json["tutorial_litellm_instrucao_prefixo_custom"] = instr_norm
        if importado_recbrothers_staging_id:
            steps_json["importado_recbrothers_staging_id"] = importado_recbrothers_staging_id
        if meta_unificacao_upload:
            steps_json["ultimo_modo_concat_video_entrada"] = meta_unificacao_upload.get(
                "modo_concat_video_entrada"
            )
            steps_json["videos_unificados_no_upload"] = {
                "nomes_originais": meta_unificacao_upload.get("nomes_originais"),
                "clips_arquivados": meta_unificacao_upload.get("clips_arquivados"),
                "modo_concat_video_entrada": meta_unificacao_upload.get("modo_concat_video_entrada"),
                "unificado_em_utc": meta_unificacao_upload.get("unificado_em_utc"),
            }
        if destino_pipeline == "reproducao_bug":
            steps_json["reproducao_bug_total_cliques"] = total_cliques_reproducao_bug
            if total_cliques_reproducao_bug <= 0:
                steps_json["reproducao_bug_sem_json_cliques"] = True
            steps_json["modo_recbrothers"] = extras_staging.get("modo_recbrothers")
        if snapshot_pipeline_custom:
            steps_json.update(snapshot_pipeline_custom)
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
    log_job_upload_registrado_e_pipeline_agendado_transcribrothers(job_id=job_id)

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


@app.post("/api/jobs/importar-transcricao", response_model=RespostaJobTranscribrothers)
async def importar_transcricao_pronta_criar_job_sem_stt_transcribrothers(
    request: Request,
    data_dir: DataDirDep,
    session_factory: SessionFactoryDep,
    destino_apos_transcricao: Annotated[str, Form()] = "so_transcricao",
    texto: Annotated[str | None, Form()] = None,
    pipeline_custom_id: Annotated[str | None, Form()] = None,
    litellm_model: Annotated[str | None, Form()] = None,
    arquivo: UploadFile | None = File(None),
) -> RespostaJobTranscribrothers:
    """Cria job a partir de texto/legendas já existentes (sem STT nem mídia)."""
    cfg = obter_cfg(request)
    destino = (destino_apos_transcricao or "").strip() or "so_transcricao"
    modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, litellm_model)

    if destino == "notas_proposta_funcionalidade" or (pipeline_custom_id or "").strip():
        if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Geração de notas usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT "
                    "(POST /v1/chat/completions)."
                ),
            )

    conteudo_arquivo: bytes | None = None
    nome_arquivo: str | None = None
    if arquivo is not None and (arquivo.filename or "").strip():
        nome_arquivo = (arquivo.filename or "").strip()
        conteudo_arquivo = await arquivo.read()
        if len(conteudo_arquivo) > int(cfg.max_video_bytes):
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo excede o limite de {int(cfg.max_video_bytes)} bytes.",
            )

    try:
        row, deve_agendar = await criar_job_a_partir_transcricao_importada_pronta_transcribrothers(
            data_dir=data_dir,
            session_factory=session_factory,
            texto=texto,
            nome_arquivo=nome_arquivo,
            conteudo_arquivo=conteudo_arquivo,
            destino_solicitado=destino,
            pipeline_custom_id=pipeline_custom_id,
            modelo_litellm=modelo_litellm,
        )
    except (
        ErroTranscricaoImportadaVaziaOuInvalidaTranscribrothers,
        ErroImportarTranscricaoProntaTranscribrothers,
    ) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if deve_agendar:
        agendar_pipeline_job_em_task_assincrona(
            job_id=row.id,
            session_factory=session_factory,
            configuracao=cfg,
        )

    async with session_factory() as session:
        criado = await session.get(JobPipelineTranscribrothers, row.id)
        assert criado is not None
        resp = _job_para_resposta(criado)
        work = _diretorio_trabalho_job(data_dir, row.id)
        steps_enriquecidos = dict(resp.steps_json)
        steps_enriquecidos["pode_gerar_outro_formato"] = (
            job_pode_gerar_outro_formato_pos_transcricao_transcribrothers(job=criado, work=work)
        )
        return resp.model_copy(update={"steps_json": steps_enriquecidos})


@app.get("/api/jobs", response_model=list[ResumoJobListaPipelineTranscribrothers])
async def listar_jobs_recentes_do_pipeline_transcribrothers(
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 40,
) -> list[ResumoJobListaPipelineTranscribrothers]:
    from transcribrothers_backend.modulo_calcular_tamanho_bytes_diretorio_job_pipeline_transcribrothers import (
        calcular_tamanho_bytes_diretorio_recursivo_transcribrothers,
    )

    async with session_factory() as session:
        stmt = (
            select(JobPipelineTranscribrothers)
            .order_by(JobPipelineTranscribrothers.updated_at.desc())
            .limit(int(limit))
        )
        rows = (await session.scalars(stmt)).all()
    saida: list[ResumoJobListaPipelineTranscribrothers] = []
    for r in rows:
        work = _diretorio_trabalho_job(data_dir, r.id)
        tamanho = calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(work)
        saida.append(_resumo_job_para_lista(r, tamanho_bytes_disco=tamanho))
    return saida


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
        resp = _job_para_resposta(row)
        steps_enriquecidos = dict(resp.steps_json)
        steps_enriquecidos["pode_gerar_outro_formato"] = (
            job_pode_gerar_outro_formato_pos_transcricao_transcribrothers(job=row, work=work)
        )
        return resp.model_copy(update={"steps_json": steps_enriquecidos})


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
        steps = dict(row2.steps_json or {})
        steps["cancelamento_pipeline_solicitado"] = True
        steps["pipeline_fase"] = "cancelamento_solicitado"
        row2.steps_json = steps
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(row2, "steps_json")
        # Libera a UI imediatamente; o worker em background para no próximo checkpoint.
        row2.status = StatusJobTranscribrothers.cancelled.value
        row2.error_message = "Cancelado pelo usuário."
        row2.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(row2)
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


@app.post("/api/jobs/{job_id}/gerar-outro-formato", response_model=RespostaJobTranscribrothers)
async def gerar_outro_formato_pos_transcricao_reutilizando_transcricao_job_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    body: CorpoGerarOutroFormatoPosTranscricaoJobTranscribrothers,
) -> RespostaJobTranscribrothers:
    cfg = obter_cfg(request)
    if not tem_credencial_para_transcricao_no_pipeline(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Transcrição: configure o proxy LiteLLM com LITELLM_API_KEY e LITELLM_ENDPOINT."
            ),
        )
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Geração de documento usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT."
            ),
        )
    modelo_litellm = _resolver_modelo_litellm_para_job_ou_erro_http_400(cfg, body.litellm_model)
    work = _diretorio_trabalho_job(data_dir, job_id)
    destino_solicitado = (body.destino_apos_transcricao or "").strip()

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        try:
            validar_job_pode_gerar_outro_formato_transcribrothers(
                job=row,
                work=work,
                novo_destino=destino_solicitado,
            )
            novo_destino, snapshot_pipeline_custom = (
                await resolver_snapshot_pipeline_custom_para_gerar_outro_formato_transcribrothers(
                    session,
                    body.pipeline_custom_id,
                    destino_solicitado,
                )
            )
        except ErroGerarOutroFormatoJobTranscribrothers as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        row = await aplicar_gerar_outro_formato_no_job_transcribrothers(
            session,
            job=row,
            novo_destino=novo_destino,
            snapshot_pipeline_custom=snapshot_pipeline_custom,
            modelo_litellm=modelo_litellm,
            session_factory=session_factory,
        )

    agendar_pipeline_job_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
    )

    async with session_factory() as session:
        criado = await session.get(JobPipelineTranscribrothers, job_id)
        assert criado is not None
        resp = _job_para_resposta(criado)
        steps_enriquecidos = dict(resp.steps_json)
        steps_enriquecidos["pode_gerar_outro_formato"] = False
        return resp.model_copy(update={"steps_json": steps_enriquecidos})


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


@app.post(
    "/api/jobs/{job_id}/anexar-gravacao-complementar-video-entrada",
    response_model=RespostaJobTranscribrothers,
)
async def anexar_gravacao_complementar_concatenar_e_reprocessar_pipeline_job_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    video: UploadFile = File(..., description="Gravação complementar para unificar ao vídeo de entrada"),
) -> RespostaJobTranscribrothers:
    """
    Concatena a gravação complementar ao `video_entrada` atual, invalida STT/tutorial
    derivados e agenda o pipeline completo de novo.
    """
    cfg = obter_cfg(request)
    if not tem_credencial_para_transcricao_no_pipeline(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Transcrição: configure o proxy LiteLLM com LITELLM_API_KEY e LITELLM_ENDPOINT."
            ),
        )
    if not tem_credencial_gateway_litellm_para_tutorial_markdown_no_proxy(cfg):
        raise HTTPException(
            status_code=503,
            detail=(
                "Geração de documento usa o proxy LiteLLM: defina LITELLM_API_KEY e LITELLM_ENDPOINT."
            ),
        )

    nome_original = (video.filename or "complementar.mp4").strip() or "complementar.mp4"
    try:
        ext = extrair_extensao_video_sanitizada_para_upload_local(nome_original)
    except ErroExtensaoVideoUploadTranscribrothers as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    work = _diretorio_trabalho_job(data_dir, job_id)
    work.mkdir(parents=True, exist_ok=True)

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        if row.status not in (
            StatusJobTranscribrothers.completed.value,
            StatusJobTranscribrothers.failed.value,
            StatusJobTranscribrothers.cancelled.value,
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Só é possível anexar gravação complementar quando o job já terminou "
                    "(completed, failed ou cancelled)."
                ),
            )
        steps = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
        if steps.get("tipo_entrada_midia") == "audio":
            raise HTTPException(
                status_code=400,
                detail="Este job é só-áudio; não é possível anexar gravação de vídeo complementar.",
            )
        if _localizar_arquivo_video_entrada_no_diretorio_job(work) is None:
            raise HTTPException(
                status_code=400,
                detail="Este job ainda não tem vídeo de entrada para unificar.",
            )

    destino_upload = work / f".upload_gravacao_complementar_tmp{ext}"
    destino_upload.unlink(missing_ok=True)
    try:
        await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
            video,
            destino_upload,
            int(cfg.max_video_bytes),
            job_id=job_id,
        )
        try:
            metadados = await unificar_video_entrada_com_gravacao_complementar_no_work_transcribrothers(
                work=work,
                caminho_video_complementar=destino_upload,
                nome_original_complementar=nome_original,
            )
        except ErroAnexarGravacaoComplementarTranscribrothers as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao unificar os vídeos: {type(e).__name__}: {e}",
            ) from e
    finally:
        destino_upload.unlink(missing_ok=True)

    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
        row.steps_json = aplicar_metadados_unificacao_nos_steps_json_transcribrothers(steps, metadados)
        flag_modified(row, "steps_json")
        row.status = StatusJobTranscribrothers.pending.value
        row.error_message = None
        row.result_markdown = None
        await session.commit()

    agendar_pipeline_job_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
    )

    async with session_factory() as session:
        atualizado = await session.get(JobPipelineTranscribrothers, job_id)
        assert atualizado is not None
        return _job_para_resposta(atualizado)


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


@app.post(
    "/api/jobs/{job_id}/gerar-narracao-tts-markdown",
    response_model=RespostaGerarNarracaoTtsMarkdownJobTranscribrothers,
)
async def gerar_narracao_tts_markdown_do_documento_job_transcribrothers(
    job_id: str,
    body: CorpoGerarNarracaoTtsMarkdownJobTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaGerarNarracaoTtsMarkdownJobTranscribrothers:
    """Narração TTS do Markdown atual do job (ação pós-documento; grava WAV em assets/)."""
    cfg = obter_cfg(request)
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
                detail="Só é possível gerar narração quando o job está concluído ou falhou.",
            )
        markdown = (row.result_markdown or "").strip()
        if not markdown:
            raise HTTPException(status_code=400, detail="Documento sem Markdown para narrar.")

    try:
        modelo = resolver_modelo_tts_para_narracao_documento_transcribrothers(
            cfg,
            body.litellm_model,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    texto = extrair_texto_plano_para_narracao_tts_a_partir_markdown_tutorial_transcribrothers(markdown)
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    assets.mkdir(parents=True, exist_ok=True)
    caminho_wav = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS

    resultado = await gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers(
        texto_plano=texto,
        modelo=modelo,
        configuracao=cfg,
        caminho_wav_saida=caminho_wav,
    )
    if not resultado.ok:
        raise HTTPException(status_code=502, detail=resultado.mensagem)

    url_asset = f"/api/jobs/{job_id}/assets/{resultado.nome_arquivo}"
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": resultado.nome_arquivo,
            "url_asset": url_asset,
            "modelo": resultado.modelo,
            "texto_caracteres": resultado.texto_caracteres,
            "texto_truncado": resultado.texto_truncado,
            "gerado_em": datetime.now(timezone.utc).isoformat(),
        }
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    return RespostaGerarNarracaoTtsMarkdownJobTranscribrothers(
        ok=True,
        mensagem=resultado.mensagem,
        nome_arquivo=resultado.nome_arquivo,
        url_asset=url_asset,
        modelo=resultado.modelo,
        texto_caracteres=resultado.texto_caracteres,
        texto_truncado=resultado.texto_truncado,
    )


@app.post(
    "/api/jobs/{job_id}/gerar-video-com-narracao-tts",
    response_model=RespostaGerarVideoComNarracaoTtsJobTranscribrothers,
)
async def gerar_video_com_narracao_tts_substituindo_audio_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaGerarVideoComNarracaoTtsJobTranscribrothers:
    """Copia o vídeo do job trocando o áudio original pela narração TTS já gerada."""
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
                detail="Só é possível gerar o vídeo com narração quando o job está concluído ou falhou.",
            )

    work = _diretorio_trabalho_job(data_dir, job_id)
    video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    if video is None or not video.is_file():
        raise HTTPException(
            status_code=400,
            detail="Este job não tem vídeo de entrada para montar a cópia com narração.",
        )

    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    wav = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    if not wav.is_file():
        raise HTTPException(
            status_code=400,
            detail=(
                "Gere a narração TTS do documento antes "
                f"(arquivo {NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS} não encontrado)."
            ),
        )

    try:
        caminho_saida = await substituir_audio_do_video_pela_narracao_tts_wav_via_ffmpeg_transcribrothers(
            caminho_video=video,
            caminho_narracao_wav=wav,
            diretorio_saida=work,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ErroFfmpegTranscribrothers as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    url_download = f"/api/jobs/{job_id}/video-com-narracao-tts"
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_saida.name,
            "url_download": url_download,
            "gerado_em": datetime.now(timezone.utc).isoformat(),
        }
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    return RespostaGerarVideoComNarracaoTtsJobTranscribrothers(
        ok=True,
        mensagem=(
            "Vídeo com narração gerado (áudio original substituído pela TTS). "
            "A duração segue o fluxo mais curto entre vídeo e narração."
        ),
        nome_arquivo=caminho_saida.name,
        url_download=url_download,
    )


@app.get("/api/jobs/{job_id}/video-com-narracao-tts")
async def baixar_video_com_narracao_tts_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    caminho = work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    if not caminho.is_file():
        raise HTTPException(
            status_code=404,
            detail="Vídeo com narração ainda não foi gerado. Use «Gerar vídeo com narração».",
        )
    return FileResponse(
        str(caminho),
        media_type="video/mp4",
        filename=NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
    )


@app.get("/api/jobs/{job_id}/midia-fonte")
async def listar_midia_fonte_e_cache_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    return inventariar_midia_fonte_e_cache_do_work_transcribrothers(work, job_id=job_id)


@app.get("/api/jobs/{job_id}/debug-cache-segmentos-video-narrado")
async def obter_debug_cache_segmentos_video_narrado_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    """Painel de debug: cache de segmentos no disco + último mux nos steps."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {}) if isinstance(row.steps_json, dict) else {}
    work = _diretorio_trabalho_job(data_dir, job_id)
    return montar_payload_debug_cache_segmentos_video_narrado_job_transcribrothers(
        work,
        steps=steps,
    )


@app.get("/api/jobs/{job_id}/midia-fonte/arquivo/{nome_arquivo}")
async def servir_arquivo_midia_fonte_do_job_transcribrothers(
    job_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    try:
        caminho = resolver_arquivo_midia_fonte_permitido_transcribrothers(work, nome_arquivo)
    except ErroMidiaFonteJobTranscribrothers as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    nome = caminho.name.lower()
    media = "application/octet-stream"
    if nome.endswith(".mp4") or nome.endswith(".webm") or nome.endswith(".mkv"):
        media = "video/mp4" if nome.endswith(".mp4") else "application/octet-stream"
    elif nome.endswith(".wav"):
        media = "audio/wav"
    elif nome.endswith(".m4a"):
        media = "audio/mp4"
    elif nome.endswith(".mp3"):
        media = "audio/mpeg"
    elif nome.endswith(".opus"):
        media = "audio/opus"
    return FileResponse(str(caminho), media_type=media, filename=caminho.name)


@app.post("/api/jobs/{job_id}/midia-fonte/limpar-cache")
async def limpar_cache_midia_fonte_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    cache_bytes = limpar_cache_regeneravel_job_transcribrothers(work)
    return {"ok": True, "cache_bytes": cache_bytes}


@app.get("/api/jobs/{job_id}/biblioteca-midias-tela")
async def listar_biblioteca_midias_tela_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    """Lista o vídeo de entrada (lógico) e os vídeos extras de tela do job."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    video_entrada = _localizar_arquivo_video_entrada_no_diretorio_job(work)
    entrada: dict[str, object] | None = None
    if video_entrada is not None and video_entrada.is_file():
        try:
            tamanho = video_entrada.stat().st_size
        except OSError:
            tamanho = 0
        entrada = {
            "id": ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS,
            "nome_arquivo": video_entrada.name,
            "nome_original": video_entrada.name,
            "criado_em": "",
            "tamanho_bytes": tamanho,
            "duracao_segundos": None,
            "url_arquivo": f"/api/jobs/{job_id}/video",
            "eh_entrada": True,
        }
    itens = [
        {**item.para_dict(job_id=job_id), "eh_entrada": False}
        for item in listar_itens_biblioteca_midias_tela_do_work_transcribrothers(work)
    ]
    return {"ok": True, "entrada": entrada, "itens": itens}


@app.post("/api/jobs/{job_id}/biblioteca-midias-tela")
async def enviar_video_para_biblioteca_midias_tela_do_job_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    video: UploadFile = File(..., description="Vídeo de tela extra (B-roll) para o projeto"),
) -> dict[str, object]:
    """Upload de mídia de tela extra — não altera nem concatena o video_entrada."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    cfg = obter_cfg(request)
    nome_original = (video.filename or "midia_tela.mp4").strip() or "midia_tela.mp4"
    try:
        ext = extrair_extensao_video_sanitizada_para_upload_local(nome_original)
    except ErroExtensaoVideoUploadTranscribrothers as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    work = _diretorio_trabalho_job(data_dir, job_id)
    item, destino = alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers(
        work=work,
        nome_original=nome_original,
        extensao_com_ponto=ext,
    )
    try:
        bytes_gravados = await gravar_arquivo_upload_video_com_limite_bytes_transcribrothers(
            video,
            destino,
            int(cfg.max_video_bytes),
            job_id=job_id,
        )
    except Exception:
        try:
            if destino.is_file():
                destino.unlink()
        except OSError:
            pass
        raise
    confirmado = confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers(
        work=work,
        item=item,
        tamanho_bytes=bytes_gravados,
    )
    return {
        "ok": True,
        "item": {**confirmado.para_dict(job_id=job_id), "eh_entrada": False},
    }


@app.get("/api/jobs/{job_id}/biblioteca-midias-tela/arquivo/{id_midia}")
async def servir_arquivo_biblioteca_midias_tela_do_job_transcribrothers(
    job_id: str,
    id_midia: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    try:
        caminho = resolver_caminho_arquivo_biblioteca_midias_tela_por_id_transcribrothers(
            work, id_midia
        )
    except ErroBibliotecaMidiasTelaTranscribrothers as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    ext = caminho.suffix.lstrip(".") or "mp4"
    return FileResponse(
        path=str(caminho),
        media_type=media_type_para_video_por_extensao(ext),
        filename=caminho.name,
    )


@app.delete("/api/jobs/{job_id}/biblioteca-midias-tela/{id_midia}")
async def apagar_item_biblioteca_midias_tela_do_job_transcribrothers(
    job_id: str,
    id_midia: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    try:
        apagar_item_biblioteca_midias_tela_por_id_transcribrothers(work, id_midia)
    except ErroBibliotecaMidiasTelaTranscribrothers as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {"ok": True, "id": id_midia}


@app.get("/api/jobs/{job_id}/videos-narrados")
async def listar_versoes_video_narrado_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    versao_atual_id, versoes = listar_versoes_video_narrado_do_work_transcribrothers(work)
    return {
        "versao_atual_id": versao_atual_id,
        "versoes": [
            {
                **v.para_dict(),
                "url_thumbnail": (
                    f"/api/jobs/{job_id}/videos-narrados/{v.id}/arquivo/"
                    f"{NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS}"
                    if v.tem_thumbnail
                    else None
                ),
                "url_download_mp4": (
                    f"/api/jobs/{job_id}/videos-narrados/{v.id}/arquivo/"
                    f"{NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS}"
                ),
            }
            for v in versoes
        ],
    }


@app.get("/api/jobs/{job_id}/videos-narrados/{versao_id}/arquivo/{nome_arquivo}")
async def servir_arquivo_versao_video_narrado_do_job_transcribrothers(
    job_id: str,
    versao_id: str,
    nome_arquivo: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    try:
        caminho = resolver_arquivo_versao_video_narrado_transcribrothers(work, versao_id, nome_arquivo)
    except ErroVersaoVideoNarradoTranscribrothers as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    nome = Path(nome_arquivo).name
    media = "application/octet-stream"
    if nome.endswith(".mp4"):
        media = "video/mp4"
    elif nome.endswith(".vtt"):
        media = "text/vtt; charset=utf-8"
    elif nome.endswith(".wav"):
        media = "audio/wav"
    elif nome.endswith(".jpg") or nome.endswith(".jpeg"):
        media = "image/jpeg"
    elif nome.endswith(".json"):
        media = "application/json"
    return FileResponse(str(caminho), media_type=media, filename=nome)


@app.post("/api/jobs/{job_id}/videos-narrados/{versao_id}/tornar-atual")
async def tornar_versao_video_narrado_atual_do_job_transcribrothers(
    job_id: str,
    versao_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            steps_novo = tornar_versao_video_narrado_atual_transcribrothers(
                work=work,
                assets=assets,
                job_id=job_id,
                versao_id=versao_id,
                steps=dict(row.steps_json or {}),
            )
        except ErroVersaoVideoNarradoTranscribrothers as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        row.steps_json = steps_novo
        flag_modified(row, "steps_json")
        await session.commit()
        await session.refresh(row)
        return _job_para_resposta(row)


@app.delete("/api/jobs/{job_id}/videos-narrados/{versao_id}")
async def apagar_versao_video_narrado_do_job_transcribrothers(
    job_id: str,
    versao_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        work = _diretorio_trabalho_job(data_dir, job_id)
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            resultado = apagar_versao_video_narrado_transcribrothers(
                work=work,
                assets=assets,
                job_id=job_id,
                versao_id=versao_id,
                steps=dict(row.steps_json or {}),
            )
        except ErroVersaoVideoNarradoTranscribrothers as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if resultado.steps_alterados:
            row.steps_json = resultado.steps
            flag_modified(row, "steps_json")
            await session.commit()
            await session.refresh(row)
        job_resp = _job_para_resposta(row)
    versao_atual_id, versoes = listar_versoes_video_narrado_do_work_transcribrothers(work)
    return {
        "ok": True,
        "versao_atual_id": versao_atual_id,
        "versoes": [v.para_dict() for v in versoes],
        "job": job_resp.model_dump(mode="json"),
    }


@app.get("/api/jobs/{job_id}/video-com-narracao-tts-com-legendas-queimadas/status")
async def status_video_com_narracao_tts_com_legendas_queimadas_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> dict[str, object]:
    """Consulta se o MP4 com legendas queimadas está pronto, gerando ou pendente."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    return consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
        job_id=job_id,
        diretorio_trabalho_job=work,
        diretorio_assets=assets,
    )


@app.post("/api/jobs/{job_id}/gerar-video-com-narracao-tts-com-legendas-queimadas")
async def gerar_video_com_narracao_tts_com_legendas_queimadas_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
    forcar: bool = False,
) -> dict[str, object]:
    """
    Agenda a queima de legendas em background (não bloqueia).
    Vídeos em alta resolução (ex.: 3K 60 fps) podem levar alguns minutos na 1ª vez.
    """
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    async with session_factory() as session:
        prefs_encode, _ = await resolver_preferencias_encode_video_narrado_efetivas_transcribrothers(
            session
        )
    return agendar_geracao_video_narrado_com_legendas_queimadas_transcribrothers(
        job_id=job_id,
        diretorio_trabalho_job=work,
        diretorio_assets=assets,
        forcar_regenerar=forcar,
        preferencias_encode=prefs_encode,
    )


@app.get("/api/jobs/{job_id}/video-com-narracao-tts-com-legendas-queimadas")
async def baixar_video_com_narracao_tts_com_legendas_queimadas_do_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    """
    Serve o MP4 com legendas queimadas se o cache estiver pronto.
    Não gera no request — use POST .../gerar-video-com-narracao-tts-com-legendas-queimadas.
    """
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
    caminho_video = work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    caminho_vtt = assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    caminho = work / NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS
    if not video_narrado_com_legendas_queimadas_esta_atualizado_transcribrothers(
        caminho_video_mp4=caminho_video,
        caminho_vtt=caminho_vtt,
        caminho_saida=caminho,
    ):
        status = consultar_status_video_narrado_com_legendas_queimadas_transcribrothers(
            job_id=job_id,
            diretorio_trabalho_job=work,
            diretorio_assets=assets,
        )
        if status.get("status") == "gerando":
            raise HTTPException(
                status_code=409,
                detail="Ainda gerando o vídeo com legendas embutidas. Aguarde e tente de novo.",
            )
        raise HTTPException(
            status_code=404,
            detail=(
                "Vídeo com legendas embutidas ainda não está pronto. "
                "Use «Baixar → Vídeo com legendas embutidas» para gerar."
            ),
        )
    return FileResponse(
        str(caminho),
        media_type="video/mp4",
        filename=NOME_ARQUIVO_VIDEO_NARRADO_COM_LEGENDAS_QUEIMADAS_MP4_TRANSCRIBROTHERS,
    )


@app.post(
    "/api/jobs/{job_id}/pipeline-video-narrado-a-partir-documento",
    response_model=RespostaJobTranscribrothers,
)
async def pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers(
    job_id: str,
    body: CorpoPipelineVideoNarradoAPartirDocumentoTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Agenda: VTT alinhada + TTS em chunks + MP4 com narração (não altera o Markdown)."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        _garantir_job_permite_reiniciar_pipeline_video_narrado_transcribrothers(
            row,
            mensagem_se_bloqueado=(
                "Só é possível iniciar o vídeo narrado quando o job está concluído, falhou ou foi cancelado."
            ),
        )
        markdown_completo = (row.result_markdown or "").strip()
        markdown_escopo = (body.markdown_narracao or "").strip() or None
        markdown_para_validar = markdown_escopo or markdown_completo
        work = _diretorio_trabalho_job(data_dir, job_id)
        try:
            validar_pre_requisitos_pipeline_video_narrado_no_disco_transcribrothers(
                work=work,
                markdown=markdown_para_validar,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            modelo_tts = resolver_modelo_tts_para_narracao_documento_transcribrothers(
                cfg,
                body.litellm_model,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            modelo_chat_limpeza = resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers(
                cfg,
                body.litellm_model_chat,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            perfil_tts = normalizar_perfil_tts_narracao_transcribrothers(body.perfil_tts)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            paralelismo_tts_experimental = (
                normalizar_paralelismo_tts_cues_experimental_transcribrothers(
                    body.paralelismo_tts_experimental
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        temperatura_tts = normalizar_temperatura_tts_narracao_transcribrothers(
            body.temperatura_tts
        )
        ritmo_tts = normalizar_ritmo_tts_narracao_transcribrothers(body.ritmo_tts)
        diretriz_conteudo_legendas = normalizar_diretriz_conteudo_legendas_transcribrothers(
            body.diretriz_conteudo_legendas
        )

        steps = dict(row.steps_json or {})
        _limpar_marcadores_cancelamento_ao_reiniciar_pipeline_video_narrado_transcribrothers(
            job_id, steps
        )
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_AGENDADO
        steps["pipeline_origem_corrida"] = "video_narrado_completo"
        steps["pipeline_video_narrado_modelo_tts"] = modelo_tts
        steps["pipeline_video_narrado_modelo_chat_limpeza"] = modelo_chat_limpeza
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS] = perfil_tts
        steps[
            CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PARALELISMO_TTS_EXPERIMENTAL_TRANSCRIBROTHERS
        ] = paralelismo_tts_experimental
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS] = (
            temperatura_tts
        )
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS] = ritmo_tts
        steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS] = (
            diretriz_conteudo_legendas
        )
        if markdown_escopo:
            titulos = [
                t.strip()
                for t in (body.titulos_secoes_escopo or [])
                if isinstance(t, str) and t.strip()
            ]
            steps[CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS] = {
                "markdown": markdown_escopo,
                "modo": "secoes",
                "titulos": titulos[:40],
            }
        else:
            steps.pop(CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS, None)
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    agendar_pipeline_video_narrado_a_partir_documento_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        modelo_tts=modelo_tts,
        modelo_chat_limpeza=modelo_chat_limpeza,
        perfil_tts=perfil_tts,
        paralelismo_tts_experimental=paralelismo_tts_experimental,
        temperatura_tts=temperatura_tts,
        ritmo_tts=ritmo_tts,
        diretriz_conteudo_legendas=diretriz_conteudo_legendas,
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/atualizar-narracao-a-partir-legendas-vtt-editadas",
    response_model=RespostaJobTranscribrothers,
)
async def atualizar_narracao_a_partir_legendas_vtt_editadas_job_transcribrothers(
    job_id: str,
    body: CorpoAtualizarNarracaoAPartirLegendasVttEditadasTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Agenda regeneração parcial: TTS só nas cues alteradas no VTT + remux."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        _garantir_job_permite_reiniciar_pipeline_video_narrado_transcribrothers(
            row,
            mensagem_se_bloqueado=(
                "Só é possível atualizar a narração quando o job está concluído, falhou ou foi cancelado."
            ),
        )
        work = _diretorio_trabalho_job(data_dir, job_id)
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            validar_pre_requisitos_atualizar_narracao_a_partir_vtt_editadas_transcribrothers(
                work=work,
                assets=assets,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            modelo_tts = resolver_modelo_tts_para_narracao_documento_transcribrothers(
                cfg,
                body.litellm_model,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        steps = dict(row.steps_json or {})
        _limpar_marcadores_cancelamento_ao_reiniciar_pipeline_video_narrado_transcribrothers(
            job_id, steps
        )
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_ATUALIZANDO_LEGENDAS_EDITADAS
        steps["pipeline_video_narrado_modelo_tts"] = modelo_tts
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    agendar_atualizacao_narracao_a_partir_legendas_vtt_editadas_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        modelo_tts=modelo_tts,
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.post(
    "/api/jobs/{job_id}/gerar-video-com-edicoes-do-modal-narrado",
    response_model=RespostaJobTranscribrothers,
)
async def gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers(
    job_id: str,
    body: CorpoGerarVideoComEdicoesDoModalNarradoTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Agenda: grava VTT/janelas do modal, TTS parcial se preciso, remux na timeline VTT."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        _garantir_job_permite_reiniciar_pipeline_video_narrado_transcribrothers(
            row,
            mensagem_se_bloqueado=(
                "Só é possível gerar o vídeo quando o job está concluído, falhou ou foi cancelado."
            ),
        )
        work = _diretorio_trabalho_job(data_dir, job_id)
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        try:
            validar_pre_requisitos_atualizar_narracao_a_partir_vtt_editadas_transcribrothers(
                work=work,
                assets=assets,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        try:
            modelo_tts = resolver_modelo_tts_para_narracao_documento_transcribrothers(
                cfg,
                body.litellm_model,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not body.cues:
            raise HTTPException(status_code=400, detail="Informe ao menos uma cue de legenda.")

        cues_brutas = [c.model_dump() for c in body.cues]
        janelas_brutas = (
            [j.model_dump() for j in body.janelas] if body.janelas is not None else None
        )

        steps = dict(row.steps_json or {})
        _limpar_marcadores_cancelamento_ao_reiniciar_pipeline_video_narrado_transcribrothers(
            job_id, steps
        )
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_GERANDO_COM_EDICOES_MODAL
        steps["pipeline_origem_corrida"] = "edicoes_modal"
        steps.pop("limpeza_legendas_ia_antes_tts", None)
        steps["pipeline_video_narrado_modelo_tts"] = modelo_tts
        if body.temperatura_tts is not None:
            steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS] = (
                normalizar_temperatura_tts_narracao_transcribrothers(body.temperatura_tts)
            )
        if body.ritmo_tts is not None and str(body.ritmo_tts).strip():
            steps[CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS] = (
                normalizar_ritmo_tts_narracao_transcribrothers(body.ritmo_tts)
            )
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
        modelo_tts=modelo_tts,
        cues_brutas=cues_brutas,
        janelas_brutas=janelas_brutas,
    )

    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.get(
    "/api/jobs/{job_id}/janelas-video-cues-narracao",
    response_model=RespostaJanelasVideoCuesNarracaoJobTranscribrothers,
)
async def listar_janelas_video_cues_narracao_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJanelasVideoCuesNarracaoJobTranscribrothers:
    """Janelas de tela por cue (manifesto) + se existe WAV para ouvir o trecho."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        prefs_voz, _ = await resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(session)
    work = _diretorio_trabalho_job(data_dir, job_id)
    resumos = montar_resumo_janelas_video_e_wavs_do_job_transcribrothers(job_id=job_id, work=work)
    voz_padrao_job = (
        str(steps.get("pipeline_video_narrado_voz_tts") or "").strip()
        or prefs_voz.voz
        or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    )
    return RespostaJanelasVideoCuesNarracaoJobTranscribrothers(
        ok=True,
        quantidade_cues=len(resumos),
        voz_tts_padrao_job=voz_padrao_job,
        cues=[
            ResumoJanelaVideoCueApiRespostaTranscribrothers(
                indice=r.indice,
                texto=r.texto,
                inicio_video_segundos=r.inicio_video_segundos,
                fim_video_segundos=r.fim_video_segundos,
                tem_wav=r.tem_wav,
                url_wav=r.url_wav,
                sem_narracao=bool(getattr(r, "sem_narracao", False)),
                voz_tts=str(getattr(r, "voz_tts", "") or "").strip() or voz_padrao_job,
                texto_tts=str(getattr(r, "texto_tts", "") or "").strip(),
                id_fonte_video=str(getattr(r, "id_fonte_video", "") or "").strip(),
            )
            for r in resumos
        ],
    )


@app.put(
    "/api/jobs/{job_id}/janelas-video-cues-narracao",
    response_model=RespostaJanelasVideoCuesNarracaoJobTranscribrothers,
)
async def salvar_janelas_video_cues_narracao_job_transcribrothers(
    job_id: str,
    body: CorpoSalvarJanelasVideoCuesNarracaoJobTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJanelasVideoCuesNarracaoJobTranscribrothers:
    """Persiste tempos de janela de tela no manifesto (impede sobreposição)."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    video = None
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for p in sorted(work.glob(pattern)):
            if p.is_file():
                video = p
                break
        if video is not None:
            break
    duracao: float | None = None
    if video is not None:
        try:
            duracao = await obter_duracao_video_segundos_via_ffprobe(video)
        except Exception:
            duracao = None
    mapa_duracao_fontes: dict[str, float] | None = None
    if video is not None and duracao is not None and duracao > 0:
        from transcribrothers_backend.modulo_montar_mapa_duracao_segundos_por_id_fonte_video_cues_job_transcribrothers import (
            montar_mapa_duracao_segundos_por_id_fonte_video_das_cues_job_transcribrothers,
        )

        ids_fonte_body = [str(getattr(j, "id_fonte_video", "") or "") for j in body.janelas]
        mapa_duracao_fontes = (
            await montar_mapa_duracao_segundos_por_id_fonte_video_das_cues_job_transcribrothers(
                work=work,
                cues_ou_ids_fonte=ids_fonte_body,
                caminho_video_entrada=video,
                duracao_video_entrada_segundos=float(duracao),
            )
        )
    try:
        salvar_janelas_video_no_manifest_validando_sobreposicao_transcribrothers(
            work=work,
            janelas_brutas=[j.model_dump() for j in body.janelas],
            duracao_video_segundos=duracao,
            duracao_por_id_fonte_video=mapa_duracao_fontes,
        )
    except ErroValidacaoJanelasVideoCuesTranscribrothers as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    resumos = montar_resumo_janelas_video_e_wavs_do_job_transcribrothers(job_id=job_id, work=work)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        steps = dict(row.steps_json or {}) if row is not None else {}
        prefs_voz, _ = await resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(session)
    voz_padrao_job = (
        str(steps.get("pipeline_video_narrado_voz_tts") or "").strip()
        or prefs_voz.voz
        or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    )
    return RespostaJanelasVideoCuesNarracaoJobTranscribrothers(
        ok=True,
        quantidade_cues=len(resumos),
        voz_tts_padrao_job=voz_padrao_job,
        cues=[
            ResumoJanelaVideoCueApiRespostaTranscribrothers(
                indice=r.indice,
                texto=r.texto,
                inicio_video_segundos=r.inicio_video_segundos,
                fim_video_segundos=r.fim_video_segundos,
                tem_wav=r.tem_wav,
                url_wav=r.url_wav,
                sem_narracao=bool(getattr(r, "sem_narracao", False)),
                voz_tts=str(getattr(r, "voz_tts", "") or "").strip() or voz_padrao_job,
                texto_tts=str(getattr(r, "texto_tts", "") or "").strip(),
                id_fonte_video=str(getattr(r, "id_fonte_video", "") or "").strip(),
            )
            for r in resumos
        ],
    )


@app.post(
    "/api/jobs/{job_id}/remux-video-narrado-apos-edicao-janelas",
    response_model=RespostaJobTranscribrothers,
)
async def remux_video_narrado_apos_edicao_janelas_job_transcribrothers(
    job_id: str,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaJobTranscribrothers:
    """Agenda remux do MP4 com as janelas do manifesto (reutiliza WAVs; sem TTS)."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        _garantir_job_permite_reiniciar_pipeline_video_narrado_transcribrothers(
            row,
            mensagem_se_bloqueado=(
                "Só é possível aplicar tempos quando o job está concluído, falhou ou foi cancelado."
            ),
        )
        work = _diretorio_trabalho_job(data_dir, job_id)
        try:
            validar_pre_requisitos_remux_janelas_editadas_transcribrothers(work=work)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        steps = dict(row.steps_json or {})
        _limpar_marcadores_cancelamento_ao_reiniciar_pipeline_video_narrado_transcribrothers(
            job_id, steps
        )
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_REMUX_JANELAS_EDITADAS
        row.status = StatusJobTranscribrothers.generating_tutorial.value
        row.error_message = None
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()

    agendar_remux_video_narrado_apos_edicao_janelas_em_task_assincrona(
        job_id=job_id,
        session_factory=session_factory,
        configuracao=cfg,
    )
    async with session_factory() as session:
        atual = await session.get(JobPipelineTranscribrothers, job_id)
        assert atual is not None
        return _job_para_resposta(atual)


@app.get("/api/jobs/{job_id}/wavs-narracao-por-cue/{indice}")
async def servir_wav_narracao_por_cue_do_job_transcribrothers(
    job_id: str,
    indice: int,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    """Serve o WAV TTS de uma cue (para prévia na UI)."""
    if indice < 0 or indice > 50_000:
        raise HTTPException(status_code=400, detail="Índice de cue inválido.")
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    caminho = obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, indice)
    if caminho is None:
        raise HTTPException(status_code=404, detail="Áudio desta cue não encontrado.")
    return FileResponse(
        str(caminho),
        media_type="audio/wav",
        filename=caminho.name,
    )


@app.post("/api/preview-tts-amostra-voz-narracao")
async def preview_tts_amostra_voz_narracao_transcribrothers(
    body: CorpoPreviewTtsAmostraVozNarracaoTranscribrothers,
    request: Request,
    data_dir: DataDirDep,
) -> FileResponse:
    """Gera e devolve WAV de amostra da voz Gemini (frase fixa; não exige job)."""
    cfg = obter_cfg(request)
    try:
        resultado = await gerar_arquivo_preview_tts_amostra_voz_narracao_transcribrothers(
            data_dir=data_dir,
            voz=body.voz,
            configuracao=cfg,
            litellm_model=body.litellm_model,
            perfil_tts=body.perfil_tts,
            temperatura_tts=body.temperatura_tts,
            ritmo_tts=body.ritmo_tts,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return FileResponse(
        str(resultado.caminho_wav),
        media_type="audio/wav",
        filename=resultado.caminho_wav.name,
    )


@app.post("/api/jobs/{job_id}/preview-tts-cue-narracao")
async def preview_tts_cue_narracao_texto_atual_job_transcribrothers(
    job_id: str,
    body: CorpoPreviewTtsCueNarracaoTextoAtualTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> FileResponse:
    """Gera e devolve WAV de prévia do texto atual da cue (não altera a narração definitiva)."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        prefs_voz, _ = await resolver_preferencias_voz_tts_narracao_efetivas_transcribrothers(session)
        steps_preview = dict(row.steps_json or {})
    perfil_preview = steps_preview.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_PERFIL_TTS_TRANSCRIBROTHERS)
    temperatura_preview = (
        body.temperatura_tts
        if body.temperatura_tts is not None
        else steps_preview.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_TEMPERATURA_TTS_TRANSCRIBROTHERS)
    )
    ritmo_preview = (
        body.ritmo_tts
        if body.ritmo_tts is not None and str(body.ritmo_tts).strip()
        else steps_preview.get(CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_RITMO_TTS_TRANSCRIBROTHERS)
    )
    work = _diretorio_trabalho_job(data_dir, job_id)
    try:
        resultado = await gerar_arquivo_preview_tts_cue_narracao_job_transcribrothers(
            work=work,
            indice=body.indice,
            texto=body.texto,
            configuracao=cfg,
            litellm_model=body.litellm_model,
            voz=body.voz or prefs_voz.voz,
            perfil_tts=str(perfil_preview) if perfil_preview is not None else None,
            temperatura_tts=(
                float(temperatura_preview)
                if isinstance(temperatura_preview, (int, float))
                else None
            ),
            ritmo_tts=str(ritmo_preview) if ritmo_preview is not None else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return FileResponse(
        str(resultado.caminho_wav),
        media_type="audio/wav",
        filename=resultado.caminho_wav.name,
    )


@app.post(
    "/api/jobs/{job_id}/resolver-cue-tts-pendente-timeout-experimental",
    response_model=RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers,
)
async def resolver_cue_tts_pendente_timeout_experimental_api_transcribrothers(
    job_id: str,
    body: CorpoResolverCueTtsPendenteTimeoutExperimentalTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers:
    """
    Reenvia cue com timeout (perfil experimental_voz). Sem retry automático.
    Quando a lista zera, a montagem do MP4 continua sozinha.
    """
    cfg = obter_cfg(request)
    try:
        resultado = await resolver_cue_tts_pendente_timeout_experimental_job_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            indice=body.indice,
            texto=body.texto,
            voz=body.voz,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers(
        ok=bool(resultado.get("ok")),
        mensagem=str(resultado.get("mensagem") or ""),
        indice=int(resultado.get("indice") or body.indice),
        pendentes_restantes=int(resultado.get("pendentes_restantes") or 0),
        pipeline_continuada=bool(resultado.get("pipeline_continuada")),
        pipeline_fase=(
            str(resultado["pipeline_fase"])
            if resultado.get("pipeline_fase") is not None
            else None
        ),
    )


@app.post(
    "/api/jobs/{job_id}/descartar-cue-tts-pendente-timeout-experimental",
    response_model=RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers,
)
async def descartar_cue_tts_pendente_timeout_experimental_api_transcribrothers(
    job_id: str,
    body: CorpoDescartarCueTtsPendenteTimeoutExperimentalTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers:
    """
    Não narrar cue com timeout: silêncio no slot + remove da lista.
    Quando a lista zera, a montagem do MP4 continua sozinha.
    """
    cfg = obter_cfg(request)
    try:
        resultado = await descartar_cue_tts_pendente_timeout_experimental_job_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            indice=body.indice,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return RespostaResolverCueTtsPendenteTimeoutExperimentalTranscribrothers(
        ok=bool(resultado.get("ok")),
        mensagem=str(resultado.get("mensagem") or ""),
        indice=int(resultado.get("indice") or body.indice),
        pendentes_restantes=int(resultado.get("pendentes_restantes") or 0),
        pipeline_continuada=bool(resultado.get("pipeline_continuada")),
        pipeline_fase=(
            str(resultado["pipeline_fase"])
            if resultado.get("pipeline_fase") is not None
            else None
        ),
    )


@app.post(
    "/api/jobs/{job_id}/sugerir-reescrita-texto-cue-narracao",
    response_model=RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers,
)
async def sugerir_reescrita_texto_cue_narracao_api_transcribrothers(
    job_id: str,
    body: CorpoSugerirReescritaTextoCueNarracaoTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers:
    """Sugere reescrita da legenda via chat (modal editar); só aplica se o usuário aceitar."""
    cfg = obter_cfg(request)
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        steps = dict(row.steps_json or {})
        modelo_steps = str(steps.get("pipeline_video_narrado_modelo_chat_limpeza") or "").strip()
    try:
        resultado = await sugerir_reescrita_texto_cue_narracao_via_litellm_chat_transcribrothers(
            configuracao=cfg,
            texto=body.texto,
            indice=body.indice,
            litellm_model_chat=body.litellm_model_chat,
            modelo_chat_fallback_steps=modelo_steps,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers(
        ok=bool(resultado.get("ok")),
        mensagem=str(resultado.get("mensagem") or ""),
        indice=int(resultado.get("indice") or body.indice),
        sugestao=str(resultado.get("sugestao") or ""),
        modelo=(str(resultado["modelo"]) if resultado.get("modelo") is not None else None),
        texto_original=(
            str(resultado["texto_original"])
            if resultado.get("texto_original") is not None
            else None
        ),
    )


@app.post(
    "/api/jobs/{job_id}/sugerir-reescrita-cue-tts-pendente-timeout-experimental",
    response_model=RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers,
)
async def sugerir_reescrita_cue_tts_pendente_timeout_experimental_api_transcribrothers(
    job_id: str,
    body: CorpoSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers,
    request: Request,
    session_factory: SessionFactoryDep,
) -> RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers:
    """Sugere reescrita via chat; o texto da cue só muda se o usuário aceitar na UI."""
    cfg = obter_cfg(request)
    try:
        resultado = await sugerir_reescrita_texto_cue_tts_pendente_timeout_experimental_transcribrothers(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            indice=body.indice,
            texto=body.texto,
            litellm_model_chat=body.litellm_model_chat,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalTranscribrothers(
        ok=bool(resultado.get("ok")),
        mensagem=str(resultado.get("mensagem") or ""),
        indice=int(resultado.get("indice") or body.indice),
        sugestao=str(resultado.get("sugestao") or ""),
        modelo=(str(resultado["modelo"]) if resultado.get("modelo") is not None else None),
        texto_original=(
            str(resultado["texto_original"])
            if resultado.get("texto_original") is not None
            else None
        ),
    )


@app.put(
    "/api/jobs/{job_id}/legendas-documento-alinhadas",
    response_model=RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers,
)
async def salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers(
    job_id: str,
    body: CorpoSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers:
    """Grava o VTT com o texto das cues editado na UI (tempos e áudio/vídeo inalterados)."""
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
        assets = _diretorio_assets_png_exportados_markdown_do_job(data_dir, job_id)
        cues_brutas = [c.model_dump() for c in body.cues]
        try:
            resultado = salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers(
                job_id=job_id,
                diretorio_assets=assets,
                steps_json=dict(row.steps_json or {}),
                cues_brutas=cues_brutas,
            )
        except ErroValidacaoLegendasDocumentoAlinhadasEditadasTranscribrothers as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Não foi possível gravar o arquivo VTT no disco: {e}",
            ) from e
        row.steps_json = resultado.steps_json_atualizado
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()
    return RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers(
        ok=True,
        nome_arquivo=resultado.nome_arquivo,
        url_asset=resultado.url_asset,
        quantidade_cues=resultado.quantidade_cues,
    )


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
    nome_lower = nome_arquivo.lower()
    if nome_lower.endswith(".wav"):
        media = "audio/wav"
    elif nome_lower.endswith(".vtt"):
        media = "text/vtt"
    elif nome_lower.endswith(".png"):
        media = "image/png"
    elif nome_lower.endswith(".jpg") or nome_lower.endswith(".jpeg"):
        media = "image/jpeg"
    else:
        media = "application/octet-stream"
    return FileResponse(str(path), media_type=media)


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
