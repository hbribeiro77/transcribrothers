/**
 * Numeração de versões do histórico por projeto (job), não pelo id global do SQLite.
 * A API devolve versões do job ordenadas por id decrescente (mais recente primeiro).
 */

/** Número da versão no projeto: 1 = mais antiga, total = mais recente. */
export function obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers(
  indiceNaListaDesc: number,
  totalVersoesNoProjeto: number,
): number {
  if (totalVersoesNoProjeto < 1) return 1;
  return Math.max(1, totalVersoesNoProjeto - indiceNaListaDesc);
}

export function montarRotuloVersaoHistoricoTutorialMarkdownParaSelectUiTranscribrothers(args: {
  indiceNaListaDesc: number;
  totalVersoesNoProjeto: number;
  criadoEmFormatado: string;
  rotuloOrigemPortugues: string;
  previewLinhaTruncada: string;
  idInternoSqlite: number;
}): { textoOpcao: string; titleOpcao: string } {
  const numero = obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers(
    args.indiceNaListaDesc,
    args.totalVersoesNoProjeto,
  );
  const prefixoVersao =
    args.totalVersoesNoProjeto > 1
      ? `v${numero} de ${args.totalVersoesNoProjeto}`
      : `v${numero}`;
  const trunc = args.previewLinhaTruncada;
  const textoOpcao = `${prefixoVersao} · ${args.criadoEmFormatado} · ${args.rotuloOrigemPortugues}${
    trunc ? ` — ${trunc}` : ""
  }`;
  const titleOpcao = `Versão ${numero} deste projeto (registro interno #${args.idInternoSqlite})`;
  return { textoOpcao, titleOpcao };
}
