import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type CueEdicaoModalNarradoParaGerarVideoApiTranscribrothers = {
  inicio_segundos: number;
  fim_segundos: number;
  texto: string;
  sem_narracao?: boolean;
  voz_tts?: string;
  /** Pronúncia para TTS; vazio/omitido = narrar `texto`. */
  texto_tts?: string;
  forcar_regenerar_tts?: boolean;
};

export type JanelaEdicaoModalNarradoParaGerarVideoApiTranscribrothers = {
  inicio_video_segundos: number;
  fim_video_segundos: number;
};

export async function agendarGerarVideoComEdicoesDoModalNarradoJobApiTranscribrothers(
  jobId: string,
  opts: {
    litellmModel?: string | null;
    cues: CueEdicaoModalNarradoParaGerarVideoApiTranscribrothers[];
    janelas?: JanelaEdicaoModalNarradoParaGerarVideoApiTranscribrothers[] | null;
  },
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/gerar-video-com-edicoes-do-modal-narrado`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      litellm_model: (opts.litellmModel || "").trim() || null,
      cues: opts.cues,
      janelas: opts.janelas ?? null,
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
