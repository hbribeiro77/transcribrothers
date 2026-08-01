import { describe, expect, it } from "vitest";
import {
  ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers,
  cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers,
  deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
} from "./modulo_util_ajustar_e_deslocar_cues_timeline_narracao_sem_sobreposicao_ui_transcribrothers.ts";

const cuesBase = [
  { inicioSegundos: 0, fimSegundos: 3, texto: "a" },
  { inicioSegundos: 3, fimSegundos: 6, texto: "b" },
  { inicioSegundos: 6, fimSegundos: 9, texto: "c" },
];

describe("ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers", () => {
  it("encolhe o fim da cue até a duração do áudio", () => {
    const r = ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(cuesBase, 0, 1.5);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[0].inicioSegundos).toBe(0);
    expect(r.cues[0].fimSegundos).toBeCloseTo(1.5);
    expect(r.cues[1].inicioSegundos).toBe(3);
  });

  it("recusa se o áudio já preenche o slot", () => {
    const r = ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(cuesBase, 0, 2.99);
    expect(r.ok).toBe(false);
  });
});

describe("deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers", () => {
  it("desloca para a direita quando há folga (após ajuste)", () => {
    const ajustada = ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(cuesBase, 0, 1.5);
    expect(ajustada.ok).toBe(true);
    if (!ajustada.ok) return;
    const r = deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
      ajustada.cues,
      1,
      -0.25,
    );
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[1].inicioSegundos).toBeCloseTo(2.75);
    expect(r.cues[1].fimSegundos).toBeCloseTo(5.75);
    expect(r.cues[0].fimSegundos).toBeCloseTo(1.5);
  });

  it("não deixa sobrepor a cue anterior", () => {
    const r = deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(cuesBase, 1, -10);
    expect(r.ok).toBe(false);
  });
});

describe("cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers", () => {
  it("true quando a ocupação está abaixo do limiar", () => {
    expect(cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(3, 1.5)).toBe(true);
    expect(cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(3, 2.9)).toBe(false);
    expect(cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(3, null)).toBe(false);
  });
});

describe("posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers", () => {
  it("posiciona no início desejado quando há folga", () => {
    const comFolga = [
      { inicioSegundos: 0, fimSegundos: 1.5, texto: "a" },
      { inicioSegundos: 3, fimSegundos: 6, texto: "b" },
      { inicioSegundos: 6, fimSegundos: 9, texto: "c" },
    ];
    const r = posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
      comFolga,
      1,
      2,
    );
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[1].inicioSegundos).toBeCloseTo(2);
    expect(r.cues[1].fimSegundos).toBeCloseTo(5);
  });

  it("prende no limite da vizinha à esquerda", () => {
    const comFolga = [
      { inicioSegundos: 0, fimSegundos: 1.5, texto: "a" },
      { inicioSegundos: 3, fimSegundos: 6, texto: "b" },
    ];
    const r = posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
      comFolga,
      1,
      0,
    );
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[1].inicioSegundos).toBeCloseTo(1.5);
  });
});
