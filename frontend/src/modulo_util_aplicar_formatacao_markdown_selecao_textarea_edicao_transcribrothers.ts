/** Ações da barra de formatação Markdown no editor do modal. */
export type TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers =
  | "negrito"
  | "italico"
  | "tachado"
  | "codigo-inline"
  | "link"
  | "lista-marcadores"
  | "lista-numerada"
  | "citacao"
  | "titulo-2"
  | "tabela";

export type ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers = {
  novoValor: string;
  selectionStart: number;
  selectionEnd: number;
};

const PLACEHOLDER_TEXTO_FORMATACAO_MARKDOWN = "texto";
const PLACEHOLDER_URL_LINK_MARKDOWN = "https://";
const MODELO_TABELA_MARKDOWN_PADRAO =
  "| Coluna 1 | Coluna 2 |\n| --- | --- |\n|  |  |";

function normalizarQuebrasLinhaMarkdown(valor: string): string {
  return valor.replace(/\r\n/g, "\n");
}

function obterExtensaoLinhasCompletasMarkdown(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
): { inicio: number; fim: number } {
  const inicio =
    selectionStart <= 0 ? 0 : valor.lastIndexOf("\n", selectionStart - 1) + 1;
  const indiceNovaLinha = valor.indexOf("\n", selectionEnd);
  const fim = indiceNovaLinha === -1 ? valor.length : indiceNovaLinha;
  return { inicio, fim };
}

function aplicarEnvolvimentoMarcadoresMarkdownTranscribrothers(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
  marcadorAntes: string,
  marcadorDepois: string,
  textoPlaceholder: string,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const selecionado = valor.slice(selectionStart, selectionEnd);
  const comprimentoMarcadores = marcadorAntes.length + marcadorDepois.length;

  if (
    selecionado.length >= comprimentoMarcadores &&
    selecionado.startsWith(marcadorAntes) &&
    selecionado.endsWith(marcadorDepois)
  ) {
    const nucleo = selecionado.slice(
      marcadorAntes.length,
      selecionado.length - marcadorDepois.length,
    );
    const novoValor =
      valor.slice(0, selectionStart) + nucleo + valor.slice(selectionEnd);
    const fim = selectionStart + nucleo.length;
    return {
      novoValor,
      selectionStart,
      selectionEnd: fim,
    };
  }

  const conteudoInserir =
    selecionado.length > 0 ? selecionado : textoPlaceholder;
  const envolvido = `${marcadorAntes}${conteudoInserir}${marcadorDepois}`;
  const novoValor =
    valor.slice(0, selectionStart) + envolvido + valor.slice(selectionEnd);
  const inicioConteudo = selectionStart + marcadorAntes.length;
  const fimConteudo = inicioConteudo + conteudoInserir.length;

  return {
    novoValor,
    selectionStart: inicioConteudo,
    selectionEnd: fimConteudo,
  };
}

function todasLinhasTemPrefixoMarkdown(
  linhas: string[],
  prefixo: string,
): boolean {
  if (linhas.length === 0) return false;
  return linhas.every((linha) => {
    const trimmed = linha.trimStart();
    return trimmed.length === 0 || trimmed.startsWith(prefixo);
  });
}

function removerPrefixoLinhaMarkdown(linha: string, prefixo: string): string {
  const trimmed = linha.trimStart();
  if (!trimmed.startsWith(prefixo)) return linha;
  const espacos = linha.length - trimmed.length;
  return `${linha.slice(0, espacos)}${trimmed.slice(prefixo.length)}`;
}

