import type { AnexoTextoContextoFabUiTranscribrothers } from "./modulo_api_anexos_contexto_fab_projeto_em_branco_transcribrothers.ts";

/** Limite alinhado ao backend (por bloco de texto no pedido). */
export const LIMITE_CARACTERES_TEXTO_ANEXO_FAB_PEDIDO_TRANSCRIBROTHERS = 48_000;

export function truncarTextoAnexoContextoFabSeNecessarioTranscribrothers(
  texto: string,
): { texto: string; truncado: boolean } {
  const t = texto.replace(/\r\n/g, "\n").trim();
  const limite = LIMITE_CARACTERES_TEXTO_ANEXO_FAB_PEDIDO_TRANSCRIBROTHERS;
  if (t.length <= limite) {
    return { texto: t, truncado: false };
  }
  return { texto: `${t.slice(0, limite)}…`, truncado: true };
}

export function rotuloExibicaoAnexoTextoContextoFabUiTranscribrothers(
  anexo: AnexoTextoContextoFabUiTranscribrothers,
  indiceNaLista?: number,
): string {
  if (anexo.nomeArquivoOrigem?.trim()) {
    return anexo.nomeArquivoOrigem.trim();
  }
  const primeiraLinha = anexo.conteudo
    .split("\n")
    .map((l) => l.trim())
    .find((l) => l.length > 0);
  if (primeiraLinha) {
    const semHeading = primeiraLinha.replace(/^#+\s*/, "");
    const curto = semHeading.slice(0, 72);
    return semHeading.length > 72 ? `${curto}…` : curto;
  }
  const n = typeof indiceNaLista === "number" ? indiceNaLista + 1 : null;
  return n != null ? `Texto ${n}` : "Texto";
}

export async function lerArquivoMarkdownOuTextoComoUtf8Transcribrothers(arquivo: File): Promise<string> {
  const texto = await arquivo.text();
  const t = texto.replace(/\r\n/g, "\n").trim();
  if (!t) {
    throw new Error("O arquivo está vazio.");
  }
  return t;
}

export function arquivoEhDocumentoTextoLocalFabTranscribrothers(arquivo: File): boolean {
  const nome = (arquivo.name || "").toLowerCase();
  return nome.endsWith(".md") || nome.endsWith(".txt");
}

export function arquivoEhPdfAnexoFabTranscribrothers(arquivo: File): boolean {
  const nome = (arquivo.name || "").toLowerCase();
  return nome.endsWith(".pdf") || arquivo.type === "application/pdf";
}

export type TipoArquivoAnexoContextoFabTranscribrothers = "imagem" | "documento" | "desconhecido";

export function classificarArquivoAnexoContextoFabTranscribrothers(
  arquivo: File,
): TipoArquivoAnexoContextoFabTranscribrothers {
  const nome = (arquivo.name || "").toLowerCase();
  const mime = (arquivo.type || "").toLowerCase();
  if (
    mime.startsWith("image/") ||
    /\.(png|jpe?g|webp|gif)$/i.test(nome)
  ) {
    return "imagem";
  }
  if (
    arquivoEhDocumentoTextoLocalFabTranscribrothers(arquivo) ||
    arquivoEhPdfAnexoFabTranscribrothers(arquivo)
  ) {
    return "documento";
  }
  return "desconhecido";
}
