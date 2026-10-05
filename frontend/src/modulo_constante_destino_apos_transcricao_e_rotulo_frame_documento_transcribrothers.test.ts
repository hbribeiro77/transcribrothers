import { describe, expect, it } from "vitest";

import {
  normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers,
  obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers,
} from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";

describe("destino tutorial passo a passo de software", () => {
  it("normaliza o destino novo e devolve rótulo distinto do tutorial ilustrativo", () => {
    expect(
      normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers("tutorial_passo_a_passo_software"),
    ).toBe("tutorial_passo_a_passo_software");
    expect(
      obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers("tutorial_passo_a_passo_software"),
    ).toBe("Passo a passo");
    expect(obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers("gerar_tutorial")).toBe(
      "Tutorial",
    );
  });
});
