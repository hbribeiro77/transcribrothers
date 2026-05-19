import type { SecaoHeadingNivel2MarkdownTutorialTranscribrothers } from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";
import { listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers } from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";
import {
  obterNumeroLinhaFimBlocoMarkdownAPartirLinhaInicioTranscribrothers,
} from "./modulo_util_bloco_ancora_linha_markdown_sincronizacao_preview_editor_transcribrothers.ts";
import {
  extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers,
  normalizarTextoComparacaoPreviewMarkdownTranscribrothers,
} from "./modulo_util_localizar_trecho_texto_linha_markdown_no_preview_sincronizacao_editor_transcribrothers.ts";

export type InsercaoMarkdownImagemAssetPendenteTranscribrothers = {
  snippetMarkdown: string;
  nomeArquivoOriginal: string;
};

export type PontoInsercaoImagemMarkdownPreviewTutorialTranscribrothers = {
  numeroLinhaInsercao: number;
  topoPxMarcador: number;
};

const SELETOR_BLOCO_DOM_PREVIEW_INSERIR_IMAGEM_MARKDOWN_TUTORIAL =
  "blockquote,.tb-imagem-tutorial-clicavel-envoltorio,h1,h2,h3,h4,h5,h6,pre,hr";

const MARGEM_PX_MARCADOR_ACIMA_BLOCO_VISUAL = 16;

type BlocoVisualPreviewOrdenadoTranscribrothers = {
  elemento: HTMLElement;
  topoViewport: number;
  baseViewport: number;
};

export function montarSnippetMarkdownImagemAssetTutorialTranscribrothers(
  nomeArquivoOriginal: string,
  altOpcional?: string,
): string {
  const alt = (altOpcional ?? nomeArquivoOriginal.replace(/\.png$/i, "")).replace(/[\[\]]/g, "");
  return `![${alt}](assets/${nomeArquivoOriginal})`;
}

/** Insere o snippet na linha indicada (1-based), com linhas em branco quando necessário. */
export function inserirSnippetMarkdownNaLinhaDocumentoTranscribrothers(
  markdown: string,
  numeroLinhaInsercao: number,
  snippet: string,
): string {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const indice = Math.max(0, Math.min(linhas.length, numeroLinhaInsercao - 1));
  const bloco: string[] = [];
  if (indice > 0 && (linhas[indice - 1] ?? "").trim() !== "") {
    bloco.push("");
  }
  bloco.push(snippet);
  if (indice < linhas.length && (linhas[indice] ?? "").trim() !== "") {
    bloco.push("");
  }
  linhas.splice(indice, 0, ...bloco);
  return linhas.join("\n");
}

function obterNumeroLinhaInsercaoAposFimBlocoMarkdownTranscribrothers(
  markdown: string,
  linhaInicioBloco: number,
): number {
  const linhaFim = obterNumeroLinhaFimBlocoMarkdownAPartirLinhaInicioTranscribrothers(
    markdown,
    linhaInicioBloco,
  );
  const totalLinhas = markdown.replace(/\r\n/g, "\n").split("\n").length;
  return Math.min(totalLinhas + 1, linhaFim + 1);
}

function obterNomesArquivoAssetBuscaMarkdownAPartirBlocoImagemTranscribrothers(
  bloco: HTMLElement,
): string[] {
  const doAtributo = bloco.getAttribute("data-tb-nome-arquivo-asset-original")?.trim();
  const nomes = new Set<string>();
  if (doAtributo) nomes.add(doAtributo);

  const img = bloco.querySelector("img[src]") as HTMLImageElement | null;
  const doSrc = img?.getAttribute("src")?.split("/").pop()?.split("?")[0]?.trim();
  if (doSrc) nomes.add(doSrc);

  if (doAtributo?.includes(".anotado.png")) {
    nomes.add(doAtributo.replace(/\.anotado\.png$/i, ".png"));
  }

  return [...nomes];
}

