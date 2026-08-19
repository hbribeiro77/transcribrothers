import { describe, expect, it } from "vitest";

import { clampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers } from "./modulo_util_clamp_janela_video_cue_dentro_da_duracao_fonte_ui_transcribrothers.ts";

describe("clampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers", () => {
  it("não altera janela válida dentro da mídia", () => {
    const r = clampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers(2, 8, 12);
    expect(r.alterou).toBe(false);
    expect(r.inicioVideoSegundos).toBe(2);
    expect(r.fimVideoSegundos).toBe(8);
  });

  it("zera e limita quando início/fim estão fora da duração", () => {
    const r = clampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers(376, 407.5, 12);
    expect(r.alterou).toBe(true);
    expect(r.inicioVideoSegundos).toBe(0);
    expect(r.fimVideoSegundos).toBe(12);
  });
});
