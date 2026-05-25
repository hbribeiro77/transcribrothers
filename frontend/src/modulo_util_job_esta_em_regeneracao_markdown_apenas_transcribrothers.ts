/** Job em regeneração de Markdown (FAB), não no pipeline inicial vídeo→tutorial. */

type JobComStepsJson = {
  status?: string;
  steps_json?: Record<string, unknown> | null;
};

export function jobEstaEmRegeneracaoMarkdownApenasTranscribrothers(
  job: JobComStepsJson | null | undefined,
): boolean {
  if (!job) return false;
  const steps = job.steps_json;
  if (!steps) return false;
  if (steps.regeneracao_apenas_markdown === true) return true;
  if (steps.regeneracao_reproducao_bug === true) return true;
  if (steps.regeneracao_notas_proposta === true) return true;
  const fase = steps.pipeline_fase;
  if (typeof fase !== "string") return false;
  if (fase.startsWith("regenerando_somente_tutorial_litellm")) return true;
  if (fase.startsWith("regenerando_markdown_reproducao_bug")) return true;
  if (fase.startsWith("regenerando_markdown_notas_proposta")) return true;
  if (fase === "regeneracao_tutorial_markdown_preview_pronta") return true;
  return false;
}

/** Ao carregar projeto: não bloquear com modal de pipeline se já há documento e só regeneração está em curso. */
export function deveAbrirModalProgressoAoCarregarProjetoTranscribrothers(
  job: JobComStepsJson & { result_markdown?: string | null },
): boolean {
  const status = job.status ?? "";
  if (status === "completed" || status === "failed" || status === "cancelled") {
    return false;
  }
  if (jobEstaEmRegeneracaoMarkdownApenasTranscribrothers(job)) {
    return false;
  }
  const temMarkdown = Boolean((job.result_markdown ?? "").trim());
  if (temMarkdown && status === "generating_tutorial") {
    return false;
  }
  return true;
}
