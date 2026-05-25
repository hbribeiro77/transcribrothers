import { normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";

type JobComStepsJson = {
  steps_json?: Record<string, unknown> | null;
};

export function jobEhNotasPropostaFuncionalidadeTranscribrothers(
  job: JobComStepsJson | null | undefined,
): boolean {
  if (!job) return false;
  return (
    normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers(job.steps_json?.destino_apos_transcricao) ===
    "notas_proposta_funcionalidade"
  );
}
