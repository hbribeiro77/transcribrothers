import { diffLines, type Change } from "diff";

export type ResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers = {
  textoIgual: boolean;
  linhasAntes: number;
  linhasDepois: number;
  linhasAdicionadas: number;
  linhasRemovidas: number;
  linhasInalteradas: number;
  secoesHeadingAlteradas: string[];
  imagensAdicionadas: number;
  imagensRemovidas: number;
};

function normalizarTextoParaComparacaoIgualdadeTranscribrothers(texto: string): string {
  return texto.replace(/\r\n/g, "\n").trim();
}

function extrairHeadingsNivel2MarkdownTranscribrothers(texto: string): string[] {
  const linhas = texto.split("\n");
  const out: string[] = [];
  for (const linha of linhas) {
    const m = /^(##\s+.+)$/.exec(linha.trim());
    if (m) out.push(m[1]!.trim());
  }
  return out;
}

function contarReferenciasImagemMarkdownTranscribrothers(texto: string): number {
  const matches = texto.match(/!\[[^\]]*\]\([^)]+\)/g);
  return matches?.length ?? 0;
}

export function calcularResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers(
  textoAntes: string,
  textoDepois: string,
): ResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers {
  const antes = textoAntes ?? "";
  const depois = textoDepois ?? "";
  const normAntes = normalizarTextoParaComparacaoIgualdadeTranscribrothers(antes);
  const normDepois = normalizarTextoParaComparacaoIgualdadeTranscribrothers(depois);
  const textoIgual = normAntes === normDepois;

  const linhasAntes = normAntes ? normAntes.split("\n").length : 0;
  const linhasDepois = normDepois ? normDepois.split("\n").length : 0;

  let linhasAdicionadas = 0;
  let linhasRemovidas = 0;
  let linhasInalteradas = 0;
  const partes = diffLines(antes, depois);
  for (const parte of partes) {
    const n = parte.value === "" ? 0 : parte.value.replace(/\n$/, "").split("\n").length;
    if (parte.added) linhasAdicionadas += n;
    else if (parte.removed) linhasRemovidas += n;
    else linhasInalteradas += n;
  }

  const headingsAntes = new Set(extrairHeadingsNivel2MarkdownTranscribrothers(antes));
  const headingsDepois = new Set(extrairHeadingsNivel2MarkdownTranscribrothers(depois));
  const secoesHeadingAlteradas: string[] = [];
  for (const h of headingsDepois) {
    if (!headingsAntes.has(h)) secoesHeadingAlteradas.push(h);
  }
  for (const h of headingsAntes) {
    if (!headingsDepois.has(h)) secoesHeadingAlteradas.push(h);
  }

  const imgAntes = contarReferenciasImagemMarkdownTranscribrothers(antes);
  const imgDepois = contarReferenciasImagemMarkdownTranscribrothers(depois);

  return {
    textoIgual,
    linhasAntes,
    linhasDepois,
    linhasAdicionadas,
    linhasRemovidas,
    linhasInalteradas,
    secoesHeadingAlteradas: [...new Set(secoesHeadingAlteradas)],
    imagensAdicionadas: Math.max(0, imgDepois - imgAntes),
    imagensRemovidas: Math.max(0, imgAntes - imgDepois),
  };
}

export type LinhaDiffUnificadaMarkdownTranscribrothers = {
  tipo: "igual" | "removida" | "adicionada";
  texto: string;
  omitida?: boolean;
  rotuloOmitida?: string;
};

const MAX_LINHAS_IGUAIS_COLAPSADAS_VISIVEIS_TRANSCRIBROTHERS = 3;

/** Diff unificado com blocos longos iguais colapsados (modo «só alterações»). */
export function montarLinhasDiffUnificadoMarkdownAntesDepoisTranscribrothers(
  textoAntes: string,
  textoDepois: string,
  opts?: { somenteAlteracoes?: boolean },
): LinhaDiffUnificadaMarkdownTranscribrothers[] {
  const partes = diffLines(textoAntes ?? "", textoDepois ?? "");
  const linhas: LinhaDiffUnificadaMarkdownTranscribrothers[] = [];
  const somenteAlteracoes = opts?.somenteAlteracoes === true;

  for (const parte of partes) {
    const tipo: LinhaDiffUnificadaMarkdownTranscribrothers["tipo"] = parte.added
      ? "adicionada"
      : parte.removed
        ? "removida"
        : "igual";
    const brutas = parte.value.split("\n");
    if (brutas.length > 0 && brutas[brutas.length - 1] === "") brutas.pop();

    if (somenteAlteracoes && tipo === "igual" && brutas.length > MAX_LINHAS_IGUAIS_COLAPSADAS_VISIVEIS_TRANSCRIBROTHERS) {
      const mostrar = brutas.slice(0, MAX_LINHAS_IGUAIS_COLAPSADAS_VISIVEIS_TRANSCRIBROTHERS);
      for (const t of mostrar) {
        linhas.push({ tipo: "igual", texto: t });
      }
      linhas.push({
        tipo: "igual",
        texto: "",
        omitida: true,
        rotuloOmitida: `${brutas.length - MAX_LINHAS_IGUAIS_COLAPSADAS_VISIVEIS_TRANSCRIBROTHERS} linha(s) sem alteração oculta(s)`,
      });
      continue;
    }

    for (const t of brutas) {
      linhas.push({ tipo, texto: t });
    }
  }

  return linhas;
}

export type ParColunasDiffLadoALadoMarkdownTranscribrothers = {
  esquerda: string | null;
  direita: string | null;
  tipo: "igual" | "removida" | "adicionada" | "substituida";
};

/** Linhas alinhadas para visualização lado a lado com destaque. */
export function montarParesColunasDiffLadoALadoMarkdownAntesDepoisTranscribrothers(
  textoAntes: string,
  textoDepois: string,
): ParColunasDiffLadoALadoMarkdownTranscribrothers[] {
  const partes = diffLines(textoAntes ?? "", textoDepois ?? "");
  const pares: ParColunasDiffLadoALadoMarkdownTranscribrothers[] = [];

  for (let i = 0; i < partes.length; i++) {
    const parte = partes[i]!;
    const linhas = parte.value.split("\n");
    if (linhas.length > 0 && linhas[linhas.length - 1] === "") linhas.pop();

    if (parte.removed) {
      const prox = partes[i + 1];
      if (prox?.added) {
        const linhasDepois = prox.value.split("\n");
        if (linhasDepois.length > 0 && linhasDepois[linhasDepois.length - 1] === "") linhasDepois.pop();
        const max = Math.max(linhas.length, linhasDepois.length);
        for (let j = 0; j < max; j++) {
          pares.push({
            esquerda: linhas[j] ?? "",
            direita: linhasDepois[j] ?? "",
            tipo: "substituida",
          });
        }
        i += 1;
        continue;
      }
      for (const t of linhas) {
        pares.push({ esquerda: t, direita: null, tipo: "removida" });
      }
    } else if (parte.added) {
      for (const t of linhas) {
        pares.push({ esquerda: null, direita: t, tipo: "adicionada" });
      }
    } else {
      for (const t of linhas) {
        pares.push({ esquerda: t, direita: t, tipo: "igual" });
      }
    }
  }

  return pares;
}

export function obterPartesDiffLinhasTranscribrothers(textoAntes: string, textoDepois: string): Change[] {
  return diffLines(textoAntes ?? "", textoDepois ?? "");
}
