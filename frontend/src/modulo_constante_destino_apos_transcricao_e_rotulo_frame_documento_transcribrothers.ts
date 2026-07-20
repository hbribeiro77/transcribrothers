/** Destino escolhido no stepper após o vídeo (persistido em `steps_json.destino_apos_transcricao`). */

export type DestinoAposTranscricaoTranscribrothers =
  | "gerar_tutorial"
  | "projeto_em_branco"
  | "reproducao_bug"
  | "notas_proposta_funcionalidade"
  | "so_transcricao";

export const DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS: DestinoAposTranscricaoTranscribrothers =
  "gerar_tutorial";

const DESTINOS_VALIDOS: readonly DestinoAposTranscricaoTranscribrothers[] = [
  "gerar_tutorial",
  "projeto_em_branco",
  "reproducao_bug",
  "notas_proposta_funcionalidade",
  "so_transcricao",
];

/** Título do frame do documento conforme o destino da transcrição. */
export const ROTULO_TITULO_FRAME_DOCUMENTO_POR_DESTINO_APOS_TRANSCRICAO_TRANSCRIBROTHERS: Record<
  DestinoAposTranscricaoTranscribrothers,
  string
> = {
  gerar_tutorial: "Tutorial",
  projeto_em_branco: "Documento",
  reproducao_bug: "Reprodução do bug",
  notas_proposta_funcionalidade: "Notas de proposta",
  so_transcricao: "Transcrição",
};

export function normalizarDestinoAposTranscricaoDeStepsJsonJobTranscribrothers(
  valor: unknown,
): DestinoAposTranscricaoTranscribrothers {
  if (typeof valor === "string" && (DESTINOS_VALIDOS as readonly string[]).includes(valor)) {
    return valor as DestinoAposTranscricaoTranscribrothers;
  }
  return DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS;
}

export function obterTituloFrameDocumentoPorDestinoAposTranscricaoTranscribrothers(
  destino: DestinoAposTranscricaoTranscribrothers,
): string {
  return ROTULO_TITULO_FRAME_DOCUMENTO_POR_DESTINO_APOS_TRANSCRICAO_TRANSCRIBROTHERS[destino];
}
