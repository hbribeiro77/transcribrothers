export type ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers = {
  indice: number;
  linha_heading: string;
};

export type ItemVerificacaoRedundanciaSecaoMarkdownTranscribrothers = {
  tema?: string;
  classificacao?: string;
  secao_ja_cobre?: string;
  trecho_ou_resumo_na_proposta?: string;
  justificativa_curta?: string;
};

export type VerificacaoRedundanciaSecaoMarkdownTranscribrothers = {
  omitida?: boolean;
  motivo?: string;
  sucesso?: boolean;
  classificacao_global?: string;
  mensagem_resumo?: string;
  itens?: ItemVerificacaoRedundanciaSecaoMarkdownTranscribrothers[];
  erro?: string;
};

export type ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers =
  | "secao_inteira"
  | "trecho_local"
  | "a_partir_de";

export type RegeneracaoSecaoMarkdownPreviewStepsJsonTranscribrothers = {
  titulo_secao_heading: string;
  indice_secao: number;
  secao_markdown_antes: string;
  secao_markdown_depois: string;
  markdown_completo_proposto: string;
  instrucoes_usadas: string;
  criado_em: string;
  modo_escopo_edicao?: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers;
  trecho_ancora_informado?: string | null;
  trecho_ancora_resolvido?: string | null;
  zona_editavel_antes?: string | null;
  zona_editavel_depois?: string | null;
  interpretacao_escopo_pedido?: {
    explicacao_curta?: string;
    modo_escopo_edicao?: string;
    confianca?: string;
    trecho_ancora?: string | null;
    titulo_secao_heading?: string | null;
    instrucoes_revisor_limpas?: string;
    pedido_usuario_original?: string;
  } | null;
  instrucoes_pedido_original?: string;
  verificacao_redundancia_outras_secoes?: VerificacaoRedundanciaSecaoMarkdownTranscribrothers | null;
  correcao_redundancia_automatica_aplicada?: boolean;
  correcao_redundancia_automatica_classificacao_disparo?: string;
  secao_markdown_depois_antes_correcao_automatica?: string;
  verificacao_redundancia_outras_secoes_antes_correcao_automatica?: VerificacaoRedundanciaSecaoMarkdownTranscribrothers | null;
};

export const CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS =
  "regeneracao_secao_markdown_preview";

