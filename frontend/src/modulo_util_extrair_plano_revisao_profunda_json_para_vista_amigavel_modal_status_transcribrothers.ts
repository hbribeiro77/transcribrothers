/**
 * Converte `steps_json.revisao_profunda_plano_json` (string ou objeto) numa lista de tópicos
 * para exibição legível na modal de status (alternativa ao JSON bruto).
 */

export type ItemEvidenciaPlanoRevisaoProfundaVistaAmigavelTranscribrothers = {
  citacao: string;
  inicio_segundos?: number;
  fim_segundos?: number;
};

export type ItemTopicoPlanoRevisaoProfundaVistaAmigavelTranscribrothers = {
  id: string;
  titulo_secao: string;
  lacunas: string[];
  evidencias: ItemEvidenciaPlanoRevisaoProfundaVistaAmigavelTranscribrothers[];
  prioridade?: number;
};

function coagirStringTranscribrothers(v: unknown): string {
  if (typeof v === "string") return v.trim();
  if (typeof v === "number" && Number.isFinite(v)) return String(v);
  return "";
}

function coagirNumeroOpcionalTranscribrothers(v: unknown): number | undefined {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim()) {
    const n = Number.parseFloat(v.trim());
    if (Number.isFinite(n)) return n;
  }
  return undefined;
}

function mapearEvidenciasDeItemTopicoTranscribrothers(raw: Record<string, unknown>): ItemEvidenciaPlanoRevisaoProfundaVistaAmigavelTranscribrothers[] {
  const arr = raw.evidencias_transcricao;
  if (!Array.isArray(arr)) return [];
  const out: ItemEvidenciaPlanoRevisaoProfundaVistaAmigavelTranscribrothers[] = [];
  for (const e of arr) {
    if (!e || typeof e !== "object") continue;
    const o = e as Record<string, unknown>;
    const cit = coagirStringTranscribrothers(o.citacao);
    if (!cit) continue;
    out.push({
      citacao: cit,
      inicio_segundos: coagirNumeroOpcionalTranscribrothers(o.inicio_segundos),
      fim_segundos: coagirNumeroOpcionalTranscribrothers(o.fim_segundos),
    });
  }
  return out;
}

function mapearLacunasDeItemTopicoTranscribrothers(raw: Record<string, unknown>): string[] {
  const arr = raw.lacunas;
  if (!Array.isArray(arr)) return [];
  return arr
    .map((x) => (typeof x === "string" ? x.trim() : String(x ?? "").trim()))
    .filter(Boolean)
    .slice(0, 32);
}

/**
 * Devolve lista de tópicos ou `null` se não for possível interpretar o plano.
 */
export function extrairTopicosPlanoRevisaoProfundaParaVistaAmigavelDeStepsJsonTranscribrothers(
  raw: unknown,
): ItemTopicoPlanoRevisaoProfundaVistaAmigavelTranscribrothers[] | null {
  let obj: unknown;
  if (raw == null) return null;
  if (typeof raw === "string") {
    const t = raw.trim();
    if (!t) return null;
    try {
      obj = JSON.parse(t) as unknown;
    } catch {
      return null;
    }
  } else if (typeof raw === "object") {
    obj = raw;
  } else {
    return null;
  }
  if (!obj || typeof obj !== "object") return null;
  const topicosRaw = (obj as Record<string, unknown>).topicos;
  if (!Array.isArray(topicosRaw)) return null;

  const topicos: ItemTopicoPlanoRevisaoProfundaVistaAmigavelTranscribrothers[] = [];
  for (const item of topicosRaw) {
    if (!item || typeof item !== "object") continue;
    const o = item as Record<string, unknown>;
    const id = coagirStringTranscribrothers(o.id);
    const titulo = coagirStringTranscribrothers(o.titulo_secao);
    if (!id && !titulo) continue;
    const pr = o.prioridade;
    const prioridade =
      typeof pr === "number" && Number.isFinite(pr) ? Math.round(pr) : coagirNumeroOpcionalTranscribrothers(pr);
    topicos.push({
      id: id || "—",
      titulo_secao: titulo || id || "Tópico",
      lacunas: mapearLacunasDeItemTopicoTranscribrothers(o),
      evidencias: mapearEvidenciasDeItemTopicoTranscribrothers(o),
      prioridade: prioridade !== undefined ? Math.max(1, Math.min(9, prioridade)) : undefined,
    });
  }
  return topicos;
}
