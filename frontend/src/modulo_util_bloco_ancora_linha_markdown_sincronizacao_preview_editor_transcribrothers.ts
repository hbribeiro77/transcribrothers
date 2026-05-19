/** Tipos de bloco exibidos no indicador de contexto da edição. */
export type TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers =
  | "titulo-h1"
  | "secao-h2"
  | "subsecao-h3"
  | "heading-outro"
  | "imagem"
  | "lista"
  | "codigo"
  | "citacao"
  | "separador"
  | "tabela"
  | "paragrafo"
  | "outro";

export function obterNumeroLinhaInicioNoNoMarkdownAstTranscribrothers(no: {
  position?: { start?: { line?: number | null } | null } | null;
}): number | null {
  const linha = no.position?.start?.line;
  return typeof linha === "number" && linha > 0 ? linha : null;
}

export function descreverTipoBlocoMarkdownNaLinhaTranscribrothers(
  linhaBruta: string,
): TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers {
  const trim = linhaBruta.trim();
  if (!trim) return "outro";
  if (/^```/.test(trim)) return "codigo";
  if (/^!\[[^\]]*\]\([^)]+\)/.test(trim) || /^<img\s/i.test(trim)) return "imagem";
  if (/^#{1,6}(?:\s|$)/.test(trim)) {
    const nivel = trim.match(/^#+/)?.[0].length ?? 0;
    if (nivel === 1) return "titulo-h1";
    if (nivel === 2) return "secao-h2";
    if (nivel === 3) return "subsecao-h3";
    return "heading-outro";
  }
  if (/^[-*+]\s+/.test(trim) || /^\d+\.\s+/.test(trim)) return "lista";
  if (/^>\s?/.test(trim)) return "citacao";
  if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(trim)) return "separador";
  if (/^\|.+\|/.test(trim)) return "tabela";
  return "paragrafo";
}

const ROTULOS_TIPO_BLOCO_MARKDOWN_PT_BR: Record<
  TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers,
  string
> = {
  "titulo-h1": "Título principal",
  "secao-h2": "Seção ##",
  "subsecao-h3": "Subseção ###",
  "heading-outro": "Título",
  imagem: "Imagem",
  lista: "Lista",
  codigo: "Código",
  citacao: "Citação",
  separador: "Separador",
  tabela: "Tabela",
  paragrafo: "Parágrafo",
  outro: "Bloco",
};

export function obterRotuloPortuguesTipoBlocoMarkdownTranscribrothers(
  tipo: TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers,
): string {
  return ROTULOS_TIPO_BLOCO_MARKDOWN_PT_BR[tipo];
}

export function obterLinhaTextoMarkdownTranscribrothers(
  markdown: string,
  numeroLinha: number,
): string {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  if (numeroLinha < 1 || numeroLinha > linhas.length) return "";
  return linhas[numeroLinha - 1] ?? "";
}

/** Linha de início do bloco mais próximo acima ou na posição do cursor (heurística por linhas âncora). */
export type AncoraBlocoMarkdownTutorialTranscribrothers = {
  numeroLinha: number;
  tipo: TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers;
};

/** Âncoras na ordem do documento-fonte (não do AST do react-markdown). */
export function listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers(
  markdown: string,
): AncoraBlocoMarkdownTutorialTranscribrothers[] {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const ancoras: AncoraBlocoMarkdownTutorialTranscribrothers[] = [];
  let dentroBlocoCodigo = false;
  let dentroBlockquote = false;

  for (let indice = 0; indice < linhas.length; indice += 1) {
    const numeroLinha = indice + 1;
    const linha = linhas[indice];
    const trim = linha.trim();

    if (/^```/.test(trim)) {
      if (!dentroBlocoCodigo) {
        ancoras.push({ numeroLinha, tipo: "codigo" });
      }
      dentroBlocoCodigo = !dentroBlocoCodigo;
      continue;
    }
    if (dentroBlocoCodigo) continue;

    if (/^>\s?/.test(trim)) {
      if (!dentroBlockquote) {
        ancoras.push({ numeroLinha, tipo: "citacao" });
        dentroBlockquote = true;
      }
      continue;
    }
    dentroBlockquote = false;

    if (!trim) continue;

    if (/^#{1,6}\s/.test(trim)) {
      ancoras.push({
        numeroLinha,
        tipo: descreverTipoBlocoMarkdownNaLinhaTranscribrothers(trim),
      });
      continue;
    }
    if (/^!\[/.test(trim) || /^<img\s/i.test(trim)) {
      ancoras.push({ numeroLinha, tipo: "imagem" });
      continue;
    }
    if (/^[-*+]\s+/.test(trim) || /^\d+\.\s+/.test(trim)) {
      ancoras.push({ numeroLinha, tipo: "lista" });
      continue;
    }
    if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(trim)) {
      ancoras.push({ numeroLinha, tipo: "separador" });
      continue;
    }
    if (/^\|/.test(trim)) {
      ancoras.push({ numeroLinha, tipo: "tabela" });
      continue;
    }

    // Parágrafo após linha vazia OU após outro tipo de bloco (ex.: imagem, título).
    // Sem isso, um parágrafo logo abaixo de `![](assets/...)` não ganha âncora e o preview
    // consome a âncora do bloco seguinte — inserção de imagem cai na linha errada.
    const trimAnterior = indice > 0 ? (linhas[indice - 1] ?? "").trim() : "";
    const inicioNovoParagrafo =
      indice === 0 ||
      !trimAnterior ||
      descreverTipoBlocoMarkdownNaLinhaTranscribrothers(trimAnterior) !== "paragrafo";
    if (inicioNovoParagrafo) {
      ancoras.push({ numeroLinha, tipo: "paragrafo" });
    }
  }

  return ancoras;
}

