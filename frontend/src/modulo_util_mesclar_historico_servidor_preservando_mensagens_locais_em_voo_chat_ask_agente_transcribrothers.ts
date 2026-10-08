export type MensagemEmVooOuHistoricoChatAskAgenteTranscribrothers = {
  id: string;
  papel: "usuario" | "assistente" | "agente";
  texto: string;
  estado?: string | null;
};

function mensagemChatAskAgenteEhLocalEmVooTranscribrothers(
  mensagem: MensagemEmVooOuHistoricoChatAskAgenteTranscribrothers,
): boolean {
  return (
    mensagem.id.includes("-usuario-local-") ||
    mensagem.id.includes("-stream-") ||
    mensagem.estado === "escrevendo"
  );
}

export function mesclarHistoricoServidorPreservandoMensagensLocaisEmVooChatAskAgenteTranscribrothers<
  T extends MensagemEmVooOuHistoricoChatAskAgenteTranscribrothers,
>(args: {
  historicoServidor: T[];
  mensagensLocais: T[];
}): T[] {
  const saida = [...args.historicoServidor];
  for (const local of args.mensagensLocais) {
    if (!mensagemChatAskAgenteEhLocalEmVooTranscribrothers(local)) continue;
    if (local.papel === "usuario") {
      const jaTem = saida.some((item) => item.papel === "usuario" && item.texto === local.texto);
      if (!jaTem) saida.push(local);
      continue;
    }
    const textoLocal = (local.texto || "").trim();
    const servidorJaTemEssaFala =
      textoLocal.length > 0 &&
      saida.some(
        (item) =>
          (item.papel === "agente" || item.papel === "assistente") && item.texto === local.texto,
      );
    if (servidorJaTemEssaFala) continue;
    const ultimo = saida[saida.length - 1];
    if (ultimo?.papel === "usuario" || saida.every((item) => item.papel !== "agente" && item.papel !== "assistente")) {
      if (!saida.some((item) => item.id === local.id)) saida.push(local);
    }
  }
  return saida;
}
