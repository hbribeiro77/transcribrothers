/** Itens do menu Ações da cue (Fonte, Origem, Regenerar, Excluir). */

export type IdItemMenuAcoesCueVideoNarradoTranscribrothers =
  | "fonte"
  | "origem"
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
}): ItemMenuAcoesCueVideoNarradoTranscribrothers[] {
  return [
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
  ];
}
