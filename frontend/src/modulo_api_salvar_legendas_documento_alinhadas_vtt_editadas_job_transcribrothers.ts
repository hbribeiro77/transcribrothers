export type CueLegendaDocumentoAlinhadaEditadaApiTranscribrothers = {
  inicio_segundos: number;
  fim_segundos: number;
  texto: string;
};

export type RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers = {
  ok: boolean;
  nome_arquivo: string;
  url_asset: string;
  quantidade_cues: number;
};

export async function salvarLegendasDocumentoAlinhadasVttEditadasJobApiTranscribrothers(
  jobId: string,
  cues: CueLegendaDocumentoAlinhadaEditadaApiTranscribrothers[],
): Promise<RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/legendas-documento-alinhadas`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cues }),
  });
  if (!r.ok) {
    const t = await r.text();
    try {
      const j = JSON.parse(t) as { detail?: unknown };
      if (typeof j.detail === "string" && j.detail.trim()) {
        throw new Error(j.detail.trim());
      }
    } catch (e) {
      if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
    }
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as RespostaSalvarLegendasDocumentoAlinhadasVttEditadasJobTranscribrothers;
}
