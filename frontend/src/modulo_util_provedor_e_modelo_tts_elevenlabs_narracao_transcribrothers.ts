export const PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS = "litellm";
export const PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS = "elevenlabs";
export const MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS = "eleven_v4";

export function normalizarProvedorTtsNarracaoUiTranscribrothers(valor: string | null | undefined): string {
  const s = String(valor || "")
    .trim()
    .toLowerCase();
  if (s === PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS) {
    return PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS;
  }
  return PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS;
}

export function modeloTtsPareceElevenlabsPeloSlugTranscribrothers(modelo: string | null | undefined): boolean {
  return String(modelo || "").trim().toLowerCase() === MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS;
}

export function mesclarModelosTtsLitellmComElevenlabsSeConfiguradoTranscribrothers(
  modelosLitellm: string[],
  elevenlabsModelos: string[],
  elevenlabsConfigurado: boolean,
): string[] {
  const out: string[] = [];
  const visto = new Set<string>();
  for (const m of modelosLitellm) {
    const s = String(m || "").trim();
    if (!s || visto.has(s)) continue;
    visto.add(s);
    out.push(s);
  }
  if (!elevenlabsConfigurado) return out;
  for (const m of elevenlabsModelos.length > 0 ? elevenlabsModelos : [MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS]) {
    const s = String(m || "").trim();
    if (!s || visto.has(s) || !modeloTtsPareceElevenlabsPeloSlugTranscribrothers(s)) continue;
    visto.add(s);
    out.push(s);
  }
  return out;
}
