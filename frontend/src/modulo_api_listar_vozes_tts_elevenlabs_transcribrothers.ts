export type VozTtsElevenlabsUiTranscribrothers = {
  id: string;
  estilo: string;
  idioma: string;
  sotaque: string;
  locale: string;
  pt_br: boolean;
};

export async function listarVozesTtsElevenlabsApiTranscribrothers(): Promise<
  VozTtsElevenlabsUiTranscribrothers[]
> {
  const r = await fetch("/api/config/transcribrothers/vozes-tts-elevenlabs");
  if (!r.ok) {
    let detalhe = "";
    try {
      const j = (await r.json()) as { detail?: unknown };
      if (typeof j.detail === "string") detalhe = j.detail;
    } catch {
      try {
        detalhe = await r.text();
      } catch {
        detalhe = "";
      }
    }
    throw new Error(detalhe || `Erro HTTP ${r.status}`);
  }
  const raw = (await r.json()) as { vozes?: unknown };
  if (!Array.isArray(raw.vozes)) return [];
  return raw.vozes
    .map((item) => {
      if (!item || typeof item !== "object") return null;
      const o = item as {
        id?: unknown;
        estilo?: unknown;
        idioma?: unknown;
        sotaque?: unknown;
        locale?: unknown;
        pt_br?: unknown;
      };
      const id = String(o.id ?? "").trim();
      if (!id) return null;
      return {
        id,
        estilo: String(o.estilo ?? "").trim() || id,
        idioma: String(o.idioma ?? "").trim(),
        sotaque: String(o.sotaque ?? "").trim(),
        locale: String(o.locale ?? "").trim(),
        pt_br: o.pt_br === true,
      };
    })
    .filter((v): v is VozTtsElevenlabsUiTranscribrothers => v != null);
}
