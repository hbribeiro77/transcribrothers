/** POST /api/jobs/{id}/sugerir-reescrita-texto-cue-narracao */

export type RespostaSugerirReescritaTextoCueNarracaoApiTranscribrothers = {
  ok: boolean;
  mensagem: string;
  indice: number;
  sugestao: string;
  modelo?: string | null;
  texto_original?: string | null;
};

async function _lerErroHttpApiTranscribrothers(r: Response): Promise<never> {
  let detalhe = "";
  try {
    const j = (await r.json()) as { detail?: unknown };
    if (typeof j.detail === "string") detalhe = j.detail;
    else if (Array.isArray(j.detail)) detalhe = JSON.stringify(j.detail);
  } catch {
    try {
      detalhe = await r.text();
    } catch {
      detalhe = "";
    }
  }
  throw new Error(detalhe || `Erro HTTP ${r.status}`);
}

export async function sugerirReescritaTextoCueNarracaoJobApiTranscribrothers(
  jobId: string,
  opts: {
    indice: number;
    texto: string;
    litellmModelChat?: string | null;
  },
): Promise<RespostaSugerirReescritaTextoCueNarracaoApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/sugerir-reescrita-texto-cue-narracao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      indice: opts.indice,
      texto: opts.texto,
      litellm_model_chat: (opts.litellmModelChat || "").trim() || null,
    }),
  });
  if (!r.ok) {
    await _lerErroHttpApiTranscribrothers(r);
  }
  return (await r.json()) as RespostaSugerirReescritaTextoCueNarracaoApiTranscribrothers;
}
