/**
 * Se a janela da cue ultrapassa a duração real do vídeo da fonte
 * (tempos herdados de outra origem), recoloca em 0…min(duração anterior, mídia).
 */

const FOLGA_MIN_JANELA_SEGUNDOS = 0.05;

export type ResultadoClampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers = {
  alterou: boolean;
  inicioVideoSegundos: number;
  fimVideoSegundos: number;
};

export function clampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers(
  inicioVideoSegundos: number,
  fimVideoSegundos: number,
  duracaoFonteSegundos: number,
): ResultadoClampJanelaVideoCueDentroDaDuracaoFonteUiTranscribrothers {
  const durFonte = Number(duracaoFonteSegundos);
  if (!(durFonte > 0) || !Number.isFinite(durFonte)) {
    return {
      alterou: false,
      inicioVideoSegundos: Math.max(0, inicioVideoSegundos),
      fimVideoSegundos: Math.max(FOLGA_MIN_JANELA_SEGUNDOS, fimVideoSegundos),
    };
  }

  const ini = Math.max(0, Number(inicioVideoSegundos) || 0);
  const fim = Math.max(ini + FOLGA_MIN_JANELA_SEGUNDOS, Number(fimVideoSegundos) || 0);
  if (ini < durFonte && fim <= durFonte + 1e-3) {
    return { alterou: false, inicioVideoSegundos: ini, fimVideoSegundos: fim };
  }

  const durAnt = Math.max(FOLGA_MIN_JANELA_SEGUNDOS, fim - ini);
  const novoFim = Math.min(durAnt, durFonte);
  return {
    alterou: true,
    inicioVideoSegundos: 0,
    fimVideoSegundos: Math.max(FOLGA_MIN_JANELA_SEGUNDOS, novoFim),
  };
}
