import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type AnexoImagemContextoFabUiTranscribrothers = {
  id: string;
  tipo: "imagem";
  nomeArquivo: string;
  caminhoRelativo: string;
};

export type AnexoTextoContextoFabUiTranscribrothers = {
  id: string;
  tipo: "texto";
  conteudo: string;
  /** Nome do arquivo quando o texto veio de upload (.md, .txt, .pdf). */
  nomeArquivoOrigem?: string;
};

export type AnexoContextoFabUiTranscribrothers =
  | AnexoImagemContextoFabUiTranscribrothers
  | AnexoTextoContextoFabUiTranscribrothers;

export type PayloadContextoFabPedidoRegeneracaoTranscribrothers = {
  caminhos_assets_png_contexto_fab: string[];
  textos_contexto_fab: string[];
};

export function montarPayloadContextoFabParaRegeneracaoApiTranscribrothers(
  anexos: AnexoContextoFabUiTranscribrothers[],
): PayloadContextoFabPedidoRegeneracaoTranscribrothers {
  const caminhos: string[] = [];
  const textos: string[] = [];
  for (const a of anexos) {
    if (a.tipo === "imagem") {
      caminhos.push(a.caminhoRelativo);
    } else {
      let bloco = a.conteudo.trim();
      if (a.nomeArquivoOrigem?.trim()) {
        bloco = `(Fonte do arquivo: ${a.nomeArquivoOrigem.trim()})\n\n${bloco}`;
      }
      textos.push(bloco);
    }
  }
  return {
    caminhos_assets_png_contexto_fab: caminhos,
    textos_contexto_fab: textos,
  };
}

export async function uploadImagemAnexoContextoFabProjetoEmBrancoApiTranscribrothers(
  jobId: string,
  arquivoImagem: File,
): Promise<{ nome_arquivo: string; caminho_relativo: string; job: JobStatus }> {
  const formulario = new FormData();
  formulario.append("imagem", arquivoImagem, arquivoImagem.name || "anexo-fab.png");

  const resposta = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/fab-anexos-contexto-imagem`,
    { method: "POST", body: formulario },
  );
  if (!resposta.ok) {
    const detalhe = await resposta.text();
    throw new Error(detalhe || `Falha ao anexar imagem (HTTP ${resposta.status}).`);
  }
  return (await resposta.json()) as {
    nome_arquivo: string;
    caminho_relativo: string;
    job: JobStatus;
  };
}

export async function extrairTextoDocumentoAnexoContextoFabProjetoEmBrancoApiTranscribrothers(
  jobId: string,
  arquivo: File,
): Promise<{ nome_arquivo: string; texto: string; truncado: boolean }> {
  const formulario = new FormData();
  formulario.append("documento", arquivo, arquivo.name || "anexo.pdf");

  const resposta = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/fab-anexos-contexto-documento`,
    { method: "POST", body: formulario },
  );
  if (!resposta.ok) {
    const detalhe = await resposta.text();
    throw new Error(detalhe || `Falha ao ler documento (HTTP ${resposta.status}).`);
  }
  return (await resposta.json()) as {
    nome_arquivo: string;
    texto: string;
    truncado: boolean;
  };
}
