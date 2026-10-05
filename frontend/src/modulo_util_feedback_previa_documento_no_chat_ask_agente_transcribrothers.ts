export const TEXTO_MENSAGEM_AGENTE_APLICOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Apliquei a alteração no documento.";

export const TEXTO_MENSAGEM_AGENTE_DESCARTOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Mantive o documento como estava.";

export const TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Preparando a prévia…";

export const MS_TETO_ESPERA_PREVIA_DOCUMENTO_CHAT_AGENTE_TRANSCRIBROTHERS = 120_000;

export function composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers(args: {
  enviandoMensagem: boolean;
  preparandoPrevia: boolean;
}): boolean {
  return args.enviandoMensagem || args.preparandoPrevia;
}

export function preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers(args: {
  preparandoPrevia: boolean;
  temObjetoPreview: boolean;
  decorridoMs: number;
  tetoMs?: number;
}): boolean {
  if (!args.preparandoPrevia || args.temObjetoPreview) return false;
  const teto = args.tetoMs ?? MS_TETO_ESPERA_PREVIA_DOCUMENTO_CHAT_AGENTE_TRANSCRIBROTHERS;
  return args.decorridoMs >= teto;
}

export function chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers(args: {
  preparandoPrevia: boolean;
  temObjetoPreview: boolean;
}): boolean {
  return args.preparandoPrevia && !args.temObjetoPreview;
}
