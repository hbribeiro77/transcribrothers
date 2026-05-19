import type { RegistroAnotacaoImagemTutorialApiTranscribrothers } from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";

/** Nome de arquivo servido por GET `/assets/{nome}` conforme metadados de duas versões. */
export function resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers(
  nomeArquivoOriginal: string,
  registro: RegistroAnotacaoImagemTutorialApiTranscribrothers | undefined,
): string {
  if (!registro) return nomeArquivoOriginal;
  if (
    registro.exibir_no_tutorial === "anotado" &&
    registro.tem_arquivo_anotado &&
    registro.nome_arquivo_anotado
  ) {
    return registro.nome_arquivo_anotado;
  }
  return nomeArquivoOriginal;
}

export function urlAssetPngJobParaNomeArquivoTranscribrothers(
  jobId: string,
  nomeArquivo: string,
): string {
  return `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivo)}`;
}
