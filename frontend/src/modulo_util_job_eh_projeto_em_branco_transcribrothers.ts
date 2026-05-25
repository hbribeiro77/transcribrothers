/** Job criado por «Projeto em branco» (sem vídeo nem pipeline de transcrição). */

export type JobComStepsJsonProjetoEmBrancoTranscribrothers = {
  source_kind?: string | null;
  steps_json?: {
    source?: unknown;
    destino_apos_transcricao?: unknown;
    projeto_em_branco?: unknown;
  } | null;
};

export function jobEhProjetoEmBrancoTranscribrothers(
  job: JobComStepsJsonProjetoEmBrancoTranscribrothers | null | undefined,
): boolean {
  if (!job) {
    return false;
  }
  if (job.source_kind === "projeto_em_branco") {
    return true;
  }
  const steps = job.steps_json;
  if (steps?.projeto_em_branco === true) {
    return true;
  }
  if (steps?.source === "projeto_em_branco") {
    return true;
  }
  if (steps?.destino_apos_transcricao === "projeto_em_branco") {
    return true;
  }
  return false;
}
