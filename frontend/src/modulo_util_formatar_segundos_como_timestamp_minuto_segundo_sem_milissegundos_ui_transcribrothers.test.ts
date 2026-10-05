import { describe, expect, it } from "vitest";
import { formatarSegundosComoTimestampMinutoSegundoSemMilissegundosUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";

describe("timestamp do cabeçalho da cue sem milissegundos", () => {
  it("arredonda para o segundo e omite horas quando for zero", () => {
    expect(
      formatarSegundosComoTimestampMinutoSegundoSemMilissegundosUiTranscribrothers(0),
    ).toBe("0:00");
    expect(
      formatarSegundosComoTimestampMinutoSegundoSemMilissegundosUiTranscribrothers(6.651),
    ).toBe("0:07");
    expect(
      formatarSegundosComoTimestampMinutoSegundoSemMilissegundosUiTranscribrothers(65.4),
    ).toBe("1:05");
  });

  it("inclui horas quando passar de 60 minutos", () => {
    expect(
      formatarSegundosComoTimestampMinutoSegundoSemMilissegundosUiTranscribrothers(3661.2),
    ).toBe("1:01:01");
  });
});
