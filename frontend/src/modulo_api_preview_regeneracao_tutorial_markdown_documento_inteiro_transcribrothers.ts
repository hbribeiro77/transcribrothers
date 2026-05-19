/** Pré-visualização da regeneração do tutorial inteiro (fluxos 2.x). */

export type VerificacaoSustentacaoTutorialMarkdownPreviewTranscribrothers = {
  omitida?: boolean;
  motivo?: string;
  sucesso?: boolean;
  classificacao_global?: string;
  mensagem_resumo?: string;
  erro?: string;
};

export type PreviewRegeneracaoTutorialMarkdownDocumentoInteiroTranscribrothers = {
  markdown_antes: string;
  markdown_depois: string;
  markdown_completo_proposto: string;
  instrucoes_usadas: string;
  criado_em: string;
  revisao_profunda_multifase?: boolean;
  instrucoes_pedido_original?: string;
  verificacao_sustentacao_tutorial?: VerificacaoSustentacaoTutorialMarkdownPreviewTranscribrothers | null;
};

export const CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS =
  "regeneracao_tutorial_markdown_preview";

export function extrairPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeStepsJsonTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): PreviewRegeneracaoTutorialMarkdownDocumentoInteiroTranscribrothers | null {
  const raw = steps?.[CHAVE_STEPS_JSON_PREVIEW_REGENERACAO_TUTORIAL_MARKDOWN_DOCUMENTO_INTEIRO_TRANSCRIBROTHERS];
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const antes = String(o.markdown_antes ?? "");
  const depois = String(o.markdown_depois ?? "");
  const proposto = String(o.markdown_completo_proposto ?? depois);
  if (!proposto) return null;
  const rawVer = o.verificacao_sustentacao_tutorial;
  const verificacao_sustentacao_tutorial =
    rawVer && typeof rawVer === "object"
      ? (rawVer as VerificacaoSustentacaoTutorialMarkdownPreviewTranscribrothers)
      : null;
  return {
    markdown_antes: antes,
    markdown_depois: depois,
    markdown_completo_proposto: proposto,
    instrucoes_usadas: String(o.instrucoes_usadas ?? ""),
    criado_em: String(o.criado_em ?? ""),
    revisao_profunda_multifase: o.revisao_profunda_multifase === true,
    instrucoes_pedido_original:
      typeof o.instrucoes_pedido_original === "string" ? o.instrucoes_pedido_original : undefined,
    verificacao_sustentacao_tutorial,
  };
}

export async function aplicarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers(
  jobId: string,
): Promise<Record<string, unknown>> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-tutorial/aplicar`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}

export async function recuperarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroDeHistoricoJobApiTranscribrothers(
  jobId: string,
): Promise<Record<string, unknown>> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-tutorial/recuperar-preview-do-historico`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}

export async function descartarPreviewRegeneracaoTutorialMarkdownDocumentoInteiroJobApiTranscribrothers(
  jobId: string,
): Promise<Record<string, unknown>> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/regenerate-tutorial/descartar`,
    { method: "POST" },
  );
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as Record<string, unknown>;
}
