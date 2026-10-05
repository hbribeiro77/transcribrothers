import {
  rotuloVozTtsElevenlabsParaSelectTranscribrothers,
} from "./modulo_util_rotulo_e_grupo_vozes_tts_elevenlabs_pt_br_transcribrothers.ts";

export type OpcaoVozCueNarracaoSelectTranscribrothers = {
  id: string;
  estilo?: string;
  idioma?: string;
  sotaque?: string;
  locale?: string;
  pt_br?: boolean;
};

function idVozPareceHashElevenlabsTranscribrothers(id: string): boolean {
  const s = (id || "").trim();
  return /^[A-Za-z0-9]{16,}$/.test(s) && /[A-Za-z]/.test(s) && /\d/.test(s);
}

export function rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers(
  op: OpcaoVozCueNarracaoSelectTranscribrothers,
): string {
  const id = (op.id || "").trim();
  const estilo = (op.estilo || "").trim();
  const pareceElevenlabs =
    op.pt_br === true ||
    Boolean((op.idioma || "").trim() || (op.locale || "").trim() || (op.sotaque || "").trim()) ||
    idVozPareceHashElevenlabsTranscribrothers(id);
  if (pareceElevenlabs) {
    const nomeVisivel =
      estilo && !idVozPareceHashElevenlabsTranscribrothers(estilo) ? estilo : "";
    if (!nomeVisivel) return "Voz do projeto";
    return rotuloVozTtsElevenlabsParaSelectTranscribrothers({
      id,
      estilo: nomeVisivel,
      idioma: op.idioma || "",
      sotaque: op.sotaque || "",
      locale: op.locale || "",
      pt_br: op.pt_br === true,
    });
  }
  if (estilo) return `${id} — ${estilo}`;
  return id;
}
