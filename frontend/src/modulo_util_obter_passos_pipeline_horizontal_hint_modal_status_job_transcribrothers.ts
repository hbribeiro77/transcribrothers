/**
 * Passos visuais horizontais do modal de status: rótulos curtos na UI e descrições longas em `hintTitulo`.
 */

export type EstadoPassoPipelineHorizontalModalStatusTranscribrothers =
  | "done"
  | "active"
  | "pending"
  | "skipped"
  | "error";

export type IdPassoPipelineHorizontalModalStatusTranscribrothers =
  | "preparacao"
  | "rascunho"
  | "plano_capturas"
  | "capturas"
  | "gerador"
  | "verificacao_imagens"
  | "escopo_edicao_secao"
  | "regeneracao_secao"
  | "redundancia_secao"
  | "preview_secao"
  | "preview_documento"
  | "planejador"
  | "editores"
  | "consolidador"
  | "auditor";

export type PassoPipelineHorizontalModalStatusTranscribrothers = {
  id: IdPassoPipelineHorizontalModalStatusTranscribrothers;
  rotuloCurto: string;
  hintTitulo: string;
  estado: EstadoPassoPipelineHorizontalModalStatusTranscribrothers;
};

/** Qual jornada a barra de passos descreve (alinhado aos fluxos 1 / 2.x da documentação de produto). */
export type ModoFluxoPipelineModalStatusJobTranscribrothers =
  | "pipeline_inicial"
  | "regeneracao_markdown"
  | "revisao_profunda"
  | "edicao_parcial_secao";

export type ContextoPipelineHorizontalModalStatusJobTranscribrothers = {
  modoFluxo: ModoFluxoPipelineModalStatusJobTranscribrothers;
  tituloFluxo: string;
  descricaoFluxo: string;
  passos: PassoPipelineHorizontalModalStatusTranscribrothers[];
};

const ROTULOS_FLUXO_PIPELINE_MODAL_STATUS_JOB_TRANSCRIBROTHERS: Record<
  ModoFluxoPipelineModalStatusJobTranscribrothers,
  { titulo: string; descricao: string }
> = {
  pipeline_inicial: {
    titulo: "Fluxo 1 — Vídeo até tutorial",
    descricao: "Transcrição, capturas de tela e primeira geração do Markdown.",
  },
  regeneracao_markdown: {
    titulo: "Fluxo 2 — Regenerar documento inteiro",
    descricao: "Novo passe ao modelo sobre o tutorial atual (sem reprocessar o vídeo).",
  },
  revisao_profunda: {
    titulo: "Fluxo 2 — Revisão profunda",
    descricao: "Plano estruturado, edição por tópicos e consolidação final.",
  },
  edicao_parcial_secao: {
    titulo: "Fluxo 2 — Edição parcial",
    descricao: "Interpreta o pedido, regenera só a região escolhida e gera pré-visualização para aplicar no editor.",
  },
};

const CHAVE_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS =
  "regeneracao_tutorial_markdown_preview";

const FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS =
  "regeneracao_tutorial_markdown_preview_pronta";

const FASES_EDICAO_PARCIAL_SECAO_MARKDOWN_TRANSCRIBROTHERS = [
  "interpretando_escopo_pedido_edicao_secao_markdown_litellm",
  "validando_escopo_edicao_secao_markdown",
  "escopo_edicao_secao_confirmado",
  "regenerando_secao_markdown_litellm",
  "verificacao_redundancia_secao_markdown_litellm",
  "verificacao_redundancia_secao_markdown_concluida",
  "corrigindo_redundancia_secao_markdown_litellm",
  "verificacao_redundancia_secao_apos_correcao_automatica_litellm",
  "correcao_redundancia_secao_markdown_concluida",
  "regeneracao_secao_markdown_preview_pronta",
] as const;

const FASES_PREPARACAO_CORE_TRANSCRIBROTHERS = new Set([
  "metadados_job_carregados",
  "video_entrada_reutilizado_sem_redownload",
  "audio_wav_reutilizado_sem_reextrair",
  "ffmpeg_extrair_audio",
  "transcrevendo_audio",
  "transcrevendo_audio_janela_litellm_multimodal",
  "transcrevendo_audio_janelas_litellm_multimodal_paralelo",
  "transcrevendo_audio_litellm_multimodal_arquivo_unico",
  "transcricao_concluida",
]);

const FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS = new Set([
  "capturando_frames_png",
  "capturando_frame_png_individual",
  "capturando_frames_png_sob_demanda",
  "capturando_frame_png_sob_demanda",
  "capturando_frames_notas_proposta",
]);

const STATUS_PREPARACAO_ATIVA_TRANSCRIBROTHERS = new Set([
  "pending",
  "downloading",
  "extracting_audio",
  "transcribing",
  "capturing_frames",
]);

function boolDeStepsJsonTranscribrothers(v: unknown): boolean {
  return v === true || v === "true";
}

