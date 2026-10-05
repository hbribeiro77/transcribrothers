import { derivarNomeArquivoPngAnotadoLocalTranscribrothers } from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";

export type EntradaResolverInsercaoDocumentoAposEdicaoCanvasAnotacaoTranscribrothers = {
  nomeArquivoOriginal: string;
  recorteFoiAplicado: boolean;
  totalObjetosCanvas: number;
  jaExisteArquivoAnotado: boolean;
  exibindoVersaoAnotadaNoCanvas: boolean;
};

export type ResultadoResolverInsercaoDocumentoAposEdicaoCanvasAnotacaoTranscribrothers = {
  nomeArquivoParaSnippet: string;
  precisaPersistirAnotacao: boolean;
};

function canvasTemEdicaoNaoSalvaAlemDaImagemDeFundoTranscribrothers(
  recorteFoiAplicado: boolean,
  totalObjetosCanvas: number,
): boolean {
  return recorteFoiAplicado || totalObjetosCanvas > 1;
}

export function resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers(
  entrada: EntradaResolverInsercaoDocumentoAposEdicaoCanvasAnotacaoTranscribrothers,
): ResultadoResolverInsercaoDocumentoAposEdicaoCanvasAnotacaoTranscribrothers {
  const nomeAnotado = derivarNomeArquivoPngAnotadoLocalTranscribrothers(entrada.nomeArquivoOriginal);
  const temEdicaoNaoSalva = canvasTemEdicaoNaoSalvaAlemDaImagemDeFundoTranscribrothers(
    entrada.recorteFoiAplicado,
    entrada.totalObjetosCanvas,
  );
  if (temEdicaoNaoSalva) {
    return { nomeArquivoParaSnippet: nomeAnotado, precisaPersistirAnotacao: true };
  }
  if (entrada.exibindoVersaoAnotadaNoCanvas && entrada.jaExisteArquivoAnotado) {
    return { nomeArquivoParaSnippet: nomeAnotado, precisaPersistirAnotacao: false };
  }
  return {
    nomeArquivoParaSnippet: entrada.nomeArquivoOriginal,
    precisaPersistirAnotacao: false,
  };
}