function aplicarPrefixoLinhasMarkdownTranscribrothers(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
  prefixo: string,
  regexRemoverAlternativo?: RegExp,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const { inicio, fim } = obterExtensaoLinhasCompletasMarkdown(
    valor,
    selectionStart,
    selectionEnd,
  );
  const bloco = valor.slice(inicio, fim);
  const linhas = bloco.split("\n");
  const remover =
    todasLinhasTemPrefixoMarkdown(linhas, prefixo) ||
    (regexRemoverAlternativo != null &&
      linhas.every((linha) => {
        const t = linha.trimStart();
        return t.length === 0 || regexRemoverAlternativo.test(t);
      }));

  const linhasNovas = linhas.map((linha) => {
    if (linha.trim().length === 0) return linha;
    if (remover) {
      if (regexRemoverAlternativo?.test(linha.trimStart())) {
        return linha.replace(/^\s*\d+\.\s+/, "");
      }
      return removerPrefixoLinhaMarkdown(linha, prefixo);
    }
    const espacos = linha.length - linha.trimStart().length;
    return `${linha.slice(0, espacos)}${prefixo}${linha.trimStart()}`;
  });

  const blocoNovo = linhasNovas.join("\n");
  const novoValor = valor.slice(0, inicio) + blocoNovo + valor.slice(fim);
  const delta = blocoNovo.length - bloco.length;

  return {
    novoValor,
    selectionStart: Math.min(selectionStart, inicio),
    selectionEnd: Math.max(selectionEnd, fim) + delta,
  };
}

function linhaTemPrefixoListaNumeradaMarkdown(linha: string): boolean {
  return /^\d+\.\s+/.test(linha.trimStart());
}

function aplicarListaNumeradaLinhasMarkdownTranscribrothers(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const { inicio, fim } = obterExtensaoLinhasCompletasMarkdown(
    valor,
    selectionStart,
    selectionEnd,
  );
  const bloco = valor.slice(inicio, fim);
  const linhas = bloco.split("\n");
  const remover = linhas.every((linha) => {
    const t = linha.trimStart();
    return t.length === 0 || linhaTemPrefixoListaNumeradaMarkdown(linha);
  });

  let indice = 1;
  const linhasNovas = linhas.map((linha) => {
    if (linha.trim().length === 0) return linha;
    const espacos = linha.length - linha.trimStart().length;
    const conteudo = linha.trimStart();
    if (remover) {
      return `${linha.slice(0, espacos)}${conteudo.replace(/^\d+\.\s+/, "")}`;
    }
    const numerada = `${indice}. ${conteudo}`;
    indice += 1;
    return `${linha.slice(0, espacos)}${numerada}`;
  });

  const blocoNovo = linhasNovas.join("\n");
  const novoValor = valor.slice(0, inicio) + blocoNovo + valor.slice(fim);
  const delta = blocoNovo.length - bloco.length;

  return {
    novoValor,
    selectionStart: Math.min(selectionStart, inicio),
    selectionEnd: Math.max(selectionEnd, fim) + delta,
  };
}

