import { describe, expect, it } from "vitest";
import { formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers } from "./modulo_util_formatar_duracao_segundos_curta_portugues_ui_transcribrothers.ts";

describe("formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers", () => {
  it("formata segundos e minutos", () => {
    expect(formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(12)).toBe("12s");
    expect(formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(65)).toBe("1m 05s");
    expect(formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(3600)).toBe("1h");
  });
});
