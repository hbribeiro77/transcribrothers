import { describe, expect, it } from "vitest";
import { prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers } from "./modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.ts";

describe("prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers", () => {
  it("formata 72s como 1:12", () => {
    expect(prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers(72)).toBe(
      "Frame anexado em 1:12.",
    );
  });
});