function faseStringDeStepsTranscribrothers(steps: Record<string, unknown> | null | undefined): string {
  const f = steps?.pipeline_fase;
  return typeof f === "string" ? f.trim() : "";
}

function temPlanoRevisaoProfundaEmStepsTranscribrothers(steps: Record<string, unknown> | null | undefined): boolean {
  const raw = steps?.revisao_profunda_plano_json;
  if (raw == null) return false;
  if (typeof raw === "string") return raw.trim().length > 0;
  return typeof raw === "object";
}

function caminhoRevisaoProfundaDetectadoEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
  fase: string,
): boolean {
  if (!steps) return fase.startsWith("revisao_profunda_");
  return (
    boolDeStepsJsonTranscribrothers(steps.revisao_profunda_multifase) ||
    boolDeStepsJsonTranscribrothers(steps.revisao_profunda_multifase_agendada) ||
    temPlanoRevisaoProfundaEmStepsTranscribrothers(steps) ||
    fase.startsWith("revisao_profunda_")
  );
}

function verificacaoSustentacaoOmitidaEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): boolean {
  const raw = steps?.verificacao_sustentacao_tutorial;
  if (!raw || typeof raw !== "object") return false;
  return boolDeStepsJsonTranscribrothers((raw as Record<string, unknown>).omitida);
}

function verificacaoImagensDuplicadasOmitidaEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): boolean {
  const raw = steps?.verificacao_imagens_duplicadas_tutorial;
  if (!raw || typeof raw !== "object") return false;
  return boolDeStepsJsonTranscribrothers((raw as Record<string, unknown>).omitida);
}

function capturaFramesSobDemandaEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): boolean {
  if (steps?.destino_apos_transcricao === "notas_proposta_funcionalidade") return true;
  return boolDeStepsJsonTranscribrothers(steps?.tutorial_captura_frames_sob_demanda);
}

function planoCapturasAplicavelNesteJobTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
  fase: string,
): boolean {
  if (!capturaFramesSobDemandaEmStepsTranscribrothers(steps)) return false;
  if (fase === "planejando_instantes_captura_frames_tutorial") return true;
  if (fase === "planejando_instantes_captura_notas_proposta") return true;
  if (steps?.planejamento_instantes_captura_frames != null) return true;
  if (steps?.planejamento_instantes_captura_notas_proposta != null) return true;
  return false;
}

function estadoPassoPipelineTranscribrothers(
  opts: {
    erro: boolean;
    ativo: boolean;
    concluido: boolean;
    omitido?: boolean;
    pendenteAposPrecedente?: boolean;
  },
): EstadoPassoPipelineHorizontalModalStatusTranscribrothers {
  if (opts.omitido) return "skipped";
  if (opts.erro) return "error";
  if (opts.ativo) return "active";
  if (opts.concluido) return "done";
  if (opts.pendenteAposPrecedente) return "pending";
  return "pending";
}

function inferirIndicePassoFalhaPipelineInicialTranscribrothers(fase: string): number {
  if (FASES_PREPARACAO_CORE_TRANSCRIBROTHERS.has(fase)) return 0;
  if (fase === "gerando_rascunho_tutorial_sem_imagens") return 1;
  if (fase === "gerando_rascunho_notas_proposta") return 1;
  if (fase === "planejando_instantes_captura_frames_tutorial") return 2;
  if (fase === "planejando_instantes_captura_notas_proposta") return 2;
  if (FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fase)) return 3;
  if (fase === "gerando_tutorial_http_chat_completions") return 4;
  if (fase.startsWith("verificacao_imagens_duplicadas")) return 5;
  if (fase.startsWith("verificacao_sustentacao")) return 6;
  return 0;
}

function faseIndicaRegeneracaoMarkdownApenasTranscribrothers(fase: string): boolean {
  return (
    fase.startsWith("regenerando_somente_tutorial_litellm") ||
    fase.startsWith("regenerando_markdown_reproducao_bug") ||
    fase.startsWith("regenerando_markdown_notas_proposta")
  );
}

function inferirIndicePassoFalhaPipelineRegeneracaoSimplesTranscribrothers(fase: string): number {
  if (faseIndicaRegeneracaoMarkdownApenasTranscribrothers(fase)) {
    return 0;
  }
  if (fase.startsWith("verificacao_imagens_duplicadas")) return 1;
  if (fase.startsWith("verificacao_sustentacao")) return 2;
  if (fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS) return 3;
  return 0;
}

function previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): boolean {
  return steps?.[CHAVE_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS] != null;
}

