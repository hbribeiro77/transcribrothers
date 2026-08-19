import { describe, expect, it } from "vitest";
import { erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers } from "./modulo_util_erro_play_midia_foi_interrompido_por_pause_ou_abort_ui_transcribrothers.ts";

describe("erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers", () => {
  it("reconhece AbortError por name", () => {
    const e = Object.assign(new Error("The play() request was interrupted by a call to pause()."), {
      name: "AbortError",
    });
    expect(erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)).toBe(true);
  });

  it("reconhece mensagem clássica do Chrome mesmo sem name AbortError", () => {
    expect(
      erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(
        new Error(
          "The play() request was interrupted by a call to pause(). https://goo.gl/LdLk22",
        ),
      ),
    ).toBe(true);
  });

  it("não engole erros reais de reprodução", () => {
    expect(
      erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(
        new Error("Não foi possível tocar a narração da cue."),
      ),
    ).toBe(false);
    expect(erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(null)).toBe(false);
  });
});
