/**
 * Produz um Markdown autocontido para download: troca `![](assets/arquivo.png)` por
 * `![](data:image/png;base64,...)` buscando cada PNG no endpoint do job.
 */
const REGEX_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = /!\[([^\]]*)\]\(([^)]+)\)/g;

function normalizarHrefImagemMarkdownParaCaminhoAssetsTranscribrothers(hrefBruto: string): string | null {
  let href = hrefBruto.trim();
  if (href.startsWith("<") && href.endsWith(">")) {
    href = href.slice(1, -1).trim();
  }
  href = href.replace(/^\.\//, "");
  if (
    href.startsWith("http://") ||
    href.startsWith("https://") ||
    href.startsWith("data:")
  ) {
    return null;
  }
  if (!href.startsWith("assets/")) {
    return null;
  }
  return href;
}

async function blobParaDataUrlViaFileReaderTranscribrothers(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => resolve(String(fr.result));
    fr.onerror = () => reject(fr.error ?? new Error("FileReader falhou ao ler imagem."));
    fr.readAsDataURL(blob);
  });
}

export async function gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers(
  markdownOriginal: string,
  jobId: string,
  resolverNomeArquivoAssetParaFetch?: (nomeArquivoNoMarkdown: string) => string,
): Promise<string> {
  const itens: Array<{
    indiceInicio: number;
    indiceFim: number;
    textoAlt: string;
    caminhoAssets: string;
  }> = [];

  const re = new RegExp(REGEX_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.source, "g");
  for (const m of markdownOriginal.matchAll(re)) {
    const caminho = normalizarHrefImagemMarkdownParaCaminhoAssetsTranscribrothers(m[2]);
    if (!caminho) continue;
    itens.push({
      indiceInicio: m.index ?? 0,
      indiceFim: (m.index ?? 0) + m[0].length,
      textoAlt: m[1],
      caminhoAssets: caminho,
    });
  }

  const caminhosUnicos = [...new Set(itens.map((i) => i.caminhoAssets))];
  const mapaDataUri = new Map<string, string>();

  await Promise.all(
    caminhosUnicos.map(async (caminho) => {
      const nomeNoMd = caminho.replace(/^assets\//, "");
      const nomeArquivo = resolverNomeArquivoAssetParaFetch
        ? resolverNomeArquivoAssetParaFetch(nomeNoMd)
        : nomeNoMd;
      const url = `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivo)}`;
      const r = await fetch(url);
      if (!r.ok) {
        throw new Error(
          `Não foi possível carregar a imagem "${nomeArquivo}" para embutir no .md (HTTP ${r.status}).`,
        );
      }
      const blob = await r.blob();
      const dataUrl = await blobParaDataUrlViaFileReaderTranscribrothers(blob);
      mapaDataUri.set(caminho, dataUrl);
    }),
  );

  const ordenadosDoFimParaInicio = [...itens].sort((a, b) => b.indiceInicio - a.indiceInicio);
  let saida = markdownOriginal;
  for (const it of ordenadosDoFimParaInicio) {
    const uri = mapaDataUri.get(it.caminhoAssets);
    if (!uri) continue;
    const trechoNovo = `![${it.textoAlt}](${uri})`;
    saida = saida.slice(0, it.indiceInicio) + trechoNovo + saida.slice(it.indiceFim);
  }

  return saida;
}
