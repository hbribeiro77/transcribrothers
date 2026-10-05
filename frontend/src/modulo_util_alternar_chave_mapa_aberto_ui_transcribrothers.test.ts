import { describe, expect, it } from "vitest";
import { alternarChaveMapaAbertoUiTranscribrothers } from "./modulo_util_alternar_chave_mapa_aberto_ui_transcribrothers.ts";

describe("alternar chave no mapa aberto", () => {
  it("abre e fecha sem mutar o mapa original", () => {
    const vazio: Record<string, true> = {};
    const aberto = alternarChaveMapaAbertoUiTranscribrothers(vazio, "cue-a");
    expect(aberto).toEqual({ "cue-a": true });
    expect(vazio).toEqual({});
    expect(alternarChaveMapaAbertoUiTranscribrothers(aberto, "cue-a")).toEqual({});
  });
});
