export function classeGridPreviewRolagemDocumentoQuandoChatAbertoTranscribrothers(
  chatAberto: boolean,
): string {
  return chatAberto ? "tb-grid-preview--rolagem-documento" : "";
}

export function classesDockGavetaChatAskAgenteDocumentoTranscribrothers(
  aberta: boolean,
): string {
  return aberta
    ? "tb-chat-ask-agente-dock-wrapper tb-chat-ask-agente-dock-wrapper--aberta"
    : "tb-chat-ask-agente-dock-wrapper";
}

export function classesPainelGavetaChatAskAgenteDocumentoTranscribrothers(args: {
  aberta: boolean;
  projetoEmBranco: boolean;
  arrastando: boolean;
  processando: boolean;
}): string {
  return [
    "tb-chat-ask-agente-painel",
    "tb-chat-ask-agente-gaveta",
    args.aberta ? "tb-chat-ask-agente-painel--aberta" : "",
    args.projetoEmBranco ? "tb-fab-regen-panel--chat-projeto-em-branco" : "",
    args.arrastando ? "tb-fab-regen-panel--arrastando-arquivo" : "",
    args.processando ? "tb-fab-regen-panel--processando-anexo" : "",
  ]
    .filter(Boolean)
    .join(" ");
}
