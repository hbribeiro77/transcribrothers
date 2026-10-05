export type RetanguloRecorteCanvasAnotacaoImagemTutorialTranscribrothers = {
  left: number;
  top: number;
  width: number;
  height: number;
};

const TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS = 6;

/**
 * Normaliza o retângulo de recorte (ordem dos cantos) e limita às dimensões do canvas.
 * Devolve null se a área for menor que o mínimo útil.
 */
export function calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  larguraCanvasPx: number,
  alturaCanvasPx: number,
): RetanguloRecorteCanvasAnotacaoImagemTutorialTranscribrothers | null {
  if (larguraCanvasPx <= 0 || alturaCanvasPx <= 0) return null;

  const leftBruto = Math.min(x1, x2);
  const topBruto = Math.min(y1, y2);
  const rightBruto = Math.max(x1, x2);
  const bottomBruto = Math.max(y1, y2);

  const left = Math.max(0, Math.min(larguraCanvasPx, leftBruto));
  const top = Math.max(0, Math.min(alturaCanvasPx, topBruto));
  const right = Math.max(0, Math.min(larguraCanvasPx, rightBruto));
  const bottom = Math.max(0, Math.min(alturaCanvasPx, bottomBruto));

  const width = right - left;
  const height = bottom - top;

  if (
    width < TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS ||
    height < TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS
  ) {
    return null;
  }

  return { left, top, width, height };
}

export { TAMANHO_MINIMO_RECORTE_PX_TRANSCRIBROTHERS };