function obterNumeroLinhaInsercaoAposBlocoImagemMarkdownTranscribrothers(
  markdown: string,
  bloco: HTMLElement,
  containerPreview: HTMLElement,
): number | null {
  const nomes = obterNomesArquivoAssetBuscaMarkdownAPartirBlocoImagemTranscribrothers(bloco);
  const linhasComAsset = nomes
    .map((nome) => {
      const todas: number[] = [];
      const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
      for (let indice = 0; indice < linhas.length; indice += 1) {
        const linha = linhas[indice] ?? "";
        if (!/!\[[^\]]*\]\([^)]+\)/.test(linha)) continue;
        if (linha.includes(`assets/${nome}`) || linha.includes(nome)) {
          todas.push(indice + 1);
        }
      }
      return todas;
    })
    .flat();

  const linhasUnicas = [...new Set(linhasComAsset)].sort((a, b) => a - b);
  if (linhasUnicas.length === 0) return null;

  const imagensDom = Array.from(
    containerPreview.querySelectorAll<HTMLElement>(".tb-imagem-tutorial-clicavel-envoltorio"),
  );
  const indiceDom = imagensDom.indexOf(bloco);
  const linhaAlvo =
    indiceDom >= 0 && indiceDom < linhasUnicas.length
      ? linhasUnicas[indiceDom]
      : linhasUnicas[linhasUnicas.length - 1];

  return obterNumeroLinhaInsercaoAposFimBlocoMarkdownTranscribrothers(markdown, linhaAlvo);
}

function obterNumeroLinhaInsercaoAposBlocoCitacaoMarkdownPorChaveTextoTranscribrothers(
  markdown: string,
  chaveVisivel: string,
): number | null {
  const alvo = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(chaveVisivel);
  if (alvo.length < 4) return null;

  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  for (let indice = 0; indice < linhas.length; indice += 1) {
    const trim = (linhas[indice] ?? "").trim();
    if (!/^>\s?/.test(trim)) continue;

    const textoLinha = extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers(trim);
    if (!textoLinha) continue;

    const normLinha = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(textoLinha);
    if (!normLinha.includes(alvo) && !alvo.includes(normLinha)) continue;

    let fimIndice = indice;
    while (fimIndice + 1 < linhas.length && /^>\s?/.test((linhas[fimIndice + 1] ?? "").trim())) {
      fimIndice += 1;
    }
    return obterNumeroLinhaInsercaoAposFimBlocoMarkdownTranscribrothers(markdown, indice + 1);
  }

  return null;
}

function extrairChaveTextoBuscaMarkdownDoBlocoDomPreviewTranscribrothers(
  bloco: HTMLElement,
): string {
  const texto = (bloco.innerText ?? "").replace(/\s+/g, " ").trim();
  const negrito = texto.match(/\*\*([^*]{4,120})\*\*/);
  if (negrito?.[1]) return negrito[1].trim();
  return texto.slice(0, 120);
}

function obterNumeroLinhaInsercaoAposBlocoDomNoMarkdownTranscribrothers(
  bloco: HTMLElement,
  markdown: string,
  secoesH2: SecaoHeadingNivel2MarkdownTutorialTranscribrothers[],
  containerPreview: HTMLElement,
): number | null {
  if (bloco.matches("blockquote")) {
    const chave = extrairChaveTextoBuscaMarkdownDoBlocoDomPreviewTranscribrothers(bloco);
    return obterNumeroLinhaInsercaoAposBlocoCitacaoMarkdownPorChaveTextoTranscribrothers(
      markdown,
      chave,
    );
  }

  if (bloco.matches(".tb-imagem-tutorial-clicavel-envoltorio")) {
    return obterNumeroLinhaInsercaoAposBlocoImagemMarkdownTranscribrothers(
      markdown,
      bloco,
      containerPreview,
    );
  }

  if (bloco instanceof HTMLHeadingElement && bloco.tagName === "H2" && bloco.id) {
    const secao = secoesH2.find((s) => s.slugIdAncoraPreview === bloco.id);
    if (secao) {
      return obterNumeroLinhaInsercaoAposFimBlocoMarkdownTranscribrothers(markdown, secao.numeroLinha);
    }
  }

  const chave = extrairChaveTextoBuscaMarkdownDoBlocoDomPreviewTranscribrothers(bloco);
  if (chave.length >= 4) {
    const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
    const alvo = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(chave);
    for (let indice = 0; indice < linhas.length; indice += 1) {
      const texto = extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers(
        (linhas[indice] ?? "").trim(),
      );
      if (!texto) continue;
      const norm = normalizarTextoComparacaoPreviewMarkdownTranscribrothers(texto);
      if (norm.includes(alvo) || alvo.includes(norm)) {
        return obterNumeroLinhaInsercaoAposFimBlocoMarkdownTranscribrothers(markdown, indice + 1);
      }
    }
  }

  return null;
}

