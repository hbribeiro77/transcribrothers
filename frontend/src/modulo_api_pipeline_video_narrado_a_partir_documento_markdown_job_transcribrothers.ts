import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type ResumoPipelineVideoNarradoDocumentoStepsJsonTranscribrothers = {
  ok?: boolean;
  mensagem?: string;
  percentual_casado?: number;
  url_asset_vtt?: string;
  nome_arquivo_vtt?: string;
};

export async function agendarPipelineVideoNarradoAPartirDocumentoJobApiTranscribrothers(
  jobId: string,
  litellmModelTts?: string | null,
  litellmModelChat?: string | null,
  opcoes?: {
    markdownNarracao?: string | null;
    titulosSecoesEscopo?: string[] | null;
  },
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/pipeline-video-narrado-a-partir-documento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      litellm_model: (litellmModelTts || "").trim() || null,
      litellm_model_chat: (litellmModelChat || "").trim() || null,
      markdown_narracao: (opcoes?.markdownNarracao || "").trim() || null,
      titulos_secoes_escopo: opcoes?.titulosSecoesEscopo?.length
        ? opcoes.titulosSecoesEscopo
        : null,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    try {
      const j = JSON.parse(t) as { detail?: unknown };
      if (typeof j.detail === "string" && j.detail.trim()) {
        throw new Error(j.detail.trim());
      }
    } catch (e) {
      if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
    }
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as JobStatus;
}

export function obterResumoPipelineVideoNarradoDocumentoDosStepsJsonTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): ResumoPipelineVideoNarradoDocumentoStepsJsonTranscribrothers | null {
  const raw = stepsJson?.pipeline_video_narrado_documento;
  if (!raw || typeof raw !== "object") return null;
  return raw as ResumoPipelineVideoNarradoDocumentoStepsJsonTranscribrothers;
}

export function obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): string | null {
  // Preferir o working set canônico: `tornar-atual` / saves atualizam esta chave com ?v= fresco.
  // `pipeline_video_narrado_documento.url_asset_vtt` pode ficar obsoleto e travar reload de cues na UI.
  const raw = stepsJson?.legendas_documento_alinhadas;
  if (raw && typeof raw === "object") {
    const url = (raw as { url_asset?: unknown }).url_asset;
    if (typeof url === "string" && url.trim()) return url.trim();
  }
  const pipeline = obterResumoPipelineVideoNarradoDocumentoDosStepsJsonTranscribrothers(stepsJson);
  if (pipeline?.url_asset_vtt && typeof pipeline.url_asset_vtt === "string") {
    const u = pipeline.url_asset_vtt.trim();
    if (u) return u;
  }
  return null;
}
