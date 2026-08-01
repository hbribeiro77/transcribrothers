import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export async function agendarAtualizacaoNarracaoAPartirLegendasVttEditadasJobApiTranscribrothers(
  jobId: string,
  litellmModel?: string | null,
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/atualizar-narracao-a-partir-legendas-vtt-editadas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      litellm_model: (litellmModel || "").trim() || null,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    try {
      const j = JSON.parse(t) as { detail?: unknown };
      if (typeof j.detail === "string" && j.detail.trim()) {
        throw new Error(j.detail.trim());
      }
    } catch (e) {
      if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
    }
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}
