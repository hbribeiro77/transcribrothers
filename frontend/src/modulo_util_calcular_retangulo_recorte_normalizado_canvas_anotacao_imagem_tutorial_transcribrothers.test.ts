import { describe, expect, it } from "vitest";
import {
  calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers,
  TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS,
} from "./modulo_util_calcular_retangulo_recorte_normalizado_canvas_anotacao_imagem_tutorial_transcribrothers.ts";

describe("calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers", () => {
  it("normaliza cantos invertidos e limita ao canvas", () => {
    const r = calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers(
      80,
      60,
      20,
      10,
      100,
      100,
    );
    expect(r).toEqual({ left: 20, top: 10, width: 60, height: 50 });
  });

  it("corta coordenadas fora do canvas", () => {
    const r = calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers(
      -10,
      -5,
      50,
      40,
      100,
      80,
    );
    expect(r).toEqual({ left: 0, top: 0, width: 50, height: 40 });
  });

  it("devolve null quando a área é menor que o mínimo", () => {
    const r = calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers(
      10,
      10,
      10 + TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS - 1,
      10 + TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS - 1,
      200,
      200,
    );
    expect(r).toBeNull();
  });
});
