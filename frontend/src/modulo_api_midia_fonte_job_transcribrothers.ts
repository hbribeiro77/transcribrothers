export type ItemMidiaFonteJobApiTranscribrothers = {
  id: string;
  rotulo: string;
  tipo: string;
  nome_arquivo: string;
  tamanho_bytes: number;
  url_download: string;
};

export type RespostaMidiaFonteJobApiTranscribrothers = {
  itens: ItemMidiaFonteJobApiTranscribrothers[];
  cache_bytes: number;
  pastas_cache?: string[];
};

async function _lerErroHttpTranscribrothers(r: Response): Promise<string> {
  const texto = await r.text();
  try {
    const j = JSON.parse(texto) as { detail?: unknown };
    if (typeof j.detail === "string" && j.detail.trim()) return j.detail.trim();
  } catch {
    /* texto bruto */
  }
  return texto || `Falha HTTP ${r.status}.`;
}

export async function listarMidiaFonteJobApiTranscribrothers(
  jobId: string,
): Promise<RespostaMidiaFonteJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/midia-fonte`);
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as RespostaMidiaFonteJobApiTranscribrothers;
}

export async function limparCacheMidiaFonteJobApiTranscribrothers(
  jobId: string,
): Promise<{ ok: boolean; cache_bytes: number }> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/midia-fonte/limpar-cache`, {
    method: "POST",
  });
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as { ok: boolean; cache_bytes: number };
}
