export const MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS =
  "Referência copiada. Cole no texto do Markdown (Ctrl+V) no ponto em que a imagem deve aparecer.";

export const MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_ANOTADA_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS =
  "Imagem editada copiada. Cole no texto do Markdown (Ctrl+V). A captura original foi preservada nos assets.";

export type AcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers = {
  deveFecharModalAnotacao: true;
  deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true;
  deveEntrarModoLinhaTracejadaNoPreview: false;
  deveInserirSnippetNoCursorDoEditor: false;
  mensagemToastSucesso: string;
};

export function resolverAcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers(args: {
  snippetUsaVersaoAnotada: boolean;
}): AcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers {
  return {
    deveFecharModalAnotacao: true,
    deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true,
    deveEntrarModoLinhaTracejadaNoPreview: false,
    deveInserirSnippetNoCursorDoEditor: false,
    mensagemToastSucesso: args.snippetUsaVersaoAnotada
      ? MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_ANOTADA_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS
      : MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
  };
}