function linhaMarkdownIniciaNovoBlocoAposParagrafoTranscribrothers(trim: string): boolean {
  if (!trim) return true;
  if (/^```/.test(trim)) return true;
  if (/^#{1,6}\s/.test(trim)) return true;
  if (/^>\s?/.test(trim)) return true;
  if (/^!\[/.test(trim) || /^<img\s/i.test(trim)) return true;
  if (/^[-*+]\s+/.test(trim) || /^\d+\.\s+/.test(trim)) return true;
  if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(trim)) return true;
  if (/^\|/.test(trim)) return true;
  return false;
}

/** Última linha (1-based) do bloco Markdown que começa em `linhaInicio`. */
export function obterNumeroLinhaFimBlocoMarkdownAPartirLinhaInicioTranscribrothers(
  markdown: string,
  linhaInicio: number,
): number {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const indiceInicio = linhaInicio - 1;
  if (indiceInicio < 0 || indiceInicio >= linhas.length) {
    return Math.max(1, Math.min(linhas.length, linhaInicio));
  }

  const trimInicio = (linhas[indiceInicio] ?? "").trim();

  if (/^```/.test(trimInicio)) {
    let indice = indiceInicio + 1;
    while (indice < linhas.length && !/^```/.test((linhas[indice] ?? "").trim())) {
      indice += 1;
    }
    if (indice < linhas.length) return indice + 1;
    return linhas.length;
  }

  if (/^>\s?/.test(trimInicio)) {
    let indice = indiceInicio;
    while (indice + 1 < linhas.length && /^>\s?/.test((linhas[indice + 1] ?? "").trim())) {
      indice += 1;
    }
    return indice + 1;
  }

  if (linhaMarkdownIniciaNovoBlocoAposParagrafoTranscribrothers(trimInicio) && trimInicio) {
    return linhaInicio;
  }

  let indice = indiceInicio;
  while (indice + 1 < linhas.length) {
    const proxima = (linhas[indice + 1] ?? "").trim();
    if (!proxima || linhaMarkdownIniciaNovoBlocoAposParagrafoTranscribrothers(proxima)) break;
    indice += 1;
  }
  return indice + 1;
}

export function obterNumeroLinhaBlocoAncoraAtivaNoCursorMarkdownTranscribrothers(
  markdown: string,
  numeroLinhaCursor: number,
): number {
  const ancoras = listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers(markdown);
  let ultimaAncora = 1;
  for (const ancora of ancoras) {
    if (ancora.numeroLinha > numeroLinhaCursor) break;
    ultimaAncora = ancora.numeroLinha;
  }
  return ultimaAncora;
}

export function obterElementoDomPreviewMarkdownParaNumeroLinhaTranscribrothers(
  container: HTMLElement,
  numeroLinhaAlvo: number,
): HTMLElement | null {
  return (
    container.querySelector<HTMLElement>(`#tb-md-linha-${numeroLinhaAlvo}`) ??
    container.querySelector<HTMLElement>(`[data-tb-linha-inicio="${numeroLinhaAlvo}"]`)
  );
}

export function obterOffsetTopoElementoRelativoContainerScrollTranscribrothers(
  elemento: HTMLElement,
  container: HTMLElement,
): number {
  const elementoRect = elemento.getBoundingClientRect();
  const containerRect = container.getBoundingClientRect();
  return elementoRect.top - containerRect.top + container.scrollTop;
}

/** Onde a linha do cursor está no viewport visível do textarea (0 = topo, 1 = base). */
export function obterFracaoVerticalLinhaNoViewportTextareaMarkdownTranscribrothers(
  textarea: HTMLTextAreaElement,
  numeroLinha: number,
): number {
  const estilo = window.getComputedStyle(textarea);
  const alturaLinha =
    Number.parseFloat(estilo.lineHeight) || Number.parseFloat(estilo.fontSize) * 1.45 || 20;
  const paddingTopo = Number.parseFloat(estilo.paddingTop) || 0;
  const offsetLinhaNoConteudo = paddingTopo + Math.max(0, numeroLinha - 1) * alturaLinha;
  const posicaoNoViewport = offsetLinhaNoConteudo - textarea.scrollTop;
  const fracao = posicaoNoViewport / Math.max(textarea.clientHeight, 1);
  return Math.min(1, Math.max(0, fracao));
}

/** Rola o preview para o bloco ficar na mesma altura relativa que o cursor no editor. */
export function rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers(
  container: HTMLElement,
  elemento: HTMLElement,
  fracaoVerticalNoViewport: number,
  margemTopoPx = 8,
): void {
  const offsetElemento = obterOffsetTopoElementoRelativoContainerScrollTranscribrothers(
    elemento,
    container,
  );
  const alvoScroll =
    offsetElemento - fracaoVerticalNoViewport * container.clientHeight + margemTopoPx;
  const maxScroll = Math.max(0, container.scrollHeight - container.clientHeight);
  container.scrollTo({
    top: Math.min(maxScroll, Math.max(0, alvoScroll)),
    behavior: "smooth",
  });
}

export function rolarContainerScrollAteElementoComOffsetTranscribrothers(
  container: HTMLElement,
  elemento: HTMLElement,
  offsetTopoPx = 8,
): void {
  rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers(
    container,
    elemento,
    0,
    offsetTopoPx,
  );
}

export function rolarPreviewMarkdownProporcionalPorNumeroLinhaTranscribrothers(
  container: HTMLElement,
  numeroLinha: number,
  totalLinhas: number,
  fracaoVerticalNoViewport = 0,
): void {
  if (totalLinhas <= 1) {
    container.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  const proporcaoDocumento = (numeroLinha - 1) / (totalLinhas - 1);
  const maxScroll = Math.max(0, container.scrollHeight - container.clientHeight);
  const alvoScroll =
    proporcaoDocumento * maxScroll - fracaoVerticalNoViewport * container.clientHeight;
  container.scrollTo({
    top: Math.min(maxScroll, Math.max(0, alvoScroll)),
    behavior: "smooth",
  });
}

export function calcularScrollTopTextareaMarkdownParaNumeroLinhaTranscribrothers(
  textarea: HTMLTextAreaElement,
  numeroLinha: number,
): number {
  const estilo = window.getComputedStyle(textarea);
  const alturaLinha =
    Number.parseFloat(estilo.lineHeight) || Number.parseFloat(estilo.fontSize) * 1.45 || 20;
  return Math.max(0, (numeroLinha - 1) * alturaLinha - textarea.clientHeight * 0.35);
}

export function rolarTextareaMarkdownParaNumeroLinhaAproximadoTranscribrothers(
  textarea: HTMLTextAreaElement,
  numeroLinha: number,
  opcoes?: { animacaoSuave?: boolean },
): void {
  const alvo = calcularScrollTopTextareaMarkdownParaNumeroLinhaTranscribrothers(
    textarea,
    numeroLinha,
  );
  if (opcoes?.animacaoSuave) {
    textarea.scrollTo({ top: alvo, behavior: "smooth" });
  } else {
    textarea.scrollTop = alvo;
  }
}

export function obterOffsetCaracteresInicioLinhaMarkdownTranscribrothers(
  markdown: string,
  numeroLinha: number,
): number {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  if (numeroLinha < 1) return 0;
  let offset = 0;
  for (let indice = 0; indice < numeroLinha - 1 && indice < linhas.length; indice += 1) {
    offset += linhas[indice].length + 1;
  }
  return offset;
}

/** Posiciona o cursor no início da linha indicada. */
export function posicionarCursorTextareaNaLinhaMarkdownTranscribrothers(
  textarea: HTMLTextAreaElement,
  markdown: string,
  numeroLinha: number,
): void {
  const fonte =
    textarea.value.length > 0 || markdown.length === 0 ? textarea.value : markdown;
  const offset = obterOffsetCaracteresInicioLinhaMarkdownTranscribrothers(
    fonte,
    numeroLinha,
  );
  textarea.focus();
  textarea.setSelectionRange(offset, offset);
}

const ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN =
  "data-tb-espelho-medicao-cursor-textarea-markdown";

function obterOuCriarEspelhoCursorTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
): HTMLDivElement {
  const existente = envoltorio.querySelector<HTMLDivElement>(
    `[${ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN}]`,
  );
  if (existente) return existente;

  const espelho = document.createElement("div");
  espelho.setAttribute(ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN, "true");
  espelho.setAttribute("aria-hidden", "true");
  espelho.className = "tb-modal-md-edit-espelho-cursor-textarea";
  envoltorio.appendChild(espelho);
  return espelho;
}

function sincronizarEstilosEspelhoComTextareaMarkdownTranscribrothers(
  espelho: HTMLDivElement,
  textarea: HTMLTextAreaElement,
  envoltorio: HTMLElement,
): void {
  const estilo = window.getComputedStyle(textarea);
  const estiloEspelho = espelho.style;

  estiloEspelho.font = estilo.font;
  estiloEspelho.letterSpacing = estilo.letterSpacing;
  estiloEspelho.tabSize = estilo.tabSize;
  estiloEspelho.padding = estilo.padding;
  estiloEspelho.border = estilo.border;
  estiloEspelho.boxSizing = estilo.boxSizing;
  estiloEspelho.lineHeight = estilo.lineHeight;
  estiloEspelho.textIndent = estilo.textIndent;
  estiloEspelho.textTransform = estilo.textTransform;
  estiloEspelho.wordSpacing = estilo.wordSpacing;

  estiloEspelho.whiteSpace = "pre-wrap";
  estiloEspelho.wordWrap = "break-word";
  estiloEspelho.overflow = "hidden";
  estiloEspelho.visibility = "hidden";
  estiloEspelho.pointerEvents = "none";
  estiloEspelho.position = "absolute";
  estiloEspelho.zIndex = "1";

  const rectTextarea = textarea.getBoundingClientRect();
  const rectEnvoltorio = envoltorio.getBoundingClientRect();
  estiloEspelho.top = `${rectTextarea.top - rectEnvoltorio.top}px`;
  estiloEspelho.left = `${rectTextarea.left - rectEnvoltorio.left}px`;
  estiloEspelho.width = `${textarea.clientWidth}px`;
  estiloEspelho.height = `${textarea.clientHeight}px`;
}

export type RetanguloDestaqueLinhaTextareaMarkdownTranscribrothers = {
  topPx: number;
  heightPx: number;
  leftPx: number;
  widthPx: number;
};

type MedicaoLinhaEspelhoTextareaMarkdownTranscribrothers = {
  espelho: HTMLDivElement;
  spanLinha: HTMLSpanElement;
};

function prepararMedicaoLinhaEspelhoTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  markdown: string,
  numeroLinha: number,
): MedicaoLinhaEspelhoTextareaMarkdownTranscribrothers | null {
  if (!textarea.isConnected || !envoltorio.isConnected) return null;

  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  if (numeroLinha < 1 || numeroLinha > linhas.length) return null;

  const offsetInicio = obterOffsetCaracteresInicioLinhaMarkdownTranscribrothers(
    markdown,
    numeroLinha,
  );
  const textoLinha = linhas[numeroLinha - 1] ?? "";
  const offsetFim = offsetInicio + textoLinha.length;

  const espelho = obterOuCriarEspelhoCursorTextareaMarkdownTranscribrothers(envoltorio);
  sincronizarEstilosEspelhoComTextareaMarkdownTranscribrothers(espelho, textarea, envoltorio);
  espelho.scrollTop = textarea.scrollTop;

  const valorTextarea = textarea.value;
  const textoAteInicio = valorTextarea.slice(0, offsetInicio);
  const textoDestaque = valorTextarea.slice(offsetInicio, offsetFim) || "\u200b";

  espelho.replaceChildren();
  if (textoAteInicio) {
    espelho.append(document.createTextNode(textoAteInicio));
  }
  const spanLinha = document.createElement("span");
  spanLinha.setAttribute("data-tb-linha-destaque-textarea", "true");
  spanLinha.textContent = textoDestaque;
  espelho.append(spanLinha);

  return { espelho, spanLinha };
}

