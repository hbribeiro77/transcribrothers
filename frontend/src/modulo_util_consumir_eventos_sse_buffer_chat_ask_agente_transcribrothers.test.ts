import { describe, expect, it } from "vitest";
import { consumirEventosSseBufferChatAskAgenteTranscribrothers } from "./modulo_util_consumir_eventos_sse_buffer_chat_ask_agente_transcribrothers.ts";

describe("buffer SSE do chat", () => {
  it("separa eventos completos e deixa o resto no buffer", () => {
    const { eventos, resto } = consumirEventosSseBufferChatAskAgenteTranscribrothers(
      'data: {"tipo":"delta","texto":"Oi"}\n\ndata: {"tipo":"del',
    );
    expect(eventos).toEqual([{ tipo: "delta", texto: "Oi" }]);
    expect(resto).toBe('data: {"tipo":"del');
  });

  it("ignora linhas sem data JSON", () => {
    const { eventos, resto } = consumirEventosSseBufferChatAskAgenteTranscribrothers(
      ":\n\ndata: {\"tipo\":\"final\"}\n\n",
    );
    expect(eventos).toEqual([{ tipo: "final" }]);
    expect(resto).toBe("");
  });
});
