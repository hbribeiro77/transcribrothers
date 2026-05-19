import type { jsPDF } from "jspdf";
import { marked } from "marked";
import { gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers } from "./modulo_util_gerar_markdown_tutorial_com_imagens_png_embutidas_data_uri_base64_download_transcribrothers.ts";

const MARGEM_PDF_MM = 14;
const LARGURA_CONTEUDO_MM = 180;
const ESCALA_HTML2CANVAS = 2;
const LARGURA_CAPTURA_PX = Math.round(LARGURA_CONTEUDO_MM * 3.779527559);
const ALTURA_UTIL_PAGINA_PX = Math.floor((297 - MARGEM_PDF_MM * 2) * 3.779527559);
/** ~48% da área útil: cabe título + texto + um screenshot na mesma folha. */
const ALTURA_MAX_IMAGEM_RENDERIZADA_PX = Math.floor(ALTURA_UTIL_PAGINA_PX * 0.48);
const ALTURA_MAX_IMAGEM_RENDERIZADA_MM = (297 - MARGEM_PDF_MM * 2 - 6) * 0.48;
const LARGURA_UTIL_CONTEUDO_PX = LARGURA_CAPTURA_PX - 16;

const ESTILOS_INLINE_EXPORTACAO_PDF_TUTORIAL_TRANSCRIBROTHERS = `
.tb-pdf-export-capture-host {
  box-sizing: border-box;
  width: ${LARGURA_CAPTURA_PX}px;
  max-width: ${LARGURA_CAPTURA_PX}px;
}
.tb-pdf-export-pagina {
  box-sizing: border-box;
  width: ${LARGURA_CAPTURA_PX}px;
  max-width: ${LARGURA_CAPTURA_PX}px;
  margin: 0;
  padding: 0 8px 8px;
  background: #ffffff;
}
.tb-pdf-export-pagina h1 { font-size: 17pt; margin: 0 0 0.6em; line-height: 1.25; color: #0f172a; }
.tb-pdf-export-pagina h2 { font-size: 13pt; margin: 1.1em 0 0.45em; line-height: 1.3; color: #0f172a; }
.tb-pdf-export-pagina h3 { font-size: 11.5pt; margin: 0.9em 0 0.35em; color: #0f172a; }
.tb-pdf-export-pagina p,
.tb-pdf-export-pagina li {
  margin: 0.35em 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 11pt;
  line-height: 1.55;
  color: #0f172a;
}
.tb-pdf-export-pagina ul,
.tb-pdf-export-pagina ol { margin: 0.4em 0 0.6em; padding-left: 1.35em; }
.tb-pdf-export-figura { display: block; margin: 10px 0 14px; }
.tb-pdf-export-lista-unica {
  margin: 0.35em 0 0.65em;
  padding-left: 1.35em;
}
.tb-pdf-export-lista-unica li { margin: 0; }
.tb-pdf-export-bloco-unificado { margin: 0.35em 0 0.65em; }
.tb-pdf-export-pagina img,
.tb-pdf-export-figura img {
  display: block;
  max-width: 100%;
  max-height: ${ALTURA_MAX_IMAGEM_RENDERIZADA_MM}mm;
  width: auto;
  height: auto;
  object-fit: contain;
  margin: 0;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.tb-pdf-export-pagina pre {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 9pt;
  white-space: pre-wrap;
  word-break: break-word;
}
.tb-pdf-export-pagina code {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 0.92em;
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
}
.tb-pdf-export-pagina pre code { background: transparent; padding: 0; }
.tb-pdf-export-pagina a { color: #1d4ed8; text-decoration: underline; }
.tb-pdf-export-ts { color: #1d4ed8; font-weight: 500; }
`;

function substituirLinksTimestampVideoPorTextoNoHtmlExportacaoPdfTranscribrothers(html: string): string {
  return html.replace(/<a href="\?t=[^"]*">([^<]*)<\/a>/gi, '<span class="tb-pdf-export-ts">$1</span>');
}

