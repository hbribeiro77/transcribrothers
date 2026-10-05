import { describe, expect, it } from "vitest";
import { jobPodeAbrirChatAskAgenteDocumentoTranscribrothers } from "./modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.ts";

describe("visibilidade do chat Ask/Agente", () => {
  it("abre só com Markdown", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "# doc",
        steps_json: {},
      }),
    ).toBe(true);
  });
  it("abre só com snapshot de regeneração", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "",
        steps_json: { regeneracao_tutorial_snapshot: { texto_completo: "fala" } },
      }),
    ).toBe(true);
  });
  it("fecha sem os dois", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "  ",
        steps_json: {},
      }),
    ).toBe(false);
  });
});
