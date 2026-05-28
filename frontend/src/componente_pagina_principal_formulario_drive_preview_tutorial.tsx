import type * as React from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  adicionarModeloLitellmExtraAoArmazenamentoLocalNavegadorTranscribrothers,
  carregarListaModelosLitellmExtrasSalvosNoNavegadorTranscribrothers,
  mesclarModelosServidorComExtrasNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_modelos_litellm_extras_navegador_transcribrothers.ts";
import { gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers } from "./modulo_util_gerar_markdown_tutorial_com_imagens_png_embutidas_data_uri_base64_download_transcribrothers.ts";
import { abrirUrlExternaNovaAbaNavegadorTranscribrothers } from "./modulo_util_abrir_url_externa_nova_aba_navegador_transcribrothers.ts";
import { abrirTutorialMarkdownRenderizadoEmNovaAbaNavegadorTranscribrothers } from "./modulo_util_abrir_tutorial_markdown_renderizado_em_nova_aba_navegador_transcribrothers.ts";
import { baixarArquivoPdfTutorialMarkdownComImagensEmbutidasTranscribrothers } from "./modulo_util_gerar_arquivo_pdf_tutorial_markdown_com_imagens_embutidas_download_transcribrothers.ts";
import {
  extrairTituloH1MarkdownTutorialTranscribrothers,
  obterNomeBaseArquivoDownloadTutorialComTituloH1MarkdownOuJobIdTranscribrothers,
} from "./modulo_util_extrair_titulo_h1_markdown_e_sanitizar_nome_arquivo_download_tutorial_transcribrothers.ts";
import { criarIssueGitlabPortalDefensoriaGatewayApiTranscribrothers } from "./modulo_api_criar_issue_gitlab_portal_defensoria_gateway_transcribrothers.ts";
import { comentarIssueGitlabDocumentoMarkdownApiTranscribrothers } from "./modulo_api_comentar_issue_gitlab_documento_markdown_transcribrothers.ts";
import { anexarDescricaoIssueGitlabDocumentoMarkdownApiTranscribrothers } from "./modulo_api_anexar_descricao_issue_gitlab_documento_markdown_transcribrothers.ts";
import { criarPaginaWikiGitlabDocumentacaoApiTranscribrothers } from "./modulo_api_criar_pagina_wiki_gitlab_documentacao_transcribrothers.ts";
import { ComponenteModalConfirmarCriarIssueGitlabDocumentoMarkdownTranscribrothers } from "./componente_modal_confirmar_criar_issue_gitlab_documento_markdown_transcribrothers.tsx";
import { ComponenteModalConfirmarComentarIssueGitlabDocumentoMarkdownTranscribrothers } from "./componente_modal_confirmar_comentar_issue_gitlab_documento_markdown_transcribrothers.tsx";
import { ComponenteModalConfirmarAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers } from "./componente_modal_confirmar_anexar_descricao_issue_gitlab_documento_markdown_transcribrothers.tsx";
import { ComponenteModalConfirmarCriarPaginaWikiGitlabDocumentoMarkdownTranscribrothers } from "./componente_modal_confirmar_criar_pagina_wiki_gitlab_documento_markdown_transcribrothers.tsx";
import { ComponenteMenuSplitExportarEDownloadMarkdownTutorialToolbarTranscribrothers } from "./componente_menu_split_exportar_e_download_markdown_tutorial_toolbar_transcribrothers.tsx";
import {
  extrairRegistrosTempoInferenciaTranscricaoJanelasDoStepsJsonTranscribrothers,
  formatarSegundosComoMmSsTranscribrothers,
  obterDescricaoLegivelProgressoJobPipelinePortuguesTranscribrothers,
  obterLinhaDetalheSubetapaProgressoJobPipelinePortuguesTranscribrothers,
} from "./modulo_util_rotulos_fase_pipeline_status_portugues_ui_transcribrothers.ts";
import {
  montarTextoHintExibicaoPainelPassoPipelineModalStatusTranscribrothers,
  obterContextoPipelineHorizontalModalStatusJobTranscribrothers,
} from "./modulo_util_obter_passos_pipeline_horizontal_hint_modal_status_job_transcribrothers.ts";
import {
  extrairTopicosPlanoRevisaoProfundaParaVistaAmigavelDeStepsJsonTranscribrothers,
} from "./modulo_util_extrair_plano_revisao_profunda_json_para_vista_amigavel_modal_status_transcribrothers.ts";
import {
  formatarDataHoraLogDecisoesIaParaExibicaoTranscribrothers,
  montarEntradasLogDecisoesIaParaModalStatusJobTranscribrothers,
  rotuloEtapaLogDecisoesIaEmPtBrTranscribrothers,
} from "./modulo_util_montar_entradas_log_decisoes_ia_modal_status_job_transcribrothers.ts";
import { formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers } from "./modulo_util_parse_instante_iso_api_utc_para_date_e_formatar_data_hora_pt_br_transcribrothers.ts";
import { listarCaminhosAssetsPngOrdemPrimeiraOcorrenciaMarkdownTutorialTranscribrothers } from "./modulo_util_listar_caminhos_assets_png_ordem_markdown_para_referencias_fab_regeneracao_transcribrothers.ts";
import { montarTextoPlanoTranscricaoOriginalAPartirDeSnapshotJobTutorialTranscribrothers } from "./modulo_util_montar_texto_plano_transcricao_original_a_partir_de_snapshot_job_tutorial_transcribrothers.ts";
import {
  carregarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownDoNavegadorTranscribrothers,
  gravarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_rascunho_instrucao_prefixo_litellm_tutorial_markdown_navegador_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import { TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_DOCUMENTO_PROJETO_EM_BRANCO_TRANSCRIBROTHERS } from "./constante_texto_instrucao_template_fab_regeneracao_documento_projeto_em_branco_transcribrothers.ts";
import { TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_TUTORIAL_SEM_REFERENCIAS_VIDEO_DOCUMENTO_AUTONOMO_TRANSCRIBROTHERS } from "./constante_texto_instrucao_template_fab_regeneracao_tutorial_sem_referencias_video_documento_autonomo_transcribrothers.ts";
import {
  aplicarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers,
  descartarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers,
  extrairPreviewRegeneracaoSecaoMarkdownDeStepsJsonTranscribrothers,
  listarSecoesNivel2TutorialMarkdownJobApiTranscribrothers,
  pedirRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers,
  type ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers,
} from "./modulo_api_edicao_por_secao_markdown_tutorial_transcribrothers.ts";
import {
  aplicarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers,
  descartarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers,
  extrairPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeStepsJsonTranscribrothers,
  recuperarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeHistoricoJobApiTranscribrothers,
} from "./modulo_api_preview_regeneracao_tutorial_markdown_documento_inteiro_transcribrothers.ts";
import { ComponenteComparacaoMarkdownAntesDepoisVisualizacaoDiffELadoALadoTranscribrothers } from "./componente_comparacao_markdown_antes_depois_visualizacao_diff_e_lado_a_lado_transcribrothers.tsx";
import { ComponenteModalEditorAnotacaoImagemTutorialFabricJsDuasVersoesTranscribrothers } from "./componente_modal_editor_anotacao_imagem_tutorial_fabric_js_duas_versoes_transcribrothers.tsx";
import { ComponenteModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers } from "./componente_modal_galeria_assets_imagens_transcricao_tutorial_transcribrothers.tsx";
import { ComponenteImagemMarkdownTutorialClicavelAbrirModalAnotacaoTranscribrothers } from "./componente_imagem_markdown_tutorial_clicavel_abrir_modal_anotacao_transcribrothers.tsx";
import { ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers } from "./componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.tsx";
import { removerReferenciaImagemAssetDoMarkdownTutorialTranscribrothers } from "./modulo_util_remover_referencia_imagem_asset_markdown_tutorial_transcribrothers.ts";
import { resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers } from "./modulo_util_resolver_nome_arquivo_png_original_a_partir_referencia_assets_transcribrothers.ts";
import { ComponenteParagrafoMarkdownReactDesembrulharQuandoFilhoUnicoEImagemTranscribrothers } from "./componente_paragrafo_markdown_react_desembrulhar_quando_filho_unico_e_imagem_transcribrothers.tsx";
import { mesclarComponentsReactMarkdownComAncorasLinhaFonteDocumentoTranscribrothers } from "./modulo_util_mesclar_components_react_markdown_com_data_linha_inicio_ast_transcribrothers.tsx";
import { listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers } from "./modulo_util_bloco_ancora_linha_markdown_sincronizacao_preview_editor_transcribrothers.ts";
import {
  definirVersaoExibicaoScreenshotTutorialJobApiTranscribrothers,
  extrairMapaAnotacoesImagensTutorialDoStepsJsonTranscribrothers,
  removerAnotacaoScreenshotTutorialJobApiTranscribrothers,
  sincronizarMarkdownComVersaoAnotadaScreenshotJobApiTranscribrothers,
} from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";
import { resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers } from "./modulo_util_resolver_nome_asset_png_para_exibicao_com_metadados_anotacao_tutorial_transcribrothers.ts";
import {
  capturarFrameManualVideoTutorialJobApiTranscribrothers,
  copiarTextoParaAreaTransferenciaNavegadorTranscribrothers,
  inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers,
} from "./modulo_api_captura_frame_manual_video_tutorial_inserir_markdown_transcribrothers.ts";
import { colarImagemClipboardMarkdownTutorialJobApiTranscribrothers } from "./modulo_api_colar_imagem_clipboard_markdown_tutorial_assets_job_transcribrothers.ts";
import {
  elementoAtivoEstaEmCampoDigitavelParaColarTextoTranscribrothers,
  extrairArquivoImagemDaApiClipboardNavegadorTranscribrothers,
  extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers,
} from "./modulo_util_imagem_insercao_editor_markdown_arrastar_soltar_e_area_transferencia_transcribrothers.ts";
import {
  type InsercaoMarkdownImagemAssetPendenteTranscribrothers,
  type PontoInsercaoImagemMarkdownPreviewTutorialTranscribrothers,
  alvoPreviewIgnoraCliqueInsercaoImagemMarkdownTranscribrothers,
  inserirSnippetMarkdownNaLinhaDocumentoTranscribrothers,
  listarSecoesH2MarkdownTutorialParaPreviewTranscribrothers,
  montarSnippetMarkdownImagemAssetTutorialTranscribrothers,
  obterNumeroLinhaInsercaoPorTopoMarcadorNoPreviewTutorialTranscribrothers,
  obterPontoInsercaoImagemMarkdownSobPonteiroNoPreviewTutorialTranscribrothers,
} from "./modulo_util_modo_inserir_snippet_imagem_markdown_tutorial_transcribrothers.ts";
import {
  ModalStepperIniciarTranscricaoEscolherVideoEDestinoTranscribrothers,
  type DestinoAposTranscricaoTranscribrothers,
  type ImportacaoRecbrothersModalStepperTranscribrothers,
} from "./componente_modal_stepper_iniciar_transcricao_escolher_video_e_destino_transcribrothers.tsx";
import {
  lerParametrosImportacaoRecbrothersDaUrl,
  limparParametrosImportacaoRecbrothersDaUrlBarraNavegador,
} from "./modulo_util_deep_link_importacao_recbrothers_transcribrothers.ts";
import {
  normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers,
  obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers,
} from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import { montarSubtituloVersaoEDataFrameDocumentoTutorialTranscribrothers } from "./modulo_util_subtitulo_versao_e_data_frame_documento_tutorial_transcribrothers.ts";
import { obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers } from "./modulo_util_rotulo_numero_versao_historico_tutorial_markdown_por_projeto_transcribrothers.ts";
import { criarProjetoEmBrancoJobApiTranscribrothers } from "./modulo_api_criar_projeto_em_branco_job_transcribrothers.ts";
import {
  type AnexoContextoFabUiTranscribrothers,
  extrairTextoDocumentoAnexoContextoFabProjetoEmBrancoApiTranscribrothers,
  montarPayloadContextoFabParaRegeneracaoApiTranscribrothers,
  uploadImagemAnexoContextoFabProjetoEmBrancoApiTranscribrothers,
} from "./modulo_api_anexos_contexto_fab_projeto_em_branco_transcribrothers.ts";
import {
  classificarArquivoAnexoContextoFabTranscribrothers,
  lerArquivoMarkdownOuTextoComoUtf8Transcribrothers,
  rotuloExibicaoAnexoTextoContextoFabUiTranscribrothers,
  truncarTextoAnexoContextoFabSeNecessarioTranscribrothers,
} from "./modulo_util_anexo_texto_contexto_fab_projeto_em_branco_transcribrothers.ts";
import { jobEhProjetoEmBrancoTranscribrothers } from "./modulo_util_job_eh_projeto_em_branco_transcribrothers.ts";
import { jobEhReproducaoBugTranscribrothers } from "./modulo_util_job_eh_reproducao_bug_transcribrothers.ts";
import { jobEhNotasPropostaFuncionalidadeTranscribrothers } from "./modulo_util_job_eh_notas_proposta_funcionalidade_transcribrothers.ts";
import { deveAbrirModalProgressoAoCarregarProjetoTranscribrothers } from "./modulo_util_job_esta_em_regeneracao_markdown_apenas_transcribrothers.ts";
import { regenerarMarkdownReproducaoBugJobApiTranscribrothers } from "./modulo_api_regenerar_markdown_reproducao_bug_job_transcribrothers.ts";
import { regenerarMarkdownNotasPropostaJobApiTranscribrothers } from "./modulo_api_regenerar_markdown_notas_proposta_job_transcribrothers.ts";
import { TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS } from "./constante_texto_instrucao_template_fab_regeneracao_reproducao_bug_sem_video_transcribrothers.ts";
import { TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS } from "./constante_texto_instrucao_template_fab_regeneracao_notas_proposta_sem_video_transcribrothers.ts";
import { ComponenteModalEdicaoMarkdownTutorialDuasColunasPreviewAoVivoTranscribrothers } from "./componente_modal_edicao_markdown_tutorial_duas_colunas_preview_ao_vivo_transcribrothers.tsx";
import { ComponenteModalColarTextoAnexoContextoFabProjetoEmBrancoTranscribrothers } from "./componente_modal_colar_texto_anexo_contexto_fab_projeto_em_branco_transcribrothers.tsx";
import { ComponenteModalEscolherVersaoHistoricoTutorialMarkdownEstiloListaProjetosTranscribrothers } from "./componente_modal_escolher_versao_historico_tutorial_markdown_estilo_lista_projetos_transcribrothers.tsx";
import { ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers } from "./componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx";
import { lerDuracaoVideoSegundosStepsJsonJobTranscribrothers } from "./modulo_util_ler_duracao_video_segundos_steps_json_job_transcribrothers.ts";
import "./componente_pagina_principal_formulario_drive_preview_tutorial.css";
import "./estilos_css_modal_escolher_versao_historico_tutorial_markdown_transcribrothers.css";

type JobStatus = {
  id: string;
  status: string;
  source_kind?: string;
  drive_url: string;
  file_id: string;
  error_message: string | null;
  result_markdown: string | null;
  steps_json: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
};

type FormatoAudioInlineMultimodalTranscribrothers = "wav" | "mp3" | "opus" | "aac";

const PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS = {
  janelaSegundos: 30,
  janelasParalelasMaxima: 5,
  formatoAudioInline: "aac" as FormatoAudioInlineMultimodalTranscribrothers,
  audioBitrateKbps: 32,
  audioMono: true,
};

function normalizarFormatoAudioInlineMultimodalDaApiTranscribrothers(
  raw: unknown,
): FormatoAudioInlineMultimodalTranscribrothers {
  const s = String(raw ?? "wav").toLowerCase();
  if (s === "mp3" || s === "opus" || s === "aac" || s === "wav") return s;
  return "wav";
}

type ConfigPublicaTranscribrothers = {
  litellm_models: string[];
  litellm_model_default: string;
  litellm_usa_endpoint_customizado: boolean;
  litellm_http_verify_ssl: boolean;
  litellm_ssl_ca_bundle_configurado: boolean;
  transcricao_backend: string;
  transcricao_modelo_multimodal_padrao?: string | null;
  transcricao_multimodal_janela_segundos: number;
  transcricao_multimodal_janelas_paralelas_maxima: number;
  transcricao_multimodal_formato_audio_inline: FormatoAudioInlineMultimodalTranscribrothers;
  transcricao_multimodal_audio_bitrate_kbps: number;
  transcricao_multimodal_audio_mono: boolean;
  transcricao_multimodal_overrides_runtime_sqlite_ativos: boolean;
  tutorial_margem_minima_segundos_entre_links_temporais_captura: number;
  tutorial_planejamento_instantes_captura_frames_litellm_habilitado: boolean;
  tutorial_max_frames_total: number;
  tutorial_frame_max_width_px: number;
  verificacao_sustentacao_tutorial_habilitada_efetiva: boolean;
  verificacao_sustentacao_tutorial_habilitada_padrao_env: boolean;
  verificacao_sustentacao_tutorial_preferencia_sqlite_definida: boolean;
  verificacao_redundancia_secao_markdown_habilitada_efetiva: boolean;
  verificacao_redundancia_secao_markdown_habilitada_padrao_env: boolean;
  verificacao_redundancia_secao_markdown_preferencia_sqlite_definida: boolean;
  verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva: boolean;
  verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app: boolean;
  verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva: boolean;
  verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app: boolean;
  verificacao_redundancia_secao_correcao_automatica_preferencia_sqlite_definida: boolean;
  gitlab_criar_issue_habilitado: boolean;
  gitlab_create_issue_project_path: string;
  gitlab_criar_wiki_habilitado: boolean;
  gitlab_wiki_project_path: string;
  gitlab_wiki_slug_prefixo_pasta: string;
};

/** Resposta de GET …/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial (somente leitura). */
type RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialApiTranscribrothers = {
  pipeline_identificador: string;
  system_verificacao_sustentacao_tutorial_markdown_vs_transcricao: string;
  system_verificacao_redundancia_secao_markdown_entre_secoes: string;
  system_revisao_profunda_analista_plano_tutorial: string;
  system_revisao_profunda_worker_item_plano_tutorial: string;
  system_revisao_profunda_resumo_plano_para_editor_final: string;
  instrucao_editor_final_revisao_profunda_consolidacao_markdown: string;
};

function normalizarRespostaConfigPublicaTranscribrothersDaApi(
  raw: Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>,
): ConfigPublicaTranscribrothers {
  return {
    litellm_models: raw.litellm_models ?? [],
    litellm_model_default: String(raw.litellm_model_default ?? ""),
    litellm_usa_endpoint_customizado: Boolean(raw.litellm_usa_endpoint_customizado),
    litellm_http_verify_ssl: Boolean(raw.litellm_http_verify_ssl),
    litellm_ssl_ca_bundle_configurado: Boolean(raw.litellm_ssl_ca_bundle_configurado),
    transcricao_backend: String(raw.transcricao_backend ?? ""),
    transcricao_modelo_multimodal_padrao:
      raw.transcricao_modelo_multimodal_padrao === undefined ||
      raw.transcricao_modelo_multimodal_padrao === null
        ? null
        : String(raw.transcricao_modelo_multimodal_padrao),
    transcricao_multimodal_janela_segundos: Number(
      raw.transcricao_multimodal_janela_segundos ?? PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.janelaSegundos,
    ),
    transcricao_multimodal_janelas_paralelas_maxima: Number(
      raw.transcricao_multimodal_janelas_paralelas_maxima ??
        PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.janelasParalelasMaxima,
    ),
    transcricao_multimodal_formato_audio_inline: normalizarFormatoAudioInlineMultimodalDaApiTranscribrothers(
      raw.transcricao_multimodal_formato_audio_inline ??
        PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.formatoAudioInline,
    ),
    transcricao_multimodal_audio_bitrate_kbps: Number(
      raw.transcricao_multimodal_audio_bitrate_kbps ??
        raw.transcricao_multimodal_mp3_bitrate_kbps ??
        PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.audioBitrateKbps,
    ),
    transcricao_multimodal_audio_mono:
      typeof raw.transcricao_multimodal_audio_mono === "boolean"
        ? raw.transcricao_multimodal_audio_mono
        : PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.audioMono,
    transcricao_multimodal_overrides_runtime_sqlite_ativos: Boolean(
      raw.transcricao_multimodal_overrides_runtime_sqlite_ativos,
    ),
    tutorial_margem_minima_segundos_entre_links_temporais_captura: Number(
      raw.tutorial_margem_minima_segundos_entre_links_temporais_captura ?? 2,
    ),
    tutorial_planejamento_instantes_captura_frames_litellm_habilitado:
      typeof raw.tutorial_planejamento_instantes_captura_frames_litellm_habilitado === "boolean"
        ? raw.tutorial_planejamento_instantes_captura_frames_litellm_habilitado
        : true,
    tutorial_max_frames_total: Number(raw.tutorial_max_frames_total ?? 0),
    tutorial_frame_max_width_px: Number(raw.tutorial_frame_max_width_px ?? 1280),
    verificacao_sustentacao_tutorial_habilitada_efetiva:
      typeof raw.verificacao_sustentacao_tutorial_habilitada_efetiva === "boolean"
        ? raw.verificacao_sustentacao_tutorial_habilitada_efetiva
        : true,
    verificacao_sustentacao_tutorial_habilitada_padrao_env:
      typeof raw.verificacao_sustentacao_tutorial_habilitada_padrao_env === "boolean"
        ? raw.verificacao_sustentacao_tutorial_habilitada_padrao_env
        : true,
    verificacao_sustentacao_tutorial_preferencia_sqlite_definida: Boolean(
      raw.verificacao_sustentacao_tutorial_preferencia_sqlite_definida,
    ),
    verificacao_redundancia_secao_markdown_habilitada_efetiva:
      typeof raw.verificacao_redundancia_secao_markdown_habilitada_efetiva === "boolean"
        ? raw.verificacao_redundancia_secao_markdown_habilitada_efetiva
        : true,
    verificacao_redundancia_secao_markdown_habilitada_padrao_env:
      typeof raw.verificacao_redundancia_secao_markdown_habilitada_padrao_env === "boolean"
        ? raw.verificacao_redundancia_secao_markdown_habilitada_padrao_env
        : true,
    verificacao_redundancia_secao_markdown_preferencia_sqlite_definida: Boolean(
      raw.verificacao_redundancia_secao_markdown_preferencia_sqlite_definida,
    ),
    verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva:
      typeof raw.verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva === "boolean"
        ? raw.verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva
        : true,
    verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app:
      typeof raw.verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app === "boolean"
        ? raw.verificacao_redundancia_secao_correcao_automatica_habilitada_padrao_app
        : true,
    verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva:
      typeof raw.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva ===
      "boolean"
        ? raw.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva
        : false,
    verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app:
      typeof raw.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app ===
      "boolean"
        ? raw.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_padrao_app
        : false,
    verificacao_redundancia_secao_correcao_automatica_preferencia_sqlite_definida: Boolean(
      raw.verificacao_redundancia_secao_correcao_automatica_preferencia_sqlite_definida,
    ),
    gitlab_criar_issue_habilitado: Boolean(raw.gitlab_criar_issue_habilitado),
    gitlab_create_issue_project_path: String(
      raw.gitlab_create_issue_project_path ?? "portal-da-defensoria/portal-defensoria-gateway",
    ),
    gitlab_criar_wiki_habilitado: Boolean(raw.gitlab_criar_wiki_habilitado),
    gitlab_wiki_project_path: String(
      raw.gitlab_wiki_project_path ?? "portal-da-defensoria/documentacao",
    ),
    gitlab_wiki_slug_prefixo_pasta: String(raw.gitlab_wiki_slug_prefixo_pasta ?? "workshop"),
  };
}

function obterTituloSugeridoIssueGitlabDeMarkdownTutorialTranscribrothers(
  markdown: string | null | undefined,
  jobId: string,
): string {
  const h1 = extrairTituloH1MarkdownTutorialTranscribrothers(markdown, 254);
  if (h1) return h1;
  const curto = jobId.length > 8 ? `${jobId.slice(0, 8)}…` : jobId;
  return `Documento Transcribrothers (${curto})`;
}

async function criarJobUploadArquivoLocal(
  video: File | null,
  litellmModel: string,
  tutorialLitellmInstrucaoPrefixoOpcional: string | null,
  destinoAposTranscricao: DestinoAposTranscricaoTranscribrothers,
  stagingIdRecbrothers?: string | null,
  cliquesJsonOpcional?: File | null,
): Promise<JobStatus> {
  const fd = new FormData();
  const stagingId = (stagingIdRecbrothers || "").trim();
  if (stagingId) {
    fd.append("staging_id", stagingId);
  } else if (video) {
    fd.append("video", video, video.name);
  } else {
    throw new Error("Informe o vídeo ou o identificador de importação RecBrothers.");
  }
  if (cliquesJsonOpcional) {
    fd.append("cliques_json", cliquesJsonOpcional, cliquesJsonOpcional.name);
  }
  fd.append("destino_apos_transcricao", destinoAposTranscricao);
  if (litellmModel.trim()) {
    fd.append("litellm_model", litellmModel.trim());
  }
  const t = (tutorialLitellmInstrucaoPrefixoOpcional ?? "").trim();
  if (t) {
    fd.append("tutorial_litellm_instrucao_prefixo", t);
  }
  const r = await fetch("/api/jobs/upload", {
    method: "POST",
    body: fd,
  });
  if (!r.ok) {
    const texto = await r.text();
    throw new Error(texto || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

async function buscarJob(jobId: string): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}`);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

async function solicitarCancelamentoJobPipelineTranscribrothers(jobId: string): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/cancel`, { method: "POST" });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

async function repetirJobPipelineAposFalhaOuCancelamentoTranscribrothers(
  jobId: string,
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/retry`, { method: "POST" });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

async function regenerarSomenteTutorialMarkdownTranscribrothers(
  jobId: string,
  opcoes: {
    instrucoesRevisaoHumana?: string;
    litellmModel?: string;
    revisaoProfundaMultifase?: boolean;
    caminhosAssetsPngContextoFab?: string[];
    textosContextoFab?: string[];
  },
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/regenerate-tutorial`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      instrucoes_revisao_humana: opcoes.instrucoesRevisaoHumana?.trim() || null,
      litellm_model: opcoes.litellmModel?.trim() || null,
      revisao_profunda_multifase: Boolean(opcoes.revisaoProfundaMultifase),
      caminhos_assets_png_contexto_fab: opcoes.caminhosAssetsPngContextoFab ?? null,
      textos_contexto_fab: opcoes.textosContextoFab ?? null,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

async function patchResultMarkdownJobTranscribrothers(jobId: string, markdown: string): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/result-markdown`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ result_markdown: markdown }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

type ResumoVersaoHistoricoTutorialMarkdownApiTranscribrothers = {
  id: number;
  criado_em: string | null;
  origem: string;
  tamanho_caracteres: number;
  preview_linha: string;
};

function obterRotuloPortuguesOrigemHistoricoVersaoTutorialMarkdownTranscribrothers(origem: string): string {
  const mapa: Record<string, string> = {
    pipeline_tutorial_inicial: "Pipeline inicial",
    regeneracao_tutorial_fab: "Regeneração",
    regeneracao_revisao_profunda: "Revisão profunda",
    regeneracao_secao_markdown: "Edição por seção (IA)",
    edicao_manual: "Edição manual",
    restauracao_versao_historico: "Restauração (histórico)",
    projeto_em_branco: "Projeto em branco",
    desconhecido: "Desconhecido",
  };
  return mapa[origem] ?? origem;
}

async function listarHistoricoVersoesTutorialMarkdownJobApiTranscribrothers(
  jobId: string,
): Promise<ResumoVersaoHistoricoTutorialMarkdownApiTranscribrothers[]> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/tutorial-markdown/historico-versoes`,
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as ResumoVersaoHistoricoTutorialMarkdownApiTranscribrothers[];
}

async function obterConteudoHistoricoVersaoTutorialMarkdownJobApiTranscribrothers(
  jobId: string,
  historicoId: number,
): Promise<{ markdown: string; origem: string; criado_em: string }> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/tutorial-markdown/historico-versoes/${encodeURIComponent(String(historicoId))}`,
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as { markdown: string; origem: string; criado_em: string };
}

async function restaurarHistoricoVersaoTutorialMarkdownJobApiTranscribrothers(
  jobId: string,
  historicoId: number,
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/tutorial-markdown/historico-versoes/${encodeURIComponent(String(historicoId))}/restaurar`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

/** Texto do tooltip (i) ao lado de «Regenerar tutorial» no painel do FAB. */
const TEXTO_TOOLTIP_INFO_PIXELS_REGENERACAO_TUTORIAL_FAB_TRANSCRIBROTHERS =
  "O servidor envia pixels só para imagens que entram no pedido: as que já estão no tutorial com ![](assets/…png) ou as que você citar nas instruções (Figura 1, imagem 2, ou o caminho assets/…png). Sem isso, regeneração é só texto. Modelo: configurações (engrenagem).";

type ResumoJobListaApiTranscribrothers = {
  id: string;
  status: string;
  source_kind: string;
  drive_url: string;
  file_id: string;
  tem_resultado_markdown: boolean;
  titulo_tutorial_markdown_h1: string | null;
  created_at: string | null;
  updated_at: string | null;
};

type InstrucoesPadraoTutorialLitellmApiTranscribrothers = {
  instrucao_sem_imagens: string;
  instrucao_com_imagens: string;
  instrucao_sem_imagens_documento_autonomo_sem_video: string;
  instrucao_com_imagens_documento_autonomo_sem_video: string;
};

async function listarJobsRecentesApiTranscribrothers(limit = 80): Promise<ResumoJobListaApiTranscribrothers[]> {
  const r = await fetch(`/api/jobs?limit=${encodeURIComponent(String(limit))}`);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as ResumoJobListaApiTranscribrothers[];
}

function IconeSvgHeaderToolbarTranscribrothers({ children }: { children: React.ReactNode }) {
  return (
    <svg className="tb-icone-header-toolbar" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
      {children}
    </svg>
  );
}

function IconeEngrenagemConfiguracaoTranscribrothers() {
  return (
    <svg className="tb-icone-header-toolbar" viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
      <path
        fill="currentColor"
        d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"
      />
    </svg>
  );
}

function IconeIniciarTranscricaoHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <polygon points="8,5 19,12 8,19" fill="currentColor" stroke="none" />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeVideoHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeGerarTutorialHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13 10V3L4 14h7v7l9-11h-7z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeZipHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeStatusHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeProjetoEmBrancoHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        d="M6 2h8l4 4v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path d="M14 2v4h4" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M8 12h8M8 16h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeJobsHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 6h16M4 10h16M4 14h16M4 18h16"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconePromptHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeAssetsImagensHeaderToolbarTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeVerTranscricaoTutorialMarkdownTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeEditarMarkdownTutorialTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function IconeColarImagemClipboardTutorialMarkdownTranscribrothers() {
  return (
    <IconeSvgHeaderToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
      />
    </IconeSvgHeaderToolbarTranscribrothers>
  );
}

function descreverMotivoAuditorOmitidoEmPtBrTranscribrothers(motivo: string | undefined): string {
  switch (motivo) {
    case "desativada_por_configuracao_ambiente":
      return "desligada no arquivo de ambiente do servidor (.env).";
    case "desativada_definicao_persistente_interface":
      return "desligada pela preferência nas Configurações (gravada na base SQLite do servidor).";
    default:
      if (motivo && motivo.trim()) return motivo.trim();
      return "motivo não indicado.";
  }
}

export function PaginaPrincipalTranscribrothersFormularioDrivePreviewTutorial() {
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const [modalIniciarTranscricaoAberto, setModalIniciarTranscricaoAberto] = useState(false);
  const [importacaoRecbrothersModalStepper, setImportacaoRecbrothersModalStepper] =
    useState<ImportacaoRecbrothersModalStepperTranscribrothers | null>(null);
  const [configApi, setConfigApi] = useState<ConfigPublicaTranscribrothers | null>(null);
  const [modeloLitellm, setModeloLitellm] = useState("");
  const [modelosExtrasNavegador, setModelosExtrasNavegador] = useState<string[]>([]);
  const [novoSlugModeloLitellm, setNovoSlugModeloLitellm] = useState("");
  const [job, setJob] = useState<JobStatus | null>(null);
  const [nomeArquivoImagemAnotacaoModalAberto, setNomeArquivoImagemAnotacaoModalAberto] = useState<
    string | null
  >(null);
  const [processandoAnotacaoImagemTutorial, setProcessandoAnotacaoImagemTutorial] = useState(false);
  const [insercaoMarkdownImagemAssetPendente, setInsercaoMarkdownImagemAssetPendente] =
    useState<InsercaoMarkdownImagemAssetPendenteTranscribrothers | null>(null);
  const [linhaMarcadorInsercaoImagemPreview, setLinhaMarcadorInsercaoImagemPreview] = useState<
    number | null
  >(null);
  const [topoPxMarcadorInsercaoImagemPreview, setTopoPxMarcadorInsercaoImagemPreview] = useState<
    number | null
  >(null);
  const [salvandoInsercaoImagemNoTutorial, setSalvandoInsercaoImagemNoTutorial] = useState(false);
  const [colandoImagemClipboardParaInsercaoPreviewTutorial, setColandoImagemClipboardParaInsercaoPreviewTutorial] =
    useState(false);
  const colandoImagemClipboardParaInsercaoPreviewTutorialRef = useRef(false);
  const [capturandoFrameManualVideo, setCapturandoFrameManualVideo] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [baixandoMarkdownComImagens, setBaixandoMarkdownComImagens] = useState(false);
  const [abrindoTutorialMarkdownNovaAba, setAbrindoTutorialMarkdownNovaAba] = useState(false);
  const [baixandoPdfTutorial, setBaixandoPdfTutorial] = useState(false);
  const [modalCriarIssueGitlabAberto, setModalCriarIssueGitlabAberto] = useState(false);
  const [criandoIssueGitlab, setCriandoIssueGitlab] = useState(false);
  const [modalComentarIssueGitlabAberto, setModalComentarIssueGitlabAberto] = useState(false);
  const [comentandoIssueGitlab, setComentandoIssueGitlab] = useState(false);
  const [modalAnexarDescricaoIssueGitlabAberto, setModalAnexarDescricaoIssueGitlabAberto] = useState(false);
  const [anexandoDescricaoIssueGitlab, setAnexandoDescricaoIssueGitlab] = useState(false);
  const [modalCriarPaginaWikiGitlabAberto, setModalCriarPaginaWikiGitlabAberto] = useState(false);
  const [criandoPaginaWikiGitlab, setCriandoPaginaWikiGitlab] = useState(false);
  const [anexosContextoFabProjetoEmBranco, setAnexosContextoFabProjetoEmBranco] = useState<
    AnexoContextoFabUiTranscribrothers[]
  >([]);
  const [processandoArquivosAnexoContextoFab, setProcessandoArquivosAnexoContextoFab] = useState(false);
  const [arrastandoArquivosSobreChatFab, setArrastandoArquivosSobreChatFab] = useState(false);
  const [menuMaisConteudoFabAberto, setMenuMaisConteudoFabAberto] = useState(false);
  const [modalTextoAnexoContextoFabAberta, setModalTextoAnexoContextoFabAberta] = useState(false);
  const refInputImagemAnexoContextoFabTranscribrothers = useRef<HTMLInputElement | null>(null);
  const refInputDocumentoAnexoContextoFabTranscribrothers = useRef<HTMLInputElement | null>(null);
  const refMenuMaisConteudoFabTranscribrothers = useRef<HTMLDivElement | null>(null);
  const refTextareaInstrucoesChatFabTranscribrothers = useRef<HTMLTextAreaElement | null>(null);
  const contadorArrasteChatFabRef = useRef(0);

  const [instrucoesRegeneracaoTutorialMarkdown, setInstrucoesRegeneracaoTutorialMarkdown] =
    useState("");
  const [regenerandoTutorialMarkdown, setRegenerandoTutorialMarkdown] = useState(false);
  const [painelConfiguracoesAberto, setPainelConfiguracoesAberto] = useState(false);
  const [promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers, setPromptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers] =
    useState<RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialApiTranscribrothers | null>(null);
  const [carregandoPromptsFixosRevisaoEVerificacaoTutorial, setCarregandoPromptsFixosRevisaoEVerificacaoTutorial] =
    useState(false);
  const [erroCarregarPromptsFixosRevisaoEVerificacaoTutorial, setErroCarregarPromptsFixosRevisaoEVerificacaoTutorial] =
    useState<string | null>(null);
  const [modalProgressoJobAberto, setModalProgressoJobAberto] = useState(false);
  const [passoPipelineModalStatusComPainelDescricaoAbertoId, setPassoPipelineModalStatusComPainelDescricaoAbertoId] =
    useState<string | null>(null);
  const [modalTranscricaoOriginalAberta, setModalTranscricaoOriginalAberta] = useState(false);
  const [modalListaJobsServidorAberta, setModalListaJobsServidorAberta] = useState(false);
  const [modalEscolherVersaoHistoricoTutorialAberta, setModalEscolherVersaoHistoricoTutorialAberta] =
    useState(false);
  const [modalGaleriaAssetsImagensAberta, setModalGaleriaAssetsImagensAberta] = useState(false);
  const [modalPromptTutorialLitellmAberta, setModalPromptTutorialLitellmAberta] = useState(false);
  const [padroesInstrucaoTutorialLitellm, setPadroesInstrucaoTutorialLitellm] =
    useState<InstrucoesPadraoTutorialLitellmApiTranscribrothers | null>(null);
  const [textoInstrucaoPrefixoLitellmTutorialUsuario, setTextoInstrucaoPrefixoLitellmTutorialUsuario] =
    useState("");
  const [modoEdicaoMarkdownTutorialAtivo, setModoEdicaoMarkdownTutorialAtivo] = useState(false);
  const [markdownTutorialRascunhoEdicao, setMarkdownTutorialRascunhoEdicao] = useState("");
  const [salvandoMarkdownTutorialEdicaoManual, setSalvandoMarkdownTutorialEdicaoManual] = useState(false);
  const [confirmacaoExclusaoImagemTutorialMarkdown, setConfirmacaoExclusaoImagemTutorialMarkdown] =
    useState<{ nomeArquivoOriginal: string; rotuloImagem: string } | null>(null);
  const [processandoExclusaoImagemTutorialMarkdown, setProcessandoExclusaoImagemTutorialMarkdown] =
    useState(false);
  const [historicoVersaoTutorialSelecionadaId, setHistoricoVersaoTutorialSelecionadaId] = useState<number | null>(
    null,
  );
  const [listaHistoricoVersoesTutorialMarkdownApi, setListaHistoricoVersoesTutorialMarkdownApi] = useState<
    ResumoVersaoHistoricoTutorialMarkdownApiTranscribrothers[] | null
  >(null);
  const [carregandoListaHistoricoVersoesTutorialMarkdown, setCarregandoListaHistoricoVersoesTutorialMarkdown] =
    useState(false);
  const [markdownPreviewVersaoHistoricoTutorialTranscribrothers, setMarkdownPreviewVersaoHistoricoTutorialTranscribrothers] =
    useState<string | null>(null);
  const [metaVersaoHistoricoTutorialMarkdownSelecionada, setMetaVersaoHistoricoTutorialMarkdownSelecionada] =
    useState<{ origem: string; criado_em: string } | null>(null);
  const [carregandoConteudoHistoricoVersaoTutorialMarkdown, setCarregandoConteudoHistoricoVersaoTutorialMarkdown] =
    useState(false);
  const [restaurandoVersaoHistoricoTutorialMarkdown, setRestaurandoVersaoHistoricoTutorialMarkdown] =
    useState(false);
  const [listaJobsServidorCache, setListaJobsServidorCache] = useState<ResumoJobListaApiTranscribrothers[] | null>(
    null,
  );
  const [carregandoListaJobsServidor, setCarregandoListaJobsServidor] = useState(false);
  const [carregandoSelecaoJobListaId, setCarregandoSelecaoJobListaId] = useState<string | null>(null);
  const [apagandoJobServidorId, setApagandoJobServidorId] = useState<string | null>(null);
  const [painelRegeneracaoFabAberto, setPainelRegeneracaoFabAberto] = useState(false);
  const [modoPainelFabAtualizarTutorial, setModoPainelFabAtualizarTutorial] = useState<
    "regeneracao_inteira" | "edicao_parcial"
  >("regeneracao_inteira");
  const [fabPresetRegeneracaoInteiraTranscribrothers, setFabPresetRegeneracaoInteiraTranscribrothers] =
    useState<"sem_video" | "revisao_profunda" | null>(null);
  const [modoEdicaoPorSecaoTutorialAtivo, setModoEdicaoPorSecaoTutorialAtivo] = useState(false);
  const [solicitarScrollPainelEdicaoSecaoTutorial, setSolicitarScrollPainelEdicaoSecaoTutorial] =
    useState(false);
  const refPainelEdicaoSecaoMarkdownTutorial = useRef<HTMLDivElement | null>(null);
  const refRecuperacaoPreviewTutorialHistoricoTentadaJobId = useRef<string | null>(null);
  const [listaSecoesNivel2TutorialMarkdown, setListaSecoesNivel2TutorialMarkdown] = useState<
    ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers[] | null
  >(null);
  const [carregandoListaSecoesNivel2Tutorial, setCarregandoListaSecoesNivel2Tutorial] = useState(false);
  const [tituloSecaoSelecionadaParaEdicao, setTituloSecaoSelecionadaParaEdicao] = useState("");
  const [instrucoesRegeneracaoSecaoMarkdown, setInstrucoesRegeneracaoSecaoMarkdown] = useState("");
  const [modoEscopoEdicaoSecaoMarkdownForm, setModoEscopoEdicaoSecaoMarkdownForm] = useState<
    "trecho_local" | "a_partir_de" | "secao_inteira"
  >("trecho_local");
  const [trechoAncoraEdicaoSecaoMarkdownForm, setTrechoAncoraEdicaoSecaoMarkdownForm] = useState("");
  const [escopoEdicaoSecaoManualAtivoForm, setEscopoEdicaoSecaoManualAtivoForm] = useState(false);
  const [regenerandoSecaoMarkdownTutorial, setRegenerandoSecaoMarkdownTutorial] = useState(false);
  const [modalPreviewRegeneracaoSecaoAberto, setModalPreviewRegeneracaoSecaoAberto] = useState(false);
  const [aplicandoPreviewRegeneracaoSecao, setAplicandoPreviewRegeneracaoSecao] = useState(false);
  const [modalPreviewRegeneracaoTutorialAberto, setModalPreviewRegeneracaoTutorialAberto] = useState(false);
  const [aplicandoPreviewRegeneracaoTutorial, setAplicandoPreviewRegeneracaoTutorial] = useState(false);
  const [mmJanelaSegundosForm, setMmJanelaSegundosForm] = useState(
    String(PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.janelaSegundos),
  );
  const [mmParalelasForm, setMmParalelasForm] = useState(
    String(PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.janelasParalelasMaxima),
  );
  const [mmFormatoAudioForm, setMmFormatoAudioForm] = useState<FormatoAudioInlineMultimodalTranscribrothers>(
    PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.formatoAudioInline,
  );
  const [mmBitrateKbpsForm, setMmBitrateKbpsForm] = useState(
    String(PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.audioBitrateKbps),
  );
  const [mmMonoForm, setMmMonoForm] = useState(PADRAO_UI_CONFIG_TRANSCRICAO_MULTIMODAL_TRANSCRIBROTHERS.audioMono);
  const [tutorialMargemLinksTemporaisForm, setTutorialMargemLinksTemporaisForm] = useState("2");
  const [tutorialPlanejamentoCapturaLitellmForm, setTutorialPlanejamentoCapturaLitellmForm] = useState(true);
  const [salvandoMmRuntime, setSalvandoMmRuntime] = useState(false);
  const [erroMmRuntime, setErroMmRuntime] = useState<string | null>(null);
  const [auditorVerificacaoHabilitadoForm, setAuditorVerificacaoHabilitadoForm] = useState(true);
  const [salvandoAuditorRuntimeSqlite, setSalvandoAuditorRuntimeSqlite] = useState(false);
  const [erroAuditorRuntimeSqlite, setErroAuditorRuntimeSqlite] = useState<string | null>(null);
  const [auditorRedundanciaSecaoHabilitadoForm, setAuditorRedundanciaSecaoHabilitadoForm] = useState(true);
  const [correcaoAutomaticaRedundanciaSecaoHabilitadaForm, setCorrecaoAutomaticaRedundanciaSecaoHabilitadaForm] =
    useState(true);
  const [
    correcaoAutomaticaRedundanciaSecaoIncluirAtencaoForm,
    setCorrecaoAutomaticaRedundanciaSecaoIncluirAtencaoForm,
  ] = useState(false);
  const [salvandoAuditorRedundanciaSecaoRuntimeSqlite, setSalvandoAuditorRedundanciaSecaoRuntimeSqlite] =
    useState(false);
  const [erroAuditorRedundanciaSecaoRuntimeSqlite, setErroAuditorRedundanciaSecaoRuntimeSqlite] = useState<
    string | null
  >(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textareaMarkdownEdicaoTutorialRef = useRef<HTMLTextAreaElement | null>(null);
  const refContainerPreviewTutorialMarkdown = useRef<HTMLDivElement | null>(null);
  const indiceAncoraRenderizadoPreviewTutorialPrincipalRef = useRef(0);
  const ultimoPontoInsercaoImagemPreviewTutorialRef =
    useRef<PontoInsercaoImagemMarkdownPreviewTutorialTranscribrothers | null>(null);

  const jobId = job?.id;

  const tutorialLitellmPrefixoCustomPersistidoNoJob = useMemo(() => {
    const v = job?.steps_json?.tutorial_litellm_instrucao_prefixo_custom;
    return typeof v === "string" && v.trim() ? v : null;
  }, [job?.steps_json?.tutorial_litellm_instrucao_prefixo_custom]);

  const carregarListaJobsNoServidorTranscribrothers = useCallback(async () => {
    setCarregandoListaJobsServidor(true);
    try {
      const arr = await listarJobsRecentesApiTranscribrothers(80);
      setListaJobsServidorCache(arr);
    } catch (e) {
      pushToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setCarregandoListaJobsServidor(false);
    }
  }, [pushToast]);

  useEffect(() => {
    if (modalListaJobsServidorAberta) {
      void carregarListaJobsNoServidorTranscribrothers();
    }
  }, [modalListaJobsServidorAberta, carregarListaJobsNoServidorTranscribrothers]);

  useEffect(() => {
    setModelosExtrasNavegador(carregarListaModelosLitellmExtrasSalvosNoNavegadorTranscribrothers());
  }, []);

  useEffect(() => {
    const params = lerParametrosImportacaoRecbrothersDaUrl();
    if (!params.recbrothers || !params.stagingId) return;
    const etapaInicial = params.etapa === "destino" ? 1 : 0;
    void fetch(`/api/staging/${encodeURIComponent(params.stagingId)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((meta: { total_cliques?: number } | null) => {
        setImportacaoRecbrothersModalStepper({
          stagingId: params.stagingId!,
          etapaInicial,
          destinoInicial: params.destino ?? undefined,
          totalCliquesStaging: meta?.total_cliques,
        });
        setModalIniciarTranscricaoAberto(true);
      })
      .catch(() => {
        setImportacaoRecbrothersModalStepper({
          stagingId: params.stagingId!,
          etapaInicial,
          destinoInicial: params.destino ?? undefined,
        });
        setModalIniciarTranscricaoAberto(true);
      });
    limparParametrosImportacaoRecbrothersDaUrlBarraNavegador();
  }, []);

  useEffect(() => {
    void fetch("/api/config/transcribrothers")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((raw: Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>) => {
        const d = normalizarRespostaConfigPublicaTranscribrothersDaApi(raw);
        setConfigApi(d);
        const def = d.litellm_model_default || d.litellm_models[0] || "";
        setModeloLitellm((m) => (m ? m : def));
      })
      .catch(() => {
        setModeloLitellm((m) => (m ? m : "openai/gpt-4o-mini"));
      });
  }, []);

  useEffect(() => {
    if (!painelConfiguracoesAberto) return;
    let cancelado = false;
    setCarregandoPromptsFixosRevisaoEVerificacaoTutorial(true);
    setErroCarregarPromptsFixosRevisaoEVerificacaoTutorial(null);
    void fetch(
      "/api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial",
    )
      .then(async (r) => {
        if (!r.ok) {
          const t = await r.text();
          throw new Error(t || `Erro HTTP ${r.status}`);
        }
        return (await r.json()) as RespostaPromptsFixosRevisaoProfundaEVerificacaoSustentacaoTutorialApiTranscribrothers;
      })
      .then((d) => {
        if (!cancelado) setPromptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers(d);
      })
      .catch((e) => {
        if (!cancelado) {
          setPromptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers(null);
          setErroCarregarPromptsFixosRevisaoEVerificacaoTutorial(
            e instanceof Error ? e.message : String(e),
          );
        }
      })
      .finally(() => {
        if (!cancelado) setCarregandoPromptsFixosRevisaoEVerificacaoTutorial(false);
      });
    return () => {
      cancelado = true;
    };
  }, [painelConfiguracoesAberto]);

  const modelosParaSelectLiteLLM = useMemo(() => {
    const base =
      configApi?.litellm_models?.length && configApi.litellm_models.length > 0
        ? configApi.litellm_models
        : [modeloLitellm || "openai/gpt-4o-mini"];
    return mesclarModelosServidorComExtrasNavegadorTranscribrothers(base, modelosExtrasNavegador);
  }, [configApi, modelosExtrasNavegador, modeloLitellm]);

  useEffect(() => {
    if (!modeloLitellm.trim()) return;
    if (!modelosParaSelectLiteLLM.includes(modeloLitellm)) {
      setModeloLitellm(modelosParaSelectLiteLLM[0] ?? "");
    }
  }, [modeloLitellm, modelosParaSelectLiteLLM]);

  useEffect(() => {
    if (!configApi) return;
    setMmJanelaSegundosForm(String(configApi.transcricao_multimodal_janela_segundos));
    setMmParalelasForm(String(configApi.transcricao_multimodal_janelas_paralelas_maxima));
    setMmFormatoAudioForm(configApi.transcricao_multimodal_formato_audio_inline);
    setMmBitrateKbpsForm(String(configApi.transcricao_multimodal_audio_bitrate_kbps));
    setMmMonoForm(configApi.transcricao_multimodal_audio_mono);
    setTutorialMargemLinksTemporaisForm(
      String(configApi.tutorial_margem_minima_segundos_entre_links_temporais_captura),
    );
    setTutorialPlanejamentoCapturaLitellmForm(
      configApi.tutorial_planejamento_instantes_captura_frames_litellm_habilitado,
    );
    setAuditorVerificacaoHabilitadoForm(configApi.verificacao_sustentacao_tutorial_habilitada_efetiva);
    setAuditorRedundanciaSecaoHabilitadoForm(configApi.verificacao_redundancia_secao_markdown_habilitada_efetiva);
    setCorrecaoAutomaticaRedundanciaSecaoHabilitadaForm(
      configApi.verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva,
    );
    setCorrecaoAutomaticaRedundanciaSecaoIncluirAtencaoForm(
      configApi.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva,
    );
    setErroAuditorRuntimeSqlite(null);
  }, [configApi]);

  useEffect(() => {
    let cancelado = false;
    void fetch("/api/config/transcribrothers/tutorial-litellm-instrucoes-padrao")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((raw: InstrucoesPadraoTutorialLitellmApiTranscribrothers) => {
        if (cancelado) return;
        setPadroesInstrucaoTutorialLitellm(raw);
      })
      .catch(() => {
        if (cancelado) return;
        setPadroesInstrucaoTutorialLitellm(null);
      });
    return () => {
      cancelado = true;
    };
  }, []);

  useEffect(() => {
    if (!modalPromptTutorialLitellmAberta || padroesInstrucaoTutorialLitellm) return;
    let cancelado = false;
    void fetch("/api/config/transcribrothers/tutorial-litellm-instrucoes-padrao")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((raw: InstrucoesPadraoTutorialLitellmApiTranscribrothers) => {
        if (cancelado) return;
        setPadroesInstrucaoTutorialLitellm(raw);
      })
      .catch(() => {
        if (cancelado) return;
        setPadroesInstrucaoTutorialLitellm(null);
      });
    return () => {
      cancelado = true;
    };
  }, [modalPromptTutorialLitellmAberta, padroesInstrucaoTutorialLitellm]);

  useEffect(() => {
    if (!padroesInstrucaoTutorialLitellm) return;
    if (modalPromptTutorialLitellmAberta) return;
    if (tutorialLitellmPrefixoCustomPersistidoNoJob) {
      setTextoInstrucaoPrefixoLitellmTutorialUsuario(tutorialLitellmPrefixoCustomPersistidoNoJob);
      return;
    }
    const rascunho = carregarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownDoNavegadorTranscribrothers();
    setTextoInstrucaoPrefixoLitellmTutorialUsuario(
      rascunho ?? padroesInstrucaoTutorialLitellm.instrucao_sem_imagens,
    );
  }, [padroesInstrucaoTutorialLitellm, tutorialLitellmPrefixoCustomPersistidoNoJob, job?.id]);

  useEffect(() => {
    if (!modalPromptTutorialLitellmAberta || !padroesInstrucaoTutorialLitellm) return;
    if (tutorialLitellmPrefixoCustomPersistidoNoJob) {
      setTextoInstrucaoPrefixoLitellmTutorialUsuario(tutorialLitellmPrefixoCustomPersistidoNoJob);
      return;
    }
    const rascunho = carregarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownDoNavegadorTranscribrothers();
    setTextoInstrucaoPrefixoLitellmTutorialUsuario(
      rascunho ?? padroesInstrucaoTutorialLitellm.instrucao_sem_imagens,
    );
  }, [modalPromptTutorialLitellmAberta, padroesInstrucaoTutorialLitellm, tutorialLitellmPrefixoCustomPersistidoNoJob]);

  const seekSegundos = useCallback((segundos: number) => {
    const v = videoRef.current;
    if (!v) return;
    v.currentTime = Math.max(0, segundos);
    void v.play().catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!jobId) {
      setInsercaoMarkdownImagemAssetPendente(null);
      setLinhaMarcadorInsercaoImagemPreview(null);
    }
  }, [jobId]);

  useEffect(() => {
    if (!insercaoMarkdownImagemAssetPendente) {
      setLinhaMarcadorInsercaoImagemPreview(null);
      setTopoPxMarcadorInsercaoImagemPreview(null);
    }
  }, [insercaoMarkdownImagemAssetPendente]);

  const capturarFrameManualVideoNoTimestampSegundosTranscribrothers = useCallback(
    async (timestampSegundos: number) => {
      if (!job?.id) return;
      setCapturandoFrameManualVideo(true);
      setErro(null);
      try {
        const resp = await capturarFrameManualVideoTutorialJobApiTranscribrothers(
          job.id,
          timestampSegundos,
        );
        setJob(resp.job);
        setNomeArquivoImagemAnotacaoModalAberto(resp.nome_arquivo);
        pushToast(
          `Frame capturado em ${formatarSegundosComoMmSsTranscribrothers(resp.timestamp_segundos_efetivo)}. Visualize e anote na janela aberta; use «Inserir no documento» quando quiser.`,
          "success",
        );
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setCapturandoFrameManualVideo(false);
      }
    },
    [job?.id, pushToast],
  );

  const mapaAnotacoesImagensTutorial = useMemo(
    () => extrairMapaAnotacoesImagensTutorialDoStepsJsonTranscribrothers(job?.steps_json),
    [job?.steps_json],
  );

  const resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers = useCallback(
    (nomeNoMarkdown: string) => {
      if (nomeNoMarkdown.toLowerCase().includes(".anotado.png")) {
        return nomeNoMarkdown;
      }
      return resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers(
        nomeNoMarkdown,
        mapaAnotacoesImagensTutorial[nomeNoMarkdown],
      );
    },
    [mapaAnotacoesImagensTutorial],
  );

  const aoAlternarVersaoExibicaoImagemTutorial = useCallback(
    async (nomeArquivoOriginal: string, versao: "original" | "anotado") => {
      if (!job?.id) return;
      setProcessandoAnotacaoImagemTutorial(true);
      setErro(null);
      try {
        const j = await definirVersaoExibicaoScreenshotTutorialJobApiTranscribrothers(
          job.id,
          nomeArquivoOriginal,
          versao,
        );
        setJob(j);
        pushToast(versao === "anotado" ? "Exibindo versão anotada." : "Exibindo captura original.", "success");
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setProcessandoAnotacaoImagemTutorial(false);
      }
    },
    [job?.id, pushToast],
  );

  const aoRemoverAnotacaoImagemTutorial = useCallback(
    async (nomeArquivoOriginal: string) => {
      if (!job?.id) return;
      if (!window.confirm("Remover a versão anotada desta imagem? A captura original será mantida.")) {
        return;
      }
      setProcessandoAnotacaoImagemTutorial(true);
      setErro(null);
      try {
        const j = await removerAnotacaoScreenshotTutorialJobApiTranscribrothers(job.id, nomeArquivoOriginal);
        setJob(j);
        pushToast("Anotação removida.", "success");
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setProcessandoAnotacaoImagemTutorial(false);
      }
    },
    [job?.id, pushToast],
  );

  const aoSincronizarMarkdownComImagemAnotada = useCallback(
    async (nomeArquivoOriginal: string) => {
      if (!job?.id) return;
      setProcessandoAnotacaoImagemTutorial(true);
      setErro(null);
      try {
        const j = await sincronizarMarkdownComVersaoAnotadaScreenshotJobApiTranscribrothers(
          job.id,
          nomeArquivoOriginal,
        );
        setJob(j);
        pushToast("Markdown atualizado para referenciar a imagem anotada.", "success");
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setProcessandoAnotacaoImagemTutorial(false);
      }
    },
    [job?.id, pushToast],
  );

  const baixarTutorialMarkdownComoArquivoComImagensEmbutidas = useCallback(async () => {
    const md = job?.result_markdown;
    const id = job?.id;
    if (!md || !id) return;
    setErro(null);
    setBaixandoMarkdownComImagens(true);
    try {
      const mdComImagens = await gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers(
        md,
        id,
        resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers,
      );
      const nomeBase = obterNomeBaseArquivoDownloadTutorialComTituloH1MarkdownOuJobIdTranscribrothers(md, id);
      const blob = new Blob([mdComImagens], { type: "text/markdown;charset=utf-8" });
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = `${nomeBase}.md`;
      a.rel = "noopener";
      a.click();
      URL.revokeObjectURL(href);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setBaixandoMarkdownComImagens(false);
    }
  }, [job?.id, job?.result_markdown, resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers]);

  const abrirTutorialMarkdownEmNovaAbaNavegador = useCallback(async () => {
    const md = job?.result_markdown;
    const id = job?.id;
    if (!md || !id) return;
    setErro(null);
    setAbrindoTutorialMarkdownNovaAba(true);
    try {
      await abrirTutorialMarkdownRenderizadoEmNovaAbaNavegadorTranscribrothers(
        md,
        id,
        resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers,
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErro(msg);
      pushToast(msg, "error");
    } finally {
      setAbrindoTutorialMarkdownNovaAba(false);
    }
  }, [job?.id, job?.result_markdown, pushToast, resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers]);

  const gitlabCriarIssueHabilitadoNoServidorTranscribrothers = Boolean(
    configApi?.gitlab_criar_issue_habilitado,
  );

  const gitlabCriarWikiHabilitadoNoServidorTranscribrothers = Boolean(
    configApi?.gitlab_criar_wiki_habilitado,
  );

  const tituloSugeridoIssueGitlabMarkdownAtualTranscribrothers = useMemo(
    () =>
      job?.id
        ? obterTituloSugeridoIssueGitlabDeMarkdownTutorialTranscribrothers(
            job.result_markdown,
            job.id,
          )
        : "",
    [job?.id, job?.result_markdown],
  );

  const quantidadeReferenciasImagensAssetsPngIssueGitlabTranscribrothers = useMemo(
    () =>
      listarCaminhosAssetsPngOrdemPrimeiraOcorrenciaMarkdownTutorialTranscribrothers(
        job?.result_markdown ?? "",
      ).length,
    [job?.result_markdown],
  );

  const confirmarCriarIssueGitlabComTituloTranscribrothers = useCallback(
    async (titulo: string, incluirImagensPngMarkdown: boolean) => {
      const id = job?.id;
      const md = job?.result_markdown;
      if (!id || !md?.trim()) return;
      setCriandoIssueGitlab(true);
      setErro(null);
      try {
        const resp = await criarIssueGitlabPortalDefensoriaGatewayApiTranscribrothers({
          titulo,
          jobId: id,
          incluirImagensPngMarkdown,
        });
        setModalCriarIssueGitlabAberto(false);
        const enviadas = resp.imagens_png_enviadas_gitlab ?? 0;
        const ignoradas = resp.imagens_png_ignoradas_gitlab ?? 0;
        let msg = `Issue #${resp.iid} criada no GitLab.`;
        if (incluirImagensPngMarkdown && enviadas > 0) {
          msg += ` ${enviadas} imagem(ns) enviada(s).`;
          if (ignoradas > 0) {
            msg += ` ${ignoradas} referência(s) sem arquivo no servidor foram mantidas como assets/.`;
          }
        }
        pushToast(msg, "success");
        abrirUrlExternaNovaAbaNavegadorTranscribrothers(resp.web_url);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setCriandoIssueGitlab(false);
      }
    },
    [job?.id, job?.result_markdown, pushToast],
  );

  const confirmarComentarIssueGitlabTranscribrothers = useCallback(
    async (issueUrl: string, incluirImagensPngMarkdown: boolean) => {
      const id = job?.id;
      const md = job?.result_markdown;
      if (!id || !md?.trim()) return;
      setComentandoIssueGitlab(true);
      setErro(null);
      try {
        const resp = await comentarIssueGitlabDocumentoMarkdownApiTranscribrothers({
          issueUrl,
          jobId: id,
          incluirImagensPngMarkdown,
        });
        setModalComentarIssueGitlabAberto(false);
        const enviadas = resp.imagens_png_enviadas_gitlab ?? 0;
        const ignoradas = resp.imagens_png_ignoradas_gitlab ?? 0;
        let msg = `Comentário publicado na issue #${resp.issue_iid}.`;
        if (incluirImagensPngMarkdown && enviadas > 0) {
          msg += ` ${enviadas} imagem(ns) enviada(s).`;
          if (ignoradas > 0) {
            msg += ` ${ignoradas} referência(s) sem arquivo no servidor foram mantidas como assets/.`;
          }
        }
        pushToast(msg, "success");
        abrirUrlExternaNovaAbaNavegadorTranscribrothers(resp.note_url || resp.issue_url);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setComentandoIssueGitlab(false);
      }
    },
    [job?.id, job?.result_markdown, pushToast],
  );

  const confirmarAnexarDescricaoIssueGitlabTranscribrothers = useCallback(
    async (issueUrl: string, incluirImagensPngMarkdown: boolean) => {
      const id = job?.id;
      const md = job?.result_markdown;
      if (!id || !md?.trim()) return;
      setAnexandoDescricaoIssueGitlab(true);
      setErro(null);
      try {
        const resp = await anexarDescricaoIssueGitlabDocumentoMarkdownApiTranscribrothers({
          issueUrl,
          jobId: id,
          incluirImagensPngMarkdown,
        });
        setModalAnexarDescricaoIssueGitlabAberto(false);
        const enviadas = resp.imagens_png_enviadas_gitlab ?? 0;
        const ignoradas = resp.imagens_png_ignoradas_gitlab ?? 0;
        let msg = `Descrição da issue #${resp.issue_iid} atualizada.`;
        if (incluirImagensPngMarkdown && enviadas > 0) {
          msg += ` ${enviadas} imagem(ns) enviada(s).`;
          if (ignoradas > 0) {
            msg += ` ${ignoradas} referência(s) sem arquivo no servidor foram mantidas como assets/.`;
          }
        }
        pushToast(msg, "success");
        abrirUrlExternaNovaAbaNavegadorTranscribrothers(resp.web_url || resp.issue_url);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setAnexandoDescricaoIssueGitlab(false);
      }
    },
    [job?.id, job?.result_markdown, pushToast],
  );

  const confirmarCriarPaginaWikiGitlabComTituloTranscribrothers = useCallback(
    async (titulo: string, incluirImagensPngMarkdown: boolean, prefixoPastaWiki: string) => {
      const id = job?.id;
      const md = job?.result_markdown;
      if (!id || !md?.trim()) return;
      setCriandoPaginaWikiGitlab(true);
      setErro(null);
      try {
        const resp = await criarPaginaWikiGitlabDocumentacaoApiTranscribrothers({
          titulo,
          jobId: id,
          prefixoPastaWiki,
          incluirImagensPngMarkdown,
        });
        const enviadas = resp.imagens_png_enviadas_gitlab ?? 0;
        const ignoradas = resp.imagens_png_ignoradas_gitlab ?? 0;
        let msg = resp.atualizada
          ? `Subpágina wiki atualizada (${resp.slug}).`
          : `Subpágina wiki criada (${resp.slug}).`;
        if (incluirImagensPngMarkdown && enviadas > 0) {
          msg += ` ${enviadas} imagem(ns) enviada(s).`;
          if (ignoradas > 0) {
            msg += ` ${ignoradas} referência(s) sem arquivo no servidor foram mantidas como assets/.`;
          }
        }
        if (resp.link_adicionado_no_indice_pasta) {
          msg += ` Link incluído na página índice ${prefixoPastaWiki || "workshop"}.`;
        }
        pushToast(msg, "success");
        abrirUrlExternaNovaAbaNavegadorTranscribrothers(resp.web_url);
        setModalCriarPaginaWikiGitlabAberto(false);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setCriandoPaginaWikiGitlab(false);
      }
    },
    [job?.id, job?.result_markdown, pushToast],
  );

  const baixarTutorialPdfComImagensEmbutidas = useCallback(async () => {
    const md = job?.result_markdown;
    const id = job?.id;
    if (!md || !id) return;
    setErro(null);
    setBaixandoPdfTutorial(true);
    try {
      const nomeBase = obterNomeBaseArquivoDownloadTutorialComTituloH1MarkdownOuJobIdTranscribrothers(md, id);
      await baixarArquivoPdfTutorialMarkdownComImagensEmbutidasTranscribrothers(
        md,
        id,
        nomeBase,
        resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers,
      );
      pushToast("PDF gerado no navegador.", "success");
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErro(msg);
      pushToast(msg, "error");
    } finally {
      setBaixandoPdfTutorial(false);
    }
  }, [job?.id, job?.result_markdown, pushToast, resolverNomeAssetPngParaDownloadComDuasVersoesTranscribrothers]);

  useEffect(() => {
    if (!jobId) return;
    if (
      job?.status === "completed" ||
      job?.status === "failed" ||
      job?.status === "cancelled"
    ) {
      return;
    }
    const id = window.setInterval(async () => {
      try {
        const j = await buscarJob(jobId);
        setJob(j);
      } catch {
        /* mantém último estado */
      }
    }, 2000);
    return () => window.clearInterval(id);
  }, [jobId, job?.status]);

  useEffect(() => {
    if (!modalProgressoJobAberto) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setModalProgressoJobAberto(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [modalProgressoJobAberto]);

  useEffect(() => {
    if (!modalProgressoJobAberto) {
      setPassoPipelineModalStatusComPainelDescricaoAbertoId(null);
    }
  }, [modalProgressoJobAberto]);

  useEffect(() => {
    setPassoPipelineModalStatusComPainelDescricaoAbertoId(null);
  }, [job?.id]);

  useEffect(() => {
    if (!painelRegeneracaoFabAberto) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setPainelRegeneracaoFabAberto(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [painelRegeneracaoFabAberto]);

  const solicitarExclusaoImagemDoMarkdownTutorialTranscribrothers = useCallback(
    (nomeArquivoOriginal: string, rotuloImagem: string) => {
      setConfirmacaoExclusaoImagemTutorialMarkdown({ nomeArquivoOriginal, rotuloImagem });
    },
    [],
  );

  const confirmarExclusaoImagemDoMarkdownTutorialTranscribrothers = useCallback(async () => {
    if (!job || !confirmacaoExclusaoImagemTutorialMarkdown) return;
    setProcessandoExclusaoImagemTutorialMarkdown(true);
    try {
      const markdownFonte = modoEdicaoMarkdownTutorialAtivo
        ? markdownTutorialRascunhoEdicao
        : (job.result_markdown ?? "");
      const novoMarkdown = removerReferenciaImagemAssetDoMarkdownTutorialTranscribrothers(
        markdownFonte,
        confirmacaoExclusaoImagemTutorialMarkdown.nomeArquivoOriginal,
      );
      if (novoMarkdown === markdownFonte) {
        pushToast("Não foi possível localizar esta imagem no Markdown.", "info");
        setConfirmacaoExclusaoImagemTutorialMarkdown(null);
        return;
      }
      if (modoEdicaoMarkdownTutorialAtivo) {
        setMarkdownTutorialRascunhoEdicao(novoMarkdown);
      } else {
        const j2 = await patchResultMarkdownJobTranscribrothers(job.id, novoMarkdown);
        setJob(j2);
      }
      if (
        nomeArquivoImagemAnotacaoModalAberto ===
        confirmacaoExclusaoImagemTutorialMarkdown.nomeArquivoOriginal
      ) {
        setNomeArquivoImagemAnotacaoModalAberto(null);
      }
      pushToast("Imagem removida do tutorial.", "success");
      setConfirmacaoExclusaoImagemTutorialMarkdown(null);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      pushToast(msg, "error");
    } finally {
      setProcessandoExclusaoImagemTutorialMarkdown(false);
    }
  }, [
    job,
    confirmacaoExclusaoImagemTutorialMarkdown,
    modoEdicaoMarkdownTutorialAtivo,
    markdownTutorialRascunhoEdicao,
    nomeArquivoImagemAnotacaoModalAberto,
    pushToast,
  ]);

  const markdownComponents = useMemo(() => {
    return {
      p: ComponenteParagrafoMarkdownReactDesembrulharQuandoFilhoUnicoEImagemTranscribrothers,
      a: ({
        href,
        children,
        ...rest
      }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => {
        if (href?.startsWith("?t=")) {
          const raw = href.slice(3);
          const segundos = Number.parseFloat(raw);
          return (
            <button
              type="button"
              className="tb-tslink"
              onClick={() => seekSegundos(Number.isFinite(segundos) ? segundos : 0)}
            >
              {children}
            </button>
          );
        }
        return (
          <a href={href} {...rest}>
            {children}
          </a>
        );
      },
      img: ({ alt, src, ...rest }: React.ImgHTMLAttributes<HTMLImageElement>) => {
        if (!src || !jobId) return null;
        const limpo = src.replace(/^\.\//, "");
        if (limpo.startsWith("assets/")) {
          const nomeNaReferencia = limpo.split("/").pop() ?? limpo;
          const nomeOriginal = resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers(
            nomeNaReferencia,
          );
          return (
            <ComponenteImagemMarkdownTutorialClicavelAbrirModalAnotacaoTranscribrothers
              jobId={jobId}
              nomeArquivoOriginal={nomeOriginal}
              registroAnotacao={mapaAnotacoesImagensTutorial[nomeOriginal]}
              alt={alt ?? ""}
              imgProps={rest}
              aoClicarAbrirEditor={setNomeArquivoImagemAnotacaoModalAberto}
              aoSolicitarExcluirImagemDoTutorial={
                historicoVersaoTutorialSelecionadaId === null
                  ? solicitarExclusaoImagemDoMarkdownTutorialTranscribrothers
                  : undefined
              }
            />
          );
        }
        return <img alt={alt ?? ""} src={src} {...rest} />;
      },
    };
  }, [
    jobId,
    mapaAnotacoesImagensTutorial,
    historicoVersaoTutorialSelecionadaId,
    solicitarExclusaoImagemDoMarkdownTutorialTranscribrothers,
  ]);

  const fecharModalEdicaoMarkdownTutorialTranscribrothers = useCallback(() => {
    setModoEdicaoMarkdownTutorialAtivo(false);
    setMarkdownTutorialRascunhoEdicao(job?.result_markdown ?? "");
  }, [job?.result_markdown]);

  const salvarModalEdicaoMarkdownTutorialTranscribrothers = useCallback(async () => {
    if (!job) return;
    setErro(null);
    setSalvandoMarkdownTutorialEdicaoManual(true);
    try {
      const j2 = await patchResultMarkdownJobTranscribrothers(job.id, markdownTutorialRascunhoEdicao);
      setJob(j2);
      pushToast("Alterações guardadas no servidor. Pode continuar a editar.", "success");
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErro(msg);
      pushToast(msg, "error");
    } finally {
      setSalvandoMarkdownTutorialEdicaoManual(false);
    }
  }, [job, markdownTutorialRascunhoEdicao, pushToast]);

  async function iniciarProjetoEmBrancoSemVideoTranscribrothers() {
    setErro(null);
    setCarregando(true);
    try {
      const j = await criarProjetoEmBrancoJobApiTranscribrothers();
      setJob(j as JobStatus);
      setHistoricoVersaoTutorialSelecionadaId(null);
      setModalIniciarTranscricaoAberto(false);
      setModalProgressoJobAberto(false);
      pushToast("Projeto em branco criado. Edite o documento e use imagens em assets/.", "success");
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }

  async function iniciarPipelineTranscricaoComArquivoLocalTranscribrothers(
    arquivo: File,
    destinoAposTranscricao: DestinoAposTranscricaoTranscribrothers,
    cliquesJsonOpcional?: File | null,
  ) {
    setErro(null);
    setCarregando(true);
    const stagingId = importacaoRecbrothersModalStepper?.stagingId ?? null;
    try {
      const modeloParaEnviar = modeloLitellm.trim();
      const prefixo = textoInstrucaoPrefixoLitellmTutorialUsuario.trim();
      const j = await criarJobUploadArquivoLocal(
        stagingId ? null : arquivo,
        modeloParaEnviar,
        prefixo ? prefixo : null,
        destinoAposTranscricao,
        stagingId,
        cliquesJsonOpcional ?? null,
      );
      setJob(j);
      setModalIniciarTranscricaoAberto(false);
      setImportacaoRecbrothersModalStepper(null);
      setModalProgressoJobAberto(true);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }

  const rotuloProgressoLegivel = useMemo(() => {
    if (!job) return "";
    const fase = job.steps_json?.pipeline_fase;
    return obterDescricaoLegivelProgressoJobPipelinePortuguesTranscribrothers(job.status, fase);
  }, [job]);

  const linhaDetalheProgressoJob = useMemo(() => {
    if (!job) return "";
    return obterLinhaDetalheSubetapaProgressoJobPipelinePortuguesTranscribrothers(job.steps_json);
  }, [job]);

  const contextoPipelineHorizontalModalStatusJob = useMemo(() => {
    if (!job) return null;
    return obterContextoPipelineHorizontalModalStatusJobTranscribrothers(job.status, job.steps_json);
  }, [job]);

  const registrosTempoInferenciaTranscricaoPorTrecho = useMemo(
    () =>
      extrairRegistrosTempoInferenciaTranscricaoJanelasDoStepsJsonTranscribrothers(job?.steps_json),
    [job?.steps_json],
  );

  const segundosTotaisInferenciaTranscricaoTrechosListados = useMemo(() => {
    return registrosTempoInferenciaTranscricaoPorTrecho.reduce(
      (acc, r) => acc + Math.max(0, r.duracao_inferencia_segundos),
      0,
    );
  }, [registrosTempoInferenciaTranscricaoPorTrecho]);

  /** Lista de tempos por trecho: expandida só enquanto a inferência multimodal ainda corre. */
  const transcricaoInferenciaPorTrechoAindaEmCurso = useMemo(() => {
    if (!job) return false;
    if (job.status !== "transcribing") return false;
    const f = typeof job.steps_json?.pipeline_fase === "string" ? job.steps_json.pipeline_fase : "";
    return f.startsWith("transcrevendo_audio");
  }, [job]);

  const textoPlanoRevisaoProfundaFormatadoParaModalTranscribrothers = useMemo(() => {
    const raw = job?.steps_json?.revisao_profunda_plano_json;
    if (raw == null) return "";
    if (typeof raw === "string") {
      const t = raw.trim();
      if (!t) return "";
      try {
        return JSON.stringify(JSON.parse(t), null, 2);
      } catch {
        return t;
      }
    }
    if (typeof raw === "object") {
      try {
        return JSON.stringify(raw, null, 2);
      } catch {
        return "";
      }
    }
    return "";
  }, [job?.steps_json]);

  const topicosPlanoRevisaoProfundaVistaAmigavelModalTranscribrothers = useMemo(() => {
    return extrairTopicosPlanoRevisaoProfundaParaVistaAmigavelDeStepsJsonTranscribrothers(
      job?.steps_json?.revisao_profunda_plano_json,
    );
  }, [job?.steps_json?.revisao_profunda_plano_json]);

  const temPlanoRevisaoProfundaNoJobParaModalStatusTranscribrothers = useMemo(() => {
    const raw = job?.steps_json?.revisao_profunda_plano_json;
    if (raw == null) return false;
    if (typeof raw === "string") return raw.trim().length > 0;
    if (typeof raw === "object") return true;
    return false;
  }, [job?.steps_json?.revisao_profunda_plano_json]);

  type DadosVerificacaoSustentacaoTutorialMarkdownStepsTranscribrothers = {
    sucesso?: boolean;
    omitida?: boolean;
    motivo?: string;
    classificacao_global?: string;
    mensagem_resumo?: string;
    erro?: string;
    itens?: Array<{
      trecho_ou_tema?: string;
      classificacao?: string;
      justificativa_curta?: string;
      citacao_transcricao_opcional?: string;
    }>;
  };

  const dadosVerificacaoSustentacaoTutorialMarkdownDoJob = useMemo(():
    | DadosVerificacaoSustentacaoTutorialMarkdownStepsTranscribrothers
    | null => {
    const raw = job?.steps_json?.verificacao_sustentacao_tutorial;
    if (!raw || typeof raw !== "object") return null;
    return raw as DadosVerificacaoSustentacaoTutorialMarkdownStepsTranscribrothers;
  }, [job?.steps_json]);

  const entradasLogDecisoesIaModalStatusJob = useMemo(
    () => montarEntradasLogDecisoesIaParaModalStatusJobTranscribrothers(job?.steps_json ?? null),
    [job?.steps_json],
  );

  const mensagemRetomadaTranscricaoMultimodal =
    job?.steps_json &&
    typeof job.steps_json.transcricao_multimodal_mensagem_retomada === "string"
      ? job.steps_json.transcricao_multimodal_mensagem_retomada.trim()
      : "";

  const rawCheckpointTrechosSalvos = job?.steps_json?.transcricao_multimodal_checkpoint_trechos_salvos;
  const trechosCheckpointSalvosParaRetomada =
    typeof rawCheckpointTrechosSalvos === "number" && Number.isFinite(rawCheckpointTrechosSalvos)
      ? rawCheckpointTrechosSalvos
      : 0;

  const jobTerminal =
    job &&
    (job.status === "completed" || job.status === "failed" || job.status === "cancelled");

  const jobPodeSerCancelado =
    job &&
    job.status !== "completed" &&
    job.status !== "failed" &&
    job.status !== "cancelled";

  const jobPodeRepetirPipeline =
    job && (job.status === "failed" || job.status === "cancelled");

  const jobPossuiSnapshotParaRegenerarTutorial =
    Boolean(job) &&
    ((typeof job.steps_json?.regeneracao_tutorial_snapshot === "object" &&
      job.steps_json.regeneracao_tutorial_snapshot !== null) ||
      (jobEhProjetoEmBrancoTranscribrothers(job) &&
        (job.status === "completed" || job.status === "failed") &&
        typeof job.result_markdown === "string" &&
        job.result_markdown.trim().length > 0));

  const previewRegeneracaoTutorialMarkdownDocumentoInteiro = useMemo(
    () =>
      extrairPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeStepsJsonTranscribrothers(job?.steps_json),
    [job?.steps_json],
  );

  const listaReferenciasFigurasImagensMarkdownTutorialFab = useMemo(() => {
    const md = job?.result_markdown;
    if (typeof md !== "string" || !md.trim()) return [];
    return listarCaminhosAssetsPngOrdemPrimeiraOcorrenciaMarkdownTutorialTranscribrothers(md);
  }, [job?.result_markdown]);

  const listaImagensContextoPedidoFabProjetoEmBranco = useMemo(() => {
    const vistos = new Set<string>();
    const saida: { rotulo: string; caminho: string }[] = [];
    for (const p of listaReferenciasFigurasImagensMarkdownTutorialFab) {
      if (!vistos.has(p)) {
        vistos.add(p);
        saida.push({ rotulo: `Doc · ${p}`, caminho: p });
      }
    }
    for (const a of anexosContextoFabProjetoEmBranco) {
      if (a.tipo === "imagem" && !vistos.has(a.caminhoRelativo)) {
        vistos.add(a.caminhoRelativo);
        saida.push({ rotulo: `Anexo · ${a.nomeArquivo}`, caminho: a.caminhoRelativo });
      }
    }
    return saida.map((item, i) => ({ ...item, figura: i + 1 }));
  }, [listaReferenciasFigurasImagensMarkdownTutorialFab, anexosContextoFabProjetoEmBranco]);

  const payloadContextoFabProjetoEmBrancoAtual = useMemo(
    () =>
      jobEhProjetoEmBrancoTranscribrothers(job)
        ? montarPayloadContextoFabParaRegeneracaoApiTranscribrothers(anexosContextoFabProjetoEmBranco)
        : { caminhos_assets_png_contexto_fab: [], textos_contexto_fab: [] },
    [job, anexosContextoFabProjetoEmBranco],
  );

  const textoPlanoTranscricaoOriginalSnapshotJob = useMemo(
    () => montarTextoPlanoTranscricaoOriginalAPartirDeSnapshotJobTutorialTranscribrothers(job?.steps_json),
    [job?.steps_json],
  );

  const jobPermiteEdicaoManualMarkdownTutorial =
    Boolean(job) &&
    (job.status === "completed" || job.status === "failed") &&
    typeof job.result_markdown === "string" &&
    !modoEdicaoPorSecaoTutorialAtivo;

  const markdownFontePreviewTutorialPrincipal = useMemo(() => {
    if (historicoVersaoTutorialSelecionadaId !== null) return null;
    return job?.result_markdown ?? null;
  }, [historicoVersaoTutorialSelecionadaId, job?.result_markdown]);

  const secoesH2MarkdownPreviewTutorialPrincipal = useMemo(
    () =>
      listarSecoesH2MarkdownTutorialParaPreviewTranscribrothers(
        markdownFontePreviewTutorialPrincipal ?? "",
      ),
    [markdownFontePreviewTutorialPrincipal],
  );

  const ancorasMarkdownPreviewTutorialPrincipal = useMemo(
    () =>
      listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers(
        markdownFontePreviewTutorialPrincipal ?? "",
      ),
    [markdownFontePreviewTutorialPrincipal],
  );

  const markdownComponentsPreviewTutorialComAncorasLinha = useMemo(
    () =>
      mesclarComponentsReactMarkdownComAncorasLinhaFonteDocumentoTranscribrothers(
        markdownComponents,
        ancorasMarkdownPreviewTutorialPrincipal,
        indiceAncoraRenderizadoPreviewTutorialPrincipalRef,
      ),
    [ancorasMarkdownPreviewTutorialPrincipal, markdownComponents],
  );

  indiceAncoraRenderizadoPreviewTutorialPrincipalRef.current = 0;

  const modoInserirImagemAssetNoPreviewTutorialAtivo = Boolean(
    insercaoMarkdownImagemAssetPendente && !modoEdicaoMarkdownTutorialAtivo,
  );

  const cancelarModoInserirImagemAssetNoTutorialTranscribrothers = useCallback(() => {
    setInsercaoMarkdownImagemAssetPendente(null);
    setLinhaMarcadorInsercaoImagemPreview(null);
    setTopoPxMarcadorInsercaoImagemPreview(null);
    ultimoPontoInsercaoImagemPreviewTutorialRef.current = null;
  }, []);

  const processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers =
    useCallback(
      async (arquivoImagem: File) => {
        if (!job?.id) return;
        if (historicoVersaoTutorialSelecionadaId !== null) {
          pushToast("Volte à versão atual do tutorial para colar imagens.", "info");
          return;
        }
        if (!jobPermiteEdicaoManualMarkdownTutorial) {
          pushToast("Não é possível editar o tutorial neste momento.", "info");
          return;
        }
        if (modoEdicaoMarkdownTutorialAtivo) return;
        if (colandoImagemClipboardParaInsercaoPreviewTutorialRef.current) return;

        colandoImagemClipboardParaInsercaoPreviewTutorialRef.current = true;
        setColandoImagemClipboardParaInsercaoPreviewTutorial(true);
        try {
          const resposta = await colarImagemClipboardMarkdownTutorialJobApiTranscribrothers(
            job.id,
            arquivoImagem,
          );
          setJob(resposta.job);
          setInsercaoMarkdownImagemAssetPendente({
            snippetMarkdown: resposta.snippet_markdown,
            nomeArquivoOriginal: resposta.nome_arquivo,
          });
          pushToast(
            "Imagem salva nos assets. Passe o mouse no tutorial e clique na linha tracejada para inserir.",
            "success",
          );
        } catch (e) {
          const msg = e instanceof Error ? e.message : String(e);
          pushToast(msg, "error");
        } finally {
          colandoImagemClipboardParaInsercaoPreviewTutorialRef.current = false;
          setColandoImagemClipboardParaInsercaoPreviewTutorial(false);
        }
      },
      [
        historicoVersaoTutorialSelecionadaId,
        job?.id,
        jobPermiteEdicaoManualMarkdownTutorial,
        modoEdicaoMarkdownTutorialAtivo,
        pushToast,
      ],
    );

  const aoColarImagemClipboardNoPreviewTutorialMarkdownTranscribrothers = useCallback(
    (evento: React.ClipboardEvent<HTMLDivElement>) => {
      const arquivo = extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers(
        evento.nativeEvent,
      );
      if (!arquivo) return;
      evento.preventDefault();
      evento.stopPropagation();
      void processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers(arquivo);
    },
    [processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers],
  );

  const iniciarInserirImagemAssetNoDocumentoMarkdownTranscribrothers = useCallback(
    async (nomeArquivoOriginal: string) => {
      if (!job?.id) return;
      if (historicoVersaoTutorialSelecionadaId !== null) {
        pushToast("Volte à versão atual do tutorial para inserir imagens.", "info");
        return;
      }
      if (!jobPermiteEdicaoManualMarkdownTutorial) {
        pushToast("Não é possível editar o tutorial neste momento.", "info");
        return;
      }
      const snippet = montarSnippetMarkdownImagemAssetTutorialTranscribrothers(nomeArquivoOriginal);
      try {
        await copiarTextoParaAreaTransferenciaNavegadorTranscribrothers(snippet);
      } catch {
        pushToast("Não foi possível copiar para a área de transferência.", "error");
        return;
      }
      setNomeArquivoImagemAnotacaoModalAberto(null);

      if (modoEdicaoMarkdownTutorialAtivo && textareaMarkdownEdicaoTutorialRef.current) {
        const { novoValor, novaPosicaoCursor } = inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers(
          textareaMarkdownEdicaoTutorialRef.current,
          snippet,
          markdownTutorialRascunhoEdicao,
        );
        setMarkdownTutorialRascunhoEdicao(novoValor);
        requestAnimationFrame(() => {
          const ta = textareaMarkdownEdicaoTutorialRef.current;
          if (!ta) return;
          ta.focus();
          ta.setSelectionRange(novaPosicaoCursor, novaPosicaoCursor);
        });
        pushToast("Referência da imagem copiada e inserida no cursor do editor.", "success");
        return;
      }

      setInsercaoMarkdownImagemAssetPendente({
        snippetMarkdown: snippet,
        nomeArquivoOriginal,
      });
      pushToast(
        "Referência copiada. Passe o mouse no tutorial e clique na linha tracejada para inserir a imagem.",
        "success",
      );
    },
    [
      historicoVersaoTutorialSelecionadaId,
      job?.id,
      jobPermiteEdicaoManualMarkdownTutorial,
      markdownTutorialRascunhoEdicao,
      modoEdicaoMarkdownTutorialAtivo,
      pushToast,
    ],
  );

  const confirmarInsercaoImagemAssetNaLinhaPreviewTutorialTranscribrothers = useCallback(
    async (numeroLinha: number) => {
      if (!job?.id || !insercaoMarkdownImagemAssetPendente || !markdownFontePreviewTutorialPrincipal) {
        return;
      }
      setSalvandoInsercaoImagemNoTutorial(true);
      setErro(null);
      try {
        const novoMarkdown = inserirSnippetMarkdownNaLinhaDocumentoTranscribrothers(
          markdownFontePreviewTutorialPrincipal,
          numeroLinha,
          insercaoMarkdownImagemAssetPendente.snippetMarkdown,
        );
        const j2 = await patchResultMarkdownJobTranscribrothers(job.id, novoMarkdown);
        setJob(j2);
        setInsercaoMarkdownImagemAssetPendente(null);
        setLinhaMarcadorInsercaoImagemPreview(null);
        pushToast("Imagem inserida no tutorial.", "success");
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setSalvandoInsercaoImagemNoTutorial(false);
      }
    },
    [insercaoMarkdownImagemAssetPendente, job?.id, markdownFontePreviewTutorialPrincipal, pushToast],
  );

  const tratarMovimentoMousePreviewTutorialInsercaoImagemTranscribrothers = useCallback(
    (evento: React.MouseEvent<HTMLDivElement>) => {
      if (!modoInserirImagemAssetNoPreviewTutorialAtivo || !markdownFontePreviewTutorialPrincipal) return;
      const container = refContainerPreviewTutorialMarkdown.current;
      if (!container) return;
      const alvo = document.elementFromPoint(evento.clientX, evento.clientY);
      if (!(alvo instanceof HTMLElement)) return;
      if (alvoPreviewIgnoraCliqueInsercaoImagemMarkdownTranscribrothers(alvo)) return;
      const ponto = obterPontoInsercaoImagemMarkdownSobPonteiroNoPreviewTutorialTranscribrothers(
        alvo,
        container,
        markdownFontePreviewTutorialPrincipal,
        secoesH2MarkdownPreviewTutorialPrincipal,
        { clientX: evento.clientX, clientY: evento.clientY },
      );
      if (ponto != null) {
        ultimoPontoInsercaoImagemPreviewTutorialRef.current = ponto;
        setLinhaMarcadorInsercaoImagemPreview(ponto.numeroLinhaInsercao);
        setTopoPxMarcadorInsercaoImagemPreview(ponto.topoPxMarcador);
      }
    },
    [
      markdownFontePreviewTutorialPrincipal,
      modoInserirImagemAssetNoPreviewTutorialAtivo,
      secoesH2MarkdownPreviewTutorialPrincipal,
    ],
  );

  const tratarCliquePreviewTutorialInsercaoImagemTranscribrothers = useCallback(
    (evento: React.MouseEvent<HTMLDivElement>) => {
      if (!modoInserirImagemAssetNoPreviewTutorialAtivo || salvandoInsercaoImagemNoTutorial) return;
      if (alvoPreviewIgnoraCliqueInsercaoImagemMarkdownTranscribrothers(evento.target)) return;
      const container = refContainerPreviewTutorialMarkdown.current;
      if (!container || !(evento.target instanceof HTMLElement)) return;

      const pontoVisual =
        ultimoPontoInsercaoImagemPreviewTutorialRef.current ??
        obterPontoInsercaoImagemMarkdownSobPonteiroNoPreviewTutorialTranscribrothers(
          evento.target,
          container,
          markdownFontePreviewTutorialPrincipal ?? "",
          secoesH2MarkdownPreviewTutorialPrincipal,
          { clientX: evento.clientX, clientY: evento.clientY },
        );
      if (pontoVisual == null) return;
      const numeroLinhaInsercao = obterNumeroLinhaInsercaoPorTopoMarcadorNoPreviewTutorialTranscribrothers(
        container,
        pontoVisual.topoPxMarcador,
        markdownFontePreviewTutorialPrincipal ?? "",
        secoesH2MarkdownPreviewTutorialPrincipal,
      );

      evento.preventDefault();
      void confirmarInsercaoImagemAssetNaLinhaPreviewTutorialTranscribrothers(numeroLinhaInsercao);
    },
    [
      confirmarInsercaoImagemAssetNaLinhaPreviewTutorialTranscribrothers,
      markdownFontePreviewTutorialPrincipal,
      modoInserirImagemAssetNoPreviewTutorialAtivo,
      salvandoInsercaoImagemNoTutorial,
      secoesH2MarkdownPreviewTutorialPrincipal,
      obterNumeroLinhaInsercaoPorTopoMarcadorNoPreviewTutorialTranscribrothers,
    ],
  );

  useEffect(() => {
    if (!modoInserirImagemAssetNoPreviewTutorialAtivo) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        cancelarModoInserirImagemAssetNoTutorialTranscribrothers();
        pushToast("Inserção de imagem cancelada.", "info");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    cancelarModoInserirImagemAssetNoTutorialTranscribrothers,
    modoInserirImagemAssetNoPreviewTutorialAtivo,
    pushToast,
  ]);

  const jobPermiteModoEdicaoPorSecaoTutorial =
    Boolean(job) &&
    jobPossuiSnapshotParaRegenerarTutorial &&
    (job.status === "completed" || job.status === "failed") &&
    typeof job.result_markdown === "string";

  const previewRegeneracaoSecaoMarkdown = useMemo(
    () => extrairPreviewRegeneracaoSecaoMarkdownDeStepsJsonTranscribrothers(job?.steps_json),
    [job?.steps_json],
  );

  const fasePipelineJobAtual = job?.steps_json?.pipeline_fase;

  const jobPodeRegenerarSomenteMarkdown =
    Boolean(jobPossuiSnapshotParaRegenerarTutorial) &&
    job &&
    (job.status === "completed" || job.status === "failed") &&
    !previewRegeneracaoSecaoMarkdown &&
    !previewRegeneracaoTutorialMarkdownDocumentoInteiro;

  const jobPodeRecuperarPreviewRegeneracaoTutorialDeHistorico =
    Boolean(job) &&
    job.status === "completed" &&
    Boolean(job.steps_json?.regeneracao_apenas_markdown) &&
    !previewRegeneracaoTutorialMarkdownDocumentoInteiro &&
    typeof job.steps_json?.regeneracao_tutorial_aplicada_em !== "string" &&
    fasePipelineJobAtual !== "regeneracao_tutorial_markdown_preview_pronta";

  const analiseEscopoEdicaoSecaoEmAndamento =
    Boolean(job) &&
    job?.status === "generating_tutorial" &&
    (fasePipelineJobAtual === "interpretando_escopo_pedido_edicao_secao_markdown_litellm" ||
      fasePipelineJobAtual === "validando_escopo_edicao_secao_markdown" ||
      fasePipelineJobAtual === "refinando_escopo_pedido_edicao_secao_markdown_litellm");

  const regeneracaoSecaoEmAndamento =
    Boolean(job) &&
    job?.status === "generating_tutorial" &&
    (fasePipelineJobAtual === "regenerando_secao_markdown_litellm" ||
      fasePipelineJobAtual === "regenerando_secao_markdown_litellm_agendado" ||
      fasePipelineJobAtual === "escopo_edicao_secao_confirmado" ||
      fasePipelineJobAtual === "verificacao_redundancia_secao_markdown_litellm" ||
      fasePipelineJobAtual === "corrigindo_redundancia_secao_markdown_litellm" ||
      fasePipelineJobAtual === "verificacao_redundancia_secao_apos_correcao_automatica_litellm" ||
      analiseEscopoEdicaoSecaoEmAndamento);

  const jobPodeConsultarHistoricoVersoesTutorialMarkdown =
    Boolean(job) &&
    (job.status === "completed" || job.status === "failed") &&
    typeof job.result_markdown === "string";

  const historicoVersaoTutorialMarkdownEstaAtivoNaUi =
    historicoVersaoTutorialSelecionadaId !== null && !modoEdicaoMarkdownTutorialAtivo;

  const jobEhProjetoEmBrancoAtual = useMemo(() => jobEhProjetoEmBrancoTranscribrothers(job), [job]);

  const jobEhReproducaoBugAtual = useMemo(() => jobEhReproducaoBugTranscribrothers(job), [job]);

  const jobEhNotasPropostaAtual = useMemo(() => jobEhNotasPropostaFuncionalidadeTranscribrothers(job), [job]);

  const destinoAposTranscricaoJobAtual = useMemo(
    () => normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers(job?.steps_json?.destino_apos_transcricao),
    [job?.steps_json?.destino_apos_transcricao],
  );

  const tituloFrameDocumentoResultadoTranscribrothers = useMemo(
    () => obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers(destinoAposTranscricaoJobAtual),
    [destinoAposTranscricaoJobAtual],
  );

  const subtituloVersaoEDataFrameDocumentoTranscribrothers = useMemo(
    () =>
      montarSubtituloVersaoEDataFrameDocumentoTutorialTranscribrothers({
        historicoVersaoSelecionadaId: historicoVersaoTutorialSelecionadaId,
        listaHistoricoVersoes: listaHistoricoVersoesTutorialMarkdownApi,
        criadoEmVersaoHistoricoSelecionada: metaVersaoHistoricoTutorialMarkdownSelecionada?.criado_em ?? null,
        formatarDataHora: formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers,
        jobUpdatedAt: job?.updated_at ?? null,
        exibirVersaoAtualServidor: historicoVersaoTutorialSelecionadaId === null && Boolean(job?.result_markdown),
      }),
    [
      historicoVersaoTutorialSelecionadaId,
      listaHistoricoVersoesTutorialMarkdownApi,
      metaVersaoHistoricoTutorialMarkdownSelecionada?.criado_em,
      job?.updated_at,
      job?.result_markdown,
    ],
  );

  const rotuloNumeroVersaoHistoricoTutorialSelecionadaNoProjeto = useMemo(() => {
    if (
      historicoVersaoTutorialSelecionadaId === null ||
      !listaHistoricoVersoesTutorialMarkdownApi?.length
    ) {
      return null;
    }
    const total = listaHistoricoVersoesTutorialMarkdownApi.length;
    const indice = listaHistoricoVersoesTutorialMarkdownApi.findIndex(
      (r) => r.id === historicoVersaoTutorialSelecionadaId,
    );
    if (indice < 0) return null;
    const numero = obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers(
      indice,
      total,
    );
    return total > 1 ? `v${numero} de ${total}` : `v${numero}`;
  }, [historicoVersaoTutorialSelecionadaId, listaHistoricoVersoesTutorialMarkdownApi]);

  const rotuloVersaoAtualServidorModalHistoricoTutorial = useMemo(() => {
    const total = listaHistoricoVersoesTutorialMarkdownApi?.length ?? 0;
    if (total > 1) {
      return `Versão atual no servidor (v${total} de ${total})`;
    }
    if (total === 1) {
      return "Versão atual no servidor (v1)";
    }
    return "Versão atual no servidor";
  }, [listaHistoricoVersoesTutorialMarkdownApi?.length]);

  const dataHoraVersaoAtualServidorModalHistoricoTutorial = useMemo(
    () =>
      job?.updated_at
        ? formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers(job.updated_at)
        : null,
    [job?.updated_at],
  );

  const podeColarImagemClipboardNoPreviewTutorialTranscribrothers =
    jobPermiteEdicaoManualMarkdownTutorial &&
    historicoVersaoTutorialSelecionadaId === null &&
    !modoEdicaoMarkdownTutorialAtivo &&
    Boolean(job?.result_markdown?.trim());

  const solicitarColarImagemClipboardNoPreviewTutorialPeloBotaoTranscribrothers = useCallback(async () => {
    if (!podeColarImagemClipboardNoPreviewTutorialTranscribrothers) return;
    const arquivo = await extrairArquivoImagemDaApiClipboardNavegadorTranscribrothers();
    if (!arquivo) {
      pushToast(
        "Nenhuma imagem na área de transferência. Copie uma captura ou use Ctrl+V com o foco no tutorial.",
        "info",
      );
      return;
    }
    await processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers(arquivo);
  }, [
    podeColarImagemClipboardNoPreviewTutorialTranscribrothers,
    processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers,
    pushToast,
  ]);

  useEffect(() => {
    if (!podeColarImagemClipboardNoPreviewTutorialTranscribrothers) return;
    const onPaste = (evento: ClipboardEvent) => {
      if (elementoAtivoEstaEmCampoDigitavelParaColarTextoTranscribrothers()) return;
      const arquivo = extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers(evento);
      if (!arquivo) return;
      evento.preventDefault();
      void processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers(arquivo);
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, [
    podeColarImagemClipboardNoPreviewTutorialTranscribrothers,
    processarArquivoImagemClipboardParaModoInsercaoPreviewTutorialTranscribrothers,
  ]);

  useEffect(() => {
    setModoEdicaoMarkdownTutorialAtivo(false);
    setModoEdicaoPorSecaoTutorialAtivo(false);
    setMarkdownTutorialRascunhoEdicao("");
    setModalTranscricaoOriginalAberta(false);
    setHistoricoVersaoTutorialSelecionadaId(null);
    setListaHistoricoVersoesTutorialMarkdownApi(null);
    setMarkdownPreviewVersaoHistoricoTutorialTranscribrothers(null);
    setMetaVersaoHistoricoTutorialMarkdownSelecionada(null);
    setListaSecoesNivel2TutorialMarkdown(null);
    setTituloSecaoSelecionadaParaEdicao("");
    setInstrucoesRegeneracaoSecaoMarkdown("");
    setModoEscopoEdicaoSecaoMarkdownForm("trecho_local");
    setTrechoAncoraEdicaoSecaoMarkdownForm("");
    setEscopoEdicaoSecaoManualAtivoForm(false);
    setModalPreviewRegeneracaoSecaoAberto(false);
    setModalPreviewRegeneracaoTutorialAberto(false);
    setModalEscolherVersaoHistoricoTutorialAberta(false);
    refRecuperacaoPreviewTutorialHistoricoTentadaJobId.current = null;
    setModoPainelFabAtualizarTutorial("regeneracao_inteira");
    setFabPresetRegeneracaoInteiraTranscribrothers(null);
    setPainelRegeneracaoFabAberto(false);
    setAnexosContextoFabProjetoEmBranco([]);
    setModalTextoAnexoContextoFabAberta(false);
    setMenuMaisConteudoFabAberto(false);
  }, [job?.id]);

  useEffect(() => {
    if (!menuMaisConteudoFabAberto) return;
    const fecharSeCliqueFora = (evento: MouseEvent) => {
      const alvo = evento.target;
      if (!(alvo instanceof Node) || refMenuMaisConteudoFabTranscribrothers.current?.contains(alvo)) {
        return;
      }
      setMenuMaisConteudoFabAberto(false);
    };
    document.addEventListener("mousedown", fecharSeCliqueFora);
    return () => document.removeEventListener("mousedown", fecharSeCliqueFora);
  }, [menuMaisConteudoFabAberto]);

  useEffect(() => {
    if (!painelRegeneracaoFabAberto) {
      setMenuMaisConteudoFabAberto(false);
    }
  }, [painelRegeneracaoFabAberto]);

  useEffect(() => {
    if (!jobId || !modoEdicaoPorSecaoTutorialAtivo || !jobPermiteModoEdicaoPorSecaoTutorial) {
      return;
    }
    let cancelado = false;
    setCarregandoListaSecoesNivel2Tutorial(true);
    void listarSecoesNivel2TutorialMarkdownJobApiTranscribrothers(jobId)
      .then((lista) => {
        if (cancelado) return;
        setListaSecoesNivel2TutorialMarkdown(lista);
        if (lista.length > 0) {
          setTituloSecaoSelecionadaParaEdicao((atual) =>
            atual && lista.some((s) => s.linha_heading === atual) ? atual : "",
          );
        }
      })
      .catch((e) => {
        if (!cancelado) {
          pushToast(e instanceof Error ? e.message : String(e), "error");
        }
      })
      .finally(() => {
        if (!cancelado) setCarregandoListaSecoesNivel2Tutorial(false);
      });
    return () => {
      cancelado = true;
    };
  }, [jobId, modoEdicaoPorSecaoTutorialAtivo, jobPermiteModoEdicaoPorSecaoTutorial, pushToast]);

  useEffect(() => {
    if (previewRegeneracaoSecaoMarkdown) {
      setModalPreviewRegeneracaoSecaoAberto(true);
    }
  }, [previewRegeneracaoSecaoMarkdown?.criado_em]);

  useEffect(() => {
    if (!previewRegeneracaoTutorialMarkdownDocumentoInteiro) return;
    setModalPreviewRegeneracaoTutorialAberto(true);
    if (job?.status === "completed" || job?.status === "failed") {
      setModalProgressoJobAberto(false);
      pushToast("Pré-visualização pronta. Confira o documento antes de aplicar.", "success");
    }
  }, [previewRegeneracaoTutorialMarkdownDocumentoInteiro?.criado_em, job?.status, pushToast]);

  useEffect(() => {
    if (!jobId || !jobPodeRecuperarPreviewRegeneracaoTutorialDeHistorico) return;
    if (refRecuperacaoPreviewTutorialHistoricoTentadaJobId.current === jobId) return;
    refRecuperacaoPreviewTutorialHistoricoTentadaJobId.current = jobId;
    void (async () => {
      try {
        const j = (await recuperarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeHistoricoJobApiTranscribrothers(
          jobId,
        )) as JobStatus;
        setJob(j);
        pushToast(
          "Pré-visualização recuperada do histórico (regeneração anterior sem preview). Confira antes de aplicar.",
          "success",
        );
      } catch {
        refRecuperacaoPreviewTutorialHistoricoTentadaJobId.current = null;
      }
    })();
  }, [jobId, jobPodeRecuperarPreviewRegeneracaoTutorialDeHistorico, pushToast]);

  useEffect(() => {
    if (modoEdicaoMarkdownTutorialAtivo) {
      setHistoricoVersaoTutorialSelecionadaId(null);
    }
  }, [modoEdicaoMarkdownTutorialAtivo]);

  useEffect(() => {
    if (!jobId || !jobPodeConsultarHistoricoVersoesTutorialMarkdown) {
      setListaHistoricoVersoesTutorialMarkdownApi(null);
      setCarregandoListaHistoricoVersoesTutorialMarkdown(false);
      return;
    }
    let cancelado = false;
    setCarregandoListaHistoricoVersoesTutorialMarkdown(true);
    void listarHistoricoVersoesTutorialMarkdownJobApiTranscribrothers(jobId)
      .then((arr) => {
        if (!cancelado) setListaHistoricoVersoesTutorialMarkdownApi(arr);
      })
      .catch((e) => {
        if (!cancelado) {
          setListaHistoricoVersoesTutorialMarkdownApi([]);
          pushToast(e instanceof Error ? e.message : String(e), "error");
        }
      })
      .finally(() => {
        if (!cancelado) setCarregandoListaHistoricoVersoesTutorialMarkdown(false);
      });
    return () => {
      cancelado = true;
    };
  }, [
    jobId,
    jobPodeConsultarHistoricoVersoesTutorialMarkdown,
    job?.result_markdown,
    job?.updated_at,
    pushToast,
  ]);

  useEffect(() => {
    if (!jobId || historicoVersaoTutorialSelecionadaId === null) {
      setMarkdownPreviewVersaoHistoricoTutorialTranscribrothers(null);
      setMetaVersaoHistoricoTutorialMarkdownSelecionada(null);
      setCarregandoConteudoHistoricoVersaoTutorialMarkdown(false);
      return;
    }
    let cancelado = false;
    setCarregandoConteudoHistoricoVersaoTutorialMarkdown(true);
    void obterConteudoHistoricoVersaoTutorialMarkdownJobApiTranscribrothers(jobId, historicoVersaoTutorialSelecionadaId)
      .then((d) => {
        if (cancelado) return;
        setMarkdownPreviewVersaoHistoricoTutorialTranscribrothers(d.markdown);
        setMetaVersaoHistoricoTutorialMarkdownSelecionada({ origem: d.origem, criado_em: d.criado_em });
      })
      .catch((e) => {
        if (cancelado) return;
        pushToast(e instanceof Error ? e.message : String(e), "error");
        setHistoricoVersaoTutorialSelecionadaId(null);
      })
      .finally(() => {
        if (!cancelado) setCarregandoConteudoHistoricoVersaoTutorialMarkdown(false);
      });
    return () => {
      cancelado = true;
    };
  }, [jobId, historicoVersaoTutorialSelecionadaId, pushToast]);

  useEffect(() => {
    if (!modoEdicaoPorSecaoTutorialAtivo || !solicitarScrollPainelEdicaoSecaoTutorial) {
      return;
    }
    if (carregandoListaSecoesNivel2Tutorial) {
      return;
    }
    setSolicitarScrollPainelEdicaoSecaoTutorial(false);
    requestAnimationFrame(() => {
      refPainelEdicaoSecaoMarkdownTutorial.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }, [
    modoEdicaoPorSecaoTutorialAtivo,
    solicitarScrollPainelEdicaoSecaoTutorial,
    carregandoListaSecoesNivel2Tutorial,
  ]);

  useEffect(() => {
    if (!job || job.status !== "generating_tutorial") {
      return;
    }
    const fase = job.steps_json?.pipeline_fase;
    if (typeof fase !== "string") {
      return;
    }
    const fasesQueAbremModalGeracaoSecao = new Set([
      "escopo_edicao_secao_confirmado",
      "regenerando_secao_markdown_litellm",
      "verificacao_redundancia_secao_markdown_litellm",
      "corrigindo_redundancia_secao_markdown_litellm",
      "verificacao_redundancia_secao_apos_correcao_automatica_litellm",
    ]);
    if (fasesQueAbremModalGeracaoSecao.has(fase)) {
      setModalProgressoJobAberto(true);
    }
  }, [job?.id, job?.status, job?.steps_json?.pipeline_fase]);

  const fabRegeneracaoTutorialVisivel =
    Boolean(job && jobPossuiSnapshotParaRegenerarTutorial) &&
    Boolean(
      job &&
        (job.status === "completed" ||
          job.status === "failed" ||
          job.status === "generating_tutorial"),
    );

  const regeneracaoTutorialEmAndamento =
    Boolean(job) && job?.status === "generating_tutorial" && Boolean(jobPossuiSnapshotParaRegenerarTutorial);

  const jobEmExecucao = Boolean(job && !jobTerminal);

  const solicitarRegeneracaoTutorialMarkdownComTextoInstrucoesTranscribrothers = useCallback(
    async (textoInstrucoes: string, extra?: { revisaoProfundaMultifase?: boolean }) => {
      if (!job) return;
      setErro(null);
      setRegenerandoTutorialMarkdown(true);
      try {
        const j = await regenerarSomenteTutorialMarkdownTranscribrothers(job.id, {
          instrucoesRevisaoHumana: textoInstrucoes,
          litellmModel: modeloLitellm.trim() || undefined,
          revisaoProfundaMultifase: extra?.revisaoProfundaMultifase,
          caminhosAssetsPngContextoFab: payloadContextoFabProjetoEmBrancoAtual.caminhos_assets_png_contexto_fab,
          textosContextoFab: payloadContextoFabProjetoEmBrancoAtual.textos_contexto_fab,
        });
        setJob(j);
        setPainelRegeneracaoFabAberto(false);
        setAnexosContextoFabProjetoEmBranco([]);
        setModalProgressoJobAberto(true);
        pushToast(
          extra?.revisaoProfundaMultifase
            ? "Revisão profunda pedida. Ao terminar, confira a pré-visualização antes de aplicar."
            : "Regeneração pedida. Ao terminar, confira a pré-visualização antes de aplicar.",
          "success",
        );
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setRegenerandoTutorialMarkdown(false);
      }
    },
    [job, modeloLitellm, payloadContextoFabProjetoEmBrancoAtual, pushToast],
  );

  const solicitarRegeneracaoReproducaoBugMarkdownComTextoInstrucoesTranscribrothers = useCallback(
    async (textoInstrucoes: string, documentoAutonomoSemVideo: boolean) => {
      if (!job) return;
      setErro(null);
      setRegenerandoTutorialMarkdown(true);
      try {
        const j = await regenerarMarkdownReproducaoBugJobApiTranscribrothers(job.id, {
          instrucoesRevisaoHumana: textoInstrucoes,
          litellmModel: modeloLitellm.trim() || undefined,
          documentoAutonomoSemVideo,
        });
        setJob(j);
        setPainelRegeneracaoFabAberto(false);
        setModalProgressoJobAberto(true);
        pushToast(
          "Regeneração do roteiro pedida. Ao terminar, confira a pré-visualização antes de aplicar.",
          "success",
        );
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setRegenerandoTutorialMarkdown(false);
      }
    },
    [job, modeloLitellm, pushToast],
  );

  const solicitarRegeneracaoNotasPropostaMarkdownComTextoInstrucoesTranscribrothers = useCallback(
    async (textoInstrucoes: string, documentoAutonomoSemVideo: boolean) => {
      if (!job) return;
      setErro(null);
      setRegenerandoTutorialMarkdown(true);
      try {
        const j = await regenerarMarkdownNotasPropostaJobApiTranscribrothers(job.id, {
          instrucoesRevisaoHumana: textoInstrucoes,
          litellmModel: modeloLitellm.trim() || undefined,
          documentoAutonomoSemVideo,
        });
        setJob(j);
        setPainelRegeneracaoFabAberto(false);
        setModalProgressoJobAberto(true);
        pushToast(
          "Regeneração das notas pedida. Ao terminar, confira a pré-visualização antes de aplicar.",
          "success",
        );
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setRegenerandoTutorialMarkdown(false);
      }
    },
    [job, modeloLitellm, pushToast],
  );

  const processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers = useCallback(
    async (arquivoImagem: File) => {
      if (!job?.id) return;
      const r = await uploadImagemAnexoContextoFabProjetoEmBrancoApiTranscribrothers(job.id, arquivoImagem);
      setJob(r.job);
      setAnexosContextoFabProjetoEmBranco((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          tipo: "imagem",
          nomeArquivo: r.nome_arquivo,
          caminhoRelativo: r.caminho_relativo,
        },
      ]);
      pushToast(`Imagem anexada ao pedido (${r.caminho_relativo}).`, "success");
    },
    [job?.id, pushToast],
  );

  const incluirTextoAnexoContextoFabNoPedidoTranscribrothers = useCallback(
    (conteudoBruto: string, nomeArquivoOrigem?: string) => {
      const { texto, truncado } = truncarTextoAnexoContextoFabSeNecessarioTranscribrothers(conteudoBruto);
      if (!texto) {
        pushToast("Digite ou cole algum texto antes de incluir.", "error");
        return;
      }
      setAnexosContextoFabProjetoEmBranco((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          tipo: "texto",
          conteudo: texto,
          nomeArquivoOrigem: nomeArquivoOrigem?.trim() || undefined,
        },
      ]);
      pushToast(
        truncado
          ? "Texto incluído (foi truncado ao limite do pedido)."
          : nomeArquivoOrigem
            ? `Arquivo incluído: ${nomeArquivoOrigem}`
            : "Texto incluído no pedido.",
        "success",
      );
    },
    [pushToast],
  );

  const processarArquivoDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers = useCallback(
    async (arquivo: File) => {
      if (!job?.id) return;
      const tipo = classificarArquivoAnexoContextoFabTranscribrothers(arquivo);
      if (tipo === "imagem") {
        await processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers(arquivo);
        return;
      }
      if (tipo !== "documento") {
        pushToast(`Formato não suportado: ${arquivo.name}`, "error");
        return;
      }
      const nome = arquivo.name.toLowerCase();
      if (nome.endsWith(".md") || nome.endsWith(".txt")) {
        const texto = await lerArquivoMarkdownOuTextoComoUtf8Transcribrothers(arquivo);
        incluirTextoAnexoContextoFabNoPedidoTranscribrothers(texto, arquivo.name);
        return;
      }
      const r = await extrairTextoDocumentoAnexoContextoFabProjetoEmBrancoApiTranscribrothers(job.id, arquivo);
      incluirTextoAnexoContextoFabNoPedidoTranscribrothers(r.texto, r.nome_arquivo);
    },
    [
      job?.id,
      incluirTextoAnexoContextoFabNoPedidoTranscribrothers,
      processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers,
      pushToast,
    ],
  );

  const processarListaArquivosAnexoContextoFabTranscribrothers = useCallback(
    async (lista: File[]) => {
      if (!job?.id || lista.length === 0) return;
      setProcessandoArquivosAnexoContextoFab(true);
      try {
        for (const arquivo of lista) {
          try {
            await processarArquivoDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers(arquivo);
          } catch (e) {
            pushToast(
              e instanceof Error ? `${arquivo.name}: ${e.message}` : `${arquivo.name}: ${String(e)}`,
              "error",
            );
          }
        }
      } finally {
        setProcessandoArquivosAnexoContextoFab(false);
      }
    },
    [job?.id, processarArquivoDocumentoAnexoContextoFabProjetoEmBrancoTranscribrothers, pushToast],
  );

  const ajustarAlturaTextareaInstrucoesChatFabTranscribrothers = useCallback(() => {
    const el = refTextareaInstrucoesChatFabTranscribrothers.current;
    if (!el) return;
    const alturaMinimaPx = 72;
    const alturaMaximaPx = 280;
    el.style.height = "0px";
    const conteudoPx = el.scrollHeight;
    const altura = Math.min(Math.max(conteudoPx, alturaMinimaPx), alturaMaximaPx);
    el.style.height = `${altura}px`;
    el.style.overflowY = conteudoPx > alturaMaximaPx ? "auto" : "hidden";
  }, []);

  useEffect(() => {
    if (!painelRegeneracaoFabAberto || !jobEhProjetoEmBrancoTranscribrothers(job)) return;
    ajustarAlturaTextareaInstrucoesChatFabTranscribrothers();
  }, [
    instrucoesRegeneracaoTutorialMarkdown,
    painelRegeneracaoFabAberto,
    job,
    ajustarAlturaTextareaInstrucoesChatFabTranscribrothers,
  ]);

  const aoEntrarArrasteChatFabTranscribrothers = useCallback((evento: React.DragEvent) => {
    if (!jobEhProjetoEmBrancoTranscribrothers(job)) return;
    evento.preventDefault();
    evento.stopPropagation();
    contadorArrasteChatFabRef.current += 1;
    setArrastandoArquivosSobreChatFab(true);
  }, [job]);

  const aoSairArrasteChatFabTranscribrothers = useCallback((evento: React.DragEvent) => {
    if (!jobEhProjetoEmBrancoTranscribrothers(job)) return;
    evento.preventDefault();
    evento.stopPropagation();
    contadorArrasteChatFabRef.current = Math.max(0, contadorArrasteChatFabRef.current - 1);
    if (contadorArrasteChatFabRef.current === 0) {
      setArrastandoArquivosSobreChatFab(false);
    }
  }, [job]);

  const aoSoltarArquivosChatFabTranscribrothers = useCallback(
    (evento: React.DragEvent) => {
      if (!jobEhProjetoEmBrancoTranscribrothers(job)) return;
      evento.preventDefault();
      evento.stopPropagation();
      contadorArrasteChatFabRef.current = 0;
      setArrastandoArquivosSobreChatFab(false);
      const arquivos = Array.from(evento.dataTransfer.files ?? []);
      if (arquivos.length > 0) {
        void processarListaArquivosAnexoContextoFabTranscribrothers(arquivos);
      }
    },
    [job, processarListaArquivosAnexoContextoFabTranscribrothers],
  );

  const solicitarRegeneracaoSecaoMarkdownTutorialTranscribrothers = useCallback(
    async (opcoes?: { instrucoesTexto?: string; fecharPainelFab?: boolean }) => {
    if (!job) return;
    const inst = (opcoes?.instrucoesTexto ?? instrucoesRegeneracaoSecaoMarkdown).trim();
    const trecho = trechoAncoraEdicaoSecaoMarkdownForm.trim();
    const manual = escopoEdicaoSecaoManualAtivoForm;
    if (!inst) {
      pushToast("Descreva o que você quer melhorar.", "error");
      return;
    }
    if (manual && modoEscopoEdicaoSecaoMarkdownForm !== "secao_inteira" && !trecho) {
      pushToast("Cole o trecho do tutorial que define o escopo.", "error");
      return;
    }
    if (manual && modoEscopoEdicaoSecaoMarkdownForm === "secao_inteira" && !tituloSecaoSelecionadaParaEdicao.trim()) {
      pushToast("Escolha a seção «##» para reescrever por inteiro.", "error");
      return;
    }
    setErro(null);
    setRegenerandoSecaoMarkdownTutorial(true);
    try {
      const j = (await pedirRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(job.id, {
        tituloSecaoHeading: tituloSecaoSelecionadaParaEdicao.trim() || undefined,
        instrucoesRevisor: inst,
        litellmModel: modeloLitellm.trim() || undefined,
        modoEscopoEdicao: modoEscopoEdicaoSecaoMarkdownForm,
        trechoAncora: manual ? trecho || undefined : undefined,
        interpretarEscopoAutomaticamente: !manual,
        caminhosAssetsPngContextoFab: payloadContextoFabProjetoEmBrancoAtual.caminhos_assets_png_contexto_fab,
        textosContextoFab: payloadContextoFabProjetoEmBrancoAtual.textos_contexto_fab,
      })) as JobStatus;
      setJob(j);
      if (opcoes?.fecharPainelFab) {
        setPainelRegeneracaoFabAberto(false);
        setAnexosContextoFabProjetoEmBranco([]);
      }
      const interpretaEscopo = !manual;
      if (interpretaEscopo) {
        pushToast("Analisando o que você pediu no tutorial…", "success");
      } else {
        setModalProgressoJobAberto(true);
        pushToast("Edição pedida. Confira a pré-visualização antes de aplicar.", "success");
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErro(msg);
      pushToast(msg, "error");
    } finally {
      setRegenerandoSecaoMarkdownTutorial(false);
    }
    },
    [
      job,
      tituloSecaoSelecionadaParaEdicao,
      instrucoesRegeneracaoSecaoMarkdown,
      escopoEdicaoSecaoManualAtivoForm,
      modoEscopoEdicaoSecaoMarkdownForm,
      trechoAncoraEdicaoSecaoMarkdownForm,
      modeloLitellm,
      payloadContextoFabProjetoEmBrancoAtual,
      pushToast,
    ],
  );

  const tratarColarImagemNoPainelFabProjetoEmBrancoTranscribrothers = useCallback(
    (evento: React.ClipboardEvent) => {
      if (!jobEhProjetoEmBrancoTranscribrothers(job)) return;
      const itens = evento.clipboardData?.items;
      if (!itens?.length) return;
      for (let i = 0; i < itens.length; i += 1) {
        const item = itens[i];
        if (item.kind !== "file" || !item.type.startsWith("image/")) continue;
        const arquivo = item.getAsFile();
        if (!arquivo) continue;
        evento.preventDefault();
        void processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers(arquivo);
        return;
      }
    },
    [job, processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers],
  );

  const enviarPedidoPainelFabAtualizarTutorialTranscribrothers = useCallback(() => {
    if (modoPainelFabAtualizarTutorial === "edicao_parcial") {
      void solicitarRegeneracaoSecaoMarkdownTutorialTranscribrothers({
        instrucoesTexto: instrucoesRegeneracaoTutorialMarkdown,
        fecharPainelFab: true,
      });
      return;
    }
    if (jobEhReproducaoBugTranscribrothers(job)) {
      void solicitarRegeneracaoReproducaoBugMarkdownComTextoInstrucoesTranscribrothers(
        instrucoesRegeneracaoTutorialMarkdown,
        fabPresetRegeneracaoInteiraTranscribrothers === "sem_video",
      );
      return;
    }
    if (jobEhNotasPropostaFuncionalidadeTranscribrothers(job)) {
      void solicitarRegeneracaoNotasPropostaMarkdownComTextoInstrucoesTranscribrothers(
        instrucoesRegeneracaoTutorialMarkdown,
        fabPresetRegeneracaoInteiraTranscribrothers === "sem_video",
      );
      return;
    }
    if (
      jobEhProjetoEmBrancoTranscribrothers(job) &&
      fabPresetRegeneracaoInteiraTranscribrothers === "revisao_profunda"
    ) {
      pushToast("Revisão profunda não está disponível em projeto em branco.", "info");
      return;
    }
    void solicitarRegeneracaoTutorialMarkdownComTextoInstrucoesTranscribrothers(
      instrucoesRegeneracaoTutorialMarkdown,
      fabPresetRegeneracaoInteiraTranscribrothers === "revisao_profunda"
        ? { revisaoProfundaMultifase: true }
        : undefined,
    );
  }, [
    job,
    modoPainelFabAtualizarTutorial,
    instrucoesRegeneracaoTutorialMarkdown,
    fabPresetRegeneracaoInteiraTranscribrothers,
    solicitarRegeneracaoSecaoMarkdownTutorialTranscribrothers,
    solicitarRegeneracaoReproducaoBugMarkdownComTextoInstrucoesTranscribrothers,
    solicitarRegeneracaoNotasPropostaMarkdownComTextoInstrucoesTranscribrothers,
    solicitarRegeneracaoTutorialMarkdownComTextoInstrucoesTranscribrothers,
    pushToast,
  ]);

  const copiarTranscricaoOriginalParaClipboardTranscribrothers = useCallback(async () => {
    const t = textoPlanoTranscricaoOriginalSnapshotJob;
    if (!t) return;
    try {
      await navigator.clipboard.writeText(t);
      pushToast("Texto copiado para a área de transferência.", "success");
    } catch {
      pushToast("Não foi possível copiar (permissão do navegador ou contexto inseguro sem HTTPS).", "error");
    }
  }, [textoPlanoTranscricaoOriginalSnapshotJob, pushToast]);

  const baixarTranscricaoOriginalComoFicheiroTxtTranscribrothers = useCallback(() => {
    const t = textoPlanoTranscricaoOriginalSnapshotJob;
    if (!t || !job) return;
    const blob = new Blob([t], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `transcricao_original_transcribrothers_${job.id}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  }, [textoPlanoTranscricaoOriginalSnapshotJob, job]);

  const tituloModalStatusJob = useMemo(() => {
    if (!job) return "Status";
    if (jobEmExecucao) return "Processando";
    if (job.status === "failed") return "Não foi possível concluir";
    if (job.status === "cancelled") return "Cancelado";
    if (job.status === "completed") return "Concluído";
    return "Status";
  }, [job, jobEmExecucao]);

  const resumoErroModal = useMemo(() => {
    if (!job?.error_message) return "";
    const t = job.error_message.trim();
    if (t.length <= 400) return t;
    return `${t.slice(0, 400)}…`;
  }, [job?.error_message]);

  function adicionarNovoModeloLitellmNaConfiguracao() {
    const t = novoSlugModeloLitellm.trim();
    if (!t) return;
    const lista = adicionarModeloLitellmExtraAoArmazenamentoLocalNavegadorTranscribrothers(t);
    setModelosExtrasNavegador(lista);
    setModeloLitellm(t);
    setNovoSlugModeloLitellm("");
  }

  const copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers = useCallback(
    async (rotuloCurto: string, texto: string) => {
      try {
        await navigator.clipboard.writeText(texto);
        pushToast(`${rotuloCurto} copiado para a área de transferência.`, "success");
      } catch {
        pushToast("Não foi possível copiar (permissão do navegador ou contexto inseguro sem HTTPS).", "error");
      }
    },
    [pushToast],
  );

  async function salvarTranscricaoMultimodalRuntimePersistidoSqliteTranscribrothers() {
    setErroMmRuntime(null);
    const j = Number.parseInt(mmJanelaSegundosForm.trim(), 10);
    const p = Number.parseInt(mmParalelasForm.trim(), 10);
    if (!Number.isFinite(j) || j < 0 || j > 86400) {
      setErroMmRuntime("Janela: use um inteiro entre 0 e 86400 (segundos).");
      return;
    }
    if (!Number.isFinite(p) || p < 1 || p > 32) {
      setErroMmRuntime("Paralelismo: use um inteiro entre 1 e 32.");
      return;
    }
    const br = Number.parseInt(mmBitrateKbpsForm.trim(), 10);
    if (!Number.isFinite(br) || br < 16 || br > 320) {
      setErroMmRuntime("Bitrate: use um inteiro entre 16 e 320 (kbps).");
      return;
    }
    const margemLinks = Number.parseFloat(tutorialMargemLinksTemporaisForm.trim().replace(",", "."));
    if (!Number.isFinite(margemLinks) || margemLinks < 0.5 || margemLinks > 120) {
      setErroMmRuntime("Margem entre links temporais: use um número entre 0,5 e 120 (segundos).");
      return;
    }
    setSalvandoMmRuntime(true);
    try {
      const r = await fetch("/api/config/transcribrothers/transcricao-multimodal-runtime", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcricao_multimodal_janela_segundos: j,
          transcricao_multimodal_janelas_paralelas_maxima: p,
          transcricao_multimodal_formato_audio_inline: mmFormatoAudioForm,
          transcricao_multimodal_audio_bitrate_kbps: br,
          transcricao_multimodal_audio_mono: mmMonoForm,
          tutorial_margem_minima_segundos_entre_links_temporais_captura: margemLinks,
          tutorial_planejamento_instantes_captura_frames_litellm_habilitado:
            tutorialPlanejamentoCapturaLitellmForm,
        }),
      });
      if (!r.ok) {
        const texto = await r.text();
        throw new Error(texto || `Erro HTTP ${r.status}`);
      }
      const raw = (await r.json()) as Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>;
      setConfigApi(normalizarRespostaConfigPublicaTranscribrothersDaApi(raw));
    } catch (e) {
      setErroMmRuntime(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvandoMmRuntime(false);
    }
  }

  async function salvarVerificacaoSustentacaoTutorialRuntimePersistidoSqliteTranscribrothers() {
    setErroAuditorRuntimeSqlite(null);
    setSalvandoAuditorRuntimeSqlite(true);
    try {
      const r = await fetch("/api/config/transcribrothers/verificacao-sustentacao-tutorial-runtime", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          verificacao_sustentacao_tutorial_habilitada: auditorVerificacaoHabilitadoForm,
        }),
      });
      if (!r.ok) {
        const texto = await r.text();
        throw new Error(texto || `Erro HTTP ${r.status}`);
      }
      const raw = (await r.json()) as Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>;
      setConfigApi(normalizarRespostaConfigPublicaTranscribrothersDaApi(raw));
      pushToast("Preferência do Auditor gravada no servidor.", "success");
    } catch (e) {
      setErroAuditorRuntimeSqlite(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvandoAuditorRuntimeSqlite(false);
    }
  }

  async function salvarVerificacaoRedundanciaSecaoMarkdownRuntimePersistidoSqliteTranscribrothers() {
    setErroAuditorRedundanciaSecaoRuntimeSqlite(null);
    setSalvandoAuditorRedundanciaSecaoRuntimeSqlite(true);
    try {
      const r = await fetch("/api/config/transcribrothers/verificacao-redundancia-secao-markdown-runtime", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          verificacao_redundancia_secao_markdown_habilitada: auditorRedundanciaSecaoHabilitadoForm,
          verificacao_redundancia_secao_correcao_automatica_habilitada:
            correcaoAutomaticaRedundanciaSecaoHabilitadaForm,
          verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao:
            correcaoAutomaticaRedundanciaSecaoIncluirAtencaoForm,
        }),
      });
      if (!r.ok) {
        const texto = await r.text();
        throw new Error(texto || `Erro HTTP ${r.status}`);
      }
      const raw = (await r.json()) as Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>;
      setConfigApi(normalizarRespostaConfigPublicaTranscribrothersDaApi(raw));
      pushToast("Preferência do auditor de redundância (seção) gravada.", "success");
    } catch (e) {
      setErroAuditorRedundanciaSecaoRuntimeSqlite(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvandoAuditorRedundanciaSecaoRuntimeSqlite(false);
    }
  }

  async function limparPreferenciaVerificacaoRedundanciaSecaoMarkdownRuntimeSqliteTranscribrothers() {
    setErroAuditorRedundanciaSecaoRuntimeSqlite(null);
    setSalvandoAuditorRedundanciaSecaoRuntimeSqlite(true);
    try {
      const r = await fetch("/api/config/transcribrothers/verificacao-redundancia-secao-markdown-runtime", {
        method: "DELETE",
      });
      if (!r.ok) {
        const texto = await r.text();
        throw new Error(texto || `Erro HTTP ${r.status}`);
      }
      const raw = (await r.json()) as Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>;
      setConfigApi(normalizarRespostaConfigPublicaTranscribrothersDaApi(raw));
      pushToast(
        "Preferências de redundância restauradas: auditor volta ao .env; correção automática ao padrão do app.",
        "success",
      );
    } catch (e) {
      setErroAuditorRedundanciaSecaoRuntimeSqlite(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvandoAuditorRedundanciaSecaoRuntimeSqlite(false);
    }
  }

  async function limparPreferenciaVerificacaoSustentacaoTutorialRuntimeSqliteTranscribrothers() {
    setErroAuditorRuntimeSqlite(null);
    setSalvandoAuditorRuntimeSqlite(true);
    try {
      const r = await fetch("/api/config/transcribrothers/verificacao-sustentacao-tutorial-runtime", {
        method: "DELETE",
      });
      if (!r.ok) {
        const texto = await r.text();
        throw new Error(texto || `Erro HTTP ${r.status}`);
      }
      const raw = (await r.json()) as Partial<ConfigPublicaTranscribrothers> & Record<string, unknown>;
      setConfigApi(normalizarRespostaConfigPublicaTranscribrothersDaApi(raw));
      pushToast("Preferência do Auditor removida: volta a valer só o .env.", "success");
    } catch (e) {
      setErroAuditorRuntimeSqlite(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvandoAuditorRuntimeSqlite(false);
    }
  }

  const conteudoGavetaConfiguracoes = configApi ? (
    <>
      <h2 id="tb-drawer-titulo" className="tb-drawer-titulo">
        Configurações
      </h2>
      <div className="tb-drawer-leadin">
        <p className="tb-muted tb-drawer-intro-uma-linha">
          Modelo do tutorial neste navegador; o restante vem do servidor.
        </p>
        <details className="tb-drawer-micro-ajuda">
          <summary>Sobre</summary>
          <div className="tb-drawer-micro-ajuda-corpo">
            <p>
              O modelo LiteLLM escolhido para gerar o markdown fica guardado no navegador. Lista de modelos, TLS,
              limites de vídeo e parâmetros públicos vêm da API.
            </p>
          </div>
        </details>
      </div>

      <label className="tb-label tb-label-spaced" htmlFor="tb-drawer-modelo">
        Modelo (LiteLLM)
      </label>
      <select
        id="tb-drawer-modelo"
        className="tb-select"
        value={modelosParaSelectLiteLLM.includes(modeloLitellm) ? modeloLitellm : modelosParaSelectLiteLLM[0]}
        onChange={(e) => setModeloLitellm(e.target.value)}
      >
        {modelosParaSelectLiteLLM.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>

      <label className="tb-label tb-label-spaced" htmlFor="tb-drawer-novo-modelo">
        Adicionar modelo (salvo neste navegador)
      </label>
      <div className="tb-row tb-row-drawer-add">
        <input
          id="tb-drawer-novo-modelo"
          className="tb-input tb-input-inline"
          type="text"
          value={novoSlugModeloLitellm}
          onChange={(e) => setNovoSlugModeloLitellm(e.target.value)}
          placeholder="ex.: gemini/gemini-2.0-flash"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              adicionarNovoModeloLitellmNaConfiguracao();
            }
          }}
        />
        <button type="button" className="tb-linkbtn" onClick={adicionarNovoModeloLitellmNaConfiguracao}>
          Adicionar
        </button>
      </div>

      <div className="tb-drawer-secao-head">
        <h3 className="tb-drawer-subtitulo">Transcrição multimodal</h3>
        <details className="tb-drawer-micro-ajuda">
          <summary>Sobre</summary>
          <div className="tb-drawer-micro-ajuda-corpo">
            <p>
              Valores gravados no <strong>SQLite</strong> do servidor (tabela{" "}
              <code>runtime_config_valores_transcribrothers</code>) para <strong>novos jobs</strong>. Sem registro na
              base, usa-se o <code>backend/.env</code>.
            </p>
          </div>
        </details>
      </div>
      {configApi.transcricao_multimodal_overrides_runtime_sqlite_ativos ? (
        <p className="tb-drawer-badge-runtime-ativo">Há valores desta seção salvos na base (prevalecem sobre o .env).</p>
      ) : (
        <p className="tb-muted tb-drawer-dica-inline">Sem override na base — em uso o padrão do .env.</p>
      )}
      <label
        className="tb-label tb-label-spaced"
        htmlFor="tb-mm-janela-seg"
        title="0 = um único POST com o áudio inteiro. Valores maiores dividem o vídeo em trechos (segundos por trecho)."
      >
        Duração de cada trecho (segundos)
      </label>
      <input
        id="tb-mm-janela-seg"
        className="tb-input"
        type="number"
        min={0}
        max={86400}
        inputMode="numeric"
        value={mmJanelaSegundosForm}
        onChange={(e) => setMmJanelaSegundosForm(e.target.value)}
      />
      <p className="tb-muted tb-drawer-dica-inline">0 = um POST com o áudio inteiro · padrão: 30 s/trecho</p>
      <label className="tb-label tb-label-spaced" htmlFor="tb-mm-paralelas">
        Trechos em paralelo (máximo)
      </label>
      <input
        id="tb-mm-paralelas"
        className="tb-input"
        type="number"
        min={1}
        max={32}
        inputMode="numeric"
        value={mmParalelasForm}
        onChange={(e) => setMmParalelasForm(e.target.value)}
      />
      <details className="tb-drawer-micro-ajuda tb-drawer-micro-ajuda--campo">
        <summary>Paralelismo — quando vale a pena</summary>
        <div className="tb-drawer-micro-ajuda-corpo">
          <p>
            <strong>1</strong> = sequencial (um POST de cada vez). Valores maiores disparam vários pedidos ao LiteLLM ao
            mesmo tempo — isso <strong>não garante</strong> trechos mais rápidos: filas, rate limit ou um único slot
            compartilhado podem aumentar o tempo <em>por trecho</em>. Se notar lentidão, experimente <strong>1</strong>{" "}
            aqui.
          </p>
        </div>
      </details>
      <label
        className="tb-label tb-label-spaced"
        htmlFor="tb-mm-formato-audio"
        title="O gateway precisa aceitar o campo input_audio.format correspondente. WAV ignora o bitrate abaixo."
      >
        Formato enviado ao modelo (inline no JSON)
      </label>
      <select
        id="tb-mm-formato-audio"
        className="tb-select"
        value={mmFormatoAudioForm}
        onChange={(e) =>
          setMmFormatoAudioForm(normalizarFormatoAudioInlineMultimodalDaApiTranscribrothers(e.target.value))
        }
      >
        <option value="wav">WAV (PCM, maior payload)</option>
        <option value="mp3">MP3 (libmp3lame)</option>
        <option value="opus">Opus Ogg (libopus; costuma ser menor que MP3)</option>
        <option value="aac">AAC em M4A (codec aac no ffmpeg)</option>
      </select>
      <details className="tb-drawer-micro-ajuda tb-drawer-micro-ajuda--campo">
        <summary>Codec / ffmpeg no servidor</summary>
        <div className="tb-drawer-micro-ajuda-corpo">
          <p>
            WAV ignora bitrate. Opus, AAC e MP3 dependem dos codecs disponíveis no ffmpeg do servidor; confirme que o
            endpoint aceita o <code>input_audio.format</code> escolhido.
          </p>
        </div>
      </details>
      <label className="tb-label tb-label-spaced" htmlFor="tb-mm-bitrate-kbps">
        Bitrate (kbps) — mp3, opus e aac
      </label>
      <input
        id="tb-mm-bitrate-kbps"
        className="tb-input"
        type="number"
        min={16}
        max={320}
        inputMode="numeric"
        value={mmBitrateKbpsForm}
        onChange={(e) => setMmBitrateKbpsForm(e.target.value)}
      />
      <label
        className="tb-label tb-label-spaced tb-label-checkbox-mm-mono"
        title="Mono (1 canal) costuma gerar arquivos menores; desmarque para manter estéreo na extração/codificação."
      >
        <input
          type="checkbox"
          checked={mmMonoForm}
          onChange={(e) => setMmMonoForm(e.target.checked)}
        />{" "}
        Áudio mono (1 canal)
      </label>
      <label
        className="tb-label tb-label-spaced"
        htmlFor="tb-tutorial-margem-links-temporais"
        title="Links ?t= mais próximos que este intervalo são tratados como o mesmo instante na deduplicação antes da captura."
      >
        Margem mínima entre links temporais (segundos)
      </label>
      <input
        id="tb-tutorial-margem-links-temporais"
        className="tb-input"
        type="number"
        min={0.5}
        max={120}
        step={0.5}
        inputMode="decimal"
        value={tutorialMargemLinksTemporaisForm}
        onChange={(e) => setTutorialMargemLinksTemporaisForm(e.target.value)}
      />
      <p className="tb-muted tb-drawer-dica-inline">
        Padrão: 2 s — instantes `?t=` mais próximos que isso são fundidos antes do ffmpeg.
      </p>
      <label
        className="tb-label tb-label-spaced tb-label-checkbox-mm-mono"
        title="Com IA ligada, um passo LiteLLM escolhe quais candidatos do rascunho merecem screenshot antes do ffmpeg."
      >
        <input
          type="checkbox"
          checked={tutorialPlanejamentoCapturaLitellmForm}
          onChange={(e) => setTutorialPlanejamentoCapturaLitellmForm(e.target.checked)}
        />{" "}
        Planejar capturas com IA (antes do ffmpeg)
      </label>
      {erroMmRuntime ? <p className="tb-drawer-erro-mm">{erroMmRuntime}</p> : null}
      <div className="tb-row tb-drawer-row-salvar-mm">
        <button
          type="button"
          className="tb-btn-drawer-primario"
          disabled={salvandoMmRuntime}
          onClick={() => void salvarTranscricaoMultimodalRuntimePersistidoSqliteTranscribrothers()}
        >
          {salvandoMmRuntime ? "Salvando…" : "Salvar no servidor"}
        </button>
      </div>

      <div className="tb-drawer-secao-head">
        <h3 className="tb-drawer-subtitulo">Auditor</h3>
        <details className="tb-drawer-micro-ajuda">
          <summary>Sobre</summary>
          <div className="tb-drawer-micro-ajuda-corpo">
            <p>
              Verificação automática do tutorial face à transcrição. A preferência grava-se no <strong>SQLite</strong> e
              prevalece sobre o <code>backend/.env</code> enquanto existir. <strong>Voltar ao .env</strong> apaga o
              registro na base.
            </p>
          </div>
        </details>
      </div>
      {configApi.verificacao_sustentacao_tutorial_preferencia_sqlite_definida ? (
        <p className="tb-drawer-badge-runtime-ativo">Preferência na base ativa (sobrepõe o .env).</p>
      ) : (
        <p className="tb-muted tb-drawer-dica-inline">
          Sem preferência na base — segue o .env (
          {configApi.verificacao_sustentacao_tutorial_habilitada_padrao_env ? "ligado" : "desligado"}).
        </p>
      )}
      <label
        className="tb-label tb-label-spaced tb-label-checkbox-mm-mono"
        title={`Estado efetivo neste momento: ${configApi.verificacao_sustentacao_tutorial_habilitada_efetiva ? "ligado" : "desligado"}. Marque, salve, e novos jobs respeitam a preferência.`}
      >
        <input
          type="checkbox"
          checked={auditorVerificacaoHabilitadoForm}
          onChange={(e) => setAuditorVerificacaoHabilitadoForm(e.target.checked)}
        />{" "}
        Executar Auditor após gerar o tutorial
      </label>
      <p className="tb-muted tb-drawer-dica-inline">
        Efetivo agora:{" "}
        <strong>{configApi.verificacao_sustentacao_tutorial_habilitada_efetiva ? "ligado" : "desligado"}</strong>
      </p>
      {erroAuditorRuntimeSqlite ? <p className="tb-drawer-erro-mm">{erroAuditorRuntimeSqlite}</p> : null}
      <div className="tb-drawer-row-salvar-mm tb-drawer-row-salvar-auditor">
        <button
          type="button"
          className="tb-btn-drawer-primario"
          disabled={salvandoAuditorRuntimeSqlite}
          onClick={() => void salvarVerificacaoSustentacaoTutorialRuntimePersistidoSqliteTranscribrothers()}
        >
          {salvandoAuditorRuntimeSqlite ? "Salvando…" : "Salvar preferência no servidor"}
        </button>
        <button
          type="button"
          className="tb-btn-drawer-secundario"
          disabled={salvandoAuditorRuntimeSqlite || !configApi.verificacao_sustentacao_tutorial_preferencia_sqlite_definida}
          onClick={() => void limparPreferenciaVerificacaoSustentacaoTutorialRuntimeSqliteTranscribrothers()}
          title={
            configApi.verificacao_sustentacao_tutorial_preferencia_sqlite_definida
              ? "Remove o registro na base e volta ao comportamento definido só pelo .env"
              : "Não há preferência gravada na base para remover"
          }
        >
          Voltar ao .env
        </button>
      </div>

      <hr className="tb-drawer-sep" />
      <div className="tb-drawer-secao-head tb-drawer-secao-head--apos-sep">
        <h3 className="tb-drawer-subtitulo">Redundância (edição por seção)</h3>
      </div>
      <p className="tb-muted tb-drawer-dica">
        Compara a seção regenerada com as outras seções <code>##</code> do tutorial (só na edição por seção).
      </p>
      <label className="tb-drawer-checkbox">
        <input
          type="checkbox"
          checked={auditorRedundanciaSecaoHabilitadoForm}
          onChange={(e) => setAuditorRedundanciaSecaoHabilitadoForm(e.target.checked)}
        />{" "}
        Executar verificação de redundância
      </label>
      <p className="tb-muted tb-drawer-dica-inline">
        Verificação efetiva:{" "}
        <strong>
          {configApi.verificacao_redundancia_secao_markdown_habilitada_efetiva ? "ligada" : "desligada"}
        </strong>
      </p>
      <label className="tb-drawer-checkbox">
        <input
          type="checkbox"
          checked={correcaoAutomaticaRedundanciaSecaoHabilitadaForm}
          disabled={!auditorRedundanciaSecaoHabilitadoForm}
          onChange={(e) => setCorrecaoAutomaticaRedundanciaSecaoHabilitadaForm(e.target.checked)}
        />{" "}
        Corrigir automaticamente quando houver redundância
      </label>
      <label className="tb-drawer-checkbox">
        <input
          type="checkbox"
          checked={correcaoAutomaticaRedundanciaSecaoIncluirAtencaoForm}
          disabled={
            !auditorRedundanciaSecaoHabilitadoForm || !correcaoAutomaticaRedundanciaSecaoHabilitadaForm
          }
          onChange={(e) => setCorrecaoAutomaticaRedundanciaSecaoIncluirAtencaoForm(e.target.checked)}
        />{" "}
        Corrigir também em classificação «atenção» (não só «redundância»)
      </label>
      <p className="tb-muted tb-drawer-dica-inline">
        Correção automática efetiva:{" "}
        <strong>
          {configApi.verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva
            ? "ligada"
            : "desligada"}
        </strong>
        {configApi.verificacao_redundancia_secao_correcao_automatica_habilitada_efetiva
          ? configApi.verificacao_redundancia_secao_correcao_automatica_incluir_classificacao_atencao_efetiva
            ? " (inclui atenção)"
            : " (só redundância)"
          : null}
      </p>
      {erroAuditorRedundanciaSecaoRuntimeSqlite ? (
        <p className="tb-drawer-erro-mm">{erroAuditorRedundanciaSecaoRuntimeSqlite}</p>
      ) : null}
      <div className="tb-drawer-row-salvar-mm">
        <button
          type="button"
          className="tb-btn-drawer-primario"
          disabled={salvandoAuditorRedundanciaSecaoRuntimeSqlite}
          onClick={() => void salvarVerificacaoRedundanciaSecaoMarkdownRuntimePersistidoSqliteTranscribrothers()}
        >
          {salvandoAuditorRedundanciaSecaoRuntimeSqlite ? "Salvando…" : "Salvar"}
        </button>
        <button
          type="button"
          className="tb-btn-drawer-secundario"
          disabled={salvandoAuditorRedundanciaSecaoRuntimeSqlite}
          onClick={() => void limparPreferenciaVerificacaoRedundanciaSecaoMarkdownRuntimeSqliteTranscribrothers()}
        >
          Restaurar padrões
        </button>
      </div>
      <hr className="tb-drawer-sep" />
      <div className="tb-drawer-secao-head tb-drawer-secao-head--apos-sep">
        <h3 className="tb-drawer-subtitulo">Prompts fixos</h3>
        <details className="tb-drawer-micro-ajuda">
          <summary>Sobre</summary>
          <div className="tb-drawer-micro-ajuda-corpo">
            <p>
              A barra da modal segue o fluxo do job. <strong>Pipeline inicial</strong> (upload): Preparação → Rascunho
              (se captura sob demanda) → Plano capturas (se planejamento LiteLLM) → Capturas → Gerador → Imagens →
              Auditor. <strong>Regeneração</strong>: Gerador → Imagens → Auditor. <strong>Revisão profunda</strong>:
              Planejador → Editores → Consolidador → Imagens → Auditor. Só entradas com texto fixo no código mostram{" "}
              <strong>Copiar</strong>
              ; as outras descrevem onde configurar (modelos, .env, instrução na página).
            </p>
          </div>
        </details>
      </div>
      {carregandoPromptsFixosRevisaoEVerificacaoTutorial ? (
        <p className="tb-muted">Carregando prompts do servidor…</p>
      ) : erroCarregarPromptsFixosRevisaoEVerificacaoTutorial ? (
        <p className="tb-drawer-erro-mm">{erroCarregarPromptsFixosRevisaoEVerificacaoTutorial}</p>
      ) : promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers ? (
        <>
          <p className="tb-muted tb-drawer-texto-compacto">
            Build:{" "}
            <code className="tb-code-inline">
              {promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.pipeline_identificador || "—"}
            </code>
          </p>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Preparação — sem prompt fixo nesta lista</summary>
            <p className="tb-muted tb-drawer-texto-compacto tb-drawer-prompt-fixo-somente-texto">
              Download, FFmpeg, transcrição e capturas usam modelos e parâmetros do servidor (por exemplo{" "}
              <code>transcricao_backend</code>, janelas multimodais, limites de screenshots). Não há um único arquivo
              «system» editável aqui — corresponde ao primeiro bloco da pipeline, antes do texto do tutorial.
            </p>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Gerador — instrução opcional na UI (não listada como fixo)</summary>
            <p className="tb-muted tb-drawer-texto-compacto tb-drawer-prompt-fixo-somente-texto">
              O passe único que gera o Markdown (ou a regeneração simples) usa o prefixo opcional que você pode editar no
              formulário («instrução / prefixo» para o tutorial). Isso não é o mesmo que os blocos fixos de revisão
              profunda abaixo; na pipeline aparece como segundo passo quando aplicável.
            </p>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Planejador — analista, plano JSON (system)</summary>
            <div className="tb-drawer-prompt-fixo-acoes">
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() =>
                  void copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers(
                    "Planejador (analista)",
                    promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_analista_plano_tutorial,
                  )
                }
              >
                Copiar
              </button>
            </div>
            <pre className="tb-drawer-prompt-fixo-pre" tabIndex={0}>
              {promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_analista_plano_tutorial}
            </pre>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Editores — um passe por tópico (system)</summary>
            <div className="tb-drawer-prompt-fixo-acoes">
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() =>
                  void copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers(
                    "Editores (worker)",
                    promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_worker_item_plano_tutorial,
                  )
                }
              >
                Copiar
              </button>
            </div>
            <pre className="tb-drawer-prompt-fixo-pre" tabIndex={0}>
              {promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_worker_item_plano_tutorial}
            </pre>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Consolidador — resumo do plano para o modelo (system)</summary>
            <div className="tb-drawer-prompt-fixo-acoes">
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() =>
                  void copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers(
                    "Consolidador (resumo plano)",
                    promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_resumo_plano_para_editor_final,
                  )
                }
              >
                Copiar
              </button>
            </div>
            <pre className="tb-drawer-prompt-fixo-pre" tabIndex={0}>
              {promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_revisao_profunda_resumo_plano_para_editor_final}
            </pre>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">
              Consolidador — instrução na mensagem user (consolidação final)
            </summary>
            <div className="tb-drawer-prompt-fixo-acoes">
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() =>
                  void copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers(
                    "Consolidador (instrução user)",
                    promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.instrucao_editor_final_revisao_profunda_consolidacao_markdown,
                  )
                }
              >
                Copiar
              </button>
            </div>
            <pre className="tb-drawer-prompt-fixo-pre" tabIndex={0}>
              {
                promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.instrucao_editor_final_revisao_profunda_consolidacao_markdown
              }
            </pre>
          </details>
          <details className="tb-drawer-prompt-fixo-details">
            <summary className="tb-drawer-prompt-fixo-summary">Auditor — verificação tutorial vs transcrição (system)</summary>
            <div className="tb-drawer-prompt-fixo-acoes">
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() =>
                  void copiarTextoPromptFixoServidorParaClipboardComToastTranscribrothers(
                    "Auditor (verificação)",
                    promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers
                      .system_verificacao_sustentacao_tutorial_markdown_vs_transcricao,
                  )
                }
              >
                Copiar
              </button>
            </div>
            <pre className="tb-drawer-prompt-fixo-pre" tabIndex={0}>
              {promptsFixosRevisaoEVerificacaoTutorialApiTranscribrothers.system_verificacao_sustentacao_tutorial_markdown_vs_transcricao}
            </pre>
          </details>
        </>
      ) : null}

      <hr className="tb-drawer-sep" />
      <h3 className="tb-drawer-subtitulo">Servidor (somente leitura)</h3>
      <ul className="tb-drawer-lista-servidor">
        <li>
          Proxy LiteLLM: <strong>{configApi.litellm_usa_endpoint_customizado ? "ativo" : "não detectado"}</strong>
        </li>
        <li>
          TLS: verificação <strong>{configApi.litellm_http_verify_ssl ? "ativada" : "desativada"}</strong>
          {configApi.litellm_ssl_ca_bundle_configurado ? "; CA customizada" : null}
        </li>
        <li>
          Transcrição: <code>{configApi.transcricao_backend}</code>
          {configApi.transcricao_modelo_multimodal_padrao ? (
            <>
              {" "}
              (multimodal padrão: <code>{configApi.transcricao_modelo_multimodal_padrao}</code>)
            </>
          ) : null}
        </li>
        <li>
          Screenshots: máx.{" "}
          <strong>
            {configApi.tutorial_max_frames_total > 0
              ? `${configApi.tutorial_max_frames_total} por job`
              : "só limite por minuto"}
          </strong>
          ; largura PNG{" "}
          <strong>
            {configApi.tutorial_frame_max_width_px > 0
              ? `${configApi.tutorial_frame_max_width_px}px`
              : "original"}
          </strong>
        </li>
      </ul>
      <p className="tb-muted tb-drawer-rodape">
        TLS, whitelist de modelos no select e limites de screenshots continuam no <code>backend/.env</code> com reinício do
        servidor.
      </p>
    </>
  ) : (
    <p className="tb-muted">Carregando configuração do servidor…</p>
  );

  const conteudoModalTranscricaoOriginal =
    job && textoPlanoTranscricaoOriginalSnapshotJob ? (
      <div
        className="tb-modal-job tb-modal-transcricao-shell"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tb-modal-transcricao-titulo"
      >
        <h2 id="tb-modal-transcricao-titulo" className="tb-modal-job-titulo">
          Transcrição original (snapshot)
        </h2>
        <p className="tb-modal-job-id">
          <span className="tb-muted">Job</span> <code className="tb-code-inline">{job.id}</code>
        </p>
        <p className="tb-muted tb-modal-transcricao-explicacao">
          Base usada para o tutorial: segmentos com tempos e, quando houver, bloco de texto corrido.
        </p>
        <div className="tb-modal-transcricao-acoes">
          <button
            type="button"
            className="tb-linkbtn"
            onClick={() => void copiarTranscricaoOriginalParaClipboardTranscribrothers()}
          >
            Copiar
          </button>
          <button
            type="button"
            className="tb-linkbtn"
            onClick={baixarTranscricaoOriginalComoFicheiroTxtTranscribrothers}
          >
            Baixar .txt
          </button>
        </div>
        <pre className="tb-modal-transcricao-pre" tabIndex={0}>
          {textoPlanoTranscricaoOriginalSnapshotJob}
        </pre>
        <div className="tb-modal-job-acoes-finais">
          <button type="button" className="tb-primary" onClick={() => setModalTranscricaoOriginalAberta(false)}>
            Fechar
          </button>
        </div>
      </div>
    ) : null;

  const conteudoModalProgressoJob =
    job === null ? null : (
      <div className="tb-modal-job tb-modal-job-status" role="dialog" aria-modal="true" aria-labelledby="tb-modal-job-titulo">
        <div className="tb-modal-job-corpo">
        <h2 id="tb-modal-job-titulo" className="tb-modal-job-titulo">
          {tituloModalStatusJob}
        </h2>
        <p className="tb-modal-job-id">
          <span className="tb-muted">ID</span> <code className="tb-code-inline">{job.id}</code>
        </p>
        <div className="tb-modal-status-card">
          <p className="tb-progresso-legivel tb-modal-andamento">{rotuloProgressoLegivel}</p>
          {linhaDetalheProgressoJob ? (
            <p className="tb-modal-andamento-detalhe tb-muted">{linhaDetalheProgressoJob}</p>
          ) : null}
          {jobEmExecucao ? (
            <div className="tb-modal-progress-indeterminate" aria-hidden="true">
              <div className="tb-modal-progress-bar" />
            </div>
          ) : null}
          {contextoPipelineHorizontalModalStatusJob ? (
            <div
              className="tb-pipeline-status-horizontal"
              role="group"
              aria-label={`${contextoPipelineHorizontalModalStatusJob.tituloFluxo}. Visão em passos da pipeline deste job.`}
            >
              <p className="tb-pipeline-status-fluxo-titulo">{contextoPipelineHorizontalModalStatusJob.tituloFluxo}</p>
              <p className="tb-pipeline-status-fluxo-descricao tb-muted">
                {contextoPipelineHorizontalModalStatusJob.descricaoFluxo}
              </p>
              {contextoPipelineHorizontalModalStatusJob.passos.length > 0 ? (
                <>
              <p className="tb-pipeline-status-horizontal-legenda tb-muted">
                Clique em um passo para abrir a descrição abaixo. Tab e Enter também funcionam.
              </p>
              <div
                className={`tb-pipeline-status-horizontal-linha${contextoPipelineHorizontalModalStatusJob.passos.length > 6 ? " tb-pipeline-status-horizontal-linha--compacta" : ""}`}
              >
                {contextoPipelineHorizontalModalStatusJob.passos.map((p, indice) => {
                  const aberto = passoPipelineModalStatusComPainelDescricaoAbertoId === p.id;
                  return (
                    <div key={p.id} className="tb-pipeline-status-segmento">
                      {indice > 0 ? <span className="tb-pipeline-status-connector" aria-hidden /> : null}
                      <button
                        type="button"
                        className={`tb-pipeline-status-step tb-pipeline-status-step--${p.estado}`}
                        aria-expanded={aberto}
                        aria-controls={`tb-pipeline-hint-painel-${job.id}`}
                        aria-label={
                          aberto
                            ? `${p.rotuloCurto}, descrição aberta abaixo`
                            : `${p.rotuloCurto}, clique para ver a descrição completa`
                        }
                        onClick={() => {
                          if (p.id === "preview_documento" && p.estado === "active") {
                            setModalPreviewRegeneracaoTutorialAberto(true);
                            setPassoPipelineModalStatusComPainelDescricaoAbertoId(null);
                            return;
                          }
                          if (p.id === "preview_secao" && p.estado === "active") {
                            setModalPreviewRegeneracaoSecaoAberto(true);
                            setPassoPipelineModalStatusComPainelDescricaoAbertoId(null);
                            return;
                          }
                          setPassoPipelineModalStatusComPainelDescricaoAbertoId((atual) =>
                            atual === p.id ? null : p.id,
                          );
                        }}
                      >
                        {p.rotuloCurto}
                      </button>
                    </div>
                  );
                })}
              </div>
              {passoPipelineModalStatusComPainelDescricaoAbertoId ? (
                <div
                  id={`tb-pipeline-hint-painel-${job.id}`}
                  className="tb-pipeline-status-hint-painel"
                  role="region"
                  aria-live="polite"
                >
                  {(() => {
                    const fasePipeline =
                      typeof job.steps_json?.pipeline_fase === "string" ? job.steps_json.pipeline_fase : "";
                    const passoSel = contextoPipelineHorizontalModalStatusJob.passos.find(
                      (x) => x.id === passoPipelineModalStatusComPainelDescricaoAbertoId,
                    );
                    if (!passoSel) return null;
                    const corpo = montarTextoHintExibicaoPainelPassoPipelineModalStatusTranscribrothers(
                      passoSel,
                      fasePipeline,
                      linhaDetalheProgressoJob,
                    );
                    return (
                      <>
                        <div className="tb-pipeline-status-hint-painel-topo">
                          <strong className="tb-pipeline-status-hint-painel-titulo">{passoSel.rotuloCurto}</strong>
                          <button
                            type="button"
                            className="tb-pipeline-status-hint-painel-fechar"
                            aria-label="Fechar descrição do passo"
                            onClick={() => setPassoPipelineModalStatusComPainelDescricaoAbertoId(null)}
                          >
                            ×
                          </button>
                        </div>
                        <p className="tb-pipeline-status-hint-painel-corpo">{corpo}</p>
                      </>
                    );
                  })()}
                </div>
              ) : null}
                </>
              ) : (
                <p className="tb-pipeline-status-sem-passos-horizontais tb-muted">
                  Esta execução não usa a barra de passos horizontais; acompanhe o preview no editor do tutorial, se
                  houver proposta pendente.
                </p>
              )}
            </div>
          ) : null}
        </div>
        {mensagemRetomadaTranscricaoMultimodal ? (
          <p className="tb-modal-aviso-retomada-transcricao-multimodal">{mensagemRetomadaTranscricaoMultimodal}</p>
        ) : null}
        {(job.status === "failed" || job.status === "cancelled") && trechosCheckpointSalvosParaRetomada > 0 ? (
          <p className="tb-modal-dica-retomada-apos-falha-transcricao">
            Há <strong>{trechosCheckpointSalvosParaRetomada}</strong> trecho(s) de transcrição já salvos neste job.
            Use <strong>Tentar de novo</strong> para continuar: o servidor reutiliza vídeo/áudio já extraídos e só
            refaz os trechos de transcrição que faltam (checkpoint), desde que janela/modelo/formato de áudio
            continuem compatíveis.
          </p>
        ) : null}
        {registrosTempoInferenciaTranscricaoPorTrecho.length > 0 ? (
          <details
            className="tb-modal-tempos-transcricao-por-trecho tb-modal-tempos-transcricao-por-trecho-details"
            defaultOpen={transcricaoInferenciaPorTrechoAindaEmCurso}
          >
            <summary className="tb-modal-tempos-transcricao-por-trecho-summary">
              Tempo por trecho de transcrição (inferência no modelo)
              <span className="tb-modal-tempos-transcricao-por-trecho-summary-meta">
                {" "}
                ({registrosTempoInferenciaTranscricaoPorTrecho.length} trecho
                {registrosTempoInferenciaTranscricaoPorTrecho.length === 1 ? "" : "s"})
              </span>
            </summary>
            <ul className="tb-modal-tempos-transcricao-por-trecho-lista">
              {registrosTempoInferenciaTranscricaoPorTrecho.map((r) => (
                <li key={r.indice}>
                  Trecho {r.indice}
                  <span className="tb-muted">
                    {" "}
                    ({formatarSegundosComoMmSsTranscribrothers(r.inicio_segundos)}–
                    {formatarSegundosComoMmSsTranscribrothers(r.fim_segundos)} no vídeo)
                  </span>
                  :{" "}
                  <strong>
                    {formatarSegundosComoMmSsTranscribrothers(
                      Math.round(Math.max(0, r.duracao_inferencia_segundos)),
                    )}
                  </strong>
                </li>
              ))}
            </ul>
            <p className="tb-modal-tempos-transcricao-por-trecho-total">
              Total (soma dos trechos acima):{" "}
              <strong>
                {formatarSegundosComoMmSsTranscribrothers(
                  Math.round(segundosTotaisInferenciaTranscricaoTrechosListados),
                )}
              </strong>
            </p>
          </details>
        ) : null}
        {entradasLogDecisoesIaModalStatusJob.length > 0 ? (
          <details className="tb-modal-log-decisoes-ia tb-modal-log-decisoes-ia-details">
            <summary className="tb-modal-log-decisoes-ia-summary">
              Log das decisões da IA
              <span className="tb-modal-log-decisoes-ia-summary-meta">
                {" "}
                ({entradasLogDecisoesIaModalStatusJob.length}{" "}
                {entradasLogDecisoesIaModalStatusJob.length === 1 ? "entrada" : "entradas"})
              </span>
            </summary>
            <p className="tb-muted tb-modal-log-decisoes-ia-legenda">
              Respostas e decisões registradas durante este job (mais recentes por último). Expanda uma entrada para
              ver o trecho completo quando disponível.
            </p>
            <ol className="tb-modal-log-decisoes-ia-lista">
              {entradasLogDecisoesIaModalStatusJob.map((entrada, idx) => {
                const quando = formatarDataHoraLogDecisoesIaParaExibicaoTranscribrothers(entrada.em);
                const rotuloEtapa = rotuloEtapaLogDecisoesIaEmPtBrTranscribrothers(entrada.etapa);
                return (
                  <li
                    key={`${entrada.em}-${entrada.etapa}-${idx}`}
                    className={
                      entrada.sucesso
                        ? "tb-modal-log-decisoes-ia-item"
                        : "tb-modal-log-decisoes-ia-item tb-modal-log-decisoes-ia-item--erro"
                    }
                  >
                    <div className="tb-modal-log-decisoes-ia-cabeca">
                      <span className="tb-modal-log-decisoes-ia-etapa">{rotuloEtapa}</span>
                      {quando ? <span className="tb-muted tb-modal-log-decisoes-ia-quando">{quando}</span> : null}
                      {entrada.modelo ? (
                        <span className="tb-muted tb-modal-log-decisoes-ia-modelo">
                          {" "}
                          · {entrada.modelo}
                        </span>
                      ) : null}
                      {!entrada.sucesso ? (
                        <span className="tb-modal-log-decisoes-ia-badge-erro"> falhou</span>
                      ) : null}
                    </div>
                    <p className="tb-modal-log-decisoes-ia-resumo">{entrada.resumo}</p>
                    {entrada.detalhe ? (
                      <details className="tb-modal-log-decisoes-ia-detalhe-details">
                        <summary className="tb-modal-log-decisoes-ia-detalhe-summary">Ver resposta / detalhe</summary>
                        <pre className="tb-modal-log-decisoes-ia-detalhe-pre" tabIndex={0}>
                          {entrada.detalhe}
                        </pre>
                      </details>
                    ) : null}
                    {entrada.metadados && Object.keys(entrada.metadados).length > 0 ? (
                      <p className="tb-muted tb-modal-log-decisoes-ia-metadados">
                        {Object.entries(entrada.metadados)
                          .filter(([k]) => k !== "legado")
                          .map(([k, v]) => `${k}: ${String(v)}`)
                          .join(" · ")}
                      </p>
                    ) : null}
                  </li>
                );
              })}
            </ol>
          </details>
        ) : null}
        {temPlanoRevisaoProfundaNoJobParaModalStatusTranscribrothers ? (
          <details
            className="tb-modal-plano-revisao-profunda"
            defaultOpen
            key={`plano-revisao-profunda-${job.id}`}
          >
            <summary className="tb-modal-plano-revisao-profunda-summary">
              Plano do planejador (revisão profunda)
            </summary>
            <div className="tb-modal-plano-amigavel-wrap">
              {topicosPlanoRevisaoProfundaVistaAmigavelModalTranscribrothers &&
              topicosPlanoRevisaoProfundaVistaAmigavelModalTranscribrothers.length > 0 ? (
                <ol className="tb-modal-plano-amigavel-lista-topic">
                  {topicosPlanoRevisaoProfundaVistaAmigavelModalTranscribrothers.map((t) => (
                    <li key={t.id} className="tb-modal-plano-amigavel-item-topico">
                      <div className="tb-modal-plano-amigavel-topico-cabeca">
                        <strong>{t.titulo_secao}</strong>
                        {t.prioridade != null ? (
                          <span className="tb-muted"> — prioridade {t.prioridade}</span>
                        ) : null}
                        <span className="tb-muted">
                          {" "}
                          (<code>{t.id}</code>)
                        </span>
                      </div>
                      {t.lacunas.length > 0 ? (
                        <div className="tb-modal-plano-amigavel-bloco-lacunas">
                          <span className="tb-modal-plano-amigavel-rotulo-bloco">Lacunas</span>
                          <ul className="tb-modal-plano-amigavel-ul-lacunas">
                            {t.lacunas.map((lac, i) => (
                              <li key={i}>{lac}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null}
                      {t.evidencias.length > 0 ? (
                        <div className="tb-modal-plano-amigavel-bloco-evidencias">
                          <span className="tb-modal-plano-amigavel-rotulo-bloco">Evidências na transcrição</span>
                          <ul className="tb-modal-plano-amigavel-ul-evidencias">
                            {t.evidencias.map((ev, i) => (
                              <li key={i}>
                                <q className="tb-modal-plano-amigavel-citacao">{ev.citacao}</q>
                                {ev.inicio_segundos != null || ev.fim_segundos != null ? (
                                  <span className="tb-muted">
                                    {" "}
                                    (
                                    {ev.inicio_segundos != null && ev.fim_segundos != null ? (
                                      <>
                                        {formatarSegundosComoMmSsTranscribrothers(Math.round(ev.inicio_segundos))}
                                        {" "}
                                        – {formatarSegundosComoMmSsTranscribrothers(Math.round(ev.fim_segundos))}
                                      </>
                                    ) : (
                                      formatarSegundosComoMmSsTranscribrothers(
                                        Math.round(ev.inicio_segundos ?? ev.fim_segundos ?? 0),
                                      )
                                    )}{" "}
                                    no vídeo)
                                  </span>
                                ) : null}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ) : null}
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="tb-muted tb-modal-plano-amigavel-sem-topic">
                  Não foi possível listar tópicos deste plano (formato diferente ou JSON inválido). Abra o JSON abaixo
                  para ver o conteúdo bruto.
                </p>
              )}
            </div>
            {textoPlanoRevisaoProfundaFormatadoParaModalTranscribrothers ? (
              <details className="tb-modal-plano-json-inner-details">
                <summary className="tb-modal-plano-json-inner-summary">Ver JSON completo do plano</summary>
                <pre className="tb-modal-plano-revisao-profunda-pre" tabIndex={0}>
                  {textoPlanoRevisaoProfundaFormatadoParaModalTranscribrothers}
                </pre>
              </details>
            ) : null}
          </details>
        ) : null}
        {dadosVerificacaoSustentacaoTutorialMarkdownDoJob ? (
          <details
            className="tb-modal-verificacao-sustentacao-tutorial"
            defaultOpen={
              (job.status === "completed" || job.status === "failed") &&
              !dadosVerificacaoSustentacaoTutorialMarkdownDoJob.omitida &&
              dadosVerificacaoSustentacaoTutorialMarkdownDoJob.sucesso !== false
            }
          >
            <summary className="tb-modal-verificacao-sustentacao-tutorial-summary">
              Auditor — verificação automática (tutorial vs transcrição)
              {dadosVerificacaoSustentacaoTutorialMarkdownDoJob.omitida ? (
                <span className="tb-muted"> — omitida</span>
              ) : dadosVerificacaoSustentacaoTutorialMarkdownDoJob.sucesso === false ? (
                <span className="tb-muted"> — falhou a verificação</span>
              ) : typeof dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global === "string" ? (
                <span className="tb-muted">
                  {" "}
                  —{" "}
                  <strong>{dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global}</strong>
                </span>
              ) : null}
            </summary>
            {dadosVerificacaoSustentacaoTutorialMarkdownDoJob.omitida ? (
              <p className="tb-muted">
                Etapa omitida:{" "}
                {descreverMotivoAuditorOmitidoEmPtBrTranscribrothers(
                  dadosVerificacaoSustentacaoTutorialMarkdownDoJob.motivo,
                )}
              </p>
            ) : dadosVerificacaoSustentacaoTutorialMarkdownDoJob.sucesso === false ? (
              <pre className="tb-pre tb-pre-modal tb-pre-verificacao-erro">
                {String(dadosVerificacaoSustentacaoTutorialMarkdownDoJob.erro ?? "Erro desconhecido.")}
              </pre>
            ) : (
              <>
                <p className="tb-modal-verificacao-resumo">
                  {dadosVerificacaoSustentacaoTutorialMarkdownDoJob.mensagem_resumo ?? ""}
                </p>
                {Array.isArray(dadosVerificacaoSustentacaoTutorialMarkdownDoJob.itens) &&
                dadosVerificacaoSustentacaoTutorialMarkdownDoJob.itens.length > 0 ? (
                  <ul className="tb-modal-verificacao-itens">
                    {dadosVerificacaoSustentacaoTutorialMarkdownDoJob.itens.map((it, idx) => (
                      <li key={idx}>
                        <code>{it.classificacao ?? "?"}</code> — {it.trecho_ou_tema ?? ""}
                        {it.justificativa_curta ? (
                          <>
                            <br />
                            <span className="tb-muted">{it.justificativa_curta}</span>
                          </>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="tb-muted">Nenhum ponto destacado pelo verificador.</p>
                )}
              </>
            )}
          </details>
        ) : null}
        <p className="tb-muted tb-modal-origem">
          Origem: <strong>{job.source_kind ?? "drive"}</strong>
        </p>

        {job.error_message ? (
          <div className="tb-modal-erro-resumo">
            <p className="tb-modal-erro-titulo">Mensagem</p>
            <pre className="tb-err tb-err-modal-compact">{resumoErroModal}</pre>
          </div>
        ) : null}

        <details className="tb-modal-detalhes tb-modal-detalhes-suporte">
          <summary>Detalhes para suporte (técnico)</summary>
          {typeof job.steps_json?.pipeline_fase === "string" ? (
            <p className="tb-modal-fase-linha">
              Fase: <code>{job.steps_json.pipeline_fase}</code>
            </p>
          ) : null}
          {job.status === "failed" && typeof job.steps_json?.error_traceback === "string" ? (
            <pre className="tb-pre tb-pre-modal">{String(job.steps_json.error_traceback)}</pre>
          ) : null}
          <pre className="tb-pre tb-pre-modal">{JSON.stringify(job.steps_json, null, 2)}</pre>
        </details>
        </div>

        <footer className="tb-modal-job-rodape">
          <div className="tb-row tb-row-status-actions">
            {jobPodeSerCancelado ? (
              <button
                type="button"
                className="tb-btn-cancel"
                onClick={() => {
                  setErro(null);
                  void (async () => {
                    try {
                      const j = await solicitarCancelamentoJobPipelineTranscribrothers(job.id);
                      setJob(j);
                      pushToast("Pedido de cancelamento enviado. O job deve parar em breve.", "success");
                    } catch (e) {
                      const msg = e instanceof Error ? e.message : String(e);
                      setErro(msg);
                      pushToast(msg, "error");
                    }
                  })();
                }}
              >
                Cancelar job
              </button>
            ) : null}
            {jobPodeRepetirPipeline ? (
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() => {
                  setErro(null);
                  void (async () => {
                    try {
                      const j = await repetirJobPipelineAposFalhaOuCancelamentoTranscribrothers(job.id);
                      setJob(j);
                      setModalProgressoJobAberto(true);
                    } catch (e) {
                      setErro(e instanceof Error ? e.message : String(e));
                    }
                  })();
                }}
              >
                Tentar de novo
              </button>
            ) : null}
          </div>
          <div className="tb-modal-job-acoes-finais">
            {jobEmExecucao ? (
              <button type="button" className="tb-linkbtn" onClick={() => setModalProgressoJobAberto(false)}>
                Continuar em segundo plano
              </button>
            ) : (
              <button type="button" className="tb-primary" onClick={() => setModalProgressoJobAberto(false)}>
                Fechar
              </button>
            )}
          </div>
        </footer>
      </div>
    );

  return (
    <div className="tb-page">
      <header className="tb-header tb-header-fixed">
        <div className="tb-header-inner">
          <div className="tb-header-bar">
            <div className="tb-header-marca">
              <h1>TranscriBrothers</h1>
              <p className="tb-sub tb-header-subtitulo">Vídeo local → transcrição, capturas e tutorial em Markdown.</p>
            </div>
            <div className="tb-header-divisoria" aria-hidden="true" />
            <div className="tb-header-toolbar" role="toolbar" aria-label="Novo projeto, abrir projeto e ferramentas">
              <button
                type="button"
                className="tb-btn-header tb-btn-header-primario"
                disabled={carregando}
                onClick={() => {
                  setImportacaoRecbrothersModalStepper(null);
                  setModalIniciarTranscricaoAberto(true);
                }}
              >
                <IconeIniciarTranscricaoHeaderToolbarTranscribrothers />
                <span>{carregando ? "A criar…" : "Novo projeto"}</span>
              </button>
              <button
                type="button"
                className="tb-btn-header tb-btn-header-secundario"
                title="Criar documento Markdown sem vídeo nem transcrição"
                disabled={carregando}
                onClick={() => void iniciarProjetoEmBrancoSemVideoTranscribrothers()}
              >
                <IconeProjetoEmBrancoHeaderToolbarTranscribrothers />
                <span>{carregando ? "A criar…" : "Projeto em branco"}</span>
              </button>
              <button
                type="button"
                className="tb-btn-header tb-btn-header-secundario"
                title="Abrir um projeto já existente neste servidor"
                onClick={() => setModalListaJobsServidorAberta(true)}
              >
                <IconeJobsHeaderToolbarTranscribrothers />
                <span>Abrir projeto</span>
              </button>
              <div className="tb-header-toolbar-separador" aria-hidden="true" />
              <div className="tb-header-btn-grupo" role="group" aria-label="Ferramentas do projeto ativo">
                {jobId ? (
                  <a
                    className="tb-btn-header tb-btn-header-secundario"
                    href={`/api/jobs/${jobId}/export.zip`}
                    title="Baixar ZIP com tutorial e imagens"
                  >
                    <IconeZipHeaderToolbarTranscribrothers />
                    <span>ZIP</span>
                  </a>
                ) : null}
                {jobId ? (
                  <button
                    type="button"
                    className="tb-btn-header tb-btn-header-secundario"
                    title="Ver capturas PNG (assets) e abrir anotação"
                    onClick={() => setModalGaleriaAssetsImagensAberta(true)}
                  >
                    <IconeAssetsImagensHeaderToolbarTranscribrothers />
                    <span>Assets</span>
                  </button>
                ) : null}
                {jobId && jobTerminal ? (
                  <button
                    type="button"
                    className="tb-btn-header tb-btn-header-secundario"
                    title="Ver estado do job e mensagens"
                    onClick={() => setModalProgressoJobAberto(true)}
                  >
                    <IconeStatusHeaderToolbarTranscribrothers />
                    <span>Status</span>
                  </button>
                ) : null}
                <button
                  type="button"
                  className="tb-btn-header tb-btn-header-secundario"
                  title="Ver ou editar o prefixo de instruções enviado ao modelo na geração do tutorial"
                  onClick={() => setModalPromptTutorialLitellmAberta(true)}
                >
                  <IconePromptHeaderToolbarTranscribrothers />
                  <span>Prompt</span>
                </button>
              </div>
              {jobEmExecucao && !modalProgressoJobAberto ? (
                <button
                  type="button"
                  className="tb-btn-header tb-btn-header-progresso"
                  onClick={() => setModalProgressoJobAberto(true)}
                >
                  <span className="tb-btn-header-progresso-ponto" aria-hidden="true" />
                  <span>Progresso</span>
                </button>
              ) : null}
              <button
                type="button"
                className="tb-btn-header tb-btn-header-icone"
                aria-label="Abrir configurações"
                aria-expanded={painelConfiguracoesAberto}
                onClick={() => setPainelConfiguracoesAberto(true)}
              >
                <IconeEngrenagemConfiguracaoTranscribrothers />
              </button>
            </div>
          </div>
          {erro ? <pre className="tb-err tb-err-header-bar">{erro}</pre> : null}
        </div>
      </header>

      <ModalStepperIniciarTranscricaoEscolherVideoEDestinoTranscribrothers
        aberto={modalIniciarTranscricaoAberto}
        carregando={carregando}
        importacaoRecbrothers={importacaoRecbrothersModalStepper}
        onFechar={() => {
          setModalIniciarTranscricaoAberto(false);
          setImportacaoRecbrothersModalStepper(null);
        }}
        onIniciar={(arquivo, destino, cliquesJsonOpcional) => {
          void iniciarPipelineTranscricaoComArquivoLocalTranscribrothers(
            arquivo,
            destino,
            cliquesJsonOpcional,
          );
        }}
      />

      {painelConfiguracoesAberto
        ? createPortal(
            <div className="tb-drawer-root" role="presentation">
              <button
                type="button"
                className="tb-drawer-backdrop"
                aria-label="Fechar configurações"
                onClick={() => setPainelConfiguracoesAberto(false)}
              />
              <aside className="tb-drawer-panel" aria-labelledby="tb-drawer-titulo">
                <div className="tb-drawer-top">
                  <button
                    type="button"
                    className="tb-drawer-fechar"
                    aria-label="Fechar configurações"
                    onClick={() => setPainelConfiguracoesAberto(false)}
                  >
                    ×
                  </button>
                </div>
                <div className="tb-drawer-body">{conteudoGavetaConfiguracoes}</div>
              </aside>
            </div>,
            document.body,
          )
        : null}

      {modalProgressoJobAberto && job
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label={jobEmExecucao ? "Fundo" : "Fechar"}
                onClick={() => {
                  if (!jobEmExecucao) setModalProgressoJobAberto(false);
                }}
              />
              <div className="tb-modal-job-shell">{conteudoModalProgressoJob}</div>
            </div>,
            document.body,
          )
        : null}

      {modalPreviewRegeneracaoSecaoAberto && job && previewRegeneracaoSecaoMarkdown
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label="Fechar pré-visualização da seção"
                onClick={() => setModalPreviewRegeneracaoSecaoAberto(false)}
              />
              <div className="tb-modal-job-shell tb-modal-job-shell-secao-preview">
                <div
                  className="tb-modal-job tb-modal-secao-preview"
                  role="dialog"
                  aria-modal="true"
                  aria-labelledby="tb-modal-secao-preview-titulo"
                >
                  <h2 id="tb-modal-secao-preview-titulo" className="tb-modal-job-titulo">
                    Pré-visualização — {previewRegeneracaoSecaoMarkdown.titulo_secao_heading}
                  </h2>
                  {previewRegeneracaoSecaoMarkdown.interpretacao_escopo_pedido?.explicacao_curta ? (
                    <p className="tb-muted tb-banner-interpretacao-escopo-secao">
                      <strong>Entendido:</strong>{" "}
                      {previewRegeneracaoSecaoMarkdown.interpretacao_escopo_pedido.explicacao_curta}
                      {previewRegeneracaoSecaoMarkdown.interpretacao_escopo_pedido.confianca ? (
                        <>
                          {" "}
                          <span className="tb-muted">
                            (confiança: {previewRegeneracaoSecaoMarkdown.interpretacao_escopo_pedido.confianca})
                          </span>
                        </>
                      ) : null}
                    </p>
                  ) : previewRegeneracaoSecaoMarkdown.modo_escopo_edicao &&
                    previewRegeneracaoSecaoMarkdown.modo_escopo_edicao !== "secao_inteira" ? (
                    <p className="tb-muted">
                      Escopo:{" "}
                      {previewRegeneracaoSecaoMarkdown.modo_escopo_edicao === "trecho_local"
                        ? "só o trecho indicado"
                        : "a partir do trecho até o fim da seção"}
                      .
                    </p>
                  ) : null}
                  <p className="tb-muted">
                    O restante do tutorial não muda até você aplicar. Use as abas abaixo para comparar antes e depois.
                  </p>
                  {previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes &&
                  !previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes.omitida ? (
                    <div
                      role="status"
                      className={`tb-banner-verificacao-redundancia-secao tb-banner-verificacao-redundancia-${
                        previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes.sucesso === false
                          ? "erro"
                          : previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes
                                .classificacao_global ?? "atencao"
                      }`}
                    >
                      <strong>Redundância com outras seções</strong>
                      {previewRegeneracaoSecaoMarkdown.correcao_redundancia_automatica_aplicada ? (
                        <p className="tb-muted">
                          Foi aplicada uma <strong>correção automática</strong> na seção (disparada por{" "}
                          {previewRegeneracaoSecaoMarkdown.correcao_redundancia_automatica_classificacao_disparo ??
                            "redundância"}
                          ). O texto «Depois» abaixo já é a versão corrigida.
                        </p>
                      ) : null}
                      {previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes.sucesso ===
                      false ? (
                        <p className="tb-muted">
                          {String(
                            previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes.erro ??
                              "Não foi possível executar a verificação.",
                          )}
                        </p>
                      ) : (
                        <p className="tb-muted">
                          Classificação:{" "}
                          <strong>
                            {
                              previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes
                                .classificacao_global
                            }
                          </strong>
                          {" — "}
                          {(
                            previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes
                              .mensagem_resumo ?? ""
                          ).slice(0, 320)}
                        </p>
                      )}
                      {(previewRegeneracaoSecaoMarkdown.verificacao_redundancia_outras_secoes.itens ?? [])
                        .filter((it) => it.classificacao === "redundancia" || it.classificacao === "atencao")
                        .slice(0, 4)
                        .map((it, idx) => (
                          <p key={idx} className="tb-muted tb-banner-redundancia-item">
                            {it.secao_ja_cobre ? `«${it.secao_ja_cobre}»: ` : ""}
                            {it.justificativa_curta ?? it.tema}
                          </p>
                        ))}
                      <p className="tb-muted tb-banner-redundancia-aviso">
                        Você pode aplicar mesmo assim; o restante do tutorial não será alterado até confirmar.
                      </p>
                    </div>
                  ) : null}
                  {previewRegeneracaoSecaoMarkdown.zona_editavel_antes &&
                  previewRegeneracaoSecaoMarkdown.zona_editavel_depois ? (
                    <ComponenteComparacaoMarkdownAntesDepoisVisualizacaoDiffELadoALadoTranscribrothers
                      rotuloBloco="Zona editada"
                      textoAntes={previewRegeneracaoSecaoMarkdown.zona_editavel_antes}
                      textoDepois={previewRegeneracaoSecaoMarkdown.zona_editavel_depois}
                      rotuloColunaAntes="Zona — antes"
                      rotuloColunaDepois="Zona — depois"
                    />
                  ) : null}
                  <ComponenteComparacaoMarkdownAntesDepoisVisualizacaoDiffELadoALadoTranscribrothers
                    rotuloBloco="Seção completa"
                    textoAntes={previewRegeneracaoSecaoMarkdown.secao_markdown_antes}
                    textoDepois={previewRegeneracaoSecaoMarkdown.secao_markdown_depois}
                    rotuloColunaAntes="Seção — antes"
                    rotuloColunaDepois="Seção — depois (proposta)"
                  />
                  <div className="tb-modal-job-acoes-finais tb-modal-secao-preview-acoes">
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={aplicandoPreviewRegeneracaoSecao}
                      onClick={() => {
                        if (!job) return;
                        void (async () => {
                          setAplicandoPreviewRegeneracaoSecao(true);
                          try {
                            const j = (await descartarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(
                              job.id,
                            )) as JobStatus;
                            setJob(j);
                            setModalPreviewRegeneracaoSecaoAberto(false);
                            pushToast("Pré-visualização descartada.", "success");
                          } catch (e) {
                            pushToast(e instanceof Error ? e.message : String(e), "error");
                          } finally {
                            setAplicandoPreviewRegeneracaoSecao(false);
                          }
                        })();
                      }}
                    >
                      Descartar
                    </button>
                    <button
                      type="button"
                      className="tb-primary"
                      disabled={aplicandoPreviewRegeneracaoSecao}
                      onClick={() => {
                        if (!job) return;
                        void (async () => {
                          setAplicandoPreviewRegeneracaoSecao(true);
                          try {
                            const j = (await aplicarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(
                              job.id,
                            )) as JobStatus;
                            setJob(j);
                            setModalPreviewRegeneracaoSecaoAberto(false);
                            pushToast("Seção aplicada ao tutorial.", "success");
                          } catch (e) {
                            pushToast(e instanceof Error ? e.message : String(e), "error");
                          } finally {
                            setAplicandoPreviewRegeneracaoSecao(false);
                          }
                        })();
                      }}
                    >
                      {aplicandoPreviewRegeneracaoSecao ? "Aplicando…" : "Aplicar ao tutorial"}
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      {modalPreviewRegeneracaoTutorialAberto &&
      job &&
      previewRegeneracaoTutorialMarkdownDocumentoInteiro
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label="Fechar pré-visualização do documento"
                onClick={() => setModalPreviewRegeneracaoTutorialAberto(false)}
              />
              <div className="tb-modal-job-shell tb-modal-job-shell-secao-preview">
                <div
                  className="tb-modal-job tb-modal-secao-preview"
                  role="dialog"
                  aria-modal="true"
                  aria-labelledby="tb-modal-tutorial-preview-titulo"
                >
                  <h2 id="tb-modal-tutorial-preview-titulo" className="tb-modal-job-titulo">
                    Pré-visualização —{" "}
                    {previewRegeneracaoTutorialMarkdownDocumentoInteiro.revisao_profunda_multifase
                      ? "revisão profunda"
                      : "documento inteiro"}
                  </h2>
                  <p className="tb-muted">
                    O tutorial publicado não muda até você aplicar. Use as abas abaixo para comparar antes e depois.
                  </p>
                  {previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial &&
                  !previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                    .omitida ? (
                    <div
                      role="status"
                      className={`tb-banner-verificacao-redundancia-secao tb-banner-verificacao-redundancia-${
                        previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                          .sucesso === false
                          ? "erro"
                          : previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                                .classificacao_global ?? "atencao"
                      }`}
                    >
                      <strong>Auditoria tutorial vs transcrição</strong>
                      {previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                        .sucesso === false ? (
                        <p className="tb-muted">
                          {String(
                            previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                              .erro ?? "Não foi possível executar a verificação.",
                          )}
                        </p>
                      ) : (
                        <p className="tb-muted">
                          Classificação:{" "}
                          <strong>
                            {
                              previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                                .classificacao_global
                            }
                          </strong>
                          {" — "}
                          {(
                            previewRegeneracaoTutorialMarkdownDocumentoInteiro.verificacao_sustentacao_tutorial
                              .mensagem_resumo ?? ""
                          ).slice(0, 400)}
                        </p>
                      )}
                      <p className="tb-muted tb-banner-redundancia-aviso">
                        Você pode aplicar mesmo assim ou descartar para manter o tutorial atual.
                      </p>
                    </div>
                  ) : null}
                  <ComponenteComparacaoMarkdownAntesDepoisVisualizacaoDiffELadoALadoTranscribrothers
                    rotuloBloco="Documento inteiro"
                    textoAntes={
                      previewRegeneracaoTutorialMarkdownDocumentoInteiro.markdown_antes ||
                      job.result_markdown ||
                      ""
                    }
                    textoDepois={
                      previewRegeneracaoTutorialMarkdownDocumentoInteiro.markdown_depois ||
                      previewRegeneracaoTutorialMarkdownDocumentoInteiro.markdown_completo_proposto
                    }
                    rotuloColunaAntes="Documento — antes"
                    rotuloColunaDepois="Documento — depois (proposta)"
                  />
                  <div className="tb-modal-job-acoes-finais tb-modal-secao-preview-acoes">
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={aplicandoPreviewRegeneracaoTutorial}
                      onClick={() => {
                        if (!job) return;
                        void (async () => {
                          setAplicandoPreviewRegeneracaoTutorial(true);
                          try {
                            const j = (await descartarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers(
                              job.id,
                            )) as JobStatus;
                            setJob(j);
                            setModalPreviewRegeneracaoTutorialAberto(false);
                            pushToast("Pré-visualização descartada.", "success");
                          } catch (e) {
                            pushToast(e instanceof Error ? e.message : String(e), "error");
                          } finally {
                            setAplicandoPreviewRegeneracaoTutorial(false);
                          }
                        })();
                      }}
                    >
                      Descartar
                    </button>
                    <button
                      type="button"
                      className="tb-primary"
                      disabled={aplicandoPreviewRegeneracaoTutorial}
                      onClick={() => {
                        if (!job) return;
                        void (async () => {
                          setAplicandoPreviewRegeneracaoTutorial(true);
                          try {
                            const j = (await aplicarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers(
                              job.id,
                            )) as JobStatus;
                            setJob(j);
                            setModalPreviewRegeneracaoTutorialAberto(false);
                            pushToast("Tutorial atualizado.", "success");
                          } catch (e) {
                            pushToast(e instanceof Error ? e.message : String(e), "error");
                          } finally {
                            setAplicandoPreviewRegeneracaoTutorial(false);
                          }
                        })();
                      }}
                    >
                      {aplicandoPreviewRegeneracaoTutorial ? "Aplicando…" : "Aplicar ao tutorial"}
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      {modalTranscricaoOriginalAberta && job && conteudoModalTranscricaoOriginal
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label="Fechar transcrição"
                onClick={() => setModalTranscricaoOriginalAberta(false)}
              />
              <div className="tb-modal-job-shell">{conteudoModalTranscricaoOriginal}</div>
            </div>,
            document.body,
          )
        : null}

      <ComponenteModalColarTextoAnexoContextoFabProjetoEmBrancoTranscribrothers
        aberta={modalTextoAnexoContextoFabAberta}
        onFechar={() => setModalTextoAnexoContextoFabAberta(false)}
        onIncluir={(texto) => incluirTextoAnexoContextoFabNoPedidoTranscribrothers(texto)}
        desabilitado={regenerandoTutorialMarkdown || regeneracaoTutorialEmAndamento}
      />

      <ComponenteModalConfirmarCriarIssueGitlabDocumentoMarkdownTranscribrothers
        aberto={modalCriarIssueGitlabAberto}
        tituloInicial={tituloSugeridoIssueGitlabMarkdownAtualTranscribrothers}
        projetoGitlab={configApi?.gitlab_create_issue_project_path ?? ""}
        tamanhoDescricaoCaracteres={(job?.result_markdown ?? "").length}
        quantidadeReferenciasImagensAssetsPng={quantidadeReferenciasImagensAssetsPngIssueGitlabTranscribrothers}
        processando={criandoIssueGitlab}
        onFechar={() => {
          if (!criandoIssueGitlab) setModalCriarIssueGitlabAberto(false);
        }}
        onConfirmar={(titulo, incluirImagens) =>
          void confirmarCriarIssueGitlabComTituloTranscribrothers(titulo, incluirImagens)
        }
      />

      <ComponenteModalConfirmarComentarIssueGitlabDocumentoMarkdownTranscribrothers
        aberto={modalComentarIssueGitlabAberto}
        tamanhoComentarioCaracteres={(job?.result_markdown ?? "").length}
        quantidadeReferenciasImagensAssetsPng={quantidadeReferenciasImagensAssetsPngIssueGitlabTranscribrothers}
        processando={comentandoIssueGitlab}
        onFechar={() => {
          if (!comentandoIssueGitlab) setModalComentarIssueGitlabAberto(false);
        }}
        onConfirmar={(issueUrl, incluirImagens) =>
          void confirmarComentarIssueGitlabTranscribrothers(issueUrl, incluirImagens)
        }
      />

      <ComponenteModalConfirmarAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers
        aberto={modalAnexarDescricaoIssueGitlabAberto}
        tamanhoDocumentoCaracteres={(job?.result_markdown ?? "").length}
        quantidadeReferenciasImagensAssetsPng={quantidadeReferenciasImagensAssetsPngIssueGitlabTranscribrothers}
        processando={anexandoDescricaoIssueGitlab}
        onFechar={() => {
          if (!anexandoDescricaoIssueGitlab) setModalAnexarDescricaoIssueGitlabAberto(false);
        }}
        onConfirmar={(issueUrl, incluirImagens) =>
          void confirmarAnexarDescricaoIssueGitlabTranscribrothers(issueUrl, incluirImagens)
        }
      />

      <ComponenteModalConfirmarCriarPaginaWikiGitlabDocumentoMarkdownTranscribrothers
        aberto={modalCriarPaginaWikiGitlabAberto}
        tituloInicial={tituloSugeridoIssueGitlabMarkdownAtualTranscribrothers}
        jobId={job?.id ?? ""}
        projetoGitlab={configApi?.gitlab_wiki_project_path ?? ""}
        prefixoPastaWikiPadrao={configApi?.gitlab_wiki_slug_prefixo_pasta ?? "workshop"}
        wikiHabilitadaNoServidor={gitlabCriarWikiHabilitadoNoServidorTranscribrothers}
        tamanhoConteudoCaracteres={(job?.result_markdown ?? "").length}
        quantidadeReferenciasImagensAssetsPng={quantidadeReferenciasImagensAssetsPngIssueGitlabTranscribrothers}
        processando={criandoPaginaWikiGitlab}
        onFechar={() => {
          if (!criandoPaginaWikiGitlab) setModalCriarPaginaWikiGitlabAberto(false);
        }}
        onConfirmar={(titulo, incluirImagens, prefixoPasta) =>
          void confirmarCriarPaginaWikiGitlabComTituloTranscribrothers(
            titulo,
            incluirImagens,
            prefixoPasta,
          )
        }
      />

      <ComponenteModalEscolherVersaoHistoricoTutorialMarkdownEstiloListaProjetosTranscribrothers
        aberta={modalEscolherVersaoHistoricoTutorialAberta}
        onFechar={() => setModalEscolherVersaoHistoricoTutorialAberta(false)}
        versaoHistoricoSelecionadaId={historicoVersaoTutorialSelecionadaId}
        onEscolherVersao={setHistoricoVersaoTutorialSelecionadaId}
        listaVersoes={listaHistoricoVersoesTutorialMarkdownApi}
        carregandoLista={carregandoListaHistoricoVersoesTutorialMarkdown}
        rotuloVersaoAtualServidor={rotuloVersaoAtualServidorModalHistoricoTutorial}
        dataHoraVersaoAtualServidor={dataHoraVersaoAtualServidorModalHistoricoTutorial}
        formatarDataHora={formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers}
        obterRotuloOrigemPortugues={
          obterRotuloPortuguesOrigemHistoricoVersaoTutorialMarkdownTranscribrothers
        }
      />

      {modalListaJobsServidorAberta
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label="Fechar lista de projetos"
                onClick={() => setModalListaJobsServidorAberta(false)}
              />
              <div className="tb-modal-job-shell tb-modal-job-shell-jobs-servidor">
                <div
                  className="tb-modal-job tb-modal-jobs-servidor-modal"
                  role="dialog"
                  aria-modal="true"
                  aria-labelledby="tb-modal-jobs-servidor-titulo"
                >
                  <h2 id="tb-modal-jobs-servidor-titulo" className="tb-modal-job-titulo">
                    Projetos neste servidor
                  </h2>
                  <p className="tb-muted tb-jobs-servidor-intro">
                    Lista os projetos recentes (cada um com vídeo, tutorial e histórico de versões).{" "}
                    <strong>Carregar projeto</strong> abre na página principal; <strong>Apagar</strong> remove o
                    registro e a pasta em <code>data/jobs/</code>. Se ainda estiver em andamento, o servidor tenta
                    cancelar o pipeline antes de excluir.
                  </p>
                  <div className="tb-jobs-servidor-toolbar">
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={carregandoListaJobsServidor}
                      onClick={() => void carregarListaJobsNoServidorTranscribrothers()}
                    >
                      {carregandoListaJobsServidor ? "A atualizar…" : "Atualizar lista"}
                    </button>
                  </div>
                  {carregandoListaJobsServidor && listaJobsServidorCache === null ? (
                    <p className="tb-muted tb-jobs-servidor-loading">A carregar…</p>
                  ) : null}
                  {listaJobsServidorCache && listaJobsServidorCache.length === 0 ? (
                    <p className="tb-muted tb-jobs-servidor-vazio">Nenhum projeto na base.</p>
                  ) : null}
                  {listaJobsServidorCache && listaJobsServidorCache.length > 0 ? (
                    <div className="tb-jobs-servidor-tabela-wrap">
                      <table className="tb-jobs-servidor-tabela">
                        <thead>
                          <tr>
                            <th>ID (prefixo)</th>
                            <th>Título (H1)</th>
                            <th>Atualizado</th>
                            <th>Estado</th>
                            <th>Tutorial .md</th>
                            <th>Origem</th>
                            <th className="tb-jobs-servidor-th-acoes">Ações</th>
                          </tr>
                        </thead>
                        <tbody>
                          {listaJobsServidorCache.map((row) => (
                            <tr key={row.id}>
                              <td>
                                <code className="tb-code-inline tb-jobs-servidor-id" title={row.id}>
                                  {row.id.slice(0, 8)}…
                                </code>
                              </td>
                              <td
                                className="tb-jobs-servidor-titulo-tutorial-h1"
                                title={row.titulo_tutorial_markdown_h1 ?? undefined}
                              >
                                {row.titulo_tutorial_markdown_h1?.trim()
                                  ? row.titulo_tutorial_markdown_h1
                                  : "—"}
                              </td>
                              <td>
                                {row.updated_at
                                  ? formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers(row.updated_at)
                                  : "—"}
                              </td>
                              <td>
                                <code className="tb-code-inline">{row.status}</code>
                              </td>
                              <td>{row.tem_resultado_markdown ? "sim" : "não"}</td>
                              <td className="tb-jobs-servidor-origem" title={row.drive_url}>
                                {row.drive_url.length > 48 ? `${row.drive_url.slice(0, 48)}…` : row.drive_url}
                              </td>
                              <td className="tb-jobs-servidor-acoes">
                                <button
                                  type="button"
                                  className="tb-linkbtn"
                                  disabled={carregandoSelecaoJobListaId === row.id}
                                  onClick={() => {
                                    setErro(null);
                                    void (async () => {
                                      setCarregandoSelecaoJobListaId(row.id);
                                      try {
                                        const j = await buscarJob(row.id);
                                        setJob(j);
                                        setModalProgressoJobAberto(
                                          deveAbrirModalProgressoAoCarregarProjetoTranscribrothers(j),
                                        );
                                        if (
                                          !deveAbrirModalProgressoAoCarregarProjetoTranscribrothers(j) &&
                                          j.status === "generating_tutorial"
                                        ) {
                                          pushToast(
                                            "Regeneração em andamento. O documento atual permanece visível; use «Progresso» no topo para acompanhar.",
                                            "info",
                                          );
                                        }
                                        setModalListaJobsServidorAberta(false);
                                        pushToast("Projeto carregado na página.", "success");
                                      } catch (e) {
                                        const msg = e instanceof Error ? e.message : String(e);
                                        pushToast(msg, "error");
                                      } finally {
                                        setCarregandoSelecaoJobListaId(null);
                                      }
                                    })();
                                  }}
                                >
                                  {carregandoSelecaoJobListaId === row.id ? "…" : "Carregar projeto"}
                                </button>
                                <button
                                  type="button"
                                  className="tb-linkbtn tb-jobs-btn-apagar"
                                  disabled={apagandoJobServidorId === row.id}
                                  onClick={() => {
                                    void (async () => {
                                      const terminais = ["completed", "failed", "cancelled"];
                                      const emAndamento = !terminais.includes(row.status);
                                      const msgConfirmacao = emAndamento
                                        ? `O job ${row.id} está em "${row.status}". Apagar vai cancelar o pipeline (se ainda estiver rodando) e remover registro e pasta no servidor. Continuar?`
                                        : `Apagar o job ${row.id} no servidor e a pasta em disco? Esta ação não pode ser desfeita.`;
                                      if (typeof window !== "undefined" && !window.confirm(msgConfirmacao)) {
                                        return;
                                      }
                                      setApagandoJobServidorId(row.id);
                                      try {
                                        const r = await fetch(`/api/jobs/${row.id}`, { method: "DELETE" });
                                        if (!r.ok) {
                                          const t = await r.text();
                                          throw new Error(t || `Erro HTTP ${r.status}`);
                                        }
                                        if (job?.id === row.id) {
                                          setJob(null);
                                        }
                                        pushToast("Job apagado do servidor e pasta removida (se existia).", "success");
                                        setListaJobsServidorCache((prev) =>
                                          prev === null ? prev : prev.filter((x) => x.id !== row.id),
                                        );
                                      } catch (e) {
                                        pushToast(e instanceof Error ? e.message : String(e), "error");
                                      } finally {
                                        setApagandoJobServidorId(null);
                                      }
                                    })();
                                  }}
                                >
                                  {apagandoJobServidorId === row.id ? "…" : "Apagar"}
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : null}
                  <div className="tb-modal-job-acoes-finais">
                    <button
                      type="button"
                      className="tb-primary"
                      onClick={() => setModalListaJobsServidorAberta(false)}
                    >
                      Fechar
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      {modalPromptTutorialLitellmAberta
        ? createPortal(
            <div className="tb-modal-job-root" role="presentation">
              <button
                type="button"
                className="tb-modal-job-backdrop"
                aria-label="Fechar prompt do tutorial"
                onClick={() => setModalPromptTutorialLitellmAberta(false)}
              />
              <div className="tb-modal-job-shell tb-modal-job-shell-prompt-litellm-tutorial">
                <div
                  className="tb-modal-job tb-modal-prompt-litellm-tutorial"
                  role="dialog"
                  aria-modal="true"
                  aria-labelledby="tb-modal-prompt-litellm-tutorial-titulo"
                >
                  <h2 id="tb-modal-prompt-litellm-tutorial-titulo" className="tb-modal-job-titulo">
                    Prompt do tutorial (LiteLLM)
                  </h2>
                  <p className="tb-muted tb-modal-prompt-litellm-tutorial-intro">
                    Este bloco é enviado como prefixo da mensagem de utilizador ao gerar o Markdown do tutorial. Se
                    estiver só com espaços ao clicar em <strong>Gerar tutorial</strong>, o servidor usa apenas as
                    instruções padrão internas (estilo “acompanhar o vídeo”). Com conteúdo, o texto é guardado no job
                    e reutilizado na regeneração. Use os atalhos abaixo para colar variantes — incluindo documento
                    autónomo para quem não vai abrir o vídeo.
                  </p>
                  <label className="tb-modal-prompt-litellm-tutorial-label" htmlFor="tb-prompt-litellm-tutorial-textarea">
                    Prefixo editável
                  </label>
                  <textarea
                    id="tb-prompt-litellm-tutorial-textarea"
                    className="tb-input tb-modal-prompt-litellm-tutorial-textarea"
                    spellCheck={false}
                    rows={16}
                    value={textoInstrucaoPrefixoLitellmTutorialUsuario}
                    onChange={(e) => setTextoInstrucaoPrefixoLitellmTutorialUsuario(e.target.value)}
                  />
                  <div className="tb-modal-prompt-litellm-tutorial-botoes-padrao">
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={!padroesInstrucaoTutorialLitellm}
                      onClick={() => {
                        if (!padroesInstrucaoTutorialLitellm) {
                          pushToast("Instruções padrão ainda não carregaram.", "error");
                          return;
                        }
                        setTextoInstrucaoPrefixoLitellmTutorialUsuario(
                          padroesInstrucaoTutorialLitellm.instrucao_sem_imagens,
                        );
                      }}
                    >
                      Colar padrão (sem imagens)
                    </button>
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={!padroesInstrucaoTutorialLitellm}
                      onClick={() => {
                        if (!padroesInstrucaoTutorialLitellm) {
                          pushToast("Instruções padrão ainda não carregaram.", "error");
                          return;
                        }
                        setTextoInstrucaoPrefixoLitellmTutorialUsuario(
                          padroesInstrucaoTutorialLitellm.instrucao_com_imagens,
                        );
                      }}
                    >
                      Colar padrão (com imagens / visão)
                    </button>
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={!padroesInstrucaoTutorialLitellm}
                      onClick={() => {
                        if (!padroesInstrucaoTutorialLitellm) {
                          pushToast("Instruções padrão ainda não carregaram.", "error");
                          return;
                        }
                        setTextoInstrucaoPrefixoLitellmTutorialUsuario(
                          padroesInstrucaoTutorialLitellm.instrucao_sem_imagens_documento_autonomo_sem_video,
                        );
                      }}
                    >
                      Colar padrão (autónomo — sem depender do vídeo, só texto+frames)
                    </button>
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={!padroesInstrucaoTutorialLitellm}
                      onClick={() => {
                        if (!padroesInstrucaoTutorialLitellm) {
                          pushToast("Instruções padrão ainda não carregaram.", "error");
                          return;
                        }
                        setTextoInstrucaoPrefixoLitellmTutorialUsuario(
                          padroesInstrucaoTutorialLitellm.instrucao_com_imagens_documento_autonomo_sem_video,
                        );
                      }}
                    >
                      Colar padrão (autónomo + visão na regeneração)
                    </button>
                    <button
                      type="button"
                      className="tb-linkbtn"
                      onClick={() => setTextoInstrucaoPrefixoLitellmTutorialUsuario("")}
                    >
                      Limpar (só padrão interno no envio)
                    </button>
                  </div>
                  <div className="tb-modal-job-acoes-finais tb-modal-prompt-litellm-tutorial-acoes-finais">
                    <button
                      type="button"
                      className="tb-btn-outline"
                      onClick={() => {
                        gravarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownNoNavegadorTranscribrothers(
                          textoInstrucaoPrefixoLitellmTutorialUsuario,
                        );
                        pushToast("Rascunho do prompt guardado neste navegador.", "success");
                      }}
                    >
                      Guardar no navegador
                    </button>
                    <button type="button" className="tb-primary" onClick={() => setModalPromptTutorialLitellmAberta(false)}>
                      Fechar
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      {jobId ? (
        <section
          className={`tb-grid tb-grid-preview${jobEhProjetoEmBrancoAtual ? " tb-grid-preview--sem-video" : ""}`}
        >
          {!jobEhProjetoEmBrancoAtual ? (
          <div className="tb-card tb-grid-col-video">
            <div className="tb-md-header tb-md-header--coluna-video">
              <div className="tb-md-header-titulo-linha">
                <h2 id="tb-video-titulo">Vídeo</h2>
              </div>
            </div>
            <div className="tb-video-sticky-inner">
              <ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers
                key={jobId}
                jobId={jobId}
                duracaoVideoSegundosDoJob={
                  lerDuracaoVideoSegundosStepsJsonJobTranscribrothers(
                    job?.steps_json as Record<string, unknown> | undefined,
                  ) || null
                }
                videoRef={videoRef}
                exibirBotaoCapturarFrame={!historicoVersaoTutorialMarkdownEstaAtivoNaUi}
                capturandoFrame={capturandoFrameManualVideo}
                aoCapturarFrameNoInstanteAtual={(timestampSegundos) => {
                  void capturarFrameManualVideoNoTimestampSegundosTranscribrothers(timestampSegundos);
                }}
                aoVideoIndisponivelParaCapturaFrame={() => {
                  pushToast("Aguarde o vídeo carregar antes de capturar.", "error");
                }}
                onDuracaoVideoConhecidaSegundos={(duracaoSegundos) => {
                  setJob((atual) => {
                    if (!atual) return atual;
                    const steps = { ...(atual.steps_json ?? {}), duracao_video_segundos: duracaoSegundos };
                    return { ...atual, steps_json: steps };
                  });
                }}
              />
            </div>
          </div>
          ) : null}
          <div
            className={`tb-card tb-md tb-grid-col-tutorial${modoInserirImagemAssetNoPreviewTutorialAtivo ? " tb-grid-col-tutorial--modo-inserir-imagem-markdown" : ""}`}
          >
            <div className="tb-md-header">
              <div className="tb-md-header-titulo-linha">
                <h2 id="tb-tutorial-markdown-titulo">{tituloFrameDocumentoResultadoTranscribrothers}</h2>
                {subtituloVersaoEDataFrameDocumentoTranscribrothers ? (
                  jobPodeConsultarHistoricoVersoesTutorialMarkdown ? (
                    <button
                      type="button"
                      className={[
                        "tb-md-header-documento-versao-disparador",
                        modalEscolherVersaoHistoricoTutorialAberta
                          ? "tb-md-header-documento-versao-disparador--aberto"
                          : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      title="Abrir histórico de versões deste projeto"
                      aria-label={`Versão e data: ${subtituloVersaoEDataFrameDocumentoTranscribrothers}. Abrir lista de versões.`}
                      aria-haspopup="dialog"
                      aria-expanded={modalEscolherVersaoHistoricoTutorialAberta}
                      onClick={() => setModalEscolherVersaoHistoricoTutorialAberta(true)}
                    >
                      <span>{subtituloVersaoEDataFrameDocumentoTranscribrothers}</span>
                      <span className="tb-md-header-documento-versao-disparador-caret" aria-hidden>
                        ▼
                      </span>
                    </button>
                  ) : (
                    <span className="tb-md-header-documento-versao-data tb-muted">
                      {subtituloVersaoEDataFrameDocumentoTranscribrothers}
                    </span>
                  )
                ) : null}
                <div
                  className="tb-md-header-toolbar"
                  role="toolbar"
                  aria-labelledby="tb-tutorial-markdown-titulo"
                >
                {textoPlanoTranscricaoOriginalSnapshotJob ? (
                  <button
                    type="button"
                    className="tb-btn-md-toolbar-icone"
                    title="Ver transcrição original do áudio"
                    aria-label="Ver transcrição original do áudio"
                    onClick={() => setModalTranscricaoOriginalAberta(true)}
                  >
                    <IconeVerTranscricaoTutorialMarkdownTranscribrothers />
                  </button>
                ) : null}
                {jobPermiteEdicaoManualMarkdownTutorial && !modoEdicaoMarkdownTutorialAtivo ? (
                  <button
                    type="button"
                    className="tb-btn-md-toolbar-icone"
                    title="Editar o Markdown do tutorial (editor e pré-visualização lado a lado)"
                    aria-label="Editar Markdown do tutorial"
                    onClick={() => {
                      cancelarModoInserirImagemAssetNoTutorialTranscribrothers();
                      setMarkdownTutorialRascunhoEdicao(job?.result_markdown ?? "");
                      setModoEdicaoMarkdownTutorialAtivo(true);
                    }}
                  >
                    <IconeEditarMarkdownTutorialTranscribrothers />
                  </button>
                ) : null}
                {podeColarImagemClipboardNoPreviewTutorialTranscribrothers ? (
                  <button
                    type="button"
                    className="tb-btn-md-toolbar-icone"
                    disabled={
                      colandoImagemClipboardParaInsercaoPreviewTutorial || salvandoInsercaoImagemNoTutorial
                    }
                    title={
                      colandoImagemClipboardParaInsercaoPreviewTutorial
                        ? "Salvando imagem nos assets…"
                        : "Colar imagem da área de transferência (salva em assets; depois escolha a posição no tutorial). Atalho: Ctrl+V"
                    }
                    aria-label={
                      colandoImagemClipboardParaInsercaoPreviewTutorial
                        ? "Salvando imagem colada nos assets"
                        : "Colar imagem da área de transferência no tutorial"
                    }
                    aria-busy={colandoImagemClipboardParaInsercaoPreviewTutorial}
                    onClick={() =>
                      void solicitarColarImagemClipboardNoPreviewTutorialPeloBotaoTranscribrothers()
                    }
                  >
                    <IconeColarImagemClipboardTutorialMarkdownTranscribrothers />
                  </button>
                ) : null}
                {job?.result_markdown && !modoEdicaoMarkdownTutorialAtivo ? (
                  <ComponenteMenuSplitExportarEDownloadMarkdownTutorialToolbarTranscribrothers
                    bloqueadoPorHistoricoVersao={historicoVersaoTutorialMarkdownEstaAtivoNaUi}
                    abrindoNovaAba={abrindoTutorialMarkdownNovaAba}
                    criandoIssueGitlab={criandoIssueGitlab}
                    comentandoIssueGitlab={comentandoIssueGitlab}
                    anexandoDescricaoIssueGitlab={anexandoDescricaoIssueGitlab}
                    criandoPaginaWikiGitlab={criandoPaginaWikiGitlab}
                    baixandoMarkdown={baixandoMarkdownComImagens}
                    baixandoPdf={baixandoPdfTutorial}
                    gitlabCriarIssueHabilitadoNoServidor={gitlabCriarIssueHabilitadoNoServidorTranscribrothers}
                    gitlabCriarWikiHabilitadoNoServidor={gitlabCriarWikiHabilitadoNoServidorTranscribrothers}
                    onAbrirTutorialMarkdownEmNovaAba={() => void abrirTutorialMarkdownEmNovaAbaNavegador()}
                    onAbrirModalCriarIssueGitlab={() => setModalCriarIssueGitlabAberto(true)}
                    onAbrirModalComentarIssueGitlab={() => setModalComentarIssueGitlabAberto(true)}
                    onAbrirModalAnexarDescricaoIssueGitlab={() => setModalAnexarDescricaoIssueGitlabAberto(true)}
                    onAbrirModalCriarPaginaWikiGitlab={() => setModalCriarPaginaWikiGitlabAberto(true)}
                    onAvisoGitlabNaoConfigurado={() =>
                      pushToast(
                        "GitLab não configurado no servidor. Defina GITLAB_BASE_URL e GITLAB_TOKEN em env.local (raiz) ou backend/.env e reinicie o uvicorn.",
                        "info",
                      )
                    }
                    onAvisoGitlabWikiNaoConfigurado={() =>
                      pushToast(
                        "Wiki GitLab não configurada no servidor. Defina GITLAB_BASE_URL, GITLAB_TOKEN e GITLAB_WIKI_PROJECT_PATH em env.local (raiz) ou backend/.env e reinicie o uvicorn.",
                        "info",
                      )
                    }
                    onBaixarMarkdown={() => void baixarTutorialMarkdownComoArquivoComImagensEmbutidas()}
                    onBaixarPdf={() => void baixarTutorialPdfComImagensEmbutidas()}
                  />
                ) : null}
                </div>
              </div>
            </div>
            {dadosVerificacaoSustentacaoTutorialMarkdownDoJob &&
            dadosVerificacaoSustentacaoTutorialMarkdownDoJob.sucesso === true &&
            !dadosVerificacaoSustentacaoTutorialMarkdownDoJob.omitida &&
            (dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global === "risco" ||
              dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global === "atencao") ? (
              <div
                role="status"
                className={`tb-banner-verificacao-sustentacao-tutorial tb-banner-verificacao-sustentacao-${dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global ?? "atencao"}`}
              >
                <strong>Auditor</strong> (
                {dadosVerificacaoSustentacaoTutorialMarkdownDoJob.classificacao_global}):{" "}
                {(dadosVerificacaoSustentacaoTutorialMarkdownDoJob.mensagem_resumo ?? "").slice(0, 420)}
                {((dadosVerificacaoSustentacaoTutorialMarkdownDoJob.mensagem_resumo ?? "").length > 420
                  ? "…"
                  : "")}{" "}
                <button type="button" className="tb-linkbtn" onClick={() => setModalProgressoJobAberto(true)}>
                  Abrir Status
                </button>
              </div>
            ) : null}
            {modoEdicaoPorSecaoTutorialAtivo && jobPermiteModoEdicaoPorSecaoTutorial ? (
              <div
                ref={refPainelEdicaoSecaoMarkdownTutorial}
                className="tb-edicao-secao-painel"
                role="region"
                aria-label="Edição por seção"
              >
                <p className="tb-muted tb-edicao-secao-intro">
                  Descreva em linguagem natural o que quer mudar — inclusive o parágrafo introdutório antes da primeira «##».
                  A IA identifica o escopo (introdução ou seção). Use «Ajustar escopo manualmente» se preferir colar o trecho.
                </p>
                {carregandoListaSecoesNivel2Tutorial ? (
                  <p className="tb-muted">Carregando seções…</p>
                ) : listaSecoesNivel2TutorialMarkdown && listaSecoesNivel2TutorialMarkdown.length === 0 ? (
                  <p className="tb-muted">
                    Este tutorial não tem seções de nível 2 (<code>## Título</code>). Use o ícone de editar Markdown ou o
                    FAB para regenerar o documento inteiro.
                  </p>
                ) : (
                  <>
                    <label className="tb-label" htmlFor="tb-instrucoes-secao-edicao">
                      O que você quer
                    </label>
                    <textarea
                      id="tb-instrucoes-secao-edicao"
                      className="tb-input tb-edicao-secao-textarea"
                      rows={5}
                      value={instrucoesRegeneracaoSecaoMarkdown}
                      disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                      onChange={(e) => setInstrucoesRegeneracaoSecaoMarkdown(e.target.value)}
                      placeholder="Ex.: Nessa parte da Visão Geral do Fluxo, faça uma intro mais detalhada. Ou: a partir de «Dinâmica do Processo», detalhe com exemplos…"
                    />
                    <details
                      className="tb-edicao-secao-escopo-manual"
                      open={escopoEdicaoSecaoManualAtivoForm}
                      onToggle={(e) => setEscopoEdicaoSecaoManualAtivoForm((e.target as HTMLDetailsElement).open)}
                    >
                      <summary>Ajustar escopo manualmente (opcional)</summary>
                      <fieldset className="tb-edicao-secao-escopo-fieldset">
                        <legend className="tb-label">Modo</legend>
                        <label className="tb-drawer-checkbox">
                          <input
                            type="radio"
                            name="tb-modo-escopo-secao"
                            checked={modoEscopoEdicaoSecaoMarkdownForm === "trecho_local"}
                            disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                            onChange={() => setModoEscopoEdicaoSecaoMarkdownForm("trecho_local")}
                          />{" "}
                          Nesta parte aqui (só o trecho colado)
                        </label>
                        <label className="tb-drawer-checkbox">
                          <input
                            type="radio"
                            name="tb-modo-escopo-secao"
                            checked={modoEscopoEdicaoSecaoMarkdownForm === "a_partir_de"}
                            disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                            onChange={() => setModoEscopoEdicaoSecaoMarkdownForm("a_partir_de")}
                          />{" "}
                          A partir daqui (até o fim da seção <code>##</code>)
                        </label>
                        <label className="tb-drawer-checkbox">
                          <input
                            type="radio"
                            name="tb-modo-escopo-secao"
                            checked={modoEscopoEdicaoSecaoMarkdownForm === "secao_inteira"}
                            disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                            onChange={() => setModoEscopoEdicaoSecaoMarkdownForm("secao_inteira")}
                          />{" "}
                          Seção inteira (<code>##</code>)
                        </label>
                      </fieldset>
                      {modoEscopoEdicaoSecaoMarkdownForm !== "secao_inteira" ? (
                        <>
                          <label className="tb-label" htmlFor="tb-trecho-ancora-secao-edicao">
                            Cole o trecho do tutorial
                          </label>
                          <textarea
                            id="tb-trecho-ancora-secao-edicao"
                            className="tb-input tb-edicao-secao-textarea"
                            rows={4}
                            value={trechoAncoraEdicaoSecaoMarkdownForm}
                            disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                            onChange={(e) => setTrechoAncoraEdicaoSecaoMarkdownForm(e.target.value)}
                            placeholder="Cole o título e/ou parágrafos exatamente como no tutorial…"
                          />
                        </>
                      ) : null}
                      <label className="tb-label" htmlFor="tb-select-secao-edicao">
                        Seção <span className="tb-muted">(opcional se colou o trecho)</span>
                      </label>
                      <select
                        id="tb-select-secao-edicao"
                        className="tb-input"
                        value={tituloSecaoSelecionadaParaEdicao}
                        disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                        onChange={(e) => setTituloSecaoSelecionadaParaEdicao(e.target.value)}
                      >
                        {modoEscopoEdicaoSecaoMarkdownForm !== "secao_inteira" ? (
                          <option value="">Detectar automaticamente</option>
                        ) : null}
                        {(listaSecoesNivel2TutorialMarkdown ?? []).map((s) => (
                          <option key={s.indice} value={s.linha_heading}>
                            {s.linha_heading}
                          </option>
                        ))}
                      </select>
                    </details>
                    <button
                      type="button"
                      className="tb-primary"
                      disabled={regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento}
                      onClick={() => void solicitarRegeneracaoSecaoMarkdownTutorialTranscribrothers()}
                    >
                      {regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento
                        ? "Regenerando seção…"
                        : "Pedir edição com IA"}
                    </button>
                    {previewRegeneracaoSecaoMarkdown ? (
                      <button
                        type="button"
                        className="tb-linkbtn"
                        onClick={() => setModalPreviewRegeneracaoSecaoAberto(true)}
                      >
                        Ver pré-visualização da seção
                      </button>
                    ) : null}
                    {previewRegeneracaoTutorialMarkdownDocumentoInteiro ? (
                      <button
                        type="button"
                        className="tb-linkbtn"
                        onClick={() => setModalPreviewRegeneracaoTutorialAberto(true)}
                      >
                        Ver pré-visualização do documento
                      </button>
                    ) : null}
                  </>
                )}
              </div>
            ) : null}
            {historicoVersaoTutorialMarkdownEstaAtivoNaUi ? (
              <>
                <div className="tb-banner-historico-versao-tutorial" role="status">
                  <span className="tb-banner-historico-versao-tutorial-texto">
                    Visualizando uma versão antiga do histórico
                    {rotuloNumeroVersaoHistoricoTutorialSelecionadaNoProjeto ||
                    metaVersaoHistoricoTutorialMarkdownSelecionada ? (
                      <>
                        {" "}
                        (
                        {rotuloNumeroVersaoHistoricoTutorialSelecionadaNoProjeto}
                        {rotuloNumeroVersaoHistoricoTutorialSelecionadaNoProjeto &&
                        metaVersaoHistoricoTutorialMarkdownSelecionada
                          ? " · "
                          : null}
                        {metaVersaoHistoricoTutorialMarkdownSelecionada ? (
                          <>
                            {formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers(
                              metaVersaoHistoricoTutorialMarkdownSelecionada.criado_em || null,
                            )}
                            {" · "}
                            {obterRotuloPortuguesOrigemHistoricoVersaoTutorialMarkdownTranscribrothers(
                              metaVersaoHistoricoTutorialMarkdownSelecionada.origem,
                            )}
                          </>
                        ) : null}
                        ).
                      </>
                    ) : (
                      "."
                    )}
                  </span>
                  <button
                    type="button"
                    className="tb-primary tb-btn-restaurar-historico-tutorial"
                    disabled={
                      restaurandoVersaoHistoricoTutorialMarkdown ||
                      carregandoConteudoHistoricoVersaoTutorialMarkdown ||
                      historicoVersaoTutorialSelecionadaId === null ||
                      !job
                    }
                    onClick={() => {
                      if (!job || historicoVersaoTutorialSelecionadaId === null) return;
                      setErro(null);
                      void (async () => {
                        setRestaurandoVersaoHistoricoTutorialMarkdown(true);
                        try {
                          const j2 = await restaurarHistoricoVersaoTutorialMarkdownJobApiTranscribrothers(
                            job.id,
                            historicoVersaoTutorialSelecionadaId,
                          );
                          setJob(j2);
                          setHistoricoVersaoTutorialSelecionadaId(null);
                          pushToast("Tutorial restaurado a partir do histórico.", "success");
                        } catch (e) {
                          const msg = e instanceof Error ? e.message : String(e);
                          setErro(msg);
                          pushToast(msg, "error");
                        } finally {
                          setRestaurandoVersaoHistoricoTutorialMarkdown(false);
                        }
                      })();
                    }}
                  >
                    {restaurandoVersaoHistoricoTutorialMarkdown ? "A restaurar…" : "Restaurar esta versão"}
                  </button>
                </div>
                {carregandoConteudoHistoricoVersaoTutorialMarkdown ? (
                  <p className="tb-muted">A carregar a versão selecionada…</p>
                ) : (
                  <div className="tb-mdwrap">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponentsPreviewTutorialComAncorasLinha}>
                      {markdownPreviewVersaoHistoricoTutorialTranscribrothers ?? ""}
                    </ReactMarkdown>
                  </div>
                )}
              </>
            ) : job?.result_markdown ? (
              <>
                {modoInserirImagemAssetNoPreviewTutorialAtivo ? (
                  <div
                    className="tb-painel-modo-inserir-imagem-markdown-tutorial"
                    role="status"
                  >
                    <strong>Modo inserir imagem.</strong> Passe o mouse sobre o tutorial: a linha tracejada
                    mostra onde a referência será inserida. Clique para confirmar. Você pode colar outra
                    imagem com <kbd>Ctrl+V</kbd> ou o botão na barra do tutorial.{" "}
                    <button
                      type="button"
                      className="tb-linkbtn"
                      disabled={salvandoInsercaoImagemNoTutorial}
                      onClick={cancelarModoInserirImagemAssetNoTutorialTranscribrothers}
                    >
                      Cancelar
                    </button>{" "}
                    (<kbd>Esc</kbd>)
                  </div>
                ) : null}
                <div
                  ref={refContainerPreviewTutorialMarkdown}
                  className={`tb-mdwrap${modoInserirImagemAssetNoPreviewTutorialAtivo ? " tb-mdwrap--modo-inserir-imagem-markdown" : ""}`}
                  tabIndex={podeColarImagemClipboardNoPreviewTutorialTranscribrothers ? 0 : undefined}
                  onPaste={
                    podeColarImagemClipboardNoPreviewTutorialTranscribrothers
                      ? aoColarImagemClipboardNoPreviewTutorialMarkdownTranscribrothers
                      : undefined
                  }
                  onMouseMove={tratarMovimentoMousePreviewTutorialInsercaoImagemTranscribrothers}
                  onMouseLeave={() => {
                    setLinhaMarcadorInsercaoImagemPreview(null);
                    setTopoPxMarcadorInsercaoImagemPreview(null);
                    ultimoPontoInsercaoImagemPreviewTutorialRef.current = null;
                  }}
                  onClick={tratarCliquePreviewTutorialInsercaoImagemTranscribrothers}
                >
                  {modoInserirImagemAssetNoPreviewTutorialAtivo &&
                  topoPxMarcadorInsercaoImagemPreview != null ? (
                    <div
                      className="tb-marcador-linha-insercao-markdown-preview tb-marcador-linha-insercao-markdown-preview--pulso"
                      style={{ top: `${topoPxMarcadorInsercaoImagemPreview}px` }}
                      aria-hidden
                    />
                  ) : null}
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponentsPreviewTutorialComAncorasLinha}>
                    {job.result_markdown}
                  </ReactMarkdown>
                </div>
                {colandoImagemClipboardParaInsercaoPreviewTutorial ? (
                  <p className="tb-muted">Salvando imagem colada nos assets…</p>
                ) : null}
                {salvandoInsercaoImagemNoTutorial ? (
                  <p className="tb-muted">Inserindo imagem no tutorial…</p>
                ) : null}
              </>
            ) : (
              <p className="tb-muted">
                {job?.status === "generating_tutorial"
                  ? "Gerando ou atualizando o Markdown…"
                  : "O tutorial aparece aqui quando estiver pronto."}
              </p>
            )}
          </div>
        </section>
      ) : null}

      {fabRegeneracaoTutorialVisivel &&
      !modalProgressoJobAberto &&
      !modalTranscricaoOriginalAberta &&
      !modalListaJobsServidorAberta &&
      !modalEscolherVersaoHistoricoTutorialAberta &&
      !modalGaleriaAssetsImagensAberta &&
      !modalPromptTutorialLitellmAberta &&
      !modalPreviewRegeneracaoSecaoAberto &&
      !modalPreviewRegeneracaoTutorialAberto &&
      !modoEdicaoMarkdownTutorialAtivo &&
      !modoInserirImagemAssetNoPreviewTutorialAtivo
        ? createPortal(
            <div className="tb-fab-regen-wrapper">
              {painelRegeneracaoFabAberto ? (
                <button
                  type="button"
                  className="tb-fab-regen-backdrop"
                  aria-label="Fechar painel de regeneração"
                  onClick={() => setPainelRegeneracaoFabAberto(false)}
                />
              ) : null}
              {painelRegeneracaoFabAberto ? (
                <div
                  className={`tb-fab-regen-panel${
                    jobEhProjetoEmBrancoAtual ? " tb-fab-regen-panel--chat-projeto-em-branco" : ""
                  }${arrastandoArquivosSobreChatFab ? " tb-fab-regen-panel--arrastando-arquivo" : ""}${
                    processandoArquivosAnexoContextoFab ? " tb-fab-regen-panel--processando-anexo" : ""
                  }`}
                  role="dialog"
                  aria-label={
                    jobEhProjetoEmBrancoAtual ? "Chat — atualizar documento" : "Atualizar tutorial"
                  }
                  onPaste={
                    jobEhProjetoEmBrancoAtual
                      ? tratarColarImagemNoPainelFabProjetoEmBrancoTranscribrothers
                      : undefined
                  }
                  onDragEnter={jobEhProjetoEmBrancoAtual ? aoEntrarArrasteChatFabTranscribrothers : undefined}
                  onDragLeave={jobEhProjetoEmBrancoAtual ? aoSairArrasteChatFabTranscribrothers : undefined}
                  onDragOver={
                    jobEhProjetoEmBrancoAtual
                      ? (e) => {
                          e.preventDefault();
                        }
                      : undefined
                  }
                  onDrop={jobEhProjetoEmBrancoAtual ? aoSoltarArquivosChatFabTranscribrothers : undefined}
                >
                  <div className="tb-fab-regen-panel-header">
                    <div className="tb-fab-regen-panel-title-row">
                      <span className="tb-fab-regen-panel-title">
                        {jobEhProjetoEmBrancoAtual
                          ? "Atualizar documento"
                          : jobEhReproducaoBugAtual
                            ? "Atualizar reprodução do bug"
                            : jobEhNotasPropostaAtual
                              ? "Atualizar notas de proposta"
                              : "Atualizar tutorial"}
                      </span>
                      <button
                        type="button"
                        className="tb-fab-regen-info-hint"
                        aria-label="Sobre imagens e pixels na regeneração"
                        title={TEXTO_TOOLTIP_INFO_PIXELS_REGENERACAO_TUTORIAL_FAB_TRANSCRIBROTHERS}
                      >
                        (i)
                      </button>
                    </div>
                    <button
                      type="button"
                      className="tb-fab-regen-fechar"
                      aria-label="Fechar painel"
                      onClick={() => setPainelRegeneracaoFabAberto(false)}
                    >
                      ×
                    </button>
                  </div>
                  {jobEhProjetoEmBrancoAtual ? (
                    <div className="tb-fab-chat-anexos-secao">
                      {anexosContextoFabProjetoEmBranco.length > 0 ||
                      processandoArquivosAnexoContextoFab ||
                      arrastandoArquivosSobreChatFab ? (
                        <div className="tb-fab-chat-corpo" aria-live="polite">
                          {processandoArquivosAnexoContextoFab ? (
                            <p className="tb-muted tb-fab-chat-status">Processando anexos…</p>
                          ) : null}
                          {arrastandoArquivosSobreChatFab ? (
                            <p className="tb-fab-chat-status tb-fab-chat-status--arraste">
                              Solte para anexar ao pedido
                            </p>
                          ) : null}
                          {anexosContextoFabProjetoEmBranco.length > 0 ? (
                            <ul className="tb-fab-anexos-lista" aria-label="Anexos do pedido">
                              {anexosContextoFabProjetoEmBranco.map((anexo, indiceAnexo) => (
                                <li key={anexo.id} className="tb-fab-anexos-item">
                                  <span className="tb-fab-anexos-item-rotulo">
                                    {anexo.tipo === "imagem"
                                      ? `Imagem · ${anexo.nomeArquivo}`
                                      : `Texto · ${rotuloExibicaoAnexoTextoContextoFabUiTranscribrothers(anexo, indiceAnexo)}`}
                                  </span>
                                  <button
                                    type="button"
                                    className="tb-fab-anexos-remover"
                                    aria-label="Remover anexo"
                                    onClick={() =>
                                      setAnexosContextoFabProjetoEmBranco((prev) =>
                                        prev.filter((x) => x.id !== anexo.id),
                                      )
                                    }
                                  >
                                    ×
                                  </button>
                                </li>
                              ))}
                            </ul>
                          ) : null}
                        </div>
                      ) : null}
                      {listaImagensContextoPedidoFabProjetoEmBranco.length > 0 ? (
                        <details className="tb-fab-refs-imagens-details">
                          <summary className="tb-fab-refs-imagens-summary">
                            Imagens que o modelo verá neste pedido
                          </summary>
                          <ol className="tb-fab-refs-imagens-ol">
                            {listaImagensContextoPedidoFabProjetoEmBranco.map((item) => (
                              <li key={item.caminho} className="tb-fab-refs-imagens-li">
                                <strong>Figura {item.figura}</strong> — {item.rotulo} —{" "}
                                <code className="tb-fab-refs-code">{item.caminho}</code>
                              </li>
                            ))}
                          </ol>
                        </details>
                      ) : null}
                    </div>
                  ) : listaReferenciasFigurasImagensMarkdownTutorialFab.length > 0 ? (
                    <details className="tb-fab-refs-imagens-details">
                      <summary className="tb-fab-refs-imagens-summary">
                        Referências no chat (ordem do tutorial)
                      </summary>
                      <ol className="tb-fab-refs-imagens-ol">
                        {listaReferenciasFigurasImagensMarkdownTutorialFab.map((p, i) => (
                          <li key={p} className="tb-fab-refs-imagens-li">
                            <strong>Figura {i + 1}</strong> — <code className="tb-fab-refs-code">{p}</code>
                          </li>
                        ))}
                      </ol>
                    </details>
                  ) : (
                    <p className="tb-muted tb-fab-refs-vazio">
                      Nenhum <code>![](assets/…png)</code> no documento: cite um arquivo em <code>assets/</code> nas
                      instruções para o modelo receber essa imagem.
                    </p>
                  )}
                  <div
                    className={`tb-fab-templates-row${
                      jobEhProjetoEmBrancoAtual ? " tb-fab-templates-row--chat" : ""
                    }`}
                  >
                    {jobEhNotasPropostaAtual ? (
                      <button
                        type="button"
                        className={`tb-fab-template-btn${fabPresetRegeneracaoInteiraTranscribrothers === null && modoPainelFabAtualizarTutorial === "regeneracao_inteira" ? " tb-fab-template-btn--ativo" : ""}`}
                        disabled={
                          regenerandoTutorialMarkdown ||
                          regeneracaoTutorialEmAndamento ||
                          !jobPodeRegenerarSomenteMarkdown
                        }
                        title="Regenera as notas com transcrição, imagens e instruções abaixo"
                        onClick={() => {
                          setModoPainelFabAtualizarTutorial("regeneracao_inteira");
                          setFabPresetRegeneracaoInteiraTranscribrothers(null);
                        }}
                      >
                        Refinar notas
                      </button>
                    ) : null}
                    {jobEhReproducaoBugAtual ? (
                      <button
                        type="button"
                        className={`tb-fab-template-btn${fabPresetRegeneracaoInteiraTranscribrothers === null && modoPainelFabAtualizarTutorial === "regeneracao_inteira" ? " tb-fab-template-btn--ativo" : ""}`}
                        disabled={
                          regenerandoTutorialMarkdown ||
                          regeneracaoTutorialEmAndamento ||
                          !jobPodeRegenerarSomenteMarkdown
                        }
                        title="Regenera o roteiro com cliques, imagens e transcrição; descreva ajustes abaixo"
                        onClick={() => {
                          setModoPainelFabAtualizarTutorial("regeneracao_inteira");
                          setFabPresetRegeneracaoInteiraTranscribrothers(null);
                        }}
                      >
                        Refinar roteiro
                      </button>
                    ) : null}
                    {jobEhReproducaoBugAtual || jobEhNotasPropostaAtual || !jobEhProjetoEmBrancoAtual ? (
                      <button
                        type="button"
                        className={`tb-fab-template-btn${fabPresetRegeneracaoInteiraTranscribrothers === "sem_video" ? " tb-fab-template-btn--ativo" : ""}`}
                        disabled={
                          regenerandoTutorialMarkdown ||
                          regeneracaoTutorialEmAndamento ||
                          !jobPodeRegenerarSomenteMarkdown
                        }
                        title={
                          jobEhReproducaoBugAtual
                            ? "Roteiro autônomo: só texto e imagens, sem links para o vídeo"
                            : jobEhNotasPropostaAtual
                              ? "Notas autônomas: só texto e imagens, sem links para o vídeo"
                            : jobEhProjetoEmBrancoAtual
                              ? "Regenera o documento inteiro só com o Markdown e imagens em assets (sem transcrição de vídeo)"
                              : "Carrega instruções para tutorial sem depender do vídeo; leia o texto e clique em Enviar quando quiser"
                        }
                        onClick={() => {
                          setModoPainelFabAtualizarTutorial("regeneracao_inteira");
                          setFabPresetRegeneracaoInteiraTranscribrothers("sem_video");
                          setInstrucoesRegeneracaoTutorialMarkdown(
                            jobEhReproducaoBugAtual
                              ? TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS
                              : jobEhNotasPropostaAtual
                                ? TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS
                              : jobEhProjetoEmBrancoAtual
                                ? TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_DOCUMENTO_PROJETO_EM_BRANCO_TRANSCRIBROTHERS
                                : TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_TUTORIAL_SEM_REFERENCIAS_VIDEO_DOCUMENTO_AUTONOMO_TRANSCRIBROTHERS,
                          );
                        }}
                      >
                        {jobEhProjetoEmBrancoAtual && !jobEhReproducaoBugAtual && !jobEhNotasPropostaAtual
                          ? "Documento inteiro"
                          : "Sem vídeo"}
                      </button>
                    ) : null}
                    {jobEhProjetoEmBrancoAtual || jobEhReproducaoBugAtual || jobEhNotasPropostaAtual ? null : (
                    <button
                      type="button"
                      className={`tb-fab-template-btn${fabPresetRegeneracaoInteiraTranscribrothers === "revisao_profunda" ? " tb-fab-template-btn--ativo" : ""}`}
                      disabled={
                        regenerandoTutorialMarkdown ||
                        regeneracaoTutorialEmAndamento ||
                        !jobPodeRegenerarSomenteMarkdown
                      }
                      title="Prepara revisão profunda (analista, tópicos e consolidação); clique em Enviar quando quiser iniciar"
                      onClick={() => {
                        setModoPainelFabAtualizarTutorial("regeneracao_inteira");
                        setFabPresetRegeneracaoInteiraTranscribrothers("revisao_profunda");
                      }}
                    >
                      Revisão profunda
                    </button>
                    )}
                    <button
                      type="button"
                      className={`tb-fab-template-btn${modoPainelFabAtualizarTutorial === "edicao_parcial" ? " tb-fab-template-btn--ativo" : ""}`}
                      disabled={
                        !jobPermiteModoEdicaoPorSecaoTutorial ||
                        regenerandoSecaoMarkdownTutorial ||
                        regeneracaoSecaoEmAndamento ||
                        Boolean(previewRegeneracaoSecaoMarkdown) ||
                        Boolean(previewRegeneracaoTutorialMarkdownDocumentoInteiro)
                      }
                      title="Altera só a introdução, um trecho ou uma seção ## — descreva abaixo e envie"
                      onClick={() => {
                        setModoPainelFabAtualizarTutorial("edicao_parcial");
                        setFabPresetRegeneracaoInteiraTranscribrothers(null);
                      }}
                    >
                      Edição parcial
                    </button>
                  </div>
                  {jobEhProjetoEmBrancoAtual ? (
                    <div className="tb-fab-chat-composer">
                      <div className="tb-fab-chat-composer-capsule">
                        <div className="tb-fab-mais-menu-wrap" ref={refMenuMaisConteudoFabTranscribrothers}>
                          <button
                            type="button"
                            className="tb-fab-mais-btn"
                            aria-label="Adicionar conteúdo ao pedido"
                            aria-expanded={menuMaisConteudoFabAberto}
                            aria-haspopup="menu"
                            disabled={
                              processandoArquivosAnexoContextoFab ||
                              regenerandoTutorialMarkdown ||
                              regeneracaoTutorialEmAndamento
                            }
                            onClick={() => setMenuMaisConteudoFabAberto((aberto) => !aberto)}
                          >
                            +
                          </button>
                          {menuMaisConteudoFabAberto ? (
                            <div className="tb-fab-mais-menu" role="menu">
                              <button
                                type="button"
                                className="tb-fab-mais-menu-item"
                                role="menuitem"
                                onClick={() => {
                                  setMenuMaisConteudoFabAberto(false);
                                  setModalTextoAnexoContextoFabAberta(true);
                                }}
                              >
                                Texto
                              </button>
                              <button
                                type="button"
                                className="tb-fab-mais-menu-item"
                                role="menuitem"
                                onClick={() => {
                                  setMenuMaisConteudoFabAberto(false);
                                  refInputImagemAnexoContextoFabTranscribrothers.current?.click();
                                }}
                              >
                                Imagem
                              </button>
                              <button
                                type="button"
                                className="tb-fab-mais-menu-item"
                                role="menuitem"
                                onClick={() => {
                                  setMenuMaisConteudoFabAberto(false);
                                  refInputDocumentoAnexoContextoFabTranscribrothers.current?.click();
                                }}
                              >
                                Arquivo (.pdf, .md, .txt)
                              </button>
                            </div>
                          ) : null}
                          <input
                            ref={refInputImagemAnexoContextoFabTranscribrothers}
                            type="file"
                            accept="image/png,image/jpeg,image/webp,image/gif"
                            className="tb-fab-anexos-input-file"
                            aria-hidden
                            tabIndex={-1}
                            onChange={(e) => {
                              const arquivo = e.target.files?.[0];
                              e.target.value = "";
                              if (arquivo) {
                                void processarArquivoAnexoImagemContextoFabProjetoEmBrancoTranscribrothers(
                                  arquivo,
                                );
                              }
                            }}
                          />
                          <input
                            ref={refInputDocumentoAnexoContextoFabTranscribrothers}
                            type="file"
                            multiple
                            accept=".md,.txt,.pdf,text/plain,text/markdown,application/pdf"
                            className="tb-fab-anexos-input-file"
                            aria-hidden
                            tabIndex={-1}
                            onChange={(e) => {
                              const lista = Array.from(e.target.files ?? []);
                              e.target.value = "";
                              if (lista.length > 0) {
                                void processarListaArquivosAnexoContextoFabTranscribrothers(lista);
                              }
                            }}
                          />
                        </div>
                        <textarea
                          ref={refTextareaInstrucoesChatFabTranscribrothers}
                          id="tb-fab-instrucoes"
                          className="tb-input tb-fab-chat-textarea"
                          rows={3}
                          value={instrucoesRegeneracaoTutorialMarkdown}
                          onChange={(e) => {
                            setInstrucoesRegeneracaoTutorialMarkdown(e.target.value);
                            setFabPresetRegeneracaoInteiraTranscribrothers((preset) =>
                              preset === "sem_video" ? null : preset,
                            );
                            requestAnimationFrame(() => {
                              ajustarAlturaTextareaInstrucoesChatFabTranscribrothers();
                            });
                          }}
                          placeholder={
                            modoPainelFabAtualizarTutorial === "edicao_parcial"
                              ? "O que mudar nesta edição…"
                              : "Mensagem para a IA (opcional)…"
                          }
                        />
                      </div>
                    </div>
                  ) : (
                    <>
                      <label className="tb-label" htmlFor="tb-fab-instrucoes">
                        {modoPainelFabAtualizarTutorial === "edicao_parcial"
                          ? "Edição parcial — o que você quer mudar"
                          : "Regenerar documento inteiro (instruções opcionais)"}
                      </label>
                      <textarea
                        id="tb-fab-instrucoes"
                        className="tb-input tb-fab-textarea"
                        rows={4}
                        value={instrucoesRegeneracaoTutorialMarkdown}
                        onChange={(e) => {
                          setInstrucoesRegeneracaoTutorialMarkdown(e.target.value);
                          setFabPresetRegeneracaoInteiraTranscribrothers((preset) =>
                            preset === "sem_video" ? null : preset,
                          );
                        }}
                        placeholder={
                          modoPainelFabAtualizarTutorial === "edicao_parcial"
                            ? "Ex.: Na intro, deixe mais claro o foco nos relatórios SEEU. Ou: nessa parte da Visão Geral, detalhe com exemplos…"
                            : "Ex.: tom mais formal. Para UI: «Figura 2» ou cole assets/….png"
                        }
                      />
                    </>
                  )}
                  <div
                    className={
                      jobEhProjetoEmBrancoAtual ? "tb-fab-chat-rodape" : "tb-fab-regen-rodape-padrao"
                    }
                  >
                    <button
                      type="button"
                      className={`tb-primary tb-fab-regen-submit${
                        jobEhProjetoEmBrancoAtual ? " tb-fab-regen-submit--chat" : ""
                      }`}
                      disabled={
                        modoPainelFabAtualizarTutorial === "edicao_parcial"
                          ? !jobPermiteModoEdicaoPorSecaoTutorial ||
                            regenerandoSecaoMarkdownTutorial ||
                            regeneracaoSecaoEmAndamento ||
                            Boolean(previewRegeneracaoSecaoMarkdown) ||
                            Boolean(previewRegeneracaoTutorialMarkdownDocumentoInteiro) ||
                            !instrucoesRegeneracaoTutorialMarkdown.trim()
                          : regenerandoTutorialMarkdown ||
                            regeneracaoTutorialEmAndamento ||
                            !jobPodeRegenerarSomenteMarkdown
                      }
                      onClick={() => void enviarPedidoPainelFabAtualizarTutorialTranscribrothers()}
                    >
                      {modoPainelFabAtualizarTutorial === "edicao_parcial"
                        ? regenerandoSecaoMarkdownTutorial || regeneracaoSecaoEmAndamento
                          ? "Pedindo…"
                          : "Enviar"
                        : regenerandoTutorialMarkdown || regeneracaoTutorialEmAndamento
                          ? "Enviando…"
                          : jobEhProjetoEmBrancoAtual
                            ? "Enviar"
                            : jobEhReproducaoBugAtual
                              ? fabPresetRegeneracaoInteiraTranscribrothers === "sem_video"
                                ? "Enviar (sem vídeo)"
                                : "Enviar refinamento"
                              : jobEhNotasPropostaAtual
                                ? fabPresetRegeneracaoInteiraTranscribrothers === "sem_video"
                                  ? "Enviar (sem vídeo)"
                                  : "Enviar refinamento"
                              : fabPresetRegeneracaoInteiraTranscribrothers === "revisao_profunda"
                                ? "Enviar revisão profunda"
                                : fabPresetRegeneracaoInteiraTranscribrothers === "sem_video"
                                  ? "Enviar (sem vídeo)"
                                  : "Enviar regeneração"}
                    </button>
                  </div>
                </div>
              ) : null}
              <button
                type="button"
                className="tb-fab-principal"
                aria-expanded={painelRegeneracaoFabAberto}
                aria-label={
                  painelRegeneracaoFabAberto
                    ? "Fechar opções de atualização"
                    : jobEhProjetoEmBrancoAtual
                      ? "Atualizar documento"
                      : jobEhReproducaoBugAtual
                        ? "Atualizar reprodução do bug"
                        : jobEhNotasPropostaAtual
                          ? "Atualizar notas de proposta"
                        : "Atualizar tutorial"
                }
                title={
                  jobEhProjetoEmBrancoAtual
                    ? "Atualizar documento com IA (edição parcial ou documento inteiro)"
                    : jobEhReproducaoBugAtual
                      ? "Atualizar roteiro de reprodução do bug (refinar, sem vídeo ou edição parcial)"
                      : jobEhNotasPropostaAtual
                        ? "Atualizar notas de proposta (refinar, sem vídeo ou edição parcial)"
                      : "Atualizar tutorial (regenerar inteiro ou edição parcial)"
                }
                onClick={() => setPainelRegeneracaoFabAberto((v) => !v)}
              >
                {regeneracaoTutorialEmAndamento ? "…" : "↻"}
              </button>
            </div>,
            document.body,
          )
        : null}

      {modoEdicaoMarkdownTutorialAtivo && job ? (
        <ComponenteModalEdicaoMarkdownTutorialDuasColunasPreviewAoVivoTranscribrothers
          valorMarkdown={markdownTutorialRascunhoEdicao}
          aoAlterarValorMarkdown={setMarkdownTutorialRascunhoEdicao}
          aoFechar={fecharModalEdicaoMarkdownTutorialTranscribrothers}
          markdownSalvoNoServidorReferenciaParaDetectarAlteracoes={job.result_markdown ?? ""}
          aoSalvar={salvarModalEdicaoMarkdownTutorialTranscribrothers}
          salvando={salvandoMarkdownTutorialEdicaoManual}
          componentsMarkdown={markdownComponents}
          refTextareaEdicaoMarkdown={textareaMarkdownEdicaoTutorialRef}
          jobId={job.id}
          aoAtualizarJobAposInserirAssetImagemMarkdown={setJob}
          aoNotificarToastMarkdown={pushToast}
        />
      ) : null}

      <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
        aberto={confirmacaoExclusaoImagemTutorialMarkdown !== null}
        titulo="Remover imagem do tutorial?"
        mensagem={
          confirmacaoExclusaoImagemTutorialMarkdown
            ? `A referência «${confirmacaoExclusaoImagemTutorialMarkdown.rotuloImagem}» será apagada do Markdown (incluindo o link de tempo do vídeo, se houver logo abaixo). O arquivo PNG em assets/ não é excluído do servidor.`
            : ""
        }
        rotuloConfirmar="Remover"
        rotuloCancelar="Cancelar"
        processando={processandoExclusaoImagemTutorialMarkdown}
        aoConfirmar={() => void confirmarExclusaoImagemDoMarkdownTutorialTranscribrothers()}
        aoCancelar={() => {
          if (!processandoExclusaoImagemTutorialMarkdown) {
            setConfirmacaoExclusaoImagemTutorialMarkdown(null);
          }
        }}
      />

      {job?.id ? (
        <ComponenteModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers
          aberto={modalGaleriaAssetsImagensAberta}
          jobId={job.id}
          aoFechar={() => setModalGaleriaAssetsImagensAberta(false)}
          aoSelecionarImagemParaAnotar={setNomeArquivoImagemAnotacaoModalAberto}
          aoJobAtualizado={(j) => {
            setJob(j);
            if (modoEdicaoMarkdownTutorialAtivo) {
              setMarkdownTutorialRascunhoEdicao(j.result_markdown ?? "");
            }
          }}
          aoNotificarToast={pushToast}
          aoAssetExcluido={(nome) => {
            if (nomeArquivoImagemAnotacaoModalAberto === nome) {
              setNomeArquivoImagemAnotacaoModalAberto(null);
            }
          }}
        />
      ) : null}

      {nomeArquivoImagemAnotacaoModalAberto && job?.id ? (
        <ComponenteModalEditorAnotacaoImagemTutorialFabricJsDuasVersoesTranscribrothers
          jobId={job.id}
          nomeArquivoOriginal={nomeArquivoImagemAnotacaoModalAberto}
          registroAnotacao={mapaAnotacoesImagensTutorial[nomeArquivoImagemAnotacaoModalAberto]}
          processandoGestaoVersoes={processandoAnotacaoImagemTutorial}
          aoFechar={() => setNomeArquivoImagemAnotacaoModalAberto(null)}
          aoSalvarComSucesso={(j) => {
            setJob(j);
            pushToast("Versão anotada salva. A original foi preservada.", "success");
          }}
          aoAlternarVersaoExibicaoNoTutorial={async (nome, versao) => {
            await aoAlternarVersaoExibicaoImagemTutorial(nome, versao);
          }}
          aoRemoverAnotacaoSalva={async (nome) => {
            await aoRemoverAnotacaoImagemTutorial(nome);
          }}
          aoSincronizarMarkdownComVersaoAnotada={async (nome) => {
            await aoSincronizarMarkdownComImagemAnotada(nome);
          }}
          aoSolicitarInserirImagemNoDocumentoMarkdown={iniciarInserirImagemAssetNoDocumentoMarkdownTranscribrothers}
        />
      ) : null}
    </div>
  );
}
