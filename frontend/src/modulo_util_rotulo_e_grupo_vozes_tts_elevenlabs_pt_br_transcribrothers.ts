import type { VozTtsElevenlabsUiTranscribrothers } from "./modulo_api_listar_vozes_tts_elevenlabs_transcribrothers.ts";

export function rotuloVozTtsElevenlabsParaSelectTranscribrothers(
  voz: VozTtsElevenlabsUiTranscribrothers,
): string {
  const nome = (voz.estilo || voz.id || "").trim() || voz.id;
  if (voz.pt_br) {
    const sotaque = (voz.sotaque || "").trim();
    return sotaque ? `${nome} — pt-BR / ${sotaque}` : `${nome} — pt-BR`;
  }
  const idioma = (voz.locale || voz.idioma || "").trim();
  const sotaque = (voz.sotaque || "").trim();
  if (idioma && sotaque) return `${nome} — ${idioma} / ${sotaque}`;
  if (idioma) return `${nome} — ${idioma}`;
  if (sotaque) return `${nome} — ${sotaque}`;
  return nome;
}

export function agruparVozesTtsElevenlabsPtBrEOutrasTranscribrothers(
  vozes: VozTtsElevenlabsUiTranscribrothers[],
): { ptBr: VozTtsElevenlabsUiTranscribrothers[]; outras: VozTtsElevenlabsUiTranscribrothers[] } {
  const ptBr: VozTtsElevenlabsUiTranscribrothers[] = [];
  const outras: VozTtsElevenlabsUiTranscribrothers[] = [];
  for (const voz of vozes) {
    if (voz.pt_br) ptBr.push(voz);
    else outras.push(voz);
  }
  return { ptBr, outras };
}

export function escolherPrimeiraVozTtsElevenlabsPreferindoPtBrTranscribrothers(
  vozes: VozTtsElevenlabsUiTranscribrothers[],
): string {
  const primeiraPtBr = vozes.find((v) => v.pt_br);
  return (primeiraPtBr || vozes[0])?.id || "";
}
