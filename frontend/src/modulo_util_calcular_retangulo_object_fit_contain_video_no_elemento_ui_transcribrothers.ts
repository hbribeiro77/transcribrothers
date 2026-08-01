/**
 * Retângulo da imagem dentro do `<video>` com `object-fit: contain`
 * (mesma caixa em que o navegador costuma desenhar as cues WebVTT).
 */
export function calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers(
  larguraElementoPx: number,
  alturaElementoPx: number,
  larguraMidiaPx: number,
  alturaMidiaPx: number,
): { left: number; top: number; width: number; height: number } {
  const cw = Math.max(0, larguraElementoPx);
  const ch = Math.max(0, alturaElementoPx);
  const mw = Math.max(0, larguraMidiaPx);
  const mh = Math.max(0, alturaMidiaPx);
  if (!(cw > 0 && ch > 0)) {
    return { left: 0, top: 0, width: 0, height: 0 };
  }
  if (!(mw > 0 && mh > 0)) {
    return { left: 0, top: 0, width: cw, height: ch };
  }
  const escala = Math.min(cw / mw, ch / mh);
  const width = mw * escala;
  const height = mh * escala;
  return {
    left: (cw - width) / 2,
    top: (ch - height) / 2,
    width,
    height,
  };
}
