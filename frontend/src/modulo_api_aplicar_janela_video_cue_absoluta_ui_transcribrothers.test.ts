import { describe, expect, it } from "vitest";
import {
  aplicarJanelaVideoCueAbsolutaUiTranscribrothers,
  avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers,
  deslizarJanelaVideoCuePeloPontoUiTranscribrothers,
  type JanelaVideoCueLocalUiTranscribrothers,
} from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";

function janelaStub(
  inicio: number,
  fim: number,
): JanelaVideoCueLocalUiTranscribrothers {
  return {
    inicioVideoSegundos: inicio,
    fimVideoSegundos: fim,
    temWav: false,
    urlWav: null,
    textoNarrado: "",
    textoTtsNarrado: "",
    semNarracao: false,
    vozTts: "Kore",
    vozNarrada: "Kore",
  };
}

describe("aplicarJanelaVideoCueAbsolutaUiTranscribrothers", () => {
  it("permite antecipar o início sem sobrepor a cue anterior", () => {
    const janelas = [janelaStub(0, 2), janelaStub(5, 8), janelaStub(10, 12)];
    const r = aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, 1, 3, 8);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.janelas[1].inicioVideoSegundos).toBe(3);
      expect(r.janelas[1].fimVideoSegundos).toBe(8);
      expect(r.avisoSobreposicao).toBeNull();
    }
  });

  it("por padrão rejeita sobreposição com a cue anterior", () => {
    const janelas = [janelaStub(0, 2), janelaStub(5, 8)];
    const r = aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, 1, 1.9, 8);
    expect(r.ok).toBe(false);
  });

  it("com avisarSobreposicaoSemBloquear aceita e avisa", () => {
    const janelas = [janelaStub(0, 2), janelaStub(5, 8)];
    const r = aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, 1, 1.9, 8, {
      avisarSobreposicaoSemBloquear: true,
    });
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.janelas[1].inicioVideoSegundos).toBe(1.9);
      expect(r.avisoSobreposicao).toMatch(/sobrepõ/i);
    }
  });

  it("rejeita janela curta demais", () => {
    const janelas = [janelaStub(0, 2)];
    const r = aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, 0, 1, 1.02);
    expect(r.ok).toBe(false);
  });
});

describe("deslizarJanelaVideoCuePeloPontoUiTranscribrothers", () => {
  it("marcar início mantém a duração e calcula o fim", () => {
    const janelas = [janelaStub(5, 8)];
    const r = deslizarJanelaVideoCuePeloPontoUiTranscribrothers(janelas, 0, "inicio", 2);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.janelas[0].inicioVideoSegundos).toBe(2);
      expect(r.janelas[0].fimVideoSegundos).toBe(5);
    }
  });

  it("marcar fim mantém a duração e calcula o início", () => {
    const janelas = [janelaStub(5, 8)];
    const r = deslizarJanelaVideoCuePeloPontoUiTranscribrothers(janelas, 0, "fim", 12);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.janelas[0].fimVideoSegundos).toBe(12);
      expect(r.janelas[0].inicioVideoSegundos).toBe(9);
    }
  });

  it("avisar sem bloquear quando o deslize sobrepõe vizinha", () => {
    const janelas = [janelaStub(0, 2), janelaStub(5, 8)];
    const r = deslizarJanelaVideoCuePeloPontoUiTranscribrothers(janelas, 1, "inicio", 1);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.janelas[1].inicioVideoSegundos).toBe(1);
      expect(r.janelas[1].fimVideoSegundos).toBe(4);
      expect(r.avisoSobreposicao).toMatch(/sobrepõ/i);
    }
  });
});

describe("avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers", () => {
  it("ignora sobreposição pré-existente entre cues que não foram alteradas", () => {
    // Cue 2 e 3 já se sobrepõem; só a cue 1 muda para um buraco livre.
    const antes = [janelaStub(60, 65), janelaStub(70, 80), janelaStub(75, 90)];
    const depois = [janelaStub(0, 5), janelaStub(70, 80), janelaStub(75, 90)];
    expect(avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(antes, depois)).toBeNull();
  });

  it("avisa quando a cue alterada invade a vizinha", () => {
    const antes = [janelaStub(60, 65), janelaStub(70, 80), janelaStub(90, 100)];
    const depois = [janelaStub(0, 72), janelaStub(70, 80), janelaStub(90, 100)];
    const aviso = avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(antes, depois);
    expect(aviso).toMatch(/cue 1/i);
    expect(aviso).toMatch(/cue 2/i);
    expect(aviso).not.toMatch(/cue 3/i);
  });

  it("não avisa quando nada mudou", () => {
    const janelas = [janelaStub(0, 2), janelaStub(5, 8)];
    expect(avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(janelas, janelas)).toBeNull();
  });
});