function montarPassoPreviewDocumentoRegeneracaoTutorialTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
  falhou: boolean,
  indiceErro: number,
  indicePassoPreview: number,
  precedenteConcluido: boolean,
  terminal: boolean,
  status: string,
  fase: string,
): PassoPipelineHorizontalModalStatusTranscribrothers {
  const previewPendente = previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps);
  const previewAplicado = typeof steps?.regeneracao_tutorial_aplicada_em === "string";
  const regenSoMarkdown = boolDeStepsJsonTranscribrothers(steps?.regeneracao_apenas_markdown);
  const omitidoSemBlobPreview =
    terminal &&
    status === "completed" &&
    regenSoMarkdown &&
    !previewPendente &&
    !previewAplicado &&
    fase !== FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS;
  return {
    id: "preview_documento",
    rotuloCurto: "Preview",
    hintTitulo: omitidoSemBlobPreview
      ? "Não há pré-visualização neste job (regeneração antiga, backend desatualizado na época, ou já aplicou/descartou). Use «Atualizar tutorial» (FAB ↻) para gerar outra regeneração — ao terminar, o passo fica ativo e abre o modal antes/depois."
      : previewPendente && !previewAplicado
        ? "Pré-visualização pendente: clique neste passo para abrir o comparativo antes/depois e aplicar ou descartar."
        : "Documento proposto pronto para comparar antes/depois. Aplique para gravar no job ou descarte para manter o tutorial atual.",
    estado: estadoPassoPipelineTranscribrothers({
      erro: falhou && indiceErro === indicePassoPreview,
      ativo: previewPendente && !previewAplicado,
      concluido: previewAplicado,
      omitido: omitidoSemBlobPreview,
      pendenteAposPrecedente: precedenteConcluido && !omitidoSemBlobPreview,
    }),
  };
}

function inferirIndicePassoFalhaPipelineRevisaoProfundaTranscribrothers(fase: string): number {
  if (
    fase === "revisao_profunda_analista_litellm" ||
    fase === "revisao_profunda_plano_concluido" ||
    fase === "revisao_profunda_analista_erro_parse"
  ) {
    return 0;
  }
  if (fase === "revisao_profunda_worker_topico") return 1;
  if (fase === "revisao_profunda_editor_final") return 2;
  if (fase.startsWith("verificacao_imagens_duplicadas")) return 3;
  if (fase.startsWith("verificacao_sustentacao")) return 4;
  if (fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS) return 5;
  return 0;
}

function montarPassosPipelineInicialUploadVideoTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
  fase: string,
  terminal: boolean,
  falhou: boolean,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  const indiceErro = falhou ? inferirIndicePassoFalhaPipelineInicialTranscribrothers(fase) : -1;

  const capturaSobDemanda = capturaFramesSobDemandaEmStepsTranscribrothers(steps);
  const rascunhoAplicavel = capturaSobDemanda;
  const planoCapturasAplicavel = planoCapturasAplicavelNesteJobTranscribrothers(steps, fase);

  const preparacaoConcluida =
    fase === "transcricao_concluida" ||
    (fase.length > 0 &&
      !FASES_PREPARACAO_CORE_TRANSCRIBROTHERS.has(fase) &&
      fase !== "gerando_rascunho_tutorial_sem_imagens" &&
      fase !== "planejando_instantes_captura_frames_tutorial" &&
      !FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fase));

  const preparacaoAtiva =
    !terminal &&
    !preparacaoConcluida &&
    (STATUS_PREPARACAO_ATIVA_TRANSCRIBROTHERS.has(status) ||
      (FASES_PREPARACAO_CORE_TRANSCRIBROTHERS.has(fase) && fase !== "transcricao_concluida"));

  const rascunhoAtivo =
    !terminal &&
    (fase === "gerando_rascunho_tutorial_sem_imagens" || fase === "gerando_rascunho_notas_proposta");
  const rascunhoConcluido =
    rascunhoAplicavel &&
    !rascunhoAtivo &&
    (boolDeStepsJsonTranscribrothers(steps?.tutorial_rascunho_sem_imagens_ok) ||
      boolDeStepsJsonTranscribrothers(steps?.notas_proposta_rascunho_sem_imagens_ok) ||
      fase === "planejando_instantes_captura_frames_tutorial" ||
      fase === "planejando_instantes_captura_notas_proposta" ||
      FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fase) ||
      preparacaoConcluida);

  const planoAtivo =
    !terminal &&
    (fase === "planejando_instantes_captura_frames_tutorial" ||
      fase === "planejando_instantes_captura_notas_proposta");
  const planoConcluido =
    planoCapturasAplicavel &&
    !planoAtivo &&
    (FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fase) || preparacaoConcluida);

  const capturasAtivo = !terminal && FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fase);
  const capturasConcluido =
    !capturasAtivo &&
    (fase === "gerando_tutorial_http_chat_completions" ||
      fase === "gerando_markdown_notas_proposta_litellm" ||
      fase.startsWith("verificacao_") ||
      (terminal && status === "completed"));

  const geradorAtivo =
    !terminal &&
    (fase === "gerando_tutorial_http_chat_completions" || fase === "gerando_markdown_notas_proposta_litellm");
  const geradorConcluido =
    !geradorAtivo &&
    (fase.startsWith("verificacao_") || (terminal && status === "completed"));

  const verifImagensOmitida = verificacaoImagensDuplicadasOmitidaEmStepsTranscribrothers(steps);
  const verifImagensAtivo = !terminal && fase.startsWith("verificacao_imagens_duplicadas");
  const verifImagensConcluido =
    fase === "verificacao_imagens_duplicadas_tutorial_concluida" ||
    fase.startsWith("verificacao_sustentacao") ||
    (terminal && status === "completed" && !verifImagensAtivo);

  const auditorOmitido = verificacaoSustentacaoOmitidaEmStepsTranscribrothers(steps);
  const auditorAtivo =
    !terminal &&
    (fase === "verificacao_sustentacao_tutorial_litellm" ||
      fase === "verificacao_sustentacao_notas_proposta_litellm");
  const auditorConcluido =
    fase === "verificacao_sustentacao_tutorial_concluida" ||
    fase === "verificacao_sustentacao_notas_proposta_concluida" ||
    (terminal && status === "completed" && !auditorOmitido && !auditorAtivo);

  const precedenteRascunhoOk = preparacaoConcluida || rascunhoConcluido;
  const precedentePlanoOk =
    !rascunhoAplicavel || rascunhoConcluido || (!planoCapturasAplicavel && precedenteRascunhoOk);
  const precedenteCapturasOk =
    (!planoCapturasAplicavel && precedenteRascunhoOk && preparacaoConcluida) ||
    (planoCapturasAplicavel && planoConcluido) ||
    capturasConcluido;

  return [
    {
      id: "preparacao",
      rotuloCurto: "Preparação",
      hintTitulo:
        "Metadados do job, extração de áudio (ffmpeg) e transcrição do vídeo. É a base antes de qualquer captura ou geração do tutorial.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 0,
        ativo: preparacaoAtiva,
        concluido: preparacaoConcluida,
      }),
    },
    {
      id: "rascunho",
      rotuloCurto: "Rascunho",
      hintTitulo:
        "Com captura sob demanda: gera um tutorial provisório só com texto e links ?t= para decidir onde tirar screenshots, antes das capturas reais.",
      estado: rascunhoAplicavel
        ? estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 1,
            ativo: rascunhoAtivo,
            concluido: rascunhoConcluido,
            pendenteAposPrecedente: preparacaoConcluida,
          })
        : "skipped",
    },
    {
      id: "plano_capturas",
      rotuloCurto: "Plano capturas",
      hintTitulo:
        "Planejamento (LiteLLM) dos instantes de captura a partir do rascunho e da transcrição, respeitando margem mínima entre links temporais.",
      estado: planoCapturasAplicavel
        ? estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 2,
            ativo: planoAtivo,
            concluido: planoConcluido,
            pendenteAposPrecedente: precedenteRascunhoOk,
          })
        : "skipped",
    },
    {
      id: "capturas",
      rotuloCurto: "Capturas",
      hintTitulo:
        "Screenshots PNG do vídeo (ffmpeg), gravados em assets/ e referenciados no tutorial. No modo legado usa amostragem por segmentos da transcrição.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 3,
        ativo: capturasAtivo,
        concluido: capturasConcluido,
        pendenteAposPrecedente: precedentePlanoOk || (preparacaoConcluida && !capturaSobDemanda),
      }),
    },
    {
      id: "gerador",
      rotuloCurto: "Gerador",
      hintTitulo:
        "Gera o tutorial em Markdown final (transcrição + imagens). Com captura sob demanda, incorpora o rascunho e as capturas já feitas.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 4,
        ativo: geradorAtivo,
        concluido: geradorConcluido,
        pendenteAposPrecedente: precedenteCapturasOk,
      }),
    },
    {
      id: "verificacao_imagens",
      rotuloCurto: "Imagens",
      hintTitulo:
        "Verificação por visão: remove ou funde referências a screenshots visualmente duplicadas no Markdown. Pode ser desligada no .env.",
      estado: verifImagensOmitida
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 5,
            ativo: verifImagensAtivo,
            concluido: verifImagensConcluido,
            pendenteAposPrecedente: geradorConcluido,
          }),
    },
    {
      id: "auditor",
      rotuloCurto: "Auditor",
      hintTitulo:
        "Verificação automática do tutorial em relação à transcrição (inconsistências). Pode ser desligada no servidor ou em Configurações.",
      estado: auditorOmitido
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 6,
            ativo: auditorAtivo,
            concluido: auditorConcluido,
            pendenteAposPrecedente: verifImagensConcluido || verifImagensOmitida,
          }),
    },
  ];
}

function montarPassosPipelineRegeneracaoSimplesTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
  fase: string,
  terminal: boolean,
  falhou: boolean,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  const indiceErro = falhou ? inferirIndicePassoFalhaPipelineRegeneracaoSimplesTranscribrothers(fase) : -1;

  const geradorAtivo = !terminal && faseIndicaRegeneracaoMarkdownApenasTranscribrothers(fase);
  const geradorConcluido =
    !geradorAtivo &&
    (fase.startsWith("verificacao_") ||
      fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
      previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
      fase === "regeneracao_tutorial_concluida" ||
      (terminal && status === "completed"));

  const verifImagensOmitida = verificacaoImagensDuplicadasOmitidaEmStepsTranscribrothers(steps);
  const verifImagensAtivo = !terminal && fase.startsWith("verificacao_imagens_duplicadas");
  const verifImagensConcluido =
    fase === "verificacao_imagens_duplicadas_tutorial_concluida" ||
    fase.startsWith("verificacao_sustentacao") ||
    fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
    fase === "regeneracao_tutorial_concluida" ||
    previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
    (terminal && status === "completed");

  const auditorOmitido = verificacaoSustentacaoOmitidaEmStepsTranscribrothers(steps);
  const auditorAtivo = !terminal && fase === "verificacao_sustentacao_tutorial_litellm";
  const auditorConcluido =
    fase === "verificacao_sustentacao_tutorial_concluida" ||
    fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
    fase === "regeneracao_tutorial_concluida" ||
    previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
    (terminal && status === "completed" && !auditorOmitido);

  const passoPreview = montarPassoPreviewDocumentoRegeneracaoTutorialTranscribrothers(
    steps,
    falhou,
    indiceErro,
    3,
    verifImagensConcluido || verifImagensOmitida,
    terminal,
    status,
    fase,
  );

  return [
    {
      id: "preparacao",
      rotuloCurto: "Preparação",
      hintTitulo: "Regeneração: reutiliza transcrição, frames e snapshot já gravados no job (sem reprocessar o vídeo).",
      estado: "done",
    },
    {
      id: "gerador",
      rotuloCurto: "Gerador",
      hintTitulo:
        "Regenera o documento inteiro em um passe ao modelo (Markdown atual + transcrição + imagens anexadas conforme instruções).",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 0,
        ativo: geradorAtivo,
        concluido: geradorConcluido,
      }),
    },
    {
      id: "verificacao_imagens",
      rotuloCurto: "Imagens",
      hintTitulo: "Verificação de screenshots duplicadas no Markdown regenerado.",
      estado: verifImagensOmitida
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 1,
            ativo: verifImagensAtivo,
            concluido: verifImagensConcluido,
            pendenteAposPrecedente: geradorConcluido,
          }),
    },
    {
      id: "auditor",
      rotuloCurto: "Auditor",
      hintTitulo: "Verificação tutorial vs transcrição após a regeneração.",
      estado: auditorOmitido
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 2,
            ativo: auditorAtivo,
            concluido: auditorConcluido,
            pendenteAposPrecedente: verifImagensConcluido || verifImagensOmitida,
          }),
    },
    passoPreview,
  ];
}

function montarPassosPipelineRevisaoProfundaTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
  fase: string,
  terminal: boolean,
  falhou: boolean,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  const indiceErro = falhou ? inferirIndicePassoFalhaPipelineRevisaoProfundaTranscribrothers(fase) : -1;

  const planoAtivo =
    !terminal &&
    (fase === "revisao_profunda_analista_litellm" ||
      fase === "revisao_profunda_plano_concluido" ||
      fase === "revisao_profunda_analista_erro_parse");
  const planoConcluido =
    !planoAtivo &&
    (fase === "revisao_profunda_worker_topico" ||
      fase === "revisao_profunda_editor_final" ||
      fase.startsWith("verificacao_") ||
      fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
      fase === "regeneracao_tutorial_concluida" ||
      previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
      (terminal && status === "completed"));

  const editoresAtivo = !terminal && fase === "revisao_profunda_worker_topico";
  const editoresConcluido =
    !editoresAtivo &&
    (fase === "revisao_profunda_editor_final" ||
      fase.startsWith("verificacao_") ||
      fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
      fase === "regeneracao_tutorial_concluida" ||
      previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
      (terminal && status === "completed"));

  const consolidadorAtivo = !terminal && fase === "revisao_profunda_editor_final";
  const consolidadorConcluido =
    !consolidadorAtivo &&
    (fase.startsWith("verificacao_") ||
      fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
      previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
      fase === "regeneracao_tutorial_concluida" ||
      (terminal && status === "completed"));

  const verifImagensOmitida = verificacaoImagensDuplicadasOmitidaEmStepsTranscribrothers(steps);
  const verifImagensAtivo = !terminal && fase.startsWith("verificacao_imagens_duplicadas");
  const verifImagensConcluido =
    fase === "verificacao_imagens_duplicadas_tutorial_concluida" ||
    fase.startsWith("verificacao_sustentacao") ||
    fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
    fase === "regeneracao_tutorial_concluida" ||
    previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
    (terminal && status === "completed");

  const auditorOmitido = verificacaoSustentacaoOmitidaEmStepsTranscribrothers(steps);
  const auditorAtivo = !terminal && fase === "verificacao_sustentacao_tutorial_litellm";
  const auditorConcluido =
    fase === "verificacao_sustentacao_tutorial_concluida" ||
    fase === FASE_PIPELINE_PREVIEW_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_PRONTA_TRANSCRIBROTHERS ||
    fase === "regeneracao_tutorial_concluida" ||
    previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps) ||
    (terminal && status === "completed" && !auditorOmitido);

  const passoPreview = montarPassoPreviewDocumentoRegeneracaoTutorialTranscribrothers(
    steps,
    falhou,
    indiceErro,
    5,
    verifImagensConcluido || verifImagensOmitida,
    terminal,
    status,
    fase,
  );

  return [
    {
      id: "preparacao",
      rotuloCurto: "Preparação",
      hintTitulo: "Revisão profunda: usa snapshot e tutorial já existentes (sem nova transcrição nem capturas).",
      estado: "done",
    },
    {
      id: "planejador",
      rotuloCurto: "Planejador",
      hintTitulo:
        "Analista lê transcrição, frames e tutorial atual e devolve um plano estruturado (JSON) com tópicos a aprofundar.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 0,
        ativo: planoAtivo,
        concluido: planoConcluido,
      }),
    },
    {
      id: "editores",
      rotuloCurto: "Editores",
      hintTitulo:
        "Um passe ao modelo por tópico do plano. O detalhe tópico x/y aparece na linha de progresso quando este passo estiver ativo.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 1,
        ativo: editoresAtivo,
        concluido: editoresConcluido,
        pendenteAposPrecedente: planoConcluido,
      }),
    },
    {
      id: "consolidador",
      rotuloCurto: "Consolidador",
      hintTitulo: "Harmoniza o Markdown completo após os passes por tópico (editor final multimodal).",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 2,
        ativo: consolidadorAtivo,
        concluido: consolidadorConcluido,
        pendenteAposPrecedente: editoresConcluido,
      }),
    },
    {
      id: "verificacao_imagens",
      rotuloCurto: "Imagens",
      hintTitulo: "Verificação de screenshots duplicadas após a consolidação.",
      estado: verifImagensOmitida
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 3,
            ativo: verifImagensAtivo,
            concluido: verifImagensConcluido,
            pendenteAposPrecedente: consolidadorConcluido,
          }),
    },
    {
      id: "auditor",
      rotuloCurto: "Auditor",
      hintTitulo: "Verificação tutorial vs transcrição após a revisão profunda.",
      estado: auditorOmitido
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 4,
            ativo: auditorAtivo,
            concluido: auditorConcluido,
            pendenteAposPrecedente: verifImagensConcluido || verifImagensOmitida,
          }),
    },
    passoPreview,
  ];
}

function fasePertenceEdicaoParcialSecaoMarkdownTranscribrothers(fase: string): boolean {
  return FASES_EDICAO_PARCIAL_SECAO_MARKDOWN_TRANSCRIBROTHERS.some((p) => fase === p || fase.startsWith(p));
}

/** Só trata como edição parcial quando essa execução é (ou foi) realmente o fluxo 2.3. */
function edicaoParcialSecaoMarkdownComoFluxoAtualEmStepsTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
  fase: string,
): boolean {
  if (!steps) return false;
  const previewPendente = steps.regeneracao_secao_markdown_preview != null;
  if (previewPendente) return true;
  if (typeof steps.regeneracao_secao_heading === "string" && steps.regeneracao_secao_heading.trim()) {
    return true;
  }
  if (status === "generating_tutorial" && fasePertenceEdicaoParcialSecaoMarkdownTranscribrothers(fase)) {
    return true;
  }
  // Fase residual após aplicar/descartar preview — não confundir com fluxo 1 concluído.
  if (fase === "regeneracao_secao_markdown_preview_pronta" && !previewPendente) {
    return false;
  }
  if (status === "completed" && fasePertenceEdicaoParcialSecaoMarkdownTranscribrothers(fase)) {
    return previewPendente;
  }
  return false;
}

function redundanciaSecaoOmitidaEmStepsTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): boolean {
  const preview = steps?.regeneracao_secao_markdown_preview;
  if (preview && typeof preview === "object") {
    const ver = (preview as Record<string, unknown>).verificacao_redundancia_outras_secoes;
    if (ver && typeof ver === "object") {
      return boolDeStepsJsonTranscribrothers((ver as Record<string, unknown>).omitida);
    }
  }
  const raw = steps?.verificacao_redundancia_secao_markdown;
  if (raw && typeof raw === "object") {
    return boolDeStepsJsonTranscribrothers((raw as Record<string, unknown>).omitida);
  }
  return false;
}

