/**
 * Converte um instante na timeline narrada (slot da cue) para o instante
 * correspondente na janela do vídeo original, por proporção linear.
 * Usado no preview de recorte de tela sem remux.
 */
export function mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
  tempoTimelineSegundos: number,
  cueInicioSegundos: number,
  cueFimSegundos: number,
  janelaInicioSegundos: number,
  janelaFimSegundos: number,
): number {
  const iniCue = Math.max(0, cueInicioSegundos);
  const fimCue = Math.max(iniCue + 1e-6, cueFimSegundos);
  const iniJanela = Math.max(0, janelaInicioSegundos);
  const fimJanela = Math.max(iniJanela + 1e-6, janelaFimSegundos);
  const durCue = fimCue - iniCue;
  const durJanela = fimJanela - iniJanela;
  const t = Math.min(Math.max(tempoTimelineSegundos, iniCue), fimCue);
  const frac = (t - iniCue) / durCue;
  return iniJanela + frac * durJanela;
}

/**
 * Inverso: instante na janela do original → instante na timeline narrada da cue.
 * Usado para a barra de progresso “parecer” o MP4 gerado durante o preview.
 */
export function mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers(
  tempoJanelaSegundos: number,
  cueInicioSegundos: number,
  cueFimSegundos: number,
  janelaInicioSegundos: number,
  janelaFimSegundos: number,
): number {
  const iniCue = Math.max(0, cueInicioSegundos);
  const fimCue = Math.max(iniCue + 1e-6, cueFimSegundos);
  const iniJanela = Math.max(0, janelaInicioSegundos);
  const fimJanela = Math.max(iniJanela + 1e-6, janelaFimSegundos);
  const durCue = fimCue - iniCue;
  const durJanela = fimJanela - iniJanela;
  const t = Math.min(Math.max(tempoJanelaSegundos, iniJanela), fimJanela);
  const frac = (t - iniJanela) / durJanela;
  return iniCue + frac * durCue;
}

export function urlVideoEntradaJobParaPreviewUiTranscribrothers(jobId: string): string {
  return `/api/jobs/${encodeURIComponent(jobId)}/video`;
}

/** URL do player de preview conforme a fonte da cue (`entrada` ou id da biblioteca). */
export function urlVideoFonteTelaCueParaPreviewUiTranscribrothers(
  jobId: string,
  idFonteVideo?: string | null,
): string {
  const id = (idFonteVideo || "").trim();
  if (!id || id === "entrada") {
    return urlVideoEntradaJobParaPreviewUiTranscribrothers(jobId);
  }
  return `/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela/arquivo/${encodeURIComponent(id)}`;
}
