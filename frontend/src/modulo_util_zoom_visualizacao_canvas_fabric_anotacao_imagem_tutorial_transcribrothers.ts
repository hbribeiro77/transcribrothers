import { fabric } from "fabric";
import type { ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers } from "./tipos_ferramenta_anotacao_imagem_tutorial_transcribrothers.ts";

/** Padding total do host (12px por lado em `.tb-anotacao-canvas-host`). */
const PADDING_TOTAL_HOST_CANVAS_ANOTACAO_PX_TRANSCRIBROTHERS = 24;

export function calcularZoomAjustarAreaCanvasFabricAnotacaoImagemTutorialTranscribrothers(
  host: HTMLElement,
  larguraImagemPx: number,
  alturaImagemPx: number,
): number {
  const areaUtilLargura = Math.max(1, host.clientWidth - PADDING_TOTAL_HOST_CANVAS_ANOTACAO_PX_TRANSCRIBROTHERS);
  const areaUtilAltura = Math.max(1, host.clientHeight - PADDING_TOTAL_HOST_CANVAS_ANOTACAO_PX_TRANSCRIBROTHERS);
  return Math.min(areaUtilLargura / larguraImagemPx, areaUtilAltura / alturaImagemPx);
}

export function obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers(
  canvas: fabric.Canvas,
  evento: fabric.IEvent<Event>,
): { x: number; y: number } | null {
  if (!evento.e) return null;
  return canvas.getPointer(evento.e as MouseEvent);
}

function obterContainerCanvasFabricAnotacaoImagemTutorialTranscribrothers(
  canvas: fabric.Canvas,
): HTMLElement | null {
  return (canvas.lowerCanvasEl?.parentElement as HTMLElement | null) ?? null;
}

function restaurarDimensoesCssCanvasFabricTamanhoRealAnotacaoImagemTutorialTranscribrothers(
  canvas: fabric.Canvas,
  larguraImagemPx: number,
  alturaImagemPx: number,
): void {
  canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
  canvas.setDimensions(
    { width: `${larguraImagemPx}px`, height: `${alturaImagemPx}px` },
    { cssOnly: true },
  );
}

function limparEstilosEscalaVisualCanvasFabricAnotacaoImagemTutorialTranscribrothers(
  mount: HTMLElement,
  canvas: fabric.Canvas,
): void {
  mount.style.removeProperty("width");
  mount.style.removeProperty("height");
  mount.style.removeProperty("overflow");

  const container = obterContainerCanvasFabricAnotacaoImagemTutorialTranscribrothers(canvas);
  if (!container) return;

  container.style.removeProperty("width");
  container.style.removeProperty("height");
  container.style.removeProperty("transform");
  container.style.removeProperty("transform-origin");
}

export function aplicarModoZoomVisualizacaoCanvasFabricAnotacaoImagemTutorialTranscribrothers(
  canvas: fabric.Canvas,
  host: HTMLElement,
  mount: HTMLElement | null,
  modo: ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers,
  larguraImagemPx: number,
  alturaImagemPx: number,
): void {
  if (larguraImagemPx <= 0 || alturaImagemPx <= 0 || !mount) return;

  const container = obterContainerCanvasFabricAnotacaoImagemTutorialTranscribrothers(canvas);

  if (modo === "tamanhoReal") {
    limparEstilosEscalaVisualCanvasFabricAnotacaoImagemTutorialTranscribrothers(mount, canvas);
    restaurarDimensoesCssCanvasFabricTamanhoRealAnotacaoImagemTutorialTranscribrothers(
      canvas,
      larguraImagemPx,
      alturaImagemPx,
    );
    canvas.calcOffset();
    host.scrollLeft = 0;
    host.scrollTop = 0;
    canvas.requestRenderAll();
    return;
  }

  if (!container) return;

  const zoom = calcularZoomAjustarAreaCanvasFabricAnotacaoImagemTutorialTranscribrothers(
    host,
    larguraImagemPx,
    alturaImagemPx,
  );
  const larguraExibicaoPx = larguraImagemPx * zoom;
  const alturaExibicaoPx = alturaImagemPx * zoom;

  restaurarDimensoesCssCanvasFabricTamanhoRealAnotacaoImagemTutorialTranscribrothers(
    canvas,
    larguraImagemPx,
    alturaImagemPx,
  );

  container.style.width = `${larguraImagemPx}px`;
  container.style.height = `${alturaImagemPx}px`;
  container.style.transformOrigin = "0 0";
  container.style.transform = `scale(${zoom})`;

  mount.style.width = `${larguraExibicaoPx}px`;
  mount.style.height = `${alturaExibicaoPx}px`;
  mount.style.overflow = "hidden";

  canvas.calcOffset();
  host.scrollLeft = 0;
  host.scrollTop = 0;
  canvas.requestRenderAll();
}

/** Garante export PNG na resolução do backstore, independente do zoom visual. */
export function exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers(canvas: fabric.Canvas): string {
  const viewportSalvo = canvas.viewportTransform?.slice() ?? [1, 0, 0, 1, 0, 0];
  const precisaRestaurarViewport =
    viewportSalvo[0] !== 1 || viewportSalvo[3] !== 1 || viewportSalvo[4] !== 0 || viewportSalvo[5] !== 0;

  if (precisaRestaurarViewport) {
    canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
  }

  const dataUrl = canvas.toDataURL({ format: "png" });

  if (precisaRestaurarViewport) {
    canvas.setViewportTransform(viewportSalvo);
    canvas.requestRenderAll();
  }

  return dataUrl;
}