function inferirIndicePassoFalhaPipelineEdicaoParcialSecaoTranscribrothers(fase: string): number {
  if (
    fase === "interpretando_escopo_pedido_edicao_secao_markdown_litellm" ||
    fase === "validando_escopo_edicao_secao_markdown" ||
    fase === "escopo_edicao_secao_confirmado"
  ) {
    return 0;
  }
  if (fase === "regenerando_secao_markdown_litellm") return 1;
  if (
    fase.startsWith("verificacao_redundancia_secao") ||
    fase.startsWith("corrigindo_redundancia_secao") ||
    fase.startsWith("correcao_redundancia_secao")
  ) {
    return 2;
  }
  if (fase === "regeneracao_secao_markdown_preview_pronta") return 3;
  return 0;
}

function montarPassosPipelineEdicaoParcialSecaoMarkdownTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
  fase: string,
  terminal: boolean,
  falhou: boolean,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  const indiceErro = falhou ? inferirIndicePassoFalhaPipelineEdicaoParcialSecaoTranscribrothers(fase) : -1;
  const previewPendente = steps?.regeneracao_secao_markdown_preview != null;
  const previewAplicado = typeof steps?.regeneracao_secao_aplicada_em === "string";

  const escopoAtivo =
    !terminal &&
    (fase === "interpretando_escopo_pedido_edicao_secao_markdown_litellm" ||
      fase === "validando_escopo_edicao_secao_markdown");
  const escopoConcluido =
    !escopoAtivo &&
    (fase === "escopo_edicao_secao_confirmado" ||
      fase === "regenerando_secao_markdown_litellm" ||
      fasePertenceEdicaoParcialSecaoMarkdownTranscribrothers(fase) ||
      previewPendente ||
      previewAplicado ||
      (terminal && status === "completed"));

  const secaoAtivo = !terminal && fase === "regenerando_secao_markdown_litellm";
  const secaoConcluido =
    !secaoAtivo &&
    (fase.startsWith("verificacao_redundancia_secao") ||
      fase.startsWith("corrigindo_redundancia") ||
      fase.startsWith("correcao_redundancia") ||
      fase === "regeneracao_secao_markdown_preview_pronta" ||
      previewPendente ||
      previewAplicado ||
      (terminal && status === "completed"));

  const redundanciaOmitida = redundanciaSecaoOmitidaEmStepsTranscribrothers(steps);
  const redundanciaAtivo =
    !terminal &&
    (fase === "verificacao_redundancia_secao_markdown_litellm" ||
      fase === "corrigindo_redundancia_secao_markdown_litellm" ||
      fase === "verificacao_redundancia_secao_apos_correcao_automatica_litellm");
  const redundanciaConcluido =
    !redundanciaAtivo &&
    (fase === "verificacao_redundancia_secao_markdown_concluida" ||
      fase === "correcao_redundancia_secao_markdown_concluida" ||
      fase === "regeneracao_secao_markdown_preview_pronta" ||
      previewPendente ||
      previewAplicado ||
      (terminal && status === "completed" && !redundanciaOmitida));

  const previewAtivo = previewPendente && !previewAplicado;
  const previewConcluido = previewAplicado;

  return [
    {
      id: "escopo_edicao_secao",
      rotuloCurto: "Escopo",
      hintTitulo:
        "Interpreta ou valida o pedido em linguagem natural: qual seção ##, trecho ou «a partir de» será editado.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 0,
        ativo: escopoAtivo,
        concluido: escopoConcluido,
      }),
    },
    {
      id: "regeneracao_secao",
      rotuloCurto: "Seção",
      hintTitulo: "Chamada ao modelo para reescrever só a região delimitada, mantendo o restante do tutorial.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 1,
        ativo: secaoAtivo,
        concluido: secaoConcluido,
        pendenteAposPrecedente: escopoConcluido,
      }),
    },
    {
      id: "redundancia_secao",
      rotuloCurto: "Redundância",
      hintTitulo:
        "Verifica se o trecho proposto repete conteúdo de outras seções; pode corrigir automaticamente conforme Configurações.",
      estado: redundanciaOmitida
        ? "skipped"
        : estadoPassoPipelineTranscribrothers({
            erro: indiceErro === 2,
            ativo: redundanciaAtivo,
            concluido: redundanciaConcluido,
            pendenteAposPrecedente: secaoConcluido,
          }),
    },
    {
      id: "preview_secao",
      rotuloCurto: "Preview",
      hintTitulo:
        "Pré-visualização pronta no editor: aplique para gravar no job ou descarte. Enquanto pendente, o passo fica ativo.",
      estado: estadoPassoPipelineTranscribrothers({
        erro: indiceErro === 3,
        ativo: previewAtivo,
        concluido: previewConcluido,
        pendenteAposPrecedente: redundanciaConcluido || redundanciaOmitida,
      }),
    },
  ];
}