function envolverImagensIsoladasEmFigurasParaExportacaoPdfTranscribrothers(html: string): string {
  return html.replace(/<p>\s*(<img\b[^>]*>)\s*<\/p>/gi, '<figure class="tb-pdf-export-figura">$1</figure>');
}

async function markdownTutorialComImagensEmbutidasParaHtmlCorpoExportacaoPdfTranscribrothers(
  markdownComImagensDataUri: string,
): Promise<string> {
  const bruto = marked.parse(markdownComImagensDataUri, { async: false, gfm: true });
  const html = typeof bruto === "string" ? bruto : await bruto;
  return envolverImagensIsoladasEmFigurasParaExportacaoPdfTranscribrothers(
    substituirLinksTimestampVideoPorTextoNoHtmlExportacaoPdfTranscribrothers(html),
  );
}

async function aguardarDecodificacaoImagensDoElementoPdfTranscribrothers(root: HTMLElement): Promise<void> {
  const imgs = [...root.querySelectorAll("img")];
  if (imgs.length === 0) return;
  await Promise.all(
    imgs.map(async (img) => {
      if (img.complete && img.naturalWidth > 0) {
        try {
          await img.decode();
        } catch {
          /* ok */
        }
        return;
      }
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () =>
          reject(new Error(`Não foi possível decodificar uma imagem para o PDF (${img.alt || "screenshot"}).`));
      });
      try {
        await img.decode();
      } catch {
        /* ok */
      }
    }),
  );
}

async function aguardarLayoutEstavelTranscribrothers(): Promise<void> {
  await new Promise<void>((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
  });
}

function calcularAlturaRenderizadaImagemPdfTranscribrothers(img: HTMLImageElement): number {
  const naturalW = img.naturalWidth || img.width || 1;
  const naturalH = img.naturalHeight || img.height || 1;
  let largura = naturalW;
  let altura = naturalH;
  if (largura > LARGURA_UTIL_CONTEUDO_PX) {
    altura = (altura * LARGURA_UTIL_CONTEUDO_PX) / largura;
    largura = LARGURA_UTIL_CONTEUDO_PX;
  }
  if (altura > ALTURA_MAX_IMAGEM_RENDERIZADA_PX) {
    altura = ALTURA_MAX_IMAGEM_RENDERIZADA_PX;
  }
  const style = getComputedStyle(img);
  const mt = Number.parseFloat(style.marginTop) || 0;
  const mb = Number.parseFloat(style.marginBottom) || 0;
  const figura = img.closest(".tb-pdf-export-figura");
  if (figura instanceof HTMLElement) {
    const fs = getComputedStyle(figura);
    return Math.ceil(altura + mt + mb + (Number.parseFloat(fs.marginTop) || 0) + (Number.parseFloat(fs.marginBottom) || 0));
  }
  return Math.ceil(altura + mt + mb);
}

function medirAlturaBlocoComMargensTranscribrothers(el: HTMLElement): number {
  if (el.tagName === "IMG") {
    return calcularAlturaRenderizadaImagemPdfTranscribrothers(el as HTMLImageElement);
  }

  const figura = el.classList.contains("tb-pdf-export-figura")
    ? el
    : el.querySelector(".tb-pdf-export-figura");
  if (figura instanceof HTMLElement) {
    const img = figura.querySelector("img");
    if (img instanceof HTMLImageElement) {
      return calcularAlturaRenderizadaImagemPdfTranscribrothers(img);
    }
  }

  const imgsNoBloco = [...el.querySelectorAll("img")];
  if (imgsNoBloco.length > 0) {
    const alturaImgs = imgsNoBloco.reduce(
      (acc, img) =>
        acc + (img instanceof HTMLImageElement ? calcularAlturaRenderizadaImagemPdfTranscribrothers(img) : 0),
      0,
    );
    const rectLi = el.getBoundingClientRect();
    const styleLi = getComputedStyle(el);
    const mtLi = Number.parseFloat(styleLi.marginTop) || 0;
    const mbLi = Number.parseFloat(styleLi.marginBottom) || 0;
    const textoExtra = Math.max(0, rectLi.height + mtLi + mbLi - alturaImgs);
    return Math.ceil(alturaImgs + textoExtra);
  }

  const rect = el.getBoundingClientRect();
  const style = getComputedStyle(el);
  const mt = Number.parseFloat(style.marginTop) || 0;
  const mb = Number.parseFloat(style.marginBottom) || 0;
  const h = rect.height + mt + mb;
  if (h > 1) return Math.ceil(h);

  const imgs = [...el.querySelectorAll("img")];
  if (imgs.length > 0) {
    return imgs.reduce(
      (acc, img) =>
        acc + (img instanceof HTMLImageElement ? calcularAlturaRenderizadaImagemPdfTranscribrothers(img) : 48),
      0,
    );
  }

  return Math.max(Math.ceil(h), 1);
}

