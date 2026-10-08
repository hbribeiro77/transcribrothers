import { instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers } from "./modulo_util_instante_segundos_de_offset_ms_no_nome_png_asset_tutorial_transcribrothers.ts";
import { resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers } from "./modulo_util_resolver_nome_arquivo_png_original_a_partir_referencia_assets_transcribrothers.ts";

const RE_LINHA_IMAGEM_MARKDOWN_ASSET_TRANSCRIBROTHERS = /!\[[^\]]*]\(\s*([^)]+?)\s*\)/;
const RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS = /^\s*\[[^\]]*]\(\?t=([^)]+)\)\s*$/;

function normalizarCaminhoAssetNaReferenciaMarkdownTranscribrothers(raw: string): string {
  let caminho = raw.trim().replace(/^["']|["']$/g, "");
  const indiceQuery = caminho.indexOf("?");
  if (indiceQuery >= 0) caminho = caminho.slice(0, indiceQuery).trim();
  const indiceHash = caminho.indexOf("#");
  if (indiceHash >= 0) caminho = caminho.slice(0, indiceHash).trim();
  return caminho.replace(/\\/g, "/").replace(/^\.\//, "");
}

function nomeArquivoDeCaminhoAssetMarkdownTranscribrothers(caminho: string): string {
  return caminho.split("/").pop() ?? caminho;
}

function linhaMarkdownEhImagemDoAssetOriginalTutorialTranscribrothers(
  linha: string,
  nomeArquivoOriginal: string,
): boolean {
  const correspondencia = linha.match(RE_LINHA_IMAGEM_MARKDOWN_ASSET_TRANSCRIBROTHERS);
  if (!correspondencia) return false;
  const caminho = normalizarCaminhoAssetNaReferenciaMarkdownTranscribrothers(correspondencia[1] ?? "");
  if (!caminho.toLowerCase().endsWith(".png")) return false;
  const nomeNaReferencia = nomeArquivoDeCaminhoAssetMarkdownTranscribrothers(caminho);
  return (
    resolverNomeArquivoPngOriginalAPartirDeReferenciaAssetsTranscribrothers(nomeNaReferencia) ===
    nomeArquivoOriginal
  );
}

export function formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers(segundos: number): string {
  const s = Math.max(0, Math.trunc(segundos));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

export function formatarSegundosParaParametroLinkTemporalTMarkdownTutorialTranscribrothers(
  segundos: number,
): string {
  const t = Math.max(0, segundos);
  const arred = Math.round(t * 100) / 100;
  if (Math.abs(arred - Math.round(arred)) < 1e-6) return String(Math.round(arred));
  return String(arred);
}

function montarLinhaImagemELinkTemporalMarkdownTutorialTranscribrothers(
  nomeArquivo: string,
  instanteSegundos: number,
): { linhaImagem: string; linhaLink: string } {
  const rotulo = formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers(instanteSegundos);
  const paramT = formatarSegundosParaParametroLinkTemporalTMarkdownTutorialTranscribrothers(instanteSegundos);
  return {
    linhaImagem: `![Tela em ${rotulo}](assets/${nomeArquivo})`,
    linhaLink: `[${rotulo}](?t=${paramT})`,
  };
}

export function instanteSegundosDaImagemAssetNoMarkdownTutorialTranscribrothers(
  markdown: string,
  nomeArquivoOriginal: string,
): number | null {
  const doNome = instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers(nomeArquivoOriginal);
  if (doNome != null) return doNome;
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  for (let indice = 0; indice < linhas.length; indice += 1) {
    if (!linhaMarkdownEhImagemDoAssetOriginalTutorialTranscribrothers(linhas[indice] ?? "", nomeArquivoOriginal)) {
      continue;
    }
    let seguinte = indice + 1;
    while (seguinte < linhas.length && (linhas[seguinte] ?? "").trim() === "") {
      seguinte += 1;
    }
    const matchLink = (linhas[seguinte] ?? "").match(RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS);
    if (!matchLink?.[1]) return null;
    const segundos = Number.parseFloat(matchLink[1]);
    return Number.isFinite(segundos) && segundos >= 0 ? segundos : null;
  }
  return null;
}

export function substituirReferenciaImagemAssetELinkTemporalNoMarkdownTutorialTranscribrothers(args: {
  markdown: string;
  nomeArquivoAnterior: string;
  nomeArquivoNovo: string;
  instanteSegundos: number;
}): string {
  const linhas = args.markdown.replace(/\r\n/g, "\n").split("\n");
  const { linhaImagem, linhaLink } = montarLinhaImagemELinkTemporalMarkdownTutorialTranscribrothers(
    args.nomeArquivoNovo,
    args.instanteSegundos,
  );
  const saida: string[] = [];
  let indice = 0;
  while (indice < linhas.length) {
    const linha = linhas[indice] ?? "";
    if (!linhaMarkdownEhImagemDoAssetOriginalTutorialTranscribrothers(linha, args.nomeArquivoAnterior)) {
      saida.push(linha);
      indice += 1;
      continue;
    }
    saida.push(linhaImagem);
    indice += 1;
    while (indice < linhas.length && (linhas[indice] ?? "").trim() === "") {
      saida.push(linhas[indice] ?? "");
      indice += 1;
    }
    if (
      indice < linhas.length &&
      RE_LINHA_LINK_TEMPORAL_VIDEO_MARKDOWN_TRANSCRIBROTHERS.test(linhas[indice] ?? "")
    ) {
      saida.push(linhaLink);
      indice += 1;
    } else {
      if (saida[saida.length - 1]?.trim() !== "") saida.push("");
      saida.push(linhaLink);
    }
  }
  return saida.join("\n");
}

export function navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers(args: {
  temVideoEntrada: boolean;
  instanteSegundos: number | null;
}): boolean {
  return args.temVideoEntrada && args.instanteSegundos != null && Number.isFinite(args.instanteSegundos);
}

export function usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers(args: {
  nomeArquivoNoDocumento: string;
  nomeArquivoCandidato: string | null;
  capturando: boolean;
}): boolean {
  if (args.capturando) return false;
  const candidato = (args.nomeArquivoCandidato || "").trim();
  if (!candidato) return false;
  return candidato !== args.nomeArquivoNoDocumento.trim();
}
