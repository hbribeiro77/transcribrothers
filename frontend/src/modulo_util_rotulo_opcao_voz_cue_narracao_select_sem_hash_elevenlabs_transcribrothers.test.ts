import { describe, expect, it } from "vitest";

import { rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers } from "./modulo_util_rotulo_opcao_voz_cue_narracao_select_sem_hash_elevenlabs_transcribrothers.ts";

describe("rótulo do select de voz na cue", () => {
  it("mantém id + estilo nas vozes Gemini", () => {
    expect(
      rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers({
        id: "Kore",
        estilo: "Firme",
      }),
    ).toBe("Kore — Firme");
  });

  it("oculta o voice_id hash da ElevenLabs e mostra o nome", () => {
    expect(
      rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers({
        id: "nPczCjzI2devNBz1zQrb",
        estilo: "Brian - Deep, Resonant and Comforting",
      }),
    ).toBe("Brian - Deep, Resonant and Comforting");
  });

  it("não mostra o hash quando a voz não tem nome", () => {
    expect(
      rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers({
        id: "CwhRBWXzGAHq8TQ4Fs17",
      }),
    ).toBe("Voz do projeto");
  });

  it("destaca pt-BR no nome, sem o hash", () => {
    expect(
      rotuloOpcaoVozCueNarracaoParaSelectSemHashElevenlabsTranscribrothers({
        id: "nPczCjzI2devNBz1zQrb",
        estilo: "Brian - Deep, Resonant and Comforting",
        pt_br: true,
        sotaque: "standard",
        locale: "pt-BR",
        idioma: "pt",
      }),
    ).toBe("Brian - Deep, Resonant and Comforting — pt-BR / standard");
  });
});