type BlocoHtmlMedidoParaPaginaPdfTranscribrothers = {
  outerHtml: string;
  alturaPx: number;
  contemImagem: boolean;
};

function blocoHtmlContemImagemTranscribrothers(outerHtml: string): boolean {
  return /<img\b/i.test(outerHtml);
}

function outerHtmlItemListaParaBlocoPaginaPdfTranscribrothers(
  li: HTMLLIElement,
  listaPai: HTMLOListElement | HTMLUListElement,
): string {
  const tag = listaPai.tagName.toLowerCase();
  if (tag === "ol") {
    const start = listaPai.getAttribute("start");
    const startAttr = start ? ` start="${start}"` : "";
    return `<ol class="tb-pdf-export-lista-unica"${startAttr}>${li.outerHTML}</ol>`;
  }
  return `<ul class="tb-pdf-export-lista-unica">${li.outerHTML}</ul>`;
}

/**
 * O marked agrupa passos em um único `<ol>`; paginar só os filhos de 1º nível
 * joga todas as imagens na “página 2”. Expandimos cada `<li>` em bloco próprio.
 */
function listarElementosHtmlParaBlocosPaginaPdfTranscribrothers(host: HTMLElement): HTMLElement[] {
  const saida: HTMLElement[] = [];
  for (const filho of [...host.children]) {
    if (!(filho instanceof HTMLElement)) continue;
    if (filho.tagName === "UL" || filho.tagName === "OL") {
      for (const item of [...filho.children]) {
        if (item instanceof HTMLLIElement) {
          const wrapper = document.createElement("di" + "v");
          wrapper.innerHTML = outerHtmlItemListaParaBlocoPaginaPdfTranscribrothers(item, filho);
          saida.push(wrapper);
        }
      }
    } else {
      saida.push(filho);
    }
  }
  return saida;
}

function medirElementoComoBlocoPaginaPdfTranscribrothers(el: HTMLElement): BlocoHtmlMedidoParaPaginaPdfTranscribrothers {
  const html =
    el.children.length === 1 &&
    (el.firstElementChild?.tagName === "OL" || el.firstElementChild?.tagName === "UL")
      ? el.innerHTML
      : el.outerHTML;
  return {
    outerHtml: html,
    alturaPx: medirAlturaBlocoComMargensTranscribrothers(el),
    contemImagem: blocoHtmlContemImagemTranscribrothers(html),
  };
}

function agruparBlocoTextoComFiguraImediataTranscribrothers(
  blocos: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[],
): BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] {
  const saida: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] = [];
  for (let i = 0; i < blocos.length; i += 1) {
    const atual = blocos[i];
    const proximo = blocos[i + 1];
    if (
      proximo &&
      !atual.contemImagem &&
      proximo.contemImagem &&
      !/^<h[1-6]\b/i.test(proximo.outerHtml.trim())
    ) {
      saida.push({
        outerHtml: `<div class="tb-pdf-export-bloco-unificado">${atual.outerHtml}${proximo.outerHtml}</div>`,
        alturaPx: atual.alturaPx + proximo.alturaPx,
        contemImagem: true,
      });
      i += 1;
      continue;
    }
    saida.push(atual);
  }
  return saida;
}

