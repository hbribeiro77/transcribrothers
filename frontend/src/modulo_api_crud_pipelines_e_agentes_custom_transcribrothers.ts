import type { RespostaCatalogoPipelinesApiTranscribrothers } from "./tipos_catalogo_pipelines_api_transcribrothers.ts";

async function parseJsonOuErroTranscribrothers(r: Response): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try {
      const j = (await r.json()) as { detail?: string };
      if (j.detail) detail = String(j.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await r.json()) as RespostaCatalogoPipelinesApiTranscribrothers;
}

export async function duplicarPipelineCustomApiTranscribrothers(
  fonteId: string,
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch("/api/pipelines/custom/duplicar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fonte_id: fonteId }),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function criarPipelineCustomApiTranscribrothers(
  fonteId: string,
  opcoes?: { titulo?: string; descricao?: string },
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch("/api/pipelines/custom/criar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fonte_id: fonteId,
      titulo: opcoes?.titulo?.trim() || null,
      descricao: opcoes?.descricao ?? null,
    }),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function reordenarPipelinesCustomApiTranscribrothers(
  pipelineIdsOrdenados: string[],
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch("/api/pipelines/custom/ordem", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pipeline_ids_ordenados: pipelineIdsOrdenados }),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function reordenarPassosPipelineCustomApiTranscribrothers(
  pipelineId: string,
  passoIdsOrdenados: string[],
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/pipelines/custom/${encodeURIComponent(pipelineId)}/passos/ordem`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ passo_ids_ordenados: passoIdsOrdenados }),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function adicionarPassoPipelineCustomApiTranscribrothers(
  pipelineId: string,
  body: { agente_fonte_id: string; rotulo?: string; descricao?: string },
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/pipelines/custom/${encodeURIComponent(pipelineId)}/passos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function removerPassoPipelineCustomApiTranscribrothers(
  pipelineId: string,
  passoId: string,
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(
    `/api/pipelines/custom/${encodeURIComponent(pipelineId)}/passos/${encodeURIComponent(passoId)}`,
    { method: "DELETE" },
  );
  return parseJsonOuErroTranscribrothers(r);
}

export async function duplicarAgenteCustomApiTranscribrothers(
  fonteId: string,
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch("/api/agentes/custom/duplicar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fonte_id: fonteId }),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function atualizarPipelineCustomApiTranscribrothers(
  pipelineId: string,
  body: { titulo?: string; descricao?: string; entradas_aceitas?: string[] },
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/pipelines/custom/${encodeURIComponent(pipelineId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function excluirPipelineCustomApiTranscribrothers(
  pipelineId: string,
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/pipelines/custom/${encodeURIComponent(pipelineId)}`, {
    method: "DELETE",
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function atualizarAgenteCustomApiTranscribrothers(
  agenteId: string,
  body: {
    rotulo?: string;
    descricao?: string;
    modelo_litellm?: string | null;
    prompts?: Array<{
      chave: string;
      tipo: string;
      rotulo: string;
      texto: string;
      observacao?: string | null;
    }>;
  },
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/agentes/custom/${encodeURIComponent(agenteId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJsonOuErroTranscribrothers(r);
}

export async function excluirAgenteCustomApiTranscribrothers(
  agenteId: string,
): Promise<RespostaCatalogoPipelinesApiTranscribrothers> {
  const r = await fetch(`/api/agentes/custom/${encodeURIComponent(agenteId)}`, {
    method: "DELETE",
  });
  return parseJsonOuErroTranscribrothers(r);
}
