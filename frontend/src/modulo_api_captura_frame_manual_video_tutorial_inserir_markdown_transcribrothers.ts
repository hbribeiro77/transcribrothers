/** Captura frame do vídeo no instante indicado e devolve snippet Markdown + job atualizado. */

import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type RespostaCapturarFrameManualVideoTutorialApiTranscribrothers = {
  nome_arquivo: string;
  caminho_relativo: string;
  snippet_markdown: string;
  timestamp_segundos_solicitado: number;
  timestamp_segundos_efetivo: number;
  job: JobStatus;
};

export async function capturarFrameManualVideoTutorialJobApiTranscribrothers(
  jobId: string,
  timestampSegundos: number,
): Promise<RespostaCapturarFrameManualVideoTutorialApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/capturar-frame-manual-video-tutorial`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ timestamp_segundos: timestampSegundos }),
  });
  if (!r.ok) {
    const det = await r.text();
    if (r.status === 404) {
      throw new Error(
        det ||
          "Endpoint de captura de frame não encontrado (HTTP 404). Reinicie o backend na porta 8000 para carregar a versão mais recente da API.",
      );
    }
    throw new Error(det || `Falha ao capturar frame (HTTP ${r.status}).`);
  }
  return (await r.json()) as RespostaCapturarFrameManualVideoTutorialApiTranscribrothers;
}

/** Insere texto na posição do cursor de um textarea. */
export function inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers(
  textarea: HTMLTextAreaElement,
  textoInserir: string,
  valorAtual: string,
): { novoValor: string; novaPosicaoCursor: number } {
  const inicio = textarea.selectionStart ?? valorAtual.length;
  const fim = textarea.selectionEnd ?? valorAtual.length;
  const antes = valorAtual.slice(0, inicio);
  const depois = valorAtual.slice(fim);
  const separadorAntes = antes.length > 0 && !antes.endsWith("\n") ? "\n\n" : "";
  const separadorDepois = depois.length > 0 && !depois.startsWith("\n") ? "\n\n" : "";
  const bloco = `${separadorAntes}${textoInserir}${separadorDepois}`;
  const novoValor = antes + bloco + depois;
  const novaPosicaoCursor = (antes + bloco).length;
  return { novoValor, novaPosicaoCursor };
}

export async function copiarTextoParaAreaTransferenciaNavegadorTranscribrothers(texto: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(texto);
    return;
  }
  const ta = document.createElement("textarea");
  ta.value = texto;
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
}