function empacotarBlocosMedidosEmPaginasPdfTranscribrothers(
  blocos: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[],
): BlocoHtmlMedidoParaPaginaPdfTranscribrothers[][] {
  const paginas: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[][] = [];
  let paginaAtual: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] = [];
  let alturaPaginaPx = 0;

  const fecharPagina = () => {
    if (paginaAtual.length > 0) {
      paginas.push(paginaAtual);
      paginaAtual = [];
      alturaPaginaPx = 0;
    }
  };

  for (const bloco of blocos) {
    const alturaEfetiva = Math.max(bloco.alturaPx, 1);

    if (alturaEfetiva > ALTURA_UTIL_PAGINA_PX && paginaAtual.length > 0) {
      fecharPagina();
    }

    if (paginaAtual.length > 0 && alturaPaginaPx + alturaEfetiva > ALTURA_UTIL_PAGINA_PX) {
      fecharPagina();
    }

    paginaAtual.push(bloco);
    alturaPaginaPx += alturaEfetiva;

    if (alturaPaginaPx >= ALTURA_UTIL_PAGINA_PX) {
      fecharPagina();
    }
  }

  fecharPagina();
  return paginas;
}

function medirBlocosHtmlParaPaginasPdfTranscribrothers(
  hostMedicao: HTMLElement,
): BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] {
  const elementos = listarElementosHtmlParaBlocosPaginaPdfTranscribrothers(hostMedicao);
  const medidos = elementos.map((el) => medirElementoComoBlocoPaginaPdfTranscribrothers(el));
  return agruparBlocoTextoComFiguraImediataTranscribrothers(medidos);
}

function criarDivPaginaCapturaPdfTranscribrothers(htmlInterno: string): HTMLDivElement {
  const pagina = document.createElement("div");
  pagina.className = "tb-pdf-export-pagina";
  pagina.innerHTML = htmlInterno;
  return pagina;
}

function montarDivsPaginaCapturaAPartirDosGruposTranscribrothers(
  grupos: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[][],
  captureHost: HTMLElement,
): HTMLDivElement[] {
  const paginas: HTMLDivElement[] = [];
  for (const grupo of grupos) {
    const pagina = criarDivPaginaCapturaPdfTranscribrothers(grupo.map((b) => b.outerHtml).join(""));
    captureHost.appendChild(pagina);
    paginas.push(pagina);
  }
  return paginas;
}

function coletarBlocosMedidosDosFilhosDasPaginasCapturaTranscribrothers(
  paginasAtuais: HTMLDivElement[],
): BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] {
  const blocos: BlocoHtmlMedidoParaPaginaPdfTranscribrothers[] = [];
  for (const pagina of paginasAtuais) {
    for (const filho of [...pagina.children]) {
      if (filho instanceof HTMLElement) {
        const html = filho.outerHTML;
        blocos.push({
          outerHtml: html,
          alturaPx: medirAlturaBlocoComMargensTranscribrothers(filho),
          contemImagem: blocoHtmlContemImagemTranscribrothers(html),
        });
      }
    }
  }
  return blocos;
}

function rebalancearPaginasCapturaQueEstouramAlturaUtilTranscribrothers(
  captureHost: HTMLElement,
  paginasAtuais: HTMLDivElement[],
): HTMLDivElement[] {
  const blocosRemedidos = coletarBlocosMedidosDosFilhosDasPaginasCapturaTranscribrothers(paginasAtuais);
  for (const pagina of paginasAtuais) {
    pagina.remove();
  }
  const grupos = empacotarBlocosMedidosEmPaginasPdfTranscribrothers(blocosRemedidos);
  return montarDivsPaginaCapturaAPartirDosGruposTranscribrothers(grupos, captureHost);
}

