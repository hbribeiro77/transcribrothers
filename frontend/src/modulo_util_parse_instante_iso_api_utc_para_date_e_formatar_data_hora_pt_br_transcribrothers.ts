/**
 * Datas vindas da API (histórico do tutorial, etc.) gravadas em UTC às vezes chegam sem sufixo `Z` ou offset.
 * O `Date` do JavaScript interpreta ISO sem fuso como hora **local**, o que no Brasil desloca ~3 h em relação ao instante UTC real.
 */

export function parseInstanteIsoApiUtcParaDateJavaScriptTranscribrothers(iso: string): Date {
  const brut = iso.trim().replace(" ", "T");
  if (!brut) return new Date(NaN);
  if (/[zZ]$|[+-]\d{2}:\d{2}$|[+-]\d{4}$/.test(brut)) {
    return new Date(brut);
  }
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?$/.test(brut)) {
    return new Date(`${brut}Z`);
  }
  return new Date(brut);
}

/** Rótulo curto para selects e listas (`pt-BR`, fuso do navegador). */
export function formatarInstanteIsoApiParaDataHoraPtBrLocalTranscribrothers(iso: string | null | undefined): string {
  if (iso == null || !String(iso).trim()) return "—";
  try {
    const d = parseInstanteIsoApiUtcParaDateJavaScriptTranscribrothers(String(iso));
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
  } catch {
    return String(iso);
  }
}
