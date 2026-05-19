import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";
import type { RegistroAnotacaoImagemTutorialApiTranscribrothers } from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";

export type ItemListaAssetImagemTutorialApiTranscribrothers = RegistroAnotacaoImagemTutorialApiTranscribrothers & {
  referenciado_no_markdown: boolean;
};

export async function listarAssetsImagensTutorialJobApiTranscribrothers(
  jobId: string,
): Promise<ItemListaAssetImagemTutorialApiTranscribrothers[]> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/imagens-tutorial/lista-assets`,
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao listar assets (HTTP ${r.status}).`);
  }
  const data = (await r.json()) as { itens?: ItemListaAssetImagemTutorialApiTranscribrothers[] };
  return data.itens ?? [];
}

export async function excluirAssetImagemTutorialJobApiTranscribrothers(
  jobId: string,
  nomeArquivoOriginal: string,
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/assets/${encodeURIComponent(nomeArquivoOriginal)}`,
    { method: "DELETE" },
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao excluir asset (HTTP ${r.status}).`);
  }
  return (await r.json()) as JobStatus;
}