async function garantirPaginasCapturaDentroDaAlturaUtilPdfTranscribrothers(
  captureHost: HTMLElement,
  paginasIniciais: HTMLDivElement[],
): Promise<HTMLDivElement[]> {
  let paginas = paginasIniciais;
  for (let tentativa = 0; tentativa < 6; tentativa += 1) {
    await aguardarLayoutEstavelTranscribrothers();
    const estourou = paginas.some((p) => p.scrollHeight > ALTURA_UTIL_PAGINA_PX * 1.03);
    if (!estourou) {
      return paginas;
    }
    paginas = rebalancearPaginasCapturaQueEstouramAlturaUtilTranscribrothers(captureHost, paginas);
    await aguardarDecodificacaoImagensDoElementoPdfTranscribrothers(captureHost);
  }
  return paginas;
}

function canvasPareceVazioTranscribrothers(canvas: HTMLCanvasElement): boolean {
  if (canvas.width < 2 || canvas.height < 2) return true;
  const ctx = canvas.getContext("2d");
  if (!ctx) return true;
  const amostra = ctx.getImageData(0, 0, Math.min(canvas.width, 64), Math.min(canvas.height, 64));
  for (let i = 0; i < amostra.data.length; i += 4) {
    const a = amostra.data[i + 3];
    const r = amostra.data[i];
    const g = amostra.data[i + 1];
    const b = amostra.data[i + 2];
    if (a > 8 && (r < 248 || g < 248 || b < 248)) return false;
  }
  return true;
}

function adicionarCanvasComoPaginaUnicaPdfA4Transcribrothers(
  pdf: jsPDF,
  canvas: HTMLCanvasElement,
  margemMm: number,
  indicePaginaPdf: number,
): void {
  const larguraPaginaMm = pdf.internal.pageSize.getWidth();
  const alturaPaginaMm = pdf.internal.pageSize.getHeight();
  const larguraUtilMm = larguraPaginaMm - margemMm * 2;
  const alturaUtilMm = alturaPaginaMm - margemMm * 2;

  if (canvas.width < 2 || canvas.height < 2) return;

  const proporcao = canvas.width / canvas.height;
  let larguraImgMm = larguraUtilMm;
  let alturaImgMm = larguraUtilMm / proporcao;

  if (alturaImgMm > alturaUtilMm) {
    alturaImgMm = alturaUtilMm;
    larguraImgMm = alturaUtilMm * proporcao;
  }

  const imgData = canvas.toDataURL("image/jpeg", 0.92);
  if (indicePaginaPdf > 0) pdf.addPage("a4", "portrait");
  pdf.addImage(imgData, "JPEG", margemMm, margemMm, larguraImgMm, alturaImgMm);
}

async function capturarElementoComoCanvasParaPdfTranscribrothers(
  elemento: HTMLElement,
): Promise<HTMLCanvasElement> {
  const { default: html2canvas } = await import("html2canvas");
  const largura = LARGURA_CAPTURA_PX;
  const altura = Math.max(elemento.scrollHeight, elemento.offsetHeight, 1);

  const canvas = await html2canvas(elemento, {
    scale: ESCALA_HTML2CANVAS,
    backgroundColor: "#ffffff",
    useCORS: true,
    allowTaint: true,
    logging: false,
    width: largura,
    height: altura,
    windowWidth: largura,
    windowHeight: altura,
    scrollX: 0,
    scrollY: 0,
  });

  if (canvasPareceVazioTranscribrothers(canvas)) {
    throw new Error(
      "A captura do tutorial para PDF saiu vazia. Recarregue a página e tente de novo; se persistir, use o download em Markdown.",
    );
  }

  return canvas;
}

