export type NomeFerramentaChatAgenteDocumentoTranscribrothers =
  | "edicao_parcial"
  | "revisao_profunda"
  | "sem_video";

export function ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers(args: {
  modoPainel: "regeneracao_inteira" | "edicao_parcial";
  preset: "sem_video" | "revisao_profunda" | null;
}): NomeFerramentaChatAgenteDocumentoTranscribrothers | null {
  if (args.modoPainel === "edicao_parcial") return "edicao_parcial";
  if (args.preset === "revisao_profunda") return "revisao_profunda";
  if (args.preset === "sem_video") return "sem_video";
  return null;
}

export function rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers(
  nome: string | null | undefined,
): string {
  if (nome === "edicao_parcial") return "Aplicar no documento";
  if (nome === "revisao_profunda") return "Revisar o documento a fundo";
  if (nome === "sem_video") return "Reescrever sem usar o vídeo";
  return "";
}

export function chipFerramentaChatAgenteDeveAparecerNaGavetaTranscribrothers(
  _nome: NomeFerramentaChatAgenteDocumentoTranscribrothers,
): boolean {
  return false;
}

export function propostaFerramentaChatAgenteExigeConfirmacaoForteTranscribrothers(
  nome: string | null | undefined,
): boolean {
  return nome === "revisao_profunda" || nome === "sem_video";
}

export function textoConfirmacaoPropostaFerramentaChatAgenteTranscribrothers(
  nome: string | null | undefined,
): string {
  if (nome === "revisao_profunda") {
    return "Isso vai varrer o documento contra a transcrição e pode mudar várias seções. Quer rodar?";
  }
  if (nome === "sem_video") {
    return "Isso vai reescrever o documento só com texto e imagens, sem usar o vídeo. Quer continuar?";
  }
  return "";
}
