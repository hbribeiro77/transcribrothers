import { describe, expect, it } from "vitest";

import { calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers } from "./modulo_util_calcular_janela_video_apos_troca_fonte_midia_tela_ui_transcribrothers.ts";

describe("calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers", () => {
  it("não altera tempos se a fonte for a mesma", () => {
    const r = calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers({
      idFonteAnterior: "entrada",
      idFonteNova: "entrada",
      inicioVideoSegundos: 376,
      fimVideoSegundos: 407.5,
      duracaoCueTimelineSegundos: 8,
      duracaoFonteNovaSegundos: 72,
    });
    expect(r.mudouFonte).toBe(false);
    expect(r.inicioVideoSegundos).toBe(376);
    expect(r.fimVideoSegundos).toBe(407.5);
  });

  it("zera a janela e limita à duração do novo vídeo ao trocar fonte", () => {
    const r = calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers({
      idFonteAnterior: "entrada",
      idFonteNova: "mabc123",
      inicioVideoSegundos: 376,
      fimVideoSegundos: 407.5,
      duracaoCueTimelineSegundos: 31.5,
      duracaoFonteNovaSegundos: 12,
    });
    expect(r.mudouFonte).toBe(true);
    expect(r.inicioVideoSegundos).toBe(0);
    expect(r.fimVideoSegundos).toBe(12);
  });

  it("limita ao slot da cue quando a nova mídia é mais longa", () => {
    const r = calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers({
      idFonteAnterior: "entrada",
      idFonteNova: "mxyz",
      inicioVideoSegundos: 10,
      fimVideoSegundos: 18,
      duracaoCueTimelineSegundos: 8,
      duracaoFonteNovaSegundos: 120,
    });
    expect(r.inicioVideoSegundos).toBe(0);
    expect(r.fimVideoSegundos).toBe(8);
  });

  it("sem duração da fonte, usa min(janela anterior, cue)", () => {
    const r = calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers({
      idFonteAnterior: "entrada",
      idFonteNova: "m1",
      inicioVideoSegundos: 100,
      fimVideoSegundos: 110,
      duracaoCueTimelineSegundos: 6,
      duracaoFonteNovaSegundos: null,
    });
    expect(r.inicioVideoSegundos).toBe(0);
    expect(r.fimVideoSegundos).toBe(6);
  });
});
