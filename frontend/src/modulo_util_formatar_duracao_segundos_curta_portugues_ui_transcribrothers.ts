/** Formata duração em rótulo curto pt-BR: `12s`, `1m 05s`, `1h 02m`. */

export function formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(
  segundos: number | null | undefined,
): string {
  if (segundos == null || !Number.isFinite(segundos) || segundos < 0) return "";
  const total = Math.round(segundos);
  if (total < 60) return `${total}s`;
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) {
    return s > 0 || m > 0 ? `${h}h ${String(m).padStart(2, "0")}m` : `${h}h`;
  }
  return s > 0 ? `${m}m ${String(s).padStart(2, "0")}s` : `${m}m`;
}