function listarBlocosVisuaisUnicosPreviewInsercaoImagemTranscribrothers(
  containerPreview: HTMLElement,
): HTMLElement[] {
  const vistos = new Set<HTMLElement>();
  const resultado: HTMLElement[] = [];

  for (const elemento of containerPreview.querySelectorAll(SELETOR_BLOCO_DOM_PREVIEW_INSERIR_IMAGEM_MARKDOWN_TUTORIAL)) {
    if (!(elemento instanceof HTMLElement)) continue;
    if (vistos.has(elemento)) continue;
    vistos.add(elemento);
    resultado.push(elemento);
  }

  return resultado;
}

function obterRectanguloVisualConteudoBlocoPreviewParaMarcadorInsercaoImagemTranscribrothers(
  bloco: HTMLElement,
): { topoViewport: number; baseViewport: number } {
  if (bloco.matches(".tb-imagem-tutorial-clicavel-envoltorio")) {
    const img = bloco.querySelector("img");
    if (img) {
      const rect = img.getBoundingClientRect();
      return { topoViewport: rect.top, baseViewport: rect.bottom };
    }
  }
  const rect = bloco.getBoundingClientRect();
  return { topoViewport: rect.top, baseViewport: rect.bottom };
}

function listarBlocosVisuaisOrdenadosPorTopoNoPreviewTranscribrothers(
  containerPreview: HTMLElement,
): BlocoVisualPreviewOrdenadoTranscribrothers[] {
  return listarBlocosVisuaisUnicosPreviewInsercaoImagemTranscribrothers(containerPreview)
    .map((elemento) => {
      const rect = obterRectanguloVisualConteudoBlocoPreviewParaMarcadorInsercaoImagemTranscribrothers(
        elemento,
      );
      return {
        elemento,
        topoViewport: rect.topoViewport,
        baseViewport: rect.baseViewport,
      };
    })
    .sort((a, b) => a.topoViewport - b.topoViewport);
}

/**
 * Último bloco cujo conteúdo visual termina em ou acima da linha tracejada → inserir depois dele.
 */
function obterBlocoDomParaInserirAposPorMarcadorYNoPreviewTranscribrothers(
  marcadorYNoViewport: number,
  blocosOrdenados: BlocoVisualPreviewOrdenadoTranscribrothers[],
): HTMLElement | null {
  if (blocosOrdenados.length === 0) return null;

  const margem = MARGEM_PX_MARCADOR_ACIMA_BLOCO_VISUAL;
  let indiceMelhor = -1;
  let maiorBase = Number.NEGATIVE_INFINITY;

  for (let indice = 0; indice < blocosOrdenados.length; indice += 1) {
    const bloco = blocosOrdenados[indice];
    if (bloco.baseViewport <= marcadorYNoViewport + margem && bloco.baseViewport > maiorBase) {
      maiorBase = bloco.baseViewport;
      indiceMelhor = indice;
    }
  }

  return indiceMelhor >= 0 ? blocosOrdenados[indiceMelhor].elemento : null;
}

