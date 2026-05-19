/** Se o Markdown aponta para `foo.anotado.png`, devolve `foo.png` para metadados e editor. */

export function resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers(
  nomeArquivoNaReferenciaMarkdown: string,
): string {
  const nome = nomeArquivoNaReferenciaMarkdown.trim();
  const sufixo = ".anotado.png";
  if (nome.toLowerCase().endsWith(sufixo)) {
    return `${nome.slice(0, -sufixo.length)}.png`;
  }
  return nome;
}
