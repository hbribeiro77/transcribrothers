export const TEXTO_MENSAGEM_AGENTE_APLICOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Apliquei a alteração no documento.";

export const TEXTO_MENSAGEM_AGENTE_DESCARTOU_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Mantive o documento como estava.";

export const TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS =
  "Preparando a prévia…";

export const TEXTO_STATUS_PENSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS = "pensando…";

export const TEXTO_STATUS_AINDA_PROCESSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS =
  "ainda processando…";

export const MS_TETO_ESPERA_PREVIA_DOCUMENTO_CHAT_AGENTE_TRANSCRIBROTHERS = 120_000;

export function composerChatAskAgenteDeveFicarTravadoPorPreviaDocumentoTranscribrothers(args: {
  enviandoMensagem: boolean;
  preparandoPrevia: boolean;
  jobGerandoMarkdown?: boolean;
}): boolean {
  return args.enviandoMensagem || args.preparandoPrevia || Boolean(args.jobGerandoMarkdown);
}

export function preparandoPreviaDocumentoChatAgenteDeveDestravarPorEstouroDeTempoTranscribrothers(args: {
  preparandoPrevia: boolean;
  temObjetoPreview: boolean;
  decorridoMs: number;
  tetoMs?: number;
  jobAindaGerandoMarkdown?: boolean;
}): boolean {
  if (!args.preparandoPrevia || args.temObjetoPreview || args.jobAindaGerandoMarkdown) return false;
  const teto = args.tetoMs ?? MS_TETO_ESPERA_PREVIA_DOCUMENTO_CHAT_AGENTE_TRANSCRIBROTHERS;
  return args.decorridoMs >= teto;
}

export function chatAskAgenteDeveMostrarSpinnerPreparandoPreviaTranscribrothers(args: {
  preparandoPrevia: boolean;
  temObjetoPreview: boolean;
  jobGerandoMarkdown?: boolean;
}): boolean {
  return (args.preparandoPrevia || Boolean(args.jobGerandoMarkdown)) && !args.temObjetoPreview;
}

export function textoIndicadorProcessandoTurnoChatAskAgenteTranscribrothers(args: {
  enviandoMensagem: boolean;
  bolhaEscrevendoJaTemTexto: boolean;
}): string | null {
  if (!args.enviandoMensagem) return null;
  return args.bolhaEscrevendoJaTemTexto
    ? TEXTO_STATUS_AINDA_PROCESSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS
    : TEXTO_STATUS_PENSANDO_TURNO_CHAT_ASK_AGENTE_TRANSCRIBROTHERS;
}
