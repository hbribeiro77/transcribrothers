const TIPOS_MIME_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS = new Set([
  "image/png",
  "image/jpeg",
  "image/jpg",
  "image/webp",
  "image/gif",
  "image/bmp",
]);

const EXTENSOES_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS = new Set([
  ".png",
  ".jpg",
  ".jpeg",
  ".webp",
  ".gif",
  ".bmp",
]);

function arquivoImagemElegivelParaInsercaoEditorMarkdownTranscribrothers(
  arquivo: File,
): boolean {
  const mime = (arquivo.type || "").toLowerCase();
  if (mime && TIPOS_MIME_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS.has(mime)) {
    return true;
  }
  const nome = (arquivo.name || "").toLowerCase();
  for (const ext of EXTENSOES_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS) {
    if (nome.endsWith(ext)) return true;
  }
  return false;
}

/** Evita colar imagem no preview quando o foco está em campo de texto (editor, formulários). */
export function elementoAtivoEstaEmCampoDigitavelParaColarTextoTranscribrothers(): boolean {
  const elemento = document.activeElement;
  if (!elemento) return false;
  if (elemento instanceof HTMLInputElement || elemento instanceof HTMLTextAreaElement) {
    return true;
  }
  if (elemento instanceof HTMLElement && elemento.isContentEditable) {
    return true;
  }
  return false;
}

/**
 * Lê a primeira imagem da área de transferência via Clipboard API (botão «Colar imagem»).
 * Requer contexto seguro e permissão do navegador; retorna null se indisponível ou vazio.
 */
export async function extrairArquivoImagemDaApiClipboardNavegadorTranscribrothers(): Promise<File | null> {
  if (!navigator.clipboard?.read) return null;

  try {
    const itens = await navigator.clipboard.read();
    for (const item of itens) {
      for (const tipo of item.types) {
        const mime = tipo.toLowerCase();
        if (!mime.startsWith("image/")) continue;
        if (!TIPOS_MIME_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS.has(mime)) continue;
        const blob = await item.getType(tipo);
        const extensao = mime === "image/jpeg" ? "jpg" : mime.split("/")[1] || "png";
        return new File([blob], `imagem-colada.${extensao}`, { type: mime });
      }
    }
  } catch {
    return null;
  }

  return null;
}

/** Retorna o primeiro arquivo de imagem em `clipboardData`, se houver. */
export function extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers(
  evento: ClipboardEvent,
): File | null {
  const itens = evento.clipboardData?.items;
  if (!itens) return null;

  for (let indice = 0; indice < itens.length; indice += 1) {
    const item = itens[indice];
    if (!item.type.startsWith("image/")) continue;
    const mime = item.type.toLowerCase();
    if (!TIPOS_MIME_IMAGEM_EDITOR_MARKDOWN_TRANSCRIBROTHERS.has(mime)) continue;
    const arquivo = item.getAsFile();
    if (arquivo) return arquivo;
  }

  return null;
}

/** Retorna a primeira imagem solta via arrastar-e-soltar. */
export function extrairArquivoImagemDoEventoArrastarSoltarEditorMarkdownTranscribrothers(
  evento: DragEvent,
): File | null {
  const arquivos = evento.dataTransfer?.files;
  if (!arquivos || arquivos.length === 0) return null;

  for (let indice = 0; indice < arquivos.length; indice += 1) {
    const arquivo = arquivos[indice];
    if (arquivoImagemElegivelParaInsercaoEditorMarkdownTranscribrothers(arquivo)) {
      return arquivo;
    }
  }

  return null;
}

export function eventoArrastarSoltarContemArquivoImagemEditorMarkdownTranscribrothers(
  evento: DragEvent,
): boolean {
  const tipos = evento.dataTransfer?.types;
  if (!tipos) return false;
  return Array.from(tipos).includes("Files");
}

/** Estima o índice do caret no textarea a partir do ponto onde a imagem foi solta. */
export function obterIndiceCaretTextareaMarkdownAPartirCoordenadasClienteTranscribrothers(
  textarea: HTMLTextAreaElement,
  clientX: number,
  clientY: number,
): number {
  const valor = textarea.value;
  if (!valor) return 0;

  const estilo = window.getComputedStyle(textarea);
  const rect = textarea.getBoundingClientRect();
  const paddingTop = parseFloat(estilo.paddingTop || "0");
  const paddingLeft = parseFloat(estilo.paddingLeft || "0");
  const paddingRight = parseFloat(estilo.paddingRight || "0");
  const lineHeight =
    parseFloat(estilo.lineHeight) || parseFloat(estilo.fontSize) * 1.35 || 18;

  const yRelativo = clientY - rect.top - paddingTop + textarea.scrollTop;
  const xRelativo = clientX - rect.left - paddingLeft;
  const linhaAlvo = Math.max(0, Math.floor(yRelativo / lineHeight));

  const linhas = valor.split("\n");
  let offset = 0;
  for (let indiceLinha = 0; indiceLinha < linhas.length; indiceLinha += 1) {
    const linha = linhas[indiceLinha] ?? "";
    if (indiceLinha === linhaAlvo) {
      const larguraUtil = Math.max(
        1,
        textarea.clientWidth - paddingLeft - paddingRight,
      );
      const coluna =
        linha.length > 0
          ? Math.round((Math.max(0, xRelativo) / larguraUtil) * linha.length)
          : 0;
      return Math.min(valor.length, offset + Math.min(Math.max(0, coluna), linha.length));
    }
    offset += linha.length + 1;
  }

  return valor.length;
}
