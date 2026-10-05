import { describe, expect, it } from "vitest";

import type { VozTtsElevenlabsUiTranscribrothers } from "./modulo_api_listar_vozes_tts_elevenlabs_transcribrothers.ts";
import {
  agruparVozesTtsElevenlabsPtBrEOutrasTranscribrothers,
  escolherPrimeiraVozTtsElevenlabsPreferindoPtBrTranscribrothers,
  rotuloVozTtsElevenlabsParaSelectTranscribrothers,
} from "./modulo_util_rotulo_e_grupo_vozes_tts_elevenlabs_pt_br_transcribrothers.ts";

function voz(
  parcial: Partial<VozTtsElevenlabsUiTranscribrothers> & Pick<VozTtsElevenlabsUiTranscribrothers, "id" | "estilo">,
): VozTtsElevenlabsUiTranscribrothers {
  return {
    idioma: "",
    sotaque: "",
    locale: "",
    pt_br: false,
    ...parcial,
  };
}

describe("rótulo e grupo de vozes ElevenLabs", () => {
  it("destaca pt-BR no rótulo do select", () => {
    expect(
      rotuloVozTtsElevenlabsParaSelectTranscribrothers(
        voz({
          id: "br1",
          estilo: "1berto",
          idioma: "pt",
          sotaque: "brazilian",
          locale: "pt-BR",
          pt_br: true,
        }),
      ),
    ).toBe("1berto — pt-BR / brazilian");
  });

  it("mostra idioma e sotaque quando não é pt-BR", () => {
    expect(
      rotuloVozTtsElevenlabsParaSelectTranscribrothers(
        voz({ id: "en1", estilo: "Roger", idioma: "en", sotaque: "american" }),
      ),
    ).toBe("Roger — en / american");
  });

  it("agrupa brasileiras primeiro e escolhe a primeira pt-BR", () => {
    const lista = [
      voz({ id: "en1", estilo: "Roger", idioma: "en" }),
      voz({ id: "br1", estilo: "1berto", pt_br: true, locale: "pt-BR" }),
    ];
    const grupos = agruparVozesTtsElevenlabsPtBrEOutrasTranscribrothers(lista);
    expect(grupos.ptBr.map((v) => v.id)).toEqual(["br1"]);
    expect(grupos.outras.map((v) => v.id)).toEqual(["en1"]);
    expect(escolherPrimeiraVozTtsElevenlabsPreferindoPtBrTranscribrothers(lista)).toBe("br1");
  });
});
