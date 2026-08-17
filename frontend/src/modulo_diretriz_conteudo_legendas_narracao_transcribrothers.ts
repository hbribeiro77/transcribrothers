/** Diretriz de conteúdo das legendas (limpeza IA antes do TTS). */

export const DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS = "conservador";
export const DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS = "mais_falavel";
export const DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS = "mais_didatico";
export const DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS = "mais_descontraido";
export const DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS =
  DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS;

export type DiretrizConteudoLegendasTranscribrothers =
  | typeof DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS
  | typeof DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS
  | typeof DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS
  | typeof DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS;

export type OpcaoDiretrizConteudoLegendasUiTranscribrothers = {
  id: DiretrizConteudoLegendasTranscribrothers;
  rotulo: string;
  descricao: string;
};

export function listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers(): OpcaoDiretrizConteudoLegendasUiTranscribrothers[] {
  return [
    {
      id: DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
      rotulo: "Conservador (padrão)",
      descricao: "Limpeza mínima: remove lixo e deixa forma narrável.",
    },
    {
      id: DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
      rotulo: "Mais falável",
      descricao: "Reescreve para frases naturais de narração em voz alta.",
    },
    {
      id: DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
      rotulo: "Mais didático",
      descricao: "Tom de tutorial passo a passo, orientando a ação.",
    },
    {
      id: DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
      rotulo: "Mais descontraído",
      descricao: "Tom leve e conversacional, ainda institucional.",
    },
  ];
}

export function normalizarDiretrizConteudoLegendasTranscribrothers(
  valor: unknown,
): DiretrizConteudoLegendasTranscribrothers {
  const t = String(valor ?? "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_")
    .replace(/\s+/g, "_");
  if (
    !t ||
    t === "conservador" ||
    t === "padrao" ||
    t === "padrão" ||
    t === "default" ||
    t === "minimo" ||
    t === "mínimo"
  ) {
    return DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS;
  }
  if (t === "mais_falavel" || t === "mais_falável" || t === "falavel" || t === "falável" || t === "natural") {
    return DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS;
  }
  if (
    t === "mais_didatico" ||
    t === "mais_didático" ||
    t === "didatico" ||
    t === "didático" ||
    t === "tutorial"
  ) {
    return DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS;
  }
  if (
    t === "mais_descontraido" ||
    t === "mais_descontraído" ||
    t === "descontraido" ||
    t === "descontraído" ||
    t === "leve" ||
    t === "casual"
  ) {
    return DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS;
  }
  return DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS;
}

export function rotuloDiretrizConteudoLegendasParaUiTranscribrothers(diretriz: unknown): string {
  const id = normalizarDiretrizConteudoLegendasTranscribrothers(diretriz);
  const op = listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers().find((o) => o.id === id);
  return op?.rotulo ?? id;
}
