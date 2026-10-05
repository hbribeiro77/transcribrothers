export const ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS = 32;
export const ALTURA_MAXIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS = 160;
export const LARGURA_MINIMA_PX_PARA_MEDIR_ALTURA_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS = 64;

export function calcularAlturaTextareaComposerChatAskAgenteTranscribrothers(scrollHeightPx: number): {
  alturaPx: number;
  overflowY: "hidden" | "auto";
} {
  const minimo = ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS;
  const maximo = ALTURA_MAXIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS;
  const alturaPx = Math.min(Math.max(scrollHeightPx, minimo), maximo);
  return {
    alturaPx,
    overflowY: scrollHeightPx > maximo ? "auto" : "hidden",
  };
}

export function aplicarAlturaTextareaComposerChatAskAgenteTranscribrothers(
  el: HTMLTextAreaElement,
): void {
  if (
    el.offsetWidth <
    LARGURA_MINIMA_PX_PARA_MEDIR_ALTURA_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS
  ) {
    el.style.height = `${ALTURA_MINIMA_PX_TEXTAREA_COMPOSER_CHAT_ASK_AGENTE_TRANSCRIBROTHERS}px`;
    el.style.overflowY = "hidden";
    return;
  }
  el.style.height = "0px";
  const { alturaPx, overflowY } = calcularAlturaTextareaComposerChatAskAgenteTranscribrothers(
    el.scrollHeight,
  );
  el.style.height = `${alturaPx}px`;
  el.style.overflowY = overflowY;
}
