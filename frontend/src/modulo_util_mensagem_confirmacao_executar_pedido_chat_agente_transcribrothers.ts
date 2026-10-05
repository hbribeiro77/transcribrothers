const PADRAO_CONFIRMACAO_PEDIDO_CHAT_AGENTE_TRANSCRIBROTHERS =
  /^(beleza[,!.]?\s*)?(pode\s+(fazer|prosseguir|aplicar|seguir)|faz(er)?(\s+isso)?|aplica(r)?(\s+isso)?|confirmo|manda)\s*[.!]*$/i;

export function mensagemEhConfirmacaoExecutarPedidoChatAgenteTranscribrothers(
  texto: string,
): boolean {
  return PADRAO_CONFIRMACAO_PEDIDO_CHAT_AGENTE_TRANSCRIBROTHERS.test(texto.trim());
}