function aplicarTituloNivel2LinhasMarkdownTranscribrothers(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const prefixo = "## ";
  const { inicio, fim } = obterExtensaoLinhasCompletasMarkdown(
    valor,
    selectionStart,
    selectionEnd,
  );
  const bloco = valor.slice(inicio, fim);
  const linhas = bloco.split("\n");
  const remover = linhas.every((linha) => {
    const t = linha.trimStart();
    return t.length === 0 || /^#{1,6}\s+/.test(t);
  });

  const linhasNovas = linhas.map((linha) => {
    if (linha.trim().length === 0) return linha;
    const espacos = linha.length - linha.trimStart().length;
    const conteudo = linha.trimStart();
    if (remover) {
      return `${linha.slice(0, espacos)}${conteudo.replace(/^#{1,6}\s+/, "")}`;
    }
    const semHash = conteudo.replace(/^#{1,6}\s+/, "");
    return `${linha.slice(0, espacos)}${prefixo}${semHash}`;
  });

  const blocoNovo = linhasNovas.join("\n");
  const novoValor = valor.slice(0, inicio) + blocoNovo + valor.slice(fim);
  const delta = blocoNovo.length - bloco.length;

  return {
    novoValor,
    selectionStart: Math.min(selectionStart, inicio),
    selectionEnd: Math.max(selectionEnd, fim) + delta,
  };
}

function inserirTextoNoCursorMarkdownTranscribrothers(
  valor: string,
  selectionStart: number,
  selectionEnd: number,
  textoInserir: string,
  selecionarInserido = true,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const novoValor =
    valor.slice(0, selectionStart) + textoInserir + valor.slice(selectionEnd);
  const fim = selectionStart + textoInserir.length;
  return {
    novoValor,
    selectionStart: selecionarInserido ? selectionStart : fim,
    selectionEnd: fim,
  };
}

/** Aplica negrito, listas, tabela etc. na seleção (ou no cursor) do textarea. */
export function aplicarFormatacaoMarkdownNaSelecaoTextareaEdicaoTranscribrothers(
  valorBruto: string,
  selectionStart: number,
  selectionEnd: number,
  acao: TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers,
): ResultadoAplicarFormatacaoMarkdownTextareaEdicaoTranscribrothers {
  const valor = normalizarQuebrasLinhaMarkdown(valorBruto);
  const inicio = Math.max(0, Math.min(selectionStart, valor.length));
  const fim = Math.max(inicio, Math.min(selectionEnd, valor.length));

  switch (acao) {
    case "negrito":
      return aplicarEnvolvimentoMarcadoresMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "**",
        "**",
        PLACEHOLDER_TEXTO_FORMATACAO_MARKDOWN,
      );
    case "italico":
      return aplicarEnvolvimentoMarcadoresMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "*",
        "*",
        PLACEHOLDER_TEXTO_FORMATACAO_MARKDOWN,
      );
    case "tachado":
      return aplicarEnvolvimentoMarcadoresMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "~~",
        "~~",
        PLACEHOLDER_TEXTO_FORMATACAO_MARKDOWN,
      );
    case "codigo-inline":
      return aplicarEnvolvimentoMarcadoresMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "`",
        "`",
        "codigo",
      );
    case "link": {
      const selecionado = valor.slice(inicio, fim);
      const matchLink = /^\[([^\]]*)\]\(([^)]*)\)$/.exec(selecionado);
      if (matchLink) {
        const texto = matchLink[1];
        return {
          novoValor: valor.slice(0, inicio) + texto + valor.slice(fim),
          selectionStart: inicio,
          selectionEnd: inicio + texto.length,
        };
      }
      const textoLink =
        selecionado.length > 0 ? selecionado : PLACEHOLDER_TEXTO_FORMATACAO_MARKDOWN;
      const envolvido = `[${textoLink}](${PLACEHOLDER_URL_LINK_MARKDOWN})`;
      const novoValor = valor.slice(0, inicio) + envolvido + valor.slice(fim);
      const inicioUrl =
        inicio + 1 + textoLink.length + 2;
      const fimUrl = inicioUrl + PLACEHOLDER_URL_LINK_MARKDOWN.length;
      return {
        novoValor,
        selectionStart: inicioUrl,
        selectionEnd: fimUrl,
      };
    }
    case "lista-marcadores":
      return aplicarPrefixoLinhasMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "- ",
      );
    case "lista-numerada":
      return aplicarListaNumeradaLinhasMarkdownTranscribrothers(valor, inicio, fim);
    case "citacao":
      return aplicarPrefixoLinhasMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        "> ",
      );
    case "titulo-2":
      return aplicarTituloNivel2LinhasMarkdownTranscribrothers(valor, inicio, fim);
    case "tabela": {
      const precisaLinhaEmBranco =
        inicio > 0 && valor[inicio - 1] !== "\n";
      const precisaLinhaDepois =
        fim < valor.length && valor[fim] !== "\n";
      const prefixo = precisaLinhaEmBranco ? "\n\n" : inicio === 0 ? "" : "\n";
      const sufixo = precisaLinhaDepois ? "\n" : "";
      const texto = `${prefixo}${MODELO_TABELA_MARKDOWN_PADRAO}${sufixo}`;
      return inserirTextoNoCursorMarkdownTranscribrothers(
        valor,
        inicio,
        fim,
        texto,
        false,
      );
    }
    default: {
      const _exaustivo: never = acao;
      return { novoValor: valor, selectionStart: inicio, selectionEnd: fim };
    }
  }
}
