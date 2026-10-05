import { describe, expect, it } from "vitest";
import { duracaoTelaDifereDoSlotCueNarracaoTranscribrothers } from "./modulo_util_duracao_tela_difere_do_slot_cue_narracao_transcribrothers.ts";

describe("duração de tela vs slot da cue", () => {
  it("esconde o chip quando a janela e o slot são iguais", () => {
    expect(duracaoTelaDifereDoSlotCueNarracaoTranscribrothers(6.51, 6.51)).toBe(false);
    expect(duracaoTelaDifereDoSlotCueNarracaoTranscribrothers(6.51, 6.55)).toBe(false);
  });

  it("mostra o chip quando a janela diverge do slot", () => {
    expect(duracaoTelaDifereDoSlotCueNarracaoTranscribrothers(6.51, 2)).toBe(true);
  });
});