export function resolverModoFluxoPipelineModalStatusJobTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
): ModoFluxoPipelineModalStatusJobTranscribrothers {
  const fase = faseStringDeStepsTranscribrothers(steps);
  const regeneracaoSoMd = boolDeStepsJsonTranscribrothers(steps?.regeneracao_apenas_markdown);
  const multifase = boolDeStepsJsonTranscribrothers(steps?.revisao_profunda_multifase);
  const deepPath = caminhoRevisaoProfundaDetectadoEmStepsTranscribrothers(steps, fase);

  if (edicaoParcialSecaoMarkdownComoFluxoAtualEmStepsTranscribrothers(status, steps, fase)) {
    return "edicao_parcial_secao";
  }
  if (previewRegeneracaoTutorialDocumentoInteiroPendenteEmStepsTranscribrothers(steps)) {
    const raw = steps?.[CHAVE_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS];
    if (raw && typeof raw === "object" && boolDeStepsJsonTranscribrothers((raw as Record<string, unknown>).revisao_profunda_multifase)) {
      return "revisao_profunda";
    }
    return "regeneracao_markdown";
  }
  if (deepPath) {
    return "revisao_profunda";
  }
  if (regeneracaoSoMd && !multifase) {
    return "regeneracao_markdown";
  }
  if (boolDeStepsJsonTranscribrothers(steps?.regeneracao_reproducao_bug)) {
    return "regeneracao_markdown";
  }
  if (boolDeStepsJsonTranscribrothers(steps?.regeneracao_notas_proposta)) {
    return "regeneracao_markdown";
  }
  if (faseIndicaRegeneracaoMarkdownApenasTranscribrothers(fase)) {
    return "regeneracao_markdown";
  }
  return "pipeline_inicial";
}

function obterPassosPipelinePorModoFluxoTranscribrothers(
  modoFluxo: ModoFluxoPipelineModalStatusJobTranscribrothers,
  status: string,
  steps: Record<string, unknown> | null | undefined,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  const fase = faseStringDeStepsTranscribrothers(steps);
  const terminal = status === "completed" || status === "failed" || status === "cancelled";
  const falhou = status === "failed";

  switch (modoFluxo) {
    case "revisao_profunda":
      return montarPassosPipelineRevisaoProfundaTranscribrothers(status, steps, fase, terminal, falhou);
    case "regeneracao_markdown":
      return montarPassosPipelineRegeneracaoSimplesTranscribrothers(status, steps, fase, terminal, falhou);
    case "edicao_parcial_secao":
      return montarPassosPipelineEdicaoParcialSecaoMarkdownTranscribrothers(
        status,
        steps,
        fase,
        terminal,
        falhou,
      );
    default:
      return montarPassosPipelineInicialUploadVideoTranscribrothers(status, steps, fase, terminal, falhou);
  }
}

/** Contexto completo da barra de pipeline na modal de status (fluxo + passos). */
export function obterContextoPipelineHorizontalModalStatusJobTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
): ContextoPipelineHorizontalModalStatusJobTranscribrothers {
  const modoFluxo = resolverModoFluxoPipelineModalStatusJobTranscribrothers(status, steps);
  const rotulos = ROTULOS_FLUXO_PIPELINE_MODAL_STATUS_JOB_TRANSCRIBROTHERS[modoFluxo];
  return {
    modoFluxo,
    tituloFluxo: rotulos.titulo,
    descricaoFluxo: rotulos.descricao,
    passos: obterPassosPipelinePorModoFluxoTranscribrothers(modoFluxo, status, steps),
  };
}

/**
 * Devolve os passos da pipeline com estado visual e hints (modal de status).
 * Prefira `obterContextoPipelineHorizontalModalStatusJobTranscribrothers` quando precisar do rótulo do fluxo.
 */
export function obterPassosPipelineHorizontalHintParaModalStatusJobTranscribrothers(
  status: string,
  steps: Record<string, unknown> | null | undefined,
): PassoPipelineHorizontalModalStatusTranscribrothers[] {
  return obterContextoPipelineHorizontalModalStatusJobTranscribrothers(status, steps).passos;
}

/** Texto completo para o painel de descrição no modal. */
export function montarTextoHintExibicaoPainelPassoPipelineModalStatusTranscribrothers(
  p: PassoPipelineHorizontalModalStatusTranscribrothers,
  fasePipeline: string,
  linhaDetalheProgressoJob: string,
): string {
  const detalheLinha =
    linhaDetalheProgressoJob.trim() &&
    ((p.id === "editores" && fasePipeline === "revisao_profunda_worker_topico") ||
      (p.id === "capturas" && FASES_CAPTURAS_FRAMES_TRANSCRIBROTHERS.has(fasePipeline)))
      ? ` ${linhaDetalheProgressoJob.trim()}`
      : "";

  if (p.estado === "skipped" && !p.hintTitulo.trim()) {
    return "Passo não aplicável neste fluxo.";
  }
  if (p.estado === "skipped") {
    return p.id === "auditor" || p.id === "verificacao_imagens"
      ? p.hintTitulo
      : `${p.hintTitulo} Passo não aplicável neste fluxo.`;
  }
  return `${p.hintTitulo}${detalheLinha}`;
}
