import { describe, expect, it } from "vitest";
import {
  TEXTO_MENSAGEM_AGENTE_APLICOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS,
  TEXTO_MENSAGEM_AGENTE_DESCARTOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS,
  TEXTO_STATUS_AINDA_PROCESSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
  TEXTO_STATUS_PENSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
  TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS,
  chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers,
  composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers,
  preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers,
  textoIndicadorProcessandoTurnoChatAskAgenteTranscribrothers,
} from "./modulo_util_feedback_previa_documento_no_chat_ask_agente_transcribrothers.ts";

describe("feedback da prévia no chat Agente", () => {
  it("trava o composer só no envio ou na prévia que o chat disparou", () => {
    expect(
      composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers({
        enviandoMensagem: false,
        preparandoPrevia: false,
      }),
    ).toBe(false);
    expect(
      composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers({
        enviandoMensagem: true,
        preparandoPrevia: false,
      }),
    ).toBe(true);
    expect(
      composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers({
        enviandoMensagem: false,
        preparandoPrevia: true,
      }),
    ).toBe(true);
    expect(
      composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers({
        enviandoMensagem: false,
        preparandoPrevia: false,
        jobGerandoMarkdown: true,
      }),
    ).toBe(true);
  });

  it("destravar por tempo só depois do teto, se a prévia não chegou", () => {
    expect(
      preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: false,
        decorridoMs: 1_000,
      }),
    ).toBe(false);
    expect(
      preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: false,
        decorridoMs: 120_000,
      }),
    ).toBe(true);
    expect(
      preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: true,
        decorridoMs: 120_000,
      }),
    ).toBe(false);
    expect(
      preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: false,
        decorridoMs: 120_000,
        jobAindaGerandoMarkdown: true,
      }),
    ).toBe(false);
  });

  it("mostra o spinner só enquanto a prévia ainda não chegou", () => {
    expect(
      chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: false,
      }),
    ).toBe(true);
    expect(
      chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers({
        preparandoPrevia: true,
        temObjetoPreview: true,
      }),
    ).toBe(false);
    expect(
      chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers({
        preparandoPrevia: false,
        temObjetoPreview: false,
      }),
    ).toBe(false);
    expect(
      chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers({
        preparandoPrevia: false,
        temObjetoPreview: false,
        jobGerandoMarkdown: true,
      }),
    ).toBe(true);
  });

  it("tem textos humanos para aplicado, descartado e espera", () => {
    expect(TEXTO_MENSAGEM_AGENTE_APLICOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS).toMatch(/Apliquei/);
    expect(TEXTO_MENSAGEM_AGENTE_DESCARTOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS).toMatch(
      /como estava/,
    );
    expect(TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS).toMatch(/prévia/);
  });

  it("mantém indicador de processamento mesmo depois do primeiro texto da bolha", () => {
    expect(
      textoIndicadorProcessandoTurnoChatAskAgenteTranscribrothers({
        enviandoMensagem: false,
        bolhaEscrevendoJaTemTexto: false,
      }),
    ).toBeNull();
    expect(
      textoIndicadorProcessandoTurnoChatAskAgenteTranscribrothers({
        enviandoMensagem: true,
        bolhaEscrevendoJaTemTexto: false,
      }),
    ).toBe(TEXTO_STATUS_PENSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS);
    expect(
      textoIndicadorProcessandoTurnoChatAskAgenteTranscribrothers({
        enviandoMensagem: true,
        bolhaEscrevendoJaTemTexto: true,
      }),
    ).toBe(TEXTO_STATUS_AINDA_PROCESSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS);
  });
});
