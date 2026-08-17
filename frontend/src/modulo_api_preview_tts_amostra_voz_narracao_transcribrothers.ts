/** Prévia WAV de amostra da voz Gemini TTS (frase fixa no servidor). */

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

export async function gerarPreviewTtsAmostraVozNarracaoApiTranscribrothers(opts: {
  voz: string;
  litellmModel?: string | null;
  perfilTts?: string | null;
  temperaturaTts?: number | null;
  ritmoTts?: string | null;
}): Promise<Blob> {
  const r = await fetch("/api/preview-tts-amostra-voz-narracao", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      voz: (opts.voz || "").trim() || "Kore",
      litellm_model: (opts.litellmModel || "").trim() || null,
      perfil_tts: (opts.perfilTts || "").trim() || null,
      temperatura_tts: typeof opts.temperaturaTts === "number" ? opts.temperaturaTts : null,
      ritmo_tts: (opts.ritmoTts || "").trim() || null,
    }),
  });
  if (!r.ok) {
    await _lerErroHttpApiTranscribrothers(r);
  }
  return await r.blob();
}