/** Reserva no fim do scroll para o caret não ficar colado no teto inferior (evita desalinhar espelho). */
export function obterMargemReservaScrollInferiorTextareaMarkdownTranscribrothers(
  textarea: HTMLTextAreaElement,
): number {
  return Math.max(48, Math.round(textarea.clientHeight * 0.42));
}

export function aplicarScrollTopTextareaMarkdownComMargemInferiorReservadaTranscribrothers(
  textarea: HTMLTextAreaElement,
  alvoScrollBruto: number,
): number {
  const maxScroll = Math.max(0, textarea.scrollHeight - textarea.clientHeight);
  const margem = obterMargemReservaScrollInferiorTextareaMarkdownTranscribrothers(textarea);
  const tetoScroll = Math.max(0, maxScroll - margem);
  const scrollTop = Math.min(tetoScroll, Math.max(0, alvoScrollBruto));
  textarea.scrollTop = scrollTop;
  return scrollTop;
}

function medirOffsetTopCaretNoConteudoEspelhoTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  offsetCaracteres: number,
): number | null {
  const valorTextarea = textarea.value;
  const offset = Math.max(0, Math.min(offsetCaracteres, valorTextarea.length));

  const espelho = obterOuCriarEspelhoCursorTextareaMarkdownTranscribrothers(envoltorio);
  sincronizarEstilosEspelhoComTextareaMarkdownTranscribrothers(espelho, textarea, envoltorio);
  espelho.scrollTop = 0;
  espelho.scrollLeft = 0;

  const textoAntes = valorTextarea.slice(0, offset);
  espelho.replaceChildren();
  if (textoAntes) {
    espelho.append(document.createTextNode(textoAntes));
  }
  espelho.append(montarNoMarcadorCaretInlineNoEspelhoTextareaMarkdownTranscribrothers());
  const textoDepois = valorTextarea.slice(offset);
  if (textoDepois) {
    espelho.append(document.createTextNode(textoDepois));
  }

  const ancora = espelho.querySelector<HTMLElement>("[data-tb-caret-marcador-inline]");
  return ancora?.offsetTop ?? null;
}

