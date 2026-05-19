/**
 * Monta texto legível da transcrição a partir de `steps_json.regeneracao_tutorial_snapshot`
 * (mesma fonte usada na regeneração do tutorial).
 */

function formatarSegundosRotuloTranscricaoTranscribrothers(seg: number): string {
  const s = Number.isFinite(seg) ? Math.max(0, seg) : 0;
  const m = Math.floor(s / 60);
  const r = Math.floor(s % 60);
  return `${m}:${String(r).padStart(2, "0")}`;
}

export function montarTextoPlanoTranscricaoOriginalAPartirDeSnapshotJobTutorialTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): string | null {
  const snap = steps?.regeneracao_tutorial_snapshot;
  if (!snap || typeof snap !== "object") return null;
  const o = snap as Record<string, unknown>;
  const textoCompleto = typeof o.texto_completo === "string" ? o.texto_completo.trim() : "";
  const segs = o.segmentos;
  const linhas: string[] = [];
  const idioma = typeof o.idioma === "string" && o.idioma.trim() ? o.idioma.trim() : null;
  if (idioma) {
    linhas.push(`Idioma (detecção): ${idioma}`, "");
  }
  if (Array.isArray(segs) && segs.length > 0) {
    for (const seg of segs) {
      if (!seg || typeof seg !== "object") continue;
      const s = seg as Record<string, unknown>;
      const ini = Number(s.inicio_segundos);
      const fim = Number(s.fim_segundos);
      const tx = String(s.texto ?? "").trim();
      const a = Number.isFinite(ini) ? ini : 0;
      const b = Number.isFinite(fim) ? fim : 0;
      linhas.push(
        `[${formatarSegundosRotuloTranscricaoTranscribrothers(a)} – ${formatarSegundosRotuloTranscricaoTranscribrothers(b)}] ${tx}`,
      );
    }
    const blocoSegmentos = linhas.join("\n").trim();
    if (textoCompleto) {
      return (
        `--- Texto corrido (modelo / junção)\n\n${textoCompleto}\n\n--- Segmentos com tempos\n\n${blocoSegmentos}`
      );
    }
    return blocoSegmentos || null;
  }
  return textoCompleto || null;
}
