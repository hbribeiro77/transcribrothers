/** Itens do menu Ações da cue (Fonte, Origem, Regenerar, Excluir). */

export type IdItemMenuAcoesCueVideoNarradoTranscribrothers =
  | "fonte"
  | "origem"
  | "ajustar-vinheta"
  | "regenerar"
  | "excluir";

export type ItemMenuAcoesCueVideoNarradoTranscribrothers = {
  id: IdItemMenuAcoesCueVideoNarradoTranscribrothers;
  rotulo: string;
  desabilitado: boolean;
  titulo: string;
  perigoso: boolean;
};

export function montarItensMenuAcoesCueVideoNarradoTranscribrothers(p: {
  fonteDesabilitada: boolean;
  tituloFonte: string;
  origemDesabilitada: boolean;
  tituloOrigem: string;
  regenerarDesabilitada: boolean;
  tituloRegenerar: string;
  excluirDesabilitada: boolean;
  tituloExcluir: string;
  mostrarAjustarVinheta?: boolean;
  tituloAjustarVinheta?: string;
  ajustarVinhetaDesabilitada?: boolean;
}): ItemMenuAcoesCueVideoNarradoTranscribrothers[] {
  const itens: ItemMenuAcoesCueVideoNarradoTranscribrothers[] = [
    {
      id: "fonte",
      rotulo: "Fonte",
      desabilitado: p.fonteDesabilitada,
      titulo: p.tituloFonte,
      perigoso: false,
    },
    {
      id: "origem",
      rotulo: "Origem",
      desabilitado: p.origemDesabilitada,
      titulo: p.tituloOrigem,
      perigoso: false,
    },
  ];
  if (p.mostrarAjustarVinheta) {
    itens.push({
      id: "ajustar-vinheta",
      rotulo: "Ajustar vinheta",
      desabilitado: Boolean(p.ajustarVinhetaDesabilitada),
      titulo: p.tituloAjustarVinheta || "Reabre a prévia e gera de novo o cartão",
      perigoso: false,
    });
  }
  itens.push(
    {
      id: "regenerar",
      rotulo: "Regenerar",
      desabilitado: p.regenerarDesabilitada,
      titulo: p.tituloRegenerar,
      perigoso: false,
    },
    {
      id: "excluir",
      rotulo: "Excluir",
      desabilitado: p.excluirDesabilitada,
      titulo: p.tituloExcluir,
      perigoso: true,
    },
  );
  return itens;
}