/** Rola o textarea até o offset do caret (selectionStart), com margem antes do fim do scroll. */
export function rolarTextareaMarkdownParaOffsetCaretComMedicaoEspelhoTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  offsetCaracteres: number,
  fracaoVerticalNoViewport = 0.35,
): void {
  const offsetTopCaret = medirOffsetTopCaretNoConteudoEspelhoTextareaMarkdownTranscribrothers(
    envoltorio,
    textarea,
    offsetCaracteres,
  );
  if (offsetTopCaret == null) return;

  const alvoScroll =
    offsetTopCaret - fracaoVerticalNoViewport * textarea.clientHeight;
  const scrollTop = aplicarScrollTopTextareaMarkdownComMargemInferiorReservadaTranscribrothers(
    textarea,
    alvoScroll,
  );

  const espelho = envoltorio.querySelector<HTMLDivElement>(
    `[${ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN}]`,
  );
  if (espelho) {
    espelho.scrollTop = scrollTop;
    espelho.scrollLeft = textarea.scrollLeft;
  }
}

/**
 * Rola o textarea para a linha usando o mesmo espelho de medição do destaque visual
 * (quebra de linha real), em vez da heurística de altura de linha fixa.
 */
export function rolarTextareaMarkdownParaNumeroLinhaComMedicaoEspelhoTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  markdown: string,
  numeroLinha: number,
  fracaoVerticalNoViewport = 0.35,
): void {
  const fonte =
    textarea.value.length > 0 || markdown.length === 0 ? textarea.value : markdown;
  const offsetInicio = obterOffsetCaracteresInicioLinhaMarkdownTranscribrothers(
    fonte,
    numeroLinha,
  );
  rolarTextareaMarkdownParaOffsetCaretComMedicaoEspelhoTranscribrothers(
    envoltorio,
    textarea,
    offsetInicio,
    fracaoVerticalNoViewport,
  );
}

