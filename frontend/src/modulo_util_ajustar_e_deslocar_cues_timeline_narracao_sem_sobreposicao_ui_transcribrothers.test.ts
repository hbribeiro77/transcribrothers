import { describe, expect, it } from "vitest";
import {
  ajustarFimCueTimelineAJanelaTelaUiTranscribrothers,
  ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers,
  cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers,
  cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers,
  deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers,
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

describe("ajustarFimCueTimelineAJanelaTelaUiTranscribrothers", () => {
  it("encolhe o fim até a duração da tela sem mover vizinhas", () => {
    const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(cuesBase, 0, 1.5);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[0].fimSegundos).toBeCloseTo(1.5);
    expect(r.cues[1].inicioSegundos).toBe(3);
    expect(r.cues[2].inicioSegundos).toBe(6);
  });

  it("estica e empurra as cues seguintes encostadas", () => {
    const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(cuesBase, 0, 7);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[0].inicioSegundos).toBe(0);
    expect(r.cues[0].fimSegundos).toBeCloseTo(7);
    expect(r.cues[1].inicioSegundos).toBeCloseTo(7);
    expect(r.cues[1].fimSegundos).toBeCloseTo(10);
    expect(r.cues[2].inicioSegundos).toBeCloseTo(10);
    expect(r.cues[2].fimSegundos).toBeCloseTo(13);
  });

  it("ao esticar preserva folga que já existia entre vizinhas", () => {
    const comFolga = [
      { inicioSegundos: 0, fimSegundos: 3, texto: "a" },
      { inicioSegundos: 5, fimSegundos: 8, texto: "b" },
      { inicioSegundos: 10, fimSegundos: 13, texto: "c" },
    ];
    const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(comFolga, 0, 7);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.cues[0].fimSegundos).toBeCloseTo(7);
    expect(r.cues[1].inicioSegundos).toBeCloseTo(7);
    expect(r.cues[1].fimSegundos).toBeCloseTo(10);
    // Folga de 2s entre b e c preservada.
    expect(r.cues[2].inicioSegundos).toBeCloseTo(12);
    expect(r.cues[2].fimSegundos).toBeCloseTo(15);
  });

  it("recusa se já está alinhada à tela", () => {
    const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(cuesBase, 0, 3.05);
    expect(r.ok).toBe(false);
  });
});

describe("cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers", () => {
  it("true quando a discrepância passa do limiar", () => {
    expect(cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers(3, 7)).toBe(true);
    expect(cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers(3, 3.05)).toBe(false);
    expect(cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers(3, null)).toBe(false);
  });
});

describe("resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers", () => {
  it("prefere a prévia válida mesmo quando o texto/voz ainda batem com o narrado (Regenerar)", () => {
    const dur = resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers({
      textoFalaAtual: "olá",
      vozAtual: "Kore",
      audioNarradoDesatualizado: false,
      preview: { texto: "olá", voz: "Kore", duracaoSegundos: 1.2 },
      duracaoWavGravadoSegundos: 2.8,
    });
    expect(dur).toBeCloseTo(1.2);
  });

  it("usa a prévia quando o áudio narrado está desatualizado", () => {
    const dur = resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers({
      textoFalaAtual: "texto novo",
      vozAtual: "Kore",
      audioNarradoDesatualizado: true,
      preview: { texto: "texto novo", voz: "Kore", duracaoSegundos: 1.5 },
      duracaoWavGravadoSegundos: 3.0,
    });
    expect(dur).toBeCloseTo(1.5);
  });

  it("retorna null se narrado está desatualizado e não há prévia válida", () => {
    const dur = resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers({
      textoFalaAtual: "texto novo",
      vozAtual: "Kore",
      audioNarradoDesatualizado: true,
      preview: { texto: "texto antigo", voz: "Kore", duracaoSegundos: 1.5 },
      duracaoWavGravadoSegundos: 3.0,
    });
    expect(dur).toBeNull();
  });

  it("usa o WAV gravado quando não há prévia e o narrado ainda vale", () => {
    const dur = resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers({
      textoFalaAtual: "olá",
      vozAtual: "Kore",
      audioNarradoDesatualizado: false,
      preview: undefined,
      duracaoWavGravadoSegundos: 2.4,
    });
    expect(dur).toBeCloseTo(2.4);
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
