function formatarTimestampSegundosParaMmssTranscribrothers(segundos: number): string {
  const total = Math.round(Math.max(0, segundos));
  const s = total % 60;
  const m = Math.floor(total / 60) % 60;
  const h = Math.floor(total / 3600);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers(
  instanteSegundos: number,
): string {
  return `Frame anexado em ${formatarTimestampSegundosParaMmssTranscribrothers(instanteSegundos)}.`;
}
