export function consumirEventosSseBufferChatAskAgenteTranscribrothers(buffer: string): {
  eventos: Record<string, unknown>[];
  resto: string;
} {
  const eventos: Record<string, unknown>[] = [];
  let restante = buffer;
  while (true) {
    const separador = restante.indexOf("\n\n");
    if (separador < 0) break;
    const bloco = restante.slice(0, separador);
    restante = restante.slice(separador + 2);
    for (const linha of bloco.split("\n")) {
      const cortada = linha.trim();
      if (!cortada.startsWith("data:")) continue;
      const cru = cortada.slice(5).trim();
      if (!cru) continue;
      try {
        const parsed = JSON.parse(cru) as unknown;
        if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
          eventos.push(parsed as Record<string, unknown>);
        }
      } catch {
        /* evento incompleto ou não-JSON */
      }
    }
  }
  return { eventos, resto: restante };
}
