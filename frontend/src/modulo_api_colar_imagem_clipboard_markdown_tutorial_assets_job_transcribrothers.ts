import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type RespostaColarImagemClipboardMarkdownTutorialApiTranscribrothers = {
  nome_arquivo: string;
  caminho_relativo: string;
  snippet_markdown: string;
  job: JobStatus;
};

export async function colarImagemClipboardMarkdownTutorialJobApiTranscribrothers(
  jobId: string,
  arquivoImagem: File,
): Promise<RespostaColarImagemClipboardMarkdownTutorialApiTranscribrothers> {
  const formulario = new FormData();
  formulario.append("imagem", arquivoImagem, arquivoImagem.name || "imagem-colada.png");

  const resposta = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/colar-imagem-clipboard-markdown-tutorial`,
    {
      method: "POST",
      body: formulario,
    },
  );

  if (!resposta.ok) {
    const detalhe = await resposta.text();
    if (resposta.status === 404) {
      throw new Error(
        detalhe ||
          "Endpoint de colar imagem não encontrado (HTTP 404). Reinicie o backend na porta 8000.",
      );
    }
    throw new Error(detalhe || `Falha ao colar imagem (HTTP ${resposta.status}).`);
  }

  return (await resposta.json()) as RespostaColarImagemClipboardMarkdownTutorialApiTranscribrothers;
}
