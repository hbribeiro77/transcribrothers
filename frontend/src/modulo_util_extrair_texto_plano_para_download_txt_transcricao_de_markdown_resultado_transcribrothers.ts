/**
 * Extrai o texto corrido da transcrição a partir do Markdown do job (destino só transcrição).
 */

export function extrairTextoPlanoParaDownloadTxtTranscricaoDeMarkdownResultadoTranscribrothers(
  markdown: string,
): string {
  const t = (markdown || "").replace(/^\uFEFF/, "").trim();
  if (!t) return "";
  const comTitulo = t.match(/^#\s+Transcri[cç][aã]o\s*\r?\n+([\s\S]*?)(?=\r?\n##\s+Segmentos\b|$)/i);
  if (comTitulo) return comTitulo[1].trim();
  return t;
}