const CLASSE_ESPELHO_MARCADOR_CARET_VISIVEL_TRANSCRIBROTHERS =
  "tb-modal-md-edit-espelho-cursor-textarea--marcador-caret-visivel";

const CLASSE_ESPELHO_MARCADOR_CARET_PULSO_TRANSCRIBROTHERS =
  "tb-modal-md-edit-espelho-cursor-textarea--marcador-caret-pulso";

function obterAlturaLinhaPxTextareaMarkdownTranscribrothers(
  textarea: HTMLTextAreaElement,
): number {
  const estilo = window.getComputedStyle(textarea);
  const altura = Number.parseFloat(estilo.lineHeight);
  if (Number.isFinite(altura) && altura > 0) return altura;
  const fonte = Number.parseFloat(estilo.fontSize) || 14;
  return fonte * 1.45;
}

function montarNoMarcadorCaretInlineNoEspelhoTextareaMarkdownTranscribrothers(): HTMLSpanElement {
  const ancora = document.createElement("span");
  ancora.className = "tb-modal-md-edit-espelho-caret-marcador-inline";
  ancora.setAttribute("data-tb-caret-marcador-inline", "true");
  ancora.textContent = "\u200b";
  return ancora;
}

function montarNoDestaqueLinhaHorizontalCaretNoEspelhoTextareaMarkdownTranscribrothers(): HTMLSpanElement {
  const destaqueLinha = document.createElement("span");
  destaqueLinha.className =
    "tb-modal-md-edit-espelho-caret-marcador-inline__destaque-linha-horizontal";
  destaqueLinha.setAttribute("data-tb-destaque-linha-horizontal-caret", "true");
  destaqueLinha.setAttribute("aria-hidden", "true");
  return destaqueLinha;
}

