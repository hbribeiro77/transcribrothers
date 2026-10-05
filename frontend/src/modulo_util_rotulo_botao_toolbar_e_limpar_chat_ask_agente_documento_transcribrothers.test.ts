import { describe, expect, it } from "vitest";
import {
  limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers,
  rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers,
} from "./modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.ts";

describe("rótulos da gaveta do chat", () => {
  it("toolbar fechada é Abrir chat", () => {
    expect(rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(false)).toBe("Abrir chat");
  });
  it("toolbar aberta é Ocultar chat", () => {
    expect(rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(true)).toBe("Ocultar chat");
  });
  it("Limpar desabilita se vazio ou enviando", () => {
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: true,
        enviando: false,
      }),
    ).toBe(true);
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: false,
        enviando: true,
      }),
    ).toBe(true);
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: false,
        enviando: false,
      }),
    ).toBe(false);
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: false,
        enviando: false,
        preparandoPrevia: true,
      }),
    ).toBe(true);
  });
});