function montarUiECorpoMedicaoPdfTutorialTranscribrothers(htmlCorpo: string): {
  ui: HTMLDivElement;
  captureHost: HTMLDivElement;
  fonteMedicao: HTMLDivElement;
} {
  const ui = document.createElement("div");
  ui.className = "tb-pdf-export-overlay-shell";
  ui.setAttribute("role", "status");
  ui.setAttribute("aria-live", "polite");
  const aviso = document.createElement("p");
  aviso.className = "tb-pdf-export-overlay-msg";
  aviso.textContent = "Gerando PDF…";
  ui.appendChild(aviso);

  const style = document.createElement("style");
  style.textContent = ESTILOS_INLINE_EXPORTACAO_PDF_TUTORIAL_TRANSCRIBROTHERS;

  const captureHost = document.createElement("di" + "v");
  captureHost.className = "tb-pdf-export-capture-host";
  Object.assign(captureHost.style, {
    position: "fixed",
    left: "-120000px",
    top: "0",
    visibility: "visible",
    opacity: "1",
    pointerEvents: "none",
    zIndex: "-1",
  });

  const fonteMedicao = document.createElement("di" + "v");
  fonteMedicao.className = "tb-pdf-export-pagina";
  fonteMedicao.innerHTML = htmlCorpo;

  captureHost.append(style, fonteMedicao);
  document.body.append(ui, captureHost);

  return { ui, captureHost, fonteMedicao };
}

export async function baixarArquivoPdfTutorialMarkdownComImagensEmbutidasTranscribrothers(
  markdownOriginal: string,
  jobId: string,
  nomeArquivoSemExtensao?: string,
  resolverNomeArquivoAssetParaFetch?: (nomeArquivoNoMarkdown: string) => string,
): Promise<void> {
  const markdownComImagens =
    await gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers(
      markdownOriginal,
      jobId,
      resolverNomeArquivoAssetParaFetch,
    );
  const htmlCorpo = await markdownTutorialComImagensEmbutidasParaHtmlCorpoExportacaoPdfTranscribrothers(
    markdownComImagens,
  );
  if (!htmlCorpo.trim()) {
    throw new Error("O tutorial está vazio — não há conteúdo para gerar PDF.");
  }

  const { ui, captureHost, fonteMedicao } = montarUiECorpoMedicaoPdfTutorialTranscribrothers(htmlCorpo);

  try {
    await aguardarDecodificacaoImagensDoElementoPdfTranscribrothers(captureHost);
    await aguardarLayoutEstavelTranscribrothers();

    const blocosMedidos = medirBlocosHtmlParaPaginasPdfTranscribrothers(fonteMedicao);
    fonteMedicao.remove();
    if (blocosMedidos.length === 0) {
      throw new Error("O tutorial não gerou blocos HTML para o PDF.");
    }

    const grupos = empacotarBlocosMedidosEmPaginasPdfTranscribrothers(blocosMedidos);
    let paginasCaptura = montarDivsPaginaCapturaAPartirDosGruposTranscribrothers(grupos, captureHost);

    await aguardarDecodificacaoImagensDoElementoPdfTranscribrothers(captureHost);
    await aguardarLayoutEstavelTranscribrothers();

    paginasCaptura = await garantirPaginasCapturaDentroDaAlturaUtilPdfTranscribrothers(
      captureHost,
      paginasCaptura,
    );

    const { jsPDF } = await import("jspdf");
    const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

    let indicePaginaPdf = 0;
    for (const pagina of paginasCaptura) {
      const canvas = await capturarElementoComoCanvasParaPdfTranscribrothers(pagina);
      adicionarCanvasComoPaginaUnicaPdfA4Transcribrothers(pdf, canvas, MARGEM_PDF_MM, indicePaginaPdf);
      indicePaginaPdf += 1;
    }

    if (indicePaginaPdf === 0) {
      throw new Error("Nenhuma página foi gerada no PDF.");
    }

    const nomeArquivo =
      (nomeArquivoSemExtensao?.trim() || "").length > 0
        ? nomeArquivoSemExtensao!.trim()
        : `tutorial-transcribrothers-${jobId}`;
    pdf.save(`${nomeArquivo}.pdf`);
  } finally {
    ui.remove();
    captureHost.remove();
  }
}