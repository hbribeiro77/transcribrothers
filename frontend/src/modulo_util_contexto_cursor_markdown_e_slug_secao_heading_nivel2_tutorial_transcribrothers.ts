/** Uma seção `## Título` no Markdown do tutorial, com linha 1-based e id estável para âncora no preview. */
export type SecaoHeadingNivel2MarkdownTutorialTranscribrothers = {
  titulo: string;
  numeroLinha: number;
  slugIdAncoraPreview: string;
};

export function contarNumeroLinhaMarkdownAPartirOffsetCaracteresTranscribrothers(
  texto: string,
  offsetCaracteres: number,
): number {
  const limite = Math.max(0, Math.min(offsetCaracteres, texto.length));
  let linhas = 1;
  for (let i = 0; i < limite; i += 1) {
    if (texto[i] === "\n") linhas += 1;
  }
  return linhas;
}

export function gerarSlugIdAncoraBaseSecaoHeadingMarkdownTutorialTranscribrothers(
  titulo: string,
): string {
  const normalizado = titulo
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalizado || "secao";
}

export function listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(
  markdown: string,
): SecaoHeadingNivel2MarkdownTutorialTranscribrothers[] {
  const linhas = markdown.replace(/\r\n/g, "\n").split("\n");
  const brutas: Array<{ titulo: string; numeroLinha: number }> = [];
  let dentroBlocoCodigo = false;

  for (let indice = 0; indice < linhas.length; indice += 1) {
    const linha = linhas[indice];
    const trim = linha.trim();
    if (/^```/.test(trim)) {
      dentroBlocoCodigo = !dentroBlocoCodigo;
      continue;
    }
    if (dentroBlocoCodigo) continue;

    const match = trim.match(/^##(?!#)\s+(.+)$/);
    if (!match) continue;

    let titulo = match[1].trim();
    while (titulo.endsWith("#")) {
      titulo = titulo.slice(0, -1).trimEnd();
    }
    if (!titulo) continue;

    brutas.push({ titulo, numeroLinha: indice + 1 });
  }

  const contagemSlugBase = new Map<string, number>();
  return brutas.map(({ titulo, numeroLinha }) => {
    const slugBase = gerarSlugIdAncoraBaseSecaoHeadingMarkdownTutorialTranscribrothers(titulo);
    const ocorrencia = contagemSlugBase.get(slugBase) ?? 0;
    contagemSlugBase.set(slugBase, ocorrencia + 1);
    const slugIdAncoraPreview = ocorrencia === 0 ? slugBase : `${slugBase}-${ocorrencia}`;
    return { titulo, numeroLinha, slugIdAncoraPreview };
  });
}

export function obterSecaoHeadingNivel2AtivaNaLinhaMarkdownTutorialTranscribrothers(
  secoes: SecaoHeadingNivel2MarkdownTutorialTranscribrothers[],
  numeroLinha: number,
): SecaoHeadingNivel2MarkdownTutorialTranscribrothers | null {
  let ativa: SecaoHeadingNivel2MarkdownTutorialTranscribrothers | null = null;
  for (const secao of secoes) {
    if (secao.numeroLinha <= numeroLinha) ativa = secao;
    else break;
  }
  return ativa;
}