/** Cola a faixa no caret via getBoundingClientRect (válido com qualquer scrollTop). */
function posicionarDestaqueLinhaHorizontalColadoNoCaretNoEspelhoTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
): void {
  const espelho = envoltorio.querySelector<HTMLDivElement>(
    `[${ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN}]`,
  );
  const ancora = espelho?.querySelector<HTMLElement>("[data-tb-caret-marcador-inline]");
  if (!ancora) return;

  let destaque = envoltorio.querySelector<HTMLElement>(
    "[data-tb-destaque-linha-horizontal-caret]",
  );
  if (!destaque) {
    destaque = montarNoDestaqueLinhaHorizontalCaretNoEspelhoTextareaMarkdownTranscribrothers();
    envoltorio.append(destaque);
  } else if (destaque.parentElement !== envoltorio) {
    envoltorio.append(destaque);
  }

  const alturaLinhaPx = obterAlturaLinhaPxTextareaMarkdownTranscribrothers(textarea);
  const ancoraRect = ancora.getBoundingClientRect();
  const envoltorioRect = envoltorio.getBoundingClientRect();

  destaque.style.top = `${ancoraRect.top - envoltorioRect.top}px`;
  destaque.style.left = `${ancoraRect.left - envoltorioRect.left}px`;
  destaque.style.height = `${alturaLinhaPx}px`;
}

