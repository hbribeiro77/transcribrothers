/**
 * Ao trocar a fonte de tela de uma cue, os tempos absolutos da origem anterior
 * (ex.: 6:16–6:47 na entrada) não fazem sentido no vídeo novo (ex.: 12s).
 * Recalcula uma janela válida a partir de 0.
 */

import { normalizarIdFonteVideoUiTranscribrothers } from "./modulo_api_biblioteca_midias_tela_job_transcribrothers.ts";

const FOLGA_MIN_JANELA_SEGUNDOS = 0.05;

export type EntradaCalcularJanelaAposTrocaFonteMidiaTelaUiTranscribrothers = {
  idFonteAnterior: string | null | undefined;
  idFonteNova: string | null | undefined;
  inicioVideoSegundos: number;
  fimVideoSegundos: number;
  /** Duração do slot da cue na timeline (fim − início). */
  duracaoCueTimelineSegundos: number;
  /** Duração conhecida do arquivo da nova fonte (ffprobe / manifesto). */
  duracaoFonteNovaSegundos?: number | null;
};

export type ResultadoCalcularJanelaAposTrocaFonteMidiaTelaUiTranscribrothers = {
  mudouFonte: boolean;
  inicioVideoSegundos: number;
  fimVideoSegundos: number;
};

export function calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers(
  entrada: EntradaCalcularJanelaAposTrocaFonteMidiaTelaUiTranscribrothers,
): ResultadoCalcularJanelaAposTrocaFonteMidiaTelaUiTranscribrothers {
  const idAnt = normalizarIdFonteVideoUiTranscribrothers(entrada.idFonteAnterior);
  const idNova = normalizarIdFonteVideoUiTranscribrothers(entrada.idFonteNova);
  if (idAnt === idNova) {
    return {
      mudouFonte: false,
      inicioVideoSegundos: Math.max(0, entrada.inicioVideoSegundos),
      fimVideoSegundos: Math.max(
        FOLGA_MIN_JANELA_SEGUNDOS,
        entrada.fimVideoSegundos,
      ),
    };
  }

  const durAnterior = Math.max(
    FOLGA_MIN_JANELA_SEGUNDOS,
    Number(entrada.fimVideoSegundos) - Number(entrada.inicioVideoSegundos),
  );
  const durCue = Math.max(FOLGA_MIN_JANELA_SEGUNDOS, Number(entrada.duracaoCueTimelineSegundos) || 0);
  const durFonte =
    entrada.duracaoFonteNovaSegundos != null && Number(entrada.duracaoFonteNovaSegundos) > 0
      ? Number(entrada.duracaoFonteNovaSegundos)
      : Number.POSITIVE_INFINITY;

  const fim = Math.min(durAnterior, durCue, durFonte);
  return {
    mudouFonte: true,
    inicioVideoSegundos: 0,
    fimVideoSegundos: Math.max(FOLGA_MIN_JANELA_SEGUNDOS, fim),
  };
}
