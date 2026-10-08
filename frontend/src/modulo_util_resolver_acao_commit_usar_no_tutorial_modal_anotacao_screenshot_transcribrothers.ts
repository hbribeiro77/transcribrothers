export const ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS =
  "Usar no tutorial";

export const ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_PROCESSANDO_MODAL_ANOTACAO_TRANSCRIBROTHERS =
  "Aplicando…";

export type VersaoExibidaNoEditorAnotacaoModalTranscribrothers = "original" | "anotado";

export type TipoAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers =
  | "promover_previsualizacao_frame"
  | "usar_original_no_tutorial"
  | "usar_anotada_no_tutorial";

export type EntradaResolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers = {
  noSlotDocumento: boolean;
  versaoExibidaNoEditor: VersaoExibidaNoEditorAnotacaoModalTranscribrothers;
  recorteFoiAplicado: boolean;
  totalObjetosCanvas: number;
};

export type DecisaoAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers = {
  tipo: TipoAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers;
  precisaPersistirAnotacao: boolean;
  versaoParaTutorial: "original" | "anotado" | null;
};

function canvasTemEdicaoAlemDaImagemDeFundoTranscribrothers(
  recorteFoiAplicado: boolean,
  totalObjetosCanvas: number,
): boolean {
  return recorteFoiAplicado || totalObjetosCanvas > 1;
}

export function resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers(
  entrada: EntradaResolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers,
): DecisaoAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers {
  const temEdicao = canvasTemEdicaoAlemDaImagemDeFundoTranscribrothers(
    entrada.recorteFoiAplicado,
    entrada.totalObjetosCanvas,
  );
  if (!entrada.noSlotDocumento) {
    return {
      tipo: "promover_previsualizacao_frame",
      precisaPersistirAnotacao: temEdicao,
      versaoParaTutorial: temEdicao ? "anotado" : null,
    };
  }
  if (entrada.versaoExibidaNoEditor === "anotado" || temEdicao) {
    return {
      tipo: "usar_anotada_no_tutorial",
      precisaPersistirAnotacao: temEdicao,
      versaoParaTutorial: "anotado",
    };
  }
  return {
    tipo: "usar_original_no_tutorial",
    precisaPersistirAnotacao: false,
    versaoParaTutorial: "original",
  };
}
