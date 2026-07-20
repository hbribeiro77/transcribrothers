/** POST /api/jobs/importar-transcricao — texto/legendas sem STT. */

import type { DestinoAposTranscricaoTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import type { RespostaJobApiTranscribrothers } from "./modulo_api_criar_projeto_em_branco_job_transcribrothers.ts";

export type DestinoImportarTranscricaoProntaTranscribrothers = Extract<
  DestinoAposTranscricaoTranscribrothers,
  "so_transcricao" | "notas_proposta_funcionalidade"
>;

export async function importarTranscricaoProntaJobApiTranscribrothers(params: {
  texto?: string;
  arquivo?: File | null;
  destino: DestinoImportarTranscricaoProntaTranscribrothers;
  pipelineCustomId?: string | null;
  litellmModel?: string | null;
}): Promise<RespostaJobApiTranscribrothers> {
  const fd = new FormData();
  fd.append("destino_apos_transcricao", params.destino);
  if (params.texto?.trim()) {
    fd.append("texto", params.texto.trim());
  }
  if (params.arquivo) {
    fd.append("arquivo", params.arquivo);
  }
  if (params.pipelineCustomId?.trim()) {
    fd.append("pipeline_custom_id", params.pipelineCustomId.trim());
  }
  if (params.litellmModel?.trim()) {
    fd.append("litellm_model", params.litellmModel.trim());
  }
  const r = await fetch("/api/jobs/importar-transcricao", {
    method: "POST",
    body: fd,
  });
  if (!r.ok) {
    let detalhe = "";
    try {
      const j = (await r.json()) as { detail?: string };
      detalhe = typeof j.detail === "string" ? j.detail : "";
    } catch {
      detalhe = await r.text();
    }
    throw new Error(detalhe || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as RespostaJobApiTranscribrothers;
}
