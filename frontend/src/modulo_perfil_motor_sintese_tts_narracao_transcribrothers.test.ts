import { describe, expect, it } from "vitest";
import {
  PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
  TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  formatarTemperaturaTtsNarracaoParaUiTranscribrothers,
  listarOpcoesParalelismoTtsCuesExperimentalParaUiTranscribrothers,
  listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers,
  normalizarParalelismoTtsCuesExperimentalTranscribrothers,
  normalizarRitmoTtsNarracaoTranscribrothers,
  normalizarTemperaturaTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";

describe("paralelismo TTS (padrao e experimental)", () => {
  it("usa padrão 3 e aceita 1–9", () => {
    expect(normalizarParalelismoTtsCuesExperimentalTranscribrothers(null)).toBe(
      PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
    );
    expect(normalizarParalelismoTtsCuesExperimentalTranscribrothers(7)).toBe(7);
    expect(normalizarParalelismoTtsCuesExperimentalTranscribrothers("9")).toBe(9);
  });

  it("fora do intervalo volta ao padrão (UI)", () => {
    expect(normalizarParalelismoTtsCuesExperimentalTranscribrothers(0)).toBe(3);
    expect(normalizarParalelismoTtsCuesExperimentalTranscribrothers(10)).toBe(3);
  });

  it("lista opções 1..9", () => {
    expect(listarOpcoesParalelismoTtsCuesExperimentalParaUiTranscribrothers()).toEqual([
      1, 2, 3, 4, 5, 6, 7, 8, 9,
    ]);
  });
});

describe("temperatura TTS", () => {
  it("usa padrão 0.4, clamp e snap 0.1", () => {
    expect(normalizarTemperaturaTtsNarracaoTranscribrothers(null)).toBe(
      TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    );
    expect(normalizarTemperaturaTtsNarracaoTranscribrothers(0.4)).toBe(0.4);
    expect(normalizarTemperaturaTtsNarracaoTranscribrothers(0.65)).toBe(0.7);
    expect(normalizarTemperaturaTtsNarracaoTranscribrothers(0.1)).toBe(0.2);
    expect(normalizarTemperaturaTtsNarracaoTranscribrothers(1.5)).toBe(1.0);
  });

  it("formata com vírgula para a UI", () => {
    expect(formatarTemperaturaTtsNarracaoParaUiTranscribrothers(0.4)).toBe("0,4");
  });
});

describe("ritmo TTS", () => {
  it("usa padrão normal e aliases", () => {
    expect(normalizarRitmoTtsNarracaoTranscribrothers(null)).toBe(
      RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    );
    expect(normalizarRitmoTtsNarracaoTranscribrothers("lento")).toBe(
      RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
    );
    expect(normalizarRitmoTtsNarracaoTranscribrothers("rápido")).toBe(
      RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
    );
    expect(normalizarRitmoTtsNarracaoTranscribrothers("muito-rapido")).toBe(
      RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
    );
    expect(normalizarRitmoTtsNarracaoTranscribrothers("xyz")).toBe(
      RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
    );
  });

  it("lista quatro opções", () => {
    expect(listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers().map((o) => o.id)).toEqual([
      RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
      RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
      RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
      RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
    ]);
  });
});
