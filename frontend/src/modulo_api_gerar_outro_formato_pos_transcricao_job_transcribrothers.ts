import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export async function gerarOutroFormatoPosTranscricaoJobApiTranscribrothers(
  jobId: string,
  opcoes: {
    destinoAposTranscricao: string;
    pipelineCustomId?: string | null;
    litellmModel?: string | null;
  },
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/gerar-outro-formato`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      destino_apos_transcricao: opcoes.destinoAposTranscricao,
      pipeline_custom_id: opcoes.pipelineCustomId?.trim() || null,
      litellm_model: opcoes.litellmModel?.trim() || null,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}
