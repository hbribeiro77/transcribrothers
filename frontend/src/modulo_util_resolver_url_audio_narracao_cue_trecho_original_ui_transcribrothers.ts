/**
 * Resolve URL de áudio TTS para o botão «Narração» na modal do vídeo original.
 * Prefere blob/prévia do editor; senão WAV gravado no job.
 */

import type { JanelaVideoCueLocalUiTranscribrothers } from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";

export function resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
  j: JanelaVideoCueLocalUiTranscribrothers | undefined,
  indice: number,
  urlsAudioNarracaoPorIndice: Record<number, string> | undefined,
): string | null {
  if (!j || j.semNarracao) return null;
  const doEditor = (urlsAudioNarracaoPorIndice?.[indice] || "").trim();
  if (doEditor) return doEditor;
  const doJob = (j.urlWav || "").trim();
  if (j.temWav && doJob) return doJob;
  return null;
}

/** Blob/data não levam cache-bust (quebraria a URL); HTTP/relativo sim. */
export function montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers(url: string): string {
  const u = url.trim();
  if (!u) return u;
  if (u.startsWith("blob:") || u.startsWith("data:")) return u;
  return `${u}${u.includes("?") ? "&" : "?"}v=${Date.now()}`;
}
