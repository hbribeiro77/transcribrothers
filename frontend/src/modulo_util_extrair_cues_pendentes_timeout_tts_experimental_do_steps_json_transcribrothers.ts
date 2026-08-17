/** Extrai cues com timeout TTS experimental aguardando reenvio manual. */

export type CuePendenteTimeoutTtsExperimentalUiTranscribrothers = {
  indice: number;
  indiceCue: number;
  texto: string;
  voz: string;
  motivo: string;
};

export function extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): CuePendenteTimeoutTtsExperimentalUiTranscribrothers[] {
  const raw = stepsJson?.video_narrado_tts_cues_pendentes_timeout;
  if (!Array.isArray(raw)) return [];
  const out: CuePendenteTimeoutTtsExperimentalUiTranscribrothers[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const o = item as Record<string, unknown>;
    const indice = typeof o.indice === "number" && Number.isFinite(o.indice) ? o.indice : null;
    if (indice === null || indice < 0) continue;
    const indiceCue =
      typeof o.indice_cue === "number" && Number.isFinite(o.indice_cue)
        ? o.indice_cue
        : indice + 1;
    const texto = typeof o.texto === "string" ? o.texto : "";
    const voz = typeof o.voz === "string" ? o.voz.trim() : "";
    const motivo = typeof o.motivo === "string" && o.motivo.trim() ? o.motivo.trim() : "timeout";
    out.push({ indice, indiceCue, texto, voz, motivo });
  }
  return out;
}

export function jobAguardandoResolucaoTtsTimeoutExperimentalTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): boolean {
  const fase =
    typeof stepsJson?.pipeline_fase === "string" ? stepsJson.pipeline_fase.trim() : "";
  if (fase === "video_narrado_aguardando_resolucao_tts_timeout") return true;
  return extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers(stepsJson).length > 0;
}