/**
 * Desenha o marcador colado no caret: o espelho replica o textarea (texto transparente)
 * e o indicador fica inline na mesma posição que selectionStart.
 */
export function exibirMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  offsetCaracteres: number,
): boolean {
  if (!textarea.isConnected || !envoltorio.isConnected) return false;

  const valorTextarea = textarea.value;
  const offset = Math.max(0, Math.min(offsetCaracteres, valorTextarea.length));

  const espelho = obterOuCriarEspelhoCursorTextareaMarkdownTranscribrothers(envoltorio);
  sincronizarEstilosEspelhoComTextareaMarkdownTranscribrothers(espelho, textarea, envoltorio);
  espelho.scrollTop = textarea.scrollTop;
  espelho.scrollLeft = textarea.scrollLeft;

  const textoAntes = valorTextarea.slice(0, offset);
  espelho.replaceChildren();
  if (textoAntes) {
    espelho.append(document.createTextNode(textoAntes));
  }
  espelho.append(montarNoMarcadorCaretInlineNoEspelhoTextareaMarkdownTranscribrothers());
  const textoDepois = valorTextarea.slice(offset);
  if (textoDepois) {
    espelho.append(document.createTextNode(textoDepois));
  }

  const reposicionarColadoNoCaret = () => {
    espelho.scrollTop = textarea.scrollTop;
    espelho.scrollLeft = textarea.scrollLeft;
    posicionarDestaqueLinhaHorizontalColadoNoCaretNoEspelhoTextareaMarkdownTranscribrothers(
      envoltorio,
      textarea,
    );
  };
  reposicionarColadoNoCaret();
  window.requestAnimationFrame(reposicionarColadoNoCaret);

  espelho.classList.add(CLASSE_ESPELHO_MARCADOR_CARET_VISIVEL_TRANSCRIBROTHERS);
  espelho.classList.remove(CLASSE_ESPELHO_MARCADOR_CARET_PULSO_TRANSCRIBROTHERS);
  void espelho.offsetWidth;
  espelho.classList.add(CLASSE_ESPELHO_MARCADOR_CARET_PULSO_TRANSCRIBROTHERS);
  return true;
}

export function ocultarMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement | null = null,
): void {
  const espelho = envoltorio.querySelector<HTMLDivElement>(
    `[${ATRIBUTO_ESPELHO_CURSOR_TEXTAREA_MARKDOWN}]`,
  );
  if (!espelho) return;
  espelho.classList.remove(
    CLASSE_ESPELHO_MARCADOR_CARET_VISIVEL_TRANSCRIBROTHERS,
    CLASSE_ESPELHO_MARCADOR_CARET_PULSO_TRANSCRIBROTHERS,
  );
  espelho.replaceChildren();
  envoltorio
    .querySelector<HTMLElement>("[data-tb-destaque-linha-horizontal-caret]")
    ?.remove();
  const textareaEfetivo =
    textarea ?? envoltorio.querySelector<HTMLTextAreaElement>("textarea");
  if (textareaEfetivo) {
    sincronizarEstilosEspelhoComTextareaMarkdownTranscribrothers(
      espelho,
      textareaEfetivo,
      envoltorio,
    );
  }
}

/** Retângulo da linha no envoltório do editor (mesmo critério visual do bloco ativo no preview). */
export function obterRetanguloDestaqueLinhaTextareaMarkdownTranscribrothers(
  envoltorio: HTMLElement,
  textarea: HTMLTextAreaElement,
  markdown: string,
  numeroLinha: number,
): RetanguloDestaqueLinhaTextareaMarkdownTranscribrothers | null {
  const medicao = prepararMedicaoLinhaEspelhoTextareaMarkdownTranscribrothers(
    envoltorio,
    textarea,
    markdown,
    numeroLinha,
  );
  if (!medicao) return null;

  const { espelho, spanLinha } = medicao;
  const topoVisivel = spanLinha.offsetTop - espelho.scrollTop;
  const altura = Math.max(spanLinha.offsetHeight, 1);

  return {
    topPx: textarea.offsetTop + topoVisivel,
    heightPx: altura,
    leftPx: textarea.offsetLeft,
    widthPx: textarea.clientWidth,
  };
}
