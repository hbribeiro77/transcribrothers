/** Gera (em background) e baixa o MP4 narrado com legendas VTT queimadas. */

export type StatusVideoNarradoComLegendasQueimadasApiTranscribrothers = {
  status: "pronto" | "gerando" | "pendente" | "erro";
  erro?: string | null;
  url_download?: string | null;
  iniciado_em_epoch?: number | null;
  progresso_percentual?: number | null;
  tempo_decorrido_segundos?: number | null;
};

async function lerDetailErroHttpTranscribrothers(resposta: Response): Promise<string> {
  const texto = await resposta.text().catch(() => "");
  try {
    const json = JSON.parse(texto) as { detail?: unknown };
    if (typeof json.detail === "string" && json.detail.trim()) return json.detail.trim();
  } catch {
    /* mantém texto bruto */
  }
  return (
    texto.trim() ||
    `Falha ao preparar vídeo com legendas embutidas (HTTP ${resposta.status}).`
  );
}

function dispararDownloadPorUrlTranscribrothers(url: string, nomeArquivo: string): void {
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
}

export async function consultarStatusVideoNarradoComLegendasQueimadasJobApiTranscribrothers(
  jobId: string,
): Promise<StatusVideoNarradoComLegendasQueimadasApiTranscribrothers> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/video-com-narracao-tts-com-legendas-queimadas/status`,
  );
  if (!r.ok) throw new Error(await lerDetailErroHttpTranscribrothers(r));
  return (await r.json()) as StatusVideoNarradoComLegendasQueimadasApiTranscribrothers;
}

export async function agendarGeracaoVideoNarradoComLegendasQueimadasJobApiTranscribrothers(
  jobId: string,
  opcoes?: { forcar?: boolean },
): Promise<StatusVideoNarradoComLegendasQueimadasApiTranscribrothers> {
  const params = new URLSearchParams();
  if (opcoes?.forcar) params.set("forcar", "true");
  const qs = params.toString();
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/gerar-video-com-narracao-tts-com-legendas-queimadas` +
      (qs ? `?${qs}` : ""),
    { method: "POST" },
  );
  if (!r.ok) throw new Error(await lerDetailErroHttpTranscribrothers(r));
  return (await r.json()) as StatusVideoNarradoComLegendasQueimadasApiTranscribrothers;
}

export type ResultadoDownloadVideoNarradoComLegendasQueimadasTranscribrothers = {
  /** true se houve espera/geração; false se o cache já estava pronto. */
  precisouGerar: boolean;
};

/**
 * Se já estiver pronto, baixa na hora.
 * Senão agenda a geração em background, faz poll e só baixa quando status for "pronto".
 */
export async function baixarVideoNarradoComLegendasQueimadasJobApiTranscribrothers(
  jobId: string,
  opcoes?: {
    forcar?: boolean;
    onStatus?: (status: StatusVideoNarradoComLegendasQueimadasApiTranscribrothers) => void;
  },
): Promise<ResultadoDownloadVideoNarradoComLegendasQueimadasTranscribrothers> {
  const nomeArquivo = `video_com_narracao_tts_com_legendas_queimadas_${jobId}.mp4`;
  const urlDownload = `/api/jobs/${encodeURIComponent(jobId)}/video-com-narracao-tts-com-legendas-queimadas`;

  let status = await consultarStatusVideoNarradoComLegendasQueimadasJobApiTranscribrothers(jobId);
  opcoes?.onStatus?.(status);

  if (status.status === "pronto" && !opcoes?.forcar) {
    dispararDownloadPorUrlTranscribrothers(urlDownload, nomeArquivo);
    return { precisouGerar: false };
  }

  if (status.status !== "gerando") {
    status = await agendarGeracaoVideoNarradoComLegendasQueimadasJobApiTranscribrothers(jobId, {
      forcar: opcoes?.forcar,
    });
    opcoes?.onStatus?.(status);
  }

  // Nunca baixar em "gerando"/"pendente" — só após o servidor marcar pronto.
  if (status.status === "pronto") {
    dispararDownloadPorUrlTranscribrothers(urlDownload, nomeArquivo);
    return { precisouGerar: Boolean(opcoes?.forcar) };
  }
  if (status.status === "erro") {
    throw new Error(status.erro || "Falha ao gerar o vídeo com legendas embutidas.");
  }

  const inicio = Date.now();
  const limiteMs = 20 * 60 * 1000;
  while (Date.now() - inicio < limiteMs) {
    await new Promise((r) => setTimeout(r, 2000));
    status = await consultarStatusVideoNarradoComLegendasQueimadasJobApiTranscribrothers(jobId);
    opcoes?.onStatus?.(status);
    if (status.status === "pronto") {
      dispararDownloadPorUrlTranscribrothers(urlDownload, nomeArquivo);
      return { precisouGerar: true };
    }
    if (status.status === "erro") {
      throw new Error(status.erro || "Falha ao gerar o vídeo com legendas embutidas.");
    }
  }
  throw new Error(
    "A geração do vídeo com legendas embutidas está demorando mais que o esperado. Tente de novo em instantes.",
  );
}
