export type RespostaResolverCueTtsPendenteTimeoutExperimentalApiTranscribrothers = {
  ok: boolean;
  mensagem: string;
  indice: number;
  pendentes_restantes: number;
  pipeline_continuada: boolean;
  pipeline_fase: string | null;
};

async function _lerErroHttpApiJsonTranscribrothers(r: Response): Promise<never> {
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

export async function resolverCueTtsPendenteTimeoutExperimentalJobApiTranscribrothers(
  jobId: string,
  opts: {
    indice: number;
    texto: string;
    voz?: string | null;
  },
): Promise<RespostaResolverCueTtsPendenteTimeoutExperimentalApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/resolver-cue-tts-pendente-timeout-experimental`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      indice: opts.indice,
      texto: opts.texto,
      voz: (opts.voz || "").trim() || null,
    }),
  });
  if (!r.ok) {
    await _lerErroHttpApiJsonTranscribrothers(r);
  }
  return (await r.json()) as RespostaResolverCueTtsPendenteTimeoutExperimentalApiTranscribrothers;
}

export async function descartarCueTtsPendenteTimeoutExperimentalJobApiTranscribrothers(
  jobId: string,
  opts: { indice: number },
): Promise<RespostaResolverCueTtsPendenteTimeoutExperimentalApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/descartar-cue-tts-pendente-timeout-experimental`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indice: opts.indice }),
  });
  if (!r.ok) {
    await _lerErroHttpApiJsonTranscribrothers(r);
  }
  return (await r.json()) as RespostaResolverCueTtsPendenteTimeoutExperimentalApiTranscribrothers;
}

export type RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalApiTranscribrothers = {
  ok: boolean;
  mensagem: string;
  indice: number;
  sugestao: string;
  modelo: string | null;
  texto_original: string | null;
};

export async function sugerirReescritaCueTtsPendenteTimeoutExperimentalJobApiTranscribrothers(
  jobId: string,
  opts: {
    indice: number;
    texto: string;
    litellmModelChat?: string | null;
  },
): Promise<RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalApiTranscribrothers> {
  const r = await fetch(
    `/api/jobs/${jobId}/sugerir-reescrita-cue-tts-pendente-timeout-experimental`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        indice: opts.indice,
        texto: opts.texto,
        litellm_model_chat: (opts.litellmModelChat || "").trim() || null,
      }),
    },
  );
  if (!r.ok) {
    await _lerErroHttpApiJsonTranscribrothers(r);
  }
  return (await r.json()) as RespostaSugerirReescritaCueTtsPendenteTimeoutExperimentalApiTranscribrothers;
}
