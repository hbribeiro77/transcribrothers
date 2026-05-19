/** API de anotação de screenshots: original + `.anotado.png` e metadados em `steps_json`. */

import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type RegistroAnotacaoImagemTutorialApiTranscribrothers = {
  nome_arquivo_original: string;
  nome_arquivo_anotado: string;
  exibir_no_tutorial: "original" | "anotado";
  tem_arquivo_anotado: boolean;
  atualizado_em?: string | null;
};

export type MapaAnotacoesImagensTutorialTranscribrothers = Record<
  string,
  RegistroAnotacaoImagemTutorialApiTranscribrothers
>;

const CHAVE_STEPS_ANOTACOES = "imagens_tutorial_anotacoes";

export function extrairMapaAnotacoesImagensTutorialDoStepsJsonTranscribrothers(
  stepsJson: Record<string, unknown> | undefined | null,
): MapaAnotacoesImagensTutorialTranscribrothers {
  if (!stepsJson) return {};
  const raw = stepsJson[CHAVE_STEPS_ANOTACOES];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};
  const saida: MapaAnotacoesImagensTutorialTranscribrothers = {};
  for (const [nome, valor] of Object.entries(raw as Record<string, unknown>)) {
    if (!valor || typeof valor !== "object" || Array.isArray(valor)) continue;
    const v = valor as Record<string, unknown>;
    const nomeAnotado =
      typeof v.nome_arquivo_anotado === "string"
        ? v.nome_arquivo_anotado
        : derivarNomeArquivoPngAnotadoLocalTranscribrothers(nome);
    const exibir = v.exibir_no_tutorial === "original" ? "original" : "anotado";
    saida[nome] = {
      nome_arquivo_original: nome,
      nome_arquivo_anotado: nomeAnotado,
      exibir_no_tutorial: exibir,
      tem_arquivo_anotado: Boolean(v.tem_arquivo_anotado),
      atualizado_em: typeof v.atualizado_em === "string" ? v.atualizado_em : null,
    };
  }
  return saida;
}

export function derivarNomeArquivoPngAnotadoLocalTranscribrothers(nomeOriginal: string): string {
  if (!nomeOriginal.toLowerCase().endsWith(".png")) return `${nomeOriginal}.anotado.png`;
  return `${nomeOriginal.slice(0, -4)}.anotado.png`;
}

export function mesclarMapaAnotacoesComRespostaListagemApiTranscribrothers(
  porArquivo: Record<string, RegistroAnotacaoImagemTutorialApiTranscribrothers>,
): MapaAnotacoesImagensTutorialTranscribrothers {
  return { ...porArquivo };
}

export async function listarMetadadosAnotacoesImagensTutorialJobApiTranscribrothers(
  jobId: string,
): Promise<MapaAnotacoesImagensTutorialTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/imagens-tutorial/anotacoes`);
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao listar anotações (HTTP ${r.status}).`);
  }
  const data = (await r.json()) as { por_arquivo?: Record<string, RegistroAnotacaoImagemTutorialApiTranscribrothers> };
  return mesclarMapaAnotacoesComRespostaListagemApiTranscribrothers(data.por_arquivo ?? {});
}

export async function gravarPngAnotadoScreenshotTutorialJobApiTranscribrothers(
  jobId: string,
  nomeArquivoOriginal: string,
  blobPng: Blob,
): Promise<JobStatus> {
  const fd = new FormData();
  fd.append("arquivo_png", blobPng, derivarNomeArquivoPngAnotadoLocalTranscribrothers(nomeArquivoOriginal));
  const r = await fetch(
    `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivoOriginal)}/anotacao`,
    { method: "PUT", body: fd },
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao salvar anotação (HTTP ${r.status}).`);
  }
  return (await r.json()) as JobStatus;
}

export async function definirVersaoExibicaoScreenshotTutorialJobApiTranscribrothers(
  jobId: string,
  nomeArquivoOriginal: string,
  versao: "original" | "anotado",
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivoOriginal)}/exibicao-imagem`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ versao }),
    },
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao alterar exibição (HTTP ${r.status}).`);
  }
  return (await r.json()) as JobStatus;
}

export async function removerAnotacaoScreenshotTutorialJobApiTranscribrothers(
  jobId: string,
  nomeArquivoOriginal: string,
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivoOriginal)}/anotacao`,
    { method: "DELETE" },
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao remover anotação (HTTP ${r.status}).`);
  }
  return (await r.json()) as JobStatus;
}

export async function sincronizarMarkdownComVersaoAnotadaScreenshotJobApiTranscribrothers(
  jobId: string,
  nomeArquivoOriginal: string,
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${jobId}/assets/${encodeURIComponent(nomeArquivoOriginal)}/sincronizar-markdown-com-versao-anotada`,
    { method: "POST" },
  );
  if (!r.ok) {
    const det = await r.text();
    throw new Error(det || `Falha ao atualizar Markdown (HTTP ${r.status}).`);
  }
  return (await r.json()) as JobStatus;
}
