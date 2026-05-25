import { obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers } from "./modulo_util_rotulo_numero_versao_historico_tutorial_markdown_por_projeto_transcribrothers.ts";

type VersaoHistoricoResumoTranscribrothers = {
  id: number;
  criado_em: string | null;
};

/**
 * Subtítulo ao lado do título do frame (ex.: «v3 de 3 · 19/05/2026, 20:32»).
 * Substitui o antigo «(Markdown)».
 */
export function montarSubtituloVersaoEDataFrameDocumentoTutorialTranscribrothers(args: {
  historicoVersaoSelecionadaId: number | null;
  listaHistoricoVersoes: VersaoHistoricoResumoTranscribrothers[] | null;
  criadoEmVersaoHistoricoSelecionada: string | null;
  formatarDataHora: (iso: string | null) => string;
  jobUpdatedAt: string | null;
  exibirVersaoAtualServidor: boolean;
}): string | null {
  const lista = args.listaHistoricoVersoes ?? [];
  const total = lista.length;

  if (args.historicoVersaoSelecionadaId !== null && total > 0) {
    const indice = lista.findIndex((r) => r.id === args.historicoVersaoSelecionadaId);
    if (indice >= 0) {
      const numero = obterNumeroVersaoHistoricoTutorialMarkdownPorIndiceNaListaDescTranscribrothers(
        indice,
        total,
      );
      const prefixoVersao = total > 1 ? `v${numero} de ${total}` : `v${numero}`;
      const data =
        args.criadoEmVersaoHistoricoSelecionada != null
          ? args.formatarDataHora(args.criadoEmVersaoHistoricoSelecionada)
          : args.formatarDataHora(lista[indice]?.criado_em ?? null);
      return data ? `${prefixoVersao} · ${data}` : prefixoVersao;
    }
  }

  if (args.exibirVersaoAtualServidor) {
    const dataAtual = args.formatarDataHora(args.jobUpdatedAt);
    if (total > 0) {
      const prefixoVersao = total > 1 ? `v${total} de ${total}` : `v1`;
      return dataAtual ? `${prefixoVersao} · ${dataAtual}` : prefixoVersao;
    }
    if (dataAtual) {
      return `Versão atual · ${dataAtual}`;
    }
    return "Versão atual";
  }

  return null;
}
