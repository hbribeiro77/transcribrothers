export const MENSAGEM_TOAST_COLE_PNG_COPIADO_DA_ANOTACAO_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS =
  "Frame copiado. Cole no Markdown (Ctrl+V) no ponto em que a imagem deve aparecer. A imagem do documento não foi substituída.";

export type AcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngTranscribrothers = {
  copiarPngDaTelaParaAreaTransferencia: true;
  persistirAnotacaoNoAssetDoDocumento: false;
  promoverPreviaParaSlotDoDocumento: false;
  deveFecharModalAnotacao: true;
  deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true;
  deveEntrarModoLinhaTracejadaNoPreview: false;
  deveInserirSnippetNoCursorDoEditor: false;
  mensagemToastSucesso: string;
};

export function resolverAcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngParaMarkdownTranscribrothers(): AcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngTranscribrothers {
  return {
    copiarPngDaTelaParaAreaTransferencia: true,
    persistirAnotacaoNoAssetDoDocumento: false,
    promoverPreviaParaSlotDoDocumento: false,
    deveFecharModalAnotacao: true,
    deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true,
    deveEntrarModoLinhaTracejadaNoPreview: false,
    deveInserirSnippetNoCursorDoEditor: false,
    mensagemToastSucesso:
      MENSAGEM_TOAST_COLE_PNG_COPIADO_DA_ANOTACAO_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
  };
}

export function inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers(args: {
  processando: boolean;
  carregando: boolean;
  aguardandoPreviewAtual: boolean;
  candidatoFramePendente: boolean;
}): boolean {
  return args.processando || args.carregando || args.aguardandoPreviewAtual;
}
