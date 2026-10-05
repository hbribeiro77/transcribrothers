import { describe, expect, it } from "vitest";
import {
  aplicarColapsoOcorrenciasRepeticaoSelecionadasEmTextoTranscricaoTranscribrothers,
  detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers,
} from "./modulo_util_detectar_e_colapsar_repeticoes_suspeitas_texto_transcricao_transcribrothers.ts";

describe("detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers", () => {
  it("detecta loop de palavra só com espaços", () => {
    const texto = "e aí de de de de de de de falaram do prazo";
    const ocorrencias = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(texto);
    expect(ocorrencias.length).toBe(1);
    expect(ocorrencias[0].textoColapsado.toLowerCase()).toBe("de");
    expect(ocorrencias[0].repeticoes).toBeGreaterThanOrEqual(4);
  });

  it("não marca ênfase curta de duas ou três palavras", () => {
    const texto = "Não, não, eu discordo. Sim sim, pode ser.";
    const ocorrencias = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(texto);
    expect(ocorrencias).toEqual([]);
  });

  it("detecta n-grama repetido", () => {
    const texto = "a gente a gente a gente a gente a gente precisa disso";
    const ocorrencias = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(texto);
    expect(ocorrencias.length).toBe(1);
    expect(ocorrencias[0].textoColapsado.toLowerCase()).toBe("a gente");
  });

  it("marca por padrão só loops extremos", () => {
    const curto = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(
      "foi foi foi foi o combinado",
    );
    expect(curto[0]?.marcadaPorPadrao).toBe(false);
    const extremo = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(
      "foi " + "foi ".repeat(10) + "o combinado",
    );
    expect(extremo[0]?.marcadaPorPadrao).toBe(true);
  });
});

describe("aplicarColapsoOcorrenciasRepeticaoSelecionadasEmTextoTranscricaoTranscribrothers", () => {
  it("colapsa só as ocorrências selecionadas", () => {
    const texto = "alpha alpha alpha alpha e beta beta beta beta fim";
    const ocorrencias = detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(texto);
    expect(ocorrencias.length).toBe(2);
    const soAlpha = aplicarColapsoOcorrenciasRepeticaoSelecionadasEmTextoTranscricaoTranscribrothers(
      texto,
      ocorrencias,
      [ocorrencias[0].id],
    );
    expect(soAlpha).toContain("alpha e beta beta beta beta fim");
    expect(soAlpha.match(/\balpha\b/gi)?.length).toBe(1);
  });
});
