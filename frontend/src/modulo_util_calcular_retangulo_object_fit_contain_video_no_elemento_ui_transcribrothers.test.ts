import { describe, expect, it } from "vitest";
import { calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers } from "./modulo_util_calcular_retangulo_object_fit_contain_video_no_elemento_ui_transcribrothers.ts";

describe("calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers", () => {
  it("centraliza letterbox vertical quando o container é mais alto", () => {
    // Container 200x200, mídia 16:9 → 200x112.5 centrada
    const r = calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers(
      200,
      200,
      1600,
      900,
    );
    expect(r.width).toBeCloseTo(200, 5);
    expect(r.height).toBeCloseTo(112.5, 5);
    expect(r.left).toBeCloseTo(0, 5);
    expect(r.top).toBeCloseTo(43.75, 5);
  });

  it("centraliza pillarbox horizontal quando o container é mais largo", () => {
    const r = calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers(
      400,
      100,
      1600,
      900,
    );
    expect(r.height).toBeCloseTo(100, 5);
    expect(r.width).toBeCloseTo(100 * (16 / 9), 5);
    expect(r.top).toBeCloseTo(0, 5);
    expect(r.left).toBeCloseTo((400 - r.width) / 2, 5);
  });
});
