import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export async function regenerarMarkdownReproducaoBugJobApiTranscribrothers(
  jobId: string,
  opcoes: {
    instrucoesRevisaoHumana?: string;
    litellmModel?: string;
    documentoAutonomoSemVideo?: boolean;
  },
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/regenerate-reproducao-bug`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      instrucoes_revisao_humana: opcoes.instrucoesRevisaoHumana?.trim() || null,
      litellm_model: opcoes.litellmModel?.trim() || null,
      documento_autonomo_sem_video: Boolean(opcoes.documentoAutonomoSemVideo),
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}