export function obterNumeroLinhaInsercaoPorTopoMarcadorNoPreviewTutorialTranscribrothers(
  containerPreview: HTMLElement,
  topoPxMarcadorRelativoContainer: number,
  markdown: string,
  secoesH2: SecaoHeadingNivel2MarkdownTutorialTranscribrothers[],
): number {
  const rectContainer = containerPreview.getBoundingClientRect();
  const marcadorYNoViewport =
    rectContainer.top + topoPxMarcadorRelativoContainer - containerPreview.scrollTop;

  const blocosOrdenados = listarBlocosVisuaisOrdenadosPorTopoNoPreviewTranscribrothers(containerPreview);
  const blocoInserirApos = obterBlocoDomParaInserirAposPorMarcadorYNoPreviewTranscribrothers(
    marcadorYNoViewport,
    blocosOrdenados,
  );

  if (blocoInserirApos) {
    const linha = obterNumeroLinhaInsercaoAposBlocoDomNoMarkdownTranscribrothers(
      blocoInserirApos,
      markdown,
      secoesH2,
      containerPreview,
    );
    if (linha != null) return linha;
  }

  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const proporcao =
    containerPreview.scrollHeight > 0
      ? topoPxMarcadorRelativoContainer / containerPreview.scrollHeight
      : 0;
  return Math.max(
    1,
    Math.min(linhas.length + 1, Math.round(proporcao * Math.max(linhas.length, 1)) + 1),
  );
}

function obterBlocoDomPreviewSobPonteiroInsercaoImagemTranscribrothers(
  alvo: HTMLElement,
  containerPreview: HTMLElement,
): HTMLElement | null {
  const citacao = alvo.closest("blockquote") as HTMLElement | null;
  if (citacao && containerPreview.contains(citacao)) return citacao;

  const bloco = alvo.closest(
    "h1,h2,h3,h4,h5,h6,p,li,.tb-imagem-tutorial-clicavel-envoltorio,pre,hr",
  ) as HTMLElement | null;
  if (bloco && containerPreview.contains(bloco)) {
    return (bloco.closest("blockquote") as HTMLElement | null) ?? bloco;
  }

  return null;
}

export function obterPontoInsercaoImagemMarkdownSobPonteiroNoPreviewTutorialTranscribrothers(
  alvo: HTMLElement,
  containerPreview: HTMLElement,
  markdown: string,
  secoesH2: SecaoHeadingNivel2MarkdownTutorialTranscribrothers[],
  coordenadas: { clientX: number; clientY: number },
): PontoInsercaoImagemMarkdownPreviewTutorialTranscribrothers | null {
  const rectContainer = containerPreview.getBoundingClientRect();
  const topoPxMarcador =
    coordenadas.clientY - rectContainer.top + containerPreview.scrollTop;

  const numeroLinhaInsercao = obterNumeroLinhaInsercaoPorTopoMarcadorNoPreviewTutorialTranscribrothers(
    containerPreview,
    topoPxMarcador,
    markdown,
    secoesH2,
  );

  return { numeroLinhaInsercao, topoPxMarcador };
}

export function listarSecoesH2MarkdownTutorialParaPreviewTranscribrothers(
  markdown: string,
): SecaoHeadingNivel2MarkdownTutorialTranscribrothers[] {
  return listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(markdown);
}

export function alvoPreviewIgnoraCliqueInsercaoImagemMarkdownTranscribrothers(
  alvo: EventTarget | null,
): boolean {
  if (!(alvo instanceof HTMLElement)) return true;
  return Boolean(
    alvo.closest("a[href]") ||
      alvo.closest("button") ||
      alvo.closest(".tb-imagem-tutorial-clicavel-anotacao") ||
      alvo.closest(".tb-imagem-tutorial-clicavel-btn-excluir") ||
      alvo.closest(".tb-tslink"),
  );
}
