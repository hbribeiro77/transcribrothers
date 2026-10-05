/**
 * Copia um blob PNG para a área de transferência via Clipboard API.
 * Exige contexto seguro (HTTPS/localhost) e permissão do navegador.
 */
export async function copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers(
  blob: Blob,
): Promise<void> {
  if (typeof navigator === "undefined" || !navigator.clipboard?.write) {
    throw new Error("Este navegador não permite copiar imagens para a área de transferência.");
  }
  if (typeof ClipboardItem === "undefined") {
    throw new Error("Este navegador não permite copiar imagens para a área de transferência.");
  }

  const tipo = blob.type && blob.type.startsWith("image/") ? blob.type : "image/png";
  const item = new ClipboardItem({ [tipo]: blob });
  await navigator.clipboard.write([item]);
}

export async function converterDataUrlPngParaBlobTranscribrothers(dataUrl: string): Promise<Blob> {
  const resposta = await fetch(dataUrl);
  return resposta.blob();
}
