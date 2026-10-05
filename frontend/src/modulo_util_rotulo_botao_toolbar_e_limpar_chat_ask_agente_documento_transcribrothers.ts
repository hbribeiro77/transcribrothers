export function rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(
  aberto: boolean,
): "Ocultar chat" | "Abrir chat" {
  return aberto ? "Ocultar chat" : "Abrir chat";
}

export function limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers(args: {
  historicoVazio: boolean;
  enviando: boolean;
  preparandoPrevia?: boolean;
}): boolean {
  return args.historicoVazio || args.enviando || args.preparandoPrevia === true;
}
