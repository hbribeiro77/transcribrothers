import { resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers } from "./modulo_util_resolver_nome_arquivo_png_original_a_partir_referencia_assets_transcribrothers.ts";

const RE_LINHA_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = /!\[[^\]]*]\(\s*([^)]+?)\s*\)/;
const RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS = /^\s*\[[^\]]*]\(\?t=[^)]+\)\s*$/;

function normalizarCaminhoAssetNaReferenciaMarkdownTranscribrothers(raw: string): string {
  let caminho = raw.trim().replace(/^["']|["']$/g, "");
  const indiceQuery = caminho.indexOf("?");
  if (indiceQuery >= 0) caminho = caminho.slice(0, indiceQuery).trim();
  const indiceHash = caminho.indexOf("#");
  if (indiceHash >= 0) caminho = caminho.slice(0, indiceHash).trim();
  return caminho.replace(/\\/g, "/").replace(/^\.\//, "");
}

function linhaMarkdownReferenciaImagemAssetTutorialTranscribrothers(
  linha: string,
  nomeArquivoOriginal: string,
): boolean {
  const correspondencia = linha.match(RE_LINHA_IMAGEM_MARKDOWN_TRANSCRIBROTHERS);
  if (!correspondencia) return false;

  const caminho = normalizarCaminhoAssetNaReferenciaMarkdownTranscribrothers(correspondencia[1]);
  if (!caminho.toLowerCase().endsWith(".png")) return false;

  const nomeNaReferencia = caminho.split("/").pop() ?? caminho;
  const nomeOriginalResolvido =
    resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers(nomeNaReferencia);
  return nomeOriginalResolvido === nomeArquivoOriginal;
}

/** Remove `![](assets/…)` da imagem e, se existir logo abaixo, o link temporal `?t=`. */
export function removerReferenciaImagemAssetDoMarkdownTutorialTranscribrothers(
  markdown: string,
  nomeArquivoOriginal: string,
): string {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const linhasFiltradas: string[] = [];
  let indice = 0;

  while (indice < linhas.length) {
    const linha = linhas[indice] ?? "";

    if (!linhaMarkdownReferenciaImagemAssetTutorialTranscribrothers(linha, nomeArquivoOriginal)) {
      linhasFiltradas.push(linha);
      indice += 1;
      continue;
    }

    indice += 1;

    while (indice < linhas.length && (linhas[indice] ?? "").trim() === "") {
      indice += 1;
    }

    if (
      indice < linhas.length &&
      RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS.test(linhas[indice] ?? "")
    ) {
      indice += 1;
      while (indice < linhas.length && (linhas[indice] ?? "").trim() === "") {
        indice += 1;
      }
    }
  }

  return linhasFiltradas
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trimEnd();
}