export function extrairPreviewRegeneracaoSecaoMarkdownDeStepsJsonTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): RegeneracaoSecaoMarkdownPreviewStepsJsonTranscribrothers | null {
  const raw = steps?.[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_SECAO_MARKDOWN_TRANSCRIBROTHERS];
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const antes = String(o.secao_markdown_antes ?? "");
  const depois = String(o.secao_markdown_depois ?? "");
  const proposto = String(o.markdown_completo_proposto ?? "");
  if (!antes || !depois || !proposto) return null;
  const rawVer = o.verificacao_redundancia_outras_secoes;
  const verificacao_redundancia_outras_secoes =
    rawVer && typeof rawVer === "object"
      ? (rawVer as VerificacaoRedundanciaSecaoMarkdownTranscribrothers)
      : null;
  return {
    titulo_secao_heading: String(o.titulo_secao_heading ?? ""),
    indice_secao: Number(o.indice_secao ?? 0),
    secao_markdown_antes: antes,
    secao_markdown_depois: depois,
    markdown_completo_proposto: proposto,
    instrucoes_usadas: String(o.instrucoes_usadas ?? ""),
    criado_em: String(o.criado_em ?? ""),
    modo_escopo_edicao:
      o.modo_escopo_edicao === "trecho_local" ||
      o.modo_escopo_edicao === "a_partir_de" ||
      o.modo_escopo_edicao === "secao_inteira"
        ? o.modo_escopo_edicao
        : undefined,
    trecho_ancora_informado:
      typeof o.trecho_ancora_informado === "string" ? o.trecho_ancora_informado : undefined,
    trecho_ancora_resolvido:
      typeof o.trecho_ancora_resolvido === "string" ? o.trecho_ancora_resolvido : undefined,
    zona_editavel_antes: typeof o.zona_editavel_antes === "string" ? o.zona_editavel_antes : undefined,
    zona_editavel_depois: typeof o.zona_editavel_depois === "string" ? o.zona_editavel_depois : undefined,
    interpretacao_escopo_pedido:
      o.interpretacao_escopo_pedido && typeof o.interpretacao_escopo_pedido === "object"
        ? (o.interpretacao_escopo_pedido as RegeneracaoSecaoMarkdownPreviewStepsJsonTranscribrothers["interpretacao_escopo_pedido"])
        : undefined,
    instrucoes_pedido_original:
      typeof o.instrucoes_pedido_original === "string" ? o.instrucoes_pedido_original : undefined,
    verificacao_redundancia_outras_secoes,
    correcao_redundancia_automatica_aplicada: Boolean(o.correcao_redundancia_automatica_aplicada),
    correcao_redundancia_automatica_classificacao_disparo:
      o.correcao_redundancia_automatica_classificacao_disparo === undefined ||
      o.correcao_redundancia_automatica_classificacao_disparo === null
        ? undefined
        : String(o.correcao_redundancia_automatica_classificacao_disparo),
    secao_markdown_depois_antes_correcao_automatica:
      typeof o.secao_markdown_depois_antes_correcao_automatica === "string"
        ? o.secao_markdown_depois_antes_correcao_automatica
        : undefined,
    verificacao_redundancia_outras_secoes_antes_correcao_automatica:
      o.verificacao_redundancia_outras_secoes_antes_correcao_automatica &&
      typeof o.verificacao_redundancia_outras_secoes_antes_correcao_automatica === "object"
        ? (o.verificacao_redundancia_outras_secoes_antes_correcao_automatica as VerificacaoRedundanciaSecaoMarkdownTranscribrothers)
        : undefined,
  };
}

export async function listarSecoesNivel2TutorialMarkdownJobApiTranscribrothers(
  jobId: string,
): Promise<ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers[]> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/tutorial-markdown/secoes-nivel-2`,
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as ResumoSecaoMarkdownNivel2TutorialApiTranscribrothers[];
}

export async function pedirRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(
  jobId: string,
  opcoes: {
    tituloSecaoHeading?: string;
    indiceSecao?: number;
    instrucoesRevisor: string;
    litellmModel?: string;
    modoEscopoEdicao?: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers;
    trechoAncora?: string;
    interpretarEscopoAutomaticamente?: boolean;
    caminhosAssetsPngContextoFab?: string[];
    textosContextoFab?: string[];
  },
): Promise<Record<string, unknown>> {
  const trecho = opcoes.trechoAncora?.trim() || null;
  const interpretar = opcoes.interpretarEscopoAutomaticamente ?? !trecho;
  const modo = interpretar ? "trecho_local" : (opcoes.modoEscopoEdicao ?? "trecho_local");
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-markdown-section`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        titulo_secao_heading: opcoes.tituloSecaoHeading?.trim() || null,
        indice_secao: opcoes.indiceSecao ?? null,
        instrucoes_revisor: opcoes.instrucoesRevisor.trim(),
        litellm_model: opcoes.litellmModel?.trim() || null,
        modo_escopo_edicao: modo,
        trecho_ancora: trecho,
        interpretar_escopo_automaticamente: interpretar,
        caminhos_assets_png_contexto_fab: opcoes.caminhosAssetsPngContextoFab ?? null,
        textos_contexto_fab: opcoes.textosContextoFab ?? null,
      }),
    },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}

export async function aplicarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(
  jobId: string,
): Promise<Record<string, unknown>> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-markdown-section/aplicar`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}

export async function descartarPreviewRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers(
  jobId: string,
): Promise<Record<string, unknown>> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-markdown-section/descartar`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}
