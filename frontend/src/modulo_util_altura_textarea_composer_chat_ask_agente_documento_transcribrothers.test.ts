import { describe, expect, it } from "vitest";
import {
  ALTURA_MAXIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
  ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
  aplicarAlturaTextareaComposerChatAskAgenteTranscribrothers,
  calcularAlturaTextareaComposerChatAskAgenteTranscribrothers,
} from "./modulo_util_altura_textarea_composer_chat_ask_agente_documento_transcribrothers.ts";

describe("altura do composer do chat", () => {
  it("uma linha fica no mínimo, sem barra", () => {
    expect(calcularAlturaTextareaComposerChatAskAgenteTranscribrothers(20)).toEqual({
      alturaPx: ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
      overflowY: "hidden",
    });
    expect(ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS).toBe(32);
  });
  it("cresce com o texto até o teto", () => {
    expect(calcularAlturaTextareaComposerChatAskAgenteTranscribrothers(96)).toEqual({
      alturaPx: 96,
      overflowY: "hidden",
    });
  });
  it("só mostra barra depois do teto", () => {
    expect(calcularAlturaTextareaComposerChatAskAgenteTranscribrothers(240)).toEqual({
      alturaPx: ALTURA_MAXIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS,
      overflowY: "auto",
    });
  });
  it("com a gaveta fechada (largura residual) volta ao mínimo em vez de esticar no teto", () => {
    const el = {
      offsetWidth: 16,
      scrollHeight: 400,
      style: { height: "160px", overflowY: "auto" },
    } as HTMLTextAreaElement;
    aplicarAlturaTextareaComposerChatAskAgenteTranscribrothers(el);
    expect(el.style.height).toBe(
      `${ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS}px`,
    );
    expect(el.style.overflowY).toBe("hidden");
  });
});
