import { describe, expect, it } from "vitest";

import {
  ajustarCuesSelecionadasAoAudioEmOrdemTranscribrothers,
  aplicarVozTtsNasJanelasCuesSelecionadasTranscribrothers,
  listarIndicesCuesElegiveisNarracaoLoteTranscribrothers,
  remaparIndicesSelecionadosAposExcluirTranscribrothers,
} from "./modulo_util_acoes_lote_cues_narracao_voz_e_ajuste_audio_transcribrothers.ts";

function cue(inicio: number, fim: number) {
  return {
    idCliente: `c-${inicio}`,
    inicioSegundos: inicio,
    fimSegundos: fim,
    texto: "oi",
    textoTts: "",
  };
}

describe("ações em lote nas cues", () => {
  it("ignora cues sem narração ao listar elegíveis", () => {
    expect(
      listarIndicesCuesElegiveisNarracaoLoteTranscribrothers(
        [{ semNarracao: false }, { semNarracao: true }, {}],
        [0, 1, 2],
      ),
    ).toEqual([0, 2]);
  });

  it("aplica a voz só nas janelas selecionadas", () => {
    const janelas = [
      { vozTts: "Kore", semNarracao: false },
      { vozTts: "Kore", semNarracao: false },
      { vozTts: "Aoede", semNarracao: false },
    ];
    const r = aplicarVozTtsNasJanelasCuesSelecionadasTranscribrothers(
      janelas,
      [0, 2],
      "nPczCjzI2devNBz1zQrb",
    );
    expect(r.map((j) => j.vozTts)).toEqual(["nPczCjzI2devNBz1zQrb", "Kore", "nPczCjzI2devNBz1zQrb"]);
  });

  it("ajusta ao áudio em ordem e empurra as seguintes", () => {
    const cues = [cue(0, 2), cue(2, 4)];
    const r = ajustarCuesSelecionadasAoAudioEmOrdemTranscribrothers(cues, [0, 1], {
      0: 3,
      1: 1.5,
    });
    expect(r.ajustadas).toBe(2);
    expect(r.cues[0].fimSegundos).toBe(3);
    expect(r.cues[1].inicioSegundos).toBe(3);
    expect(r.cues[1].fimSegundos).toBe(4.5);
  });

  it("no modo só alongar, não encolhe cue cujo áudio é mais curto", () => {
    const cues = [cue(0, 2), cue(2, 4)];
    const r = ajustarCuesSelecionadasAoAudioEmOrdemTranscribrothers(
      cues,
      [0, 1],
      { 0: 3, 1: 1.5 },
      "so_alongar",
    );
    expect(r.ajustadas).toBe(1);
    expect(r.cues[0].fimSegundos).toBe(3);
    expect(r.cues[1].inicioSegundos).toBe(3);
    expect(r.cues[1].fimSegundos).toBe(5);
  });

  it("remaia seleção depois de excluir uma cue", () => {
    expect(remaparIndicesSelecionadosAposExcluirTranscribrothers([0, 2, 3], 2)).toEqual([0, 2]);
  });
});
