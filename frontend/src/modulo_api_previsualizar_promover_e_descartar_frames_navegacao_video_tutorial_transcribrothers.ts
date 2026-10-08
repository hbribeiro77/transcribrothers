import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type ItemPrevisualizacaoFrameNavegacaoVideoTutorialApiTranscribrothers = {
  timestamp_segundos_solicitado: number;
  timestamp_segundos_efetivo: number;
  nome_arquivo: string;
  url_preview: string;
};

async function lerErroHttpApiTranscribrothers(r: Response, fallback: string): Promise<string> {
  const det = await r.text();
  return det || `${fallback} (HTTP ${r.status}).`;
}

export async function previsualizarFramesNavegacaoVideoTutorialJobApiTranscribrothers(
  jobId: string,
  timestampsSegundos: number[],
): Promise<ItemPrevisualizacaoFrameNavegacaoVideoTutorialApiTranscribrothers[]> {
  const r = await fetch(`/api/jobs/${jobId}/previsualizar-frames-video-tutorial`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ timestamps_segundos: timestampsSegundos }),
  });
  if (!r.ok) {
    throw new Error(await lerErroHttpApiTranscribrothers(r, "Falha ao pré-visualizar frames do vídeo"));
  }
  const body = (await r.json()) as {
    itens?: ItemPrevisualizacaoFrameNavegacaoVideoTutorialApiTranscribrothers[];
  };
  return Array.isArray(body.itens) ? body.itens : [];
}

export async function promoverFramePrevisualizacaoParaAssetsVideoTutorialJobApiTranscribrothers(
  jobId: string,
  nomeArquivoPreview: string,
  timestampSegundos: number,
): Promise<{ nome_arquivo: string; caminho_relativo: string; timestamp_segundos: number; job: JobStatus }> {
  const r = await fetch(`/api/jobs/${jobId}/promover-frame-previsualizacao-para-assets-video-tutorial`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nome_arquivo_preview: nomeArquivoPreview,
      timestamp_segundos: timestampSegundos,
    }),
  });
  if (!r.ok) {
    throw new Error(await lerErroHttpApiTranscribrothers(r, "Falha ao usar este frame no documento"));
  }
  return (await r.json()) as {
    nome_arquivo: string;
    caminho_relativo: string;
    timestamp_segundos: number;
    job: JobStatus;
  };
}

export async function descartarPrevisualizacaoFramesNavegacaoVideoTutorialJobApiTranscribrothers(
  jobId: string,
  nomesParaApagar: string[],
  nomesProtegidos: string[],
): Promise<void> {
  const r = await fetch(`/api/jobs/${jobId}/previsualizar-frames-video-tutorial`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nomes_para_apagar: nomesParaApagar,
      nomes_protegidos: nomesProtegidos,
    }),
  });
  if (!r.ok) {
    throw new Error(await lerErroHttpApiTranscribrothers(r, "Falha ao descartar prévias de frame"));
  }
}
