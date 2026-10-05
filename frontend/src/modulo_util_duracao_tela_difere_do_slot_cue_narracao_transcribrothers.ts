/** Chip «tela Xs» só quando a janela de origem diverge do slot narrado. */
export function duracaoTelaDifereDoSlotCueNarracaoTranscribrothers(
  duracaoSlotSegundos: number,
  duracaoTelaSegundos: number,
  toleranciaSegundos = 0.15,
): boolean {
  const slot = Number(duracaoSlotSegundos);
  const tela = Number(duracaoTelaSegundos);
  if (!Number.isFinite(slot) || !Number.isFinite(tela)) return false;
  return Math.abs(slot - tela) > toleranciaSegundos;
}
