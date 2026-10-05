import {
  extrairTituloH1MarkdownTutorialTranscribrothers,
  sanitizarNomeBaseArquivoDownloadTutorialTranscribrothers,
} from "./modulo_util_extrair_titulo_h1_markdown_e_sanitizar_nome_arquivo_download_tutorial_transcribrothers.ts";

export function resolverTituloInicialVideoNarradoAPartirDoH1MarkdownTranscribrothers(
  markdown: string | null | undefined,
  fallback = "Vídeo narrado",
): string {
  const h1 = extrairTituloH1MarkdownTutorialTranscribrothers(markdown);
  const titulo = (h1 || "").trim();
  return titulo || fallback;
}

export function chaveSessionStorageTituloVideoNarradoTranscribrothers(jobId: string): string {
  return `transcribrothers.titulo_video_narrado.${jobId}`;
}

export function lerTituloVideoNarradoDoSessionStorageTranscribrothers(jobId: string): string {
  try {
    return (sessionStorage.getItem(chaveSessionStorageTituloVideoNarradoTranscribrothers(jobId)) || "").trim();
  } catch {
    return "";
  }
}

export function gravarTituloVideoNarradoNoSessionStorageTranscribrothers(
  jobId: string,
  titulo: string,
): void {
  try {
    const chave = chaveSessionStorageTituloVideoNarradoTranscribrothers(jobId);
    const limpo = titulo.trim();
    if (!limpo) {
      sessionStorage.removeItem(chave);
      return;
    }
    sessionStorage.setItem(chave, limpo);
  } catch {
    /* storage indisponível */
  }
}

export function resolverTituloVideoNarradoPersistidoOuH1Transcribrothers(
  persistido: string | null | undefined,
  markdown: string | null | undefined,
  fallback = "Vídeo narrado",
): string {
  const titulo = (persistido || "").trim();
  if (titulo) return titulo;
  return resolverTituloInicialVideoNarradoAPartirDoH1MarkdownTranscribrothers(markdown, fallback);
}

export function montarUrlDownloadVideoNarradoComNomeArquivoQueryTranscribrothers(
  urlBase: string,
  nomeArquivo: string,
): string {
  const trimmed = nomeArquivo.trim();
  if (!trimmed) return urlBase;
  const params = new URLSearchParams();
  params.set("nome_arquivo", trimmed);
  const sep = urlBase.includes("?") ? "&" : "?";
  return `${urlBase}${sep}${params.toString()}`;
}

export function montarNomeArquivoDownloadVideoNarradoComTituloTranscribrothers(
  titulo: string,
  opcoes?: { legendado?: boolean; jobId?: string },
): string {
  const sanitizado = sanitizarNomeBaseArquivoDownloadTutorialTranscribrothers(titulo || "");
  const base =
    sanitizado ||
    `video-narrado-${(opcoes?.jobId || "").trim() || "sem-titulo"}`;
  return opcoes?.legendado ? `${base} legendado.mp4` : `${base}.mp4`;
}

export function dispararDownloadArquivoPorUrlComNomeTranscribrothers(
  url: string,
  nomeArquivo: string,
): void {
  const a = document.createElement("a");
  a.href = montarUrlDownloadVideoNarradoComNomeArquivoQueryTranscribrothers(url, nomeArquivo);
  a.download = nomeArquivo;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
}
