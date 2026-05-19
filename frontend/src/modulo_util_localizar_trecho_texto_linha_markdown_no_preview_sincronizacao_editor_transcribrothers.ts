import type { SecaoHeadingNivel2MarkdownTutorialTranscribrothers } from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";

/** Texto legível da linha Markdown para buscar no preview renderizado. */
export function extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers(
  linhaBruta: string,
): string | null {
  const trim = linhaBruta.trim();
  if (!trim) return null;
  if (/^```/.test(trim)) return null;
  if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(trim)) return null;

  const heading = trim.match(/^#{1,6}\s+(.+)$/);
  if (heading) return limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(heading[1]);

  const citacao = trim.match(/^>\s?(.*)$/);
  if (citacao) return limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(citacao[1]);

  const itemLista = trim.match(/^(?:[-*+]|\d+\.)\s+(.+)$/);
  if (itemLista) {
    return limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(itemLista[1]);
  }

  const imagem = trim.match(/^!\[([^\]]*)\]/);
  if (imagem) {
    const alt = imagem[1]?.trim();
    return alt || null;
  }

  if (/^\|/.test(trim)) {
    const celulas = trim
      .split("|")
      .map((c) => c.trim())
      .filter((c) => c && !/^[-:]+$/.test(c));
    if (celulas.length > 0) {
      return limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(celulas[0]);
    }
    return null;
  }

  return limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(trim);
}

function limparMarcacaoInlineMarkdownParaBuscaPreviewTranscribrothers(texto: string): string {
  return texto
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/__([^_]+)__/g, "$1")
    .replace(/_([^_]+)_/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function normalizarTextoComparacaoPreviewMarkdownTranscribrothers(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

const SELETOR_ELEMENTOS_BUSCA_TEXTO_PREVIEW_MARKDOWN =
  "h1,h2,h3,h4,h5,h6,p,li,blockquote,td,th,pre,code,figcaption,.tb-modal-md-edit-bloco-wrap";

export type ResultadoLocalizacaoTextoLinhaPreviewMarkdownTranscribrothers = {
  elemento: HTMLElement;
  /** Topo do trecho (ou do bloco) em px, relativo ao envoltório do preview. */
  topoPxRelativoEnvoltorio: number;
};

export function obterTopoPxMarcadorRelativoEnvoltorioParaTrechoTextoNoElementoTranscribrothers(
  envoltorio: HTMLElement,
  elemento: HTMLElement,
  textoBusca: string,
): number | null {
  const busca = textoBusca.trim();
  if (!busca) return null;

  const buscaLower = busca.toLowerCase();
  const envRect = envoltorio.getBoundingClientRect();
  const walker = document.createTreeWalker(elemento, NodeFilter.SHOW_TEXT);
  let node: Text | null;

  while ((node = walker.nextNode() as Text | null)) {
    const content = node.textContent ?? "";
    const idx = content.toLowerCase().indexOf(buscaLower);
    if (idx < 0) continue;

    const range = document.createRange();
    range.setStart(node, idx);
    range.setEnd(node, Math.min(content.length, idx + busca.length));
    const rect = range.getBoundingClientRect();
    if (rect.height === 0 && rect.width === 0) continue;

    return rect.top - envRect.top;
  }

  return elemento.getBoundingClientRect().top - envRect.top;
}

export function localizarTrechoPreviewMarkdownPorTextoLinhaTranscribrothers(
  containerPreview: HTMLElement,
  envoltorioScroll: HTMLElement,
  textoBusca: string,
  opcoes?: {
    numeroLinhaReferencia?: number;
    totalLinhasDocumento?: number;
  },
): ResultadoLocalizacaoTextoLinhaPreviewMarkdownTranscribrothers | null {
  const busca = textoBusca.trim();
  if (busca.length < 2) return null;

  const alvo = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(busca);
  const candidatos: HTMLElement[] = [];

  containerPreview.querySelectorAll(SELETOR_ELEMENTOS_BUSCA_TEXTO_PREVIEW_MARKDOWN).forEach((no) => {
    if (!(no instanceof HTMLElement)) return;
    const textoElemento = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(
      no.innerText ?? "",
    );
    if (!textoElemento) return;
    if (textoElemento === alvo || textoElemento.includes(alvo)) {
      candidatos.push(no);
    }
  });

  if (candidatos.length === 0) {
    const topoTrecho = localizarTopoTrechoTextoEmQualquerNoPreviewTranscribrothers(
      containerPreview,
      envoltorioScroll,
      busca,
    );
    if (topoTrecho == null) return null;

    return {
      elemento: topoTrecho.elemento,
      topoPxRelativoEnvoltorio: topoTrecho.topoPx,
    };
  }

  const exatos = candidatos.filter(
    (el) =>
      normalizarTextoComparacaoPreviewMarkdownTranscribrothers(el.innerText ?? "") === alvo,
  );

  let pool = exatos.length > 0 ? exatos : candidatos;

  const headingsNoPool = pool.filter((el) => /^H[1-6]$/i.test(el.tagName));
  if (headingsNoPool.length > 0) {
    const headingPreferido =
      headingsNoPool.find((el) => {
        const textoHeading = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(
          el.innerText ?? "",
        );
        return textoHeading === alvo;
      }) ?? headingsNoPool[0];
    pool = [headingPreferido];
  }

  const totalLinhas = opcoes?.totalLinhasDocumento ?? 1;
  const numeroLinha = opcoes?.numeroLinhaReferencia ?? 1;
  const proporcaoDocumento =
    totalLinhas <= 1 ? 0 : (numeroLinha - 1) / (totalLinhas - 1);
  const alvoScrollAproximado = proporcaoDocumento * containerPreview.scrollHeight;

  const elementoEscolhido = pool
    .map((el) => ({
      el,
      distanciaScroll: Math.abs(
        el.offsetTop - alvoScrollAproximado,
      ),
      tamanhoTexto: (el.innerText ?? "").length,
    }))
    .sort((a, b) => {
      if (a.distanciaScroll !== b.distanciaScroll) {
        return a.distanciaScroll - b.distanciaScroll;
      }
      return a.tamanhoTexto - b.tamanhoTexto;
    })[0]?.el;

  if (!elementoEscolhido) return null;

  const topoPx =
    obterTopoPxMarcadorRelativoEnvoltorioParaTrechoTextoNoElementoTranscribrothers(
      envoltorioScroll,
      elementoEscolhido,
      busca,
    ) ??
    elementoEscolhido.getBoundingClientRect().top -
      envoltorioScroll.getBoundingClientRect().top;

  return {
    elemento: elementoEscolhido,
    topoPxRelativoEnvoltorio: topoPx,
  };
}

function localizarTopoTrechoTextoEmQualquerNoPreviewTranscribrothers(
  containerPreview: HTMLElement,
  envoltorioScroll: HTMLElement,
  textoBusca: string,
): { elemento: HTMLElement; topoPx: number } | null {
  const buscaLower = textoBusca.toLowerCase();
  const envRect = envoltorioScroll.getBoundingClientRect();
  const walker = document.createTreeWalker(containerPreview, NodeFilter.SHOW_TEXT);
  let node: Text | null;
  let melhor: { elemento: HTMLElement; topoPx: number; offsetTop: number } | null = null;

  while ((node = walker.nextNode() as Text | null)) {
    const content = node.textContent ?? "";
    const idx = content.toLowerCase().indexOf(buscaLower);
    if (idx < 0) continue;

    const pai =
      node.parentElement?.closest<HTMLElement>(
        "h1,h2,h3,h4,h5,h6,p,li,blockquote,td,th,pre,figcaption,.tb-modal-md-edit-bloco-wrap",
      ) ?? node.parentElement;

    if (!pai) continue;

    const range = document.createRange();
    range.setStart(node, idx);
    range.setEnd(node, Math.min(content.length, idx + textoBusca.length));
    const rect = range.getBoundingClientRect();
    const topoPx = rect.top - envRect.top;
    const offsetTop = pai.offsetTop;

    if (
      !melhor ||
      offsetTop < melhor.offsetTop ||
      (offsetTop === melhor.offsetTop && topoPx < melhor.topoPx)
    ) {
      melhor = { elemento: pai, topoPx, offsetTop };
    }
  }

  return melhor;
}

export function obterTrechoTextoNoPontoCliquePreviewMarkdownTranscribrothers(
  clientX: number,
  clientY: number,
): string | null {
  const doc = document;
  let no: Node | null = null;
  let offset = 0;

  if (typeof doc.caretRangeFromPoint === "function") {
    const range = doc.caretRangeFromPoint(clientX, clientY);
    if (range) {
      no = range.startContainer;
      offset = range.startOffset;
    }
  } else {
    const pos = (
      doc as Document & {
        caretPositionFromPoint?: (
          x: number,
          y: number,
        ) => { offsetNode: Node; offset: number } | null;
      }
    ).caretPositionFromPoint?.(clientX, clientY);
    if (pos) {
      no = pos.offsetNode;
      offset = pos.offset;
    }
  }

  if (!no) return null;

  if (no.nodeType === Node.TEXT_NODE) {
    const texto = no.textContent ?? "";
    const inicio = Math.max(0, offset - 48);
    const fim = Math.min(texto.length, offset + 48);
    const trecho = texto.slice(inicio, fim).trim();
    return trecho.length >= 3 ? trecho : null;
  }

  if (no instanceof HTMLElement) {
    const texto = (no.innerText ?? "").trim();
    return texto.length >= 3 ? texto.slice(0, 120) : null;
  }

  return null;
}

export function localizarNumeroLinhaMarkdownPorTrechoTextoPreviewTranscribrothers(
  markdown: string,
  trechoPreview: string,
): number | null {
  const alvo = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(trechoPreview);
  if (alvo.length < 3) return null;

  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  let melhor: { numeroLinha: number; pontuacao: number } | null = null;

  for (let indice = 0; indice < linhas.length; indice += 1) {
    const linhaBruta = linhas[indice];
    const textoLinha =
      extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers(linhaBruta) ??
      linhaBruta.trim();
    const normLinha = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(textoLinha);
    if (!normLinha) continue;

    if (normLinha === alvo) {
      return indice + 1;
    }

    if (normLinha.includes(alvo) || alvo.includes(normLinha)) {
      const pontuacao =
        Math.min(normLinha.length, alvo.length) / Math.max(normLinha.length, alvo.length, 1);
      if (!melhor || pontuacao > melhor.pontuacao) {
        melhor = { numeroLinha: indice + 1, pontuacao };
      }
    }
  }

  return melhor?.numeroLinha ?? null;
}

export function obterNumeroLinhaMarkdownAPartirCliquePreviewTranscribrothers(
  alvo: HTMLElement,
  containerPreview: HTMLElement,
  markdown: string,
  secoesH2: SecaoHeadingNivel2MarkdownTutorialTranscribrothers[],
  coordenadasClique?: { clientX: number; clientY: number },
): number | null {
  if (coordenadasClique) {
    const trechoNoPonto = obterTrechoTextoNoPontoCliquePreviewMarkdownTranscribrothers(
      coordenadasClique.clientX,
      coordenadasClique.clientY,
    );
    if (trechoNoPonto) {
      const linhaPorTrecho = localizarNumeroLinhaMarkdownPorTrechoTextoPreviewTranscribrothers(
        markdown,
        trechoNoPonto,
      );
      if (linhaPorTrecho != null) return linhaPorTrecho;
    }
  }

  const comAncora = alvo.closest("[data-tb-linha-inicio]") as HTMLElement | null;
  if (comAncora) {
    const numero = Number.parseInt(comAncora.getAttribute("data-tb-linha-inicio") ?? "", 10);
    if (numero > 0) return numero;
  }

  const comIdLinha = alvo.closest('[id^="tb-md-linha-"]') as HTMLElement | null;
  if (comIdLinha?.id) {
    const correspondencia = comIdLinha.id.match(/^tb-md-linha-(\d+)$/);
    if (correspondencia) {
      return Number.parseInt(correspondencia[1], 10);
    }
  }

  const headingSecao = alvo.closest("h2[id]") as HTMLElement | null;
  if (headingSecao?.id) {
    const secao = secoesH2.find((s) => s.slugIdAncoraPreview === headingSecao.id);
    if (secao) return secao.numeroLinha;
  }

  const bloco = alvo.closest(SELETOR_ELEMENTOS_BUSCA_TEXTO_PREVIEW_MARKDOWN) as HTMLElement | null;
  if (bloco) {
    const primeiraLinha = (bloco.innerText ?? "").trim().split(/\n/)[0]?.trim() ?? "";
    if (primeiraLinha) {
      const linha = localizarNumeroLinhaMarkdownPorTrechoTextoPreviewTranscribrothers(
        markdown,
        primeiraLinha.slice(0, 160),
      );
      if (linha != null) return linha;
    }
  }

  if (alvo instanceof HTMLImageElement && alvo.alt) {
    const linhaImagem = localizarNumeroLinhaMarkdownPorTrechoTextoPreviewTranscribrothers(
      markdown,
      alvo.alt,
    );
    if (linhaImagem != null) return linhaImagem;
  }

  const proporcao =
    containerPreview.scrollHeight > 0
      ? (alvo.getBoundingClientRect().top -
          containerPreview.getBoundingClientRect().top +
          containerPreview.scrollTop) /
        containerPreview.scrollHeight
      : 0;

  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const linhaAproximada = Math.max(
    1,
    Math.min(linhas.length, Math.round(proporcao * Math.max(linhas.length - 1, 0)) + 1),
  );
  return linhaAproximada;
}

export function obterElementoBlocoPreviewParaLinhaMarkdownTranscribrothers(
  containerPreview: HTMLElement,
  numeroLinha: number,
): HTMLElement | null {
  return (
    containerPreview.querySelector<HTMLElement>(`#tb-md-linha-${numeroLinha}`) ??
    containerPreview.querySelector<HTMLElement>(
      `[data-tb-linha-inicio="${numeroLinha}"]`,
    )
  );
}
