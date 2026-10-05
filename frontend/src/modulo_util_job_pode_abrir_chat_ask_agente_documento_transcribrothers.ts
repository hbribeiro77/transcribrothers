export function jobPodeAbrirChatAskAgenteDocumentoTranscribrothers(
  job: {
    result_markdown?: string | null;
    steps_json?: Record<string, unknown> | null;
  } | null,
): boolean {
  if (job === null) {
    return false;
  }
  const markdown = job.result_markdown?.trim() ?? "";
  if (markdown.length > 0) {
    return true;
  }
  const snapshot = job.steps_json?.regeneracao_tutorial_snapshot;
  return snapshot !== null && typeof snapshot === "object";
}
