/** API do painel de debug: cache de segmentos do vídeo narrado. */

export type SegmentosCacheDiscoDebugApiTranscribrothers = {
  nome_pasta: string;
  pasta_existe: boolean;
  quantidade_mp4: number;
  bytes_pasta: number;
  tem_cache_segmentos: boolean;
};

export type UltimoMuxCacheSegmentosDebugApiTranscribrothers = {
  hits_cache: number | null;
  total_segmentos: number | null;
  fase_mux: string | null;
  paralelismo: number | null;
  resolucao: string | null;
  fps: number | null;
  modo_montagem: string | null;
  gerado_em: string | null;
  pipeline_fase: string | null;
};

export type EdicoesModalDebugApiTranscribrothers = {
  origem_corrida: string | null;
  cues_sujas: number | null;
  wavs_reusados: number | null;
  pipeline_fase: string | null;
  mux_hits_cache: number | null;
  mux_total_segmentos: number | null;
};

export type PayloadDebugCacheSegmentosVideoNarradoApiTranscribrothers = {
  segmentos: SegmentosCacheDiscoDebugApiTranscribrothers;
  cache_bytes_total_regeneravel: number;
  pastas_cache_regeneravel: string[];
  ultimo_mux: UltimoMuxCacheSegmentosDebugApiTranscribrothers | null;
  edicoes_modal: EdicoesModalDebugApiTranscribrothers | null;
};

export async function obterDebugCacheSegmentosVideoNarradoJobApiTranscribrothers(
  jobId: string,
): Promise<PayloadDebugCacheSegmentosVideoNarradoApiTranscribrothers> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/debug-cache-segmentos-video-narrado`,
  );
  if (!r.ok) {
    const texto = await r.text().catch(() => "");
    throw new Error(texto || `Falha ao carregar debug de cache (${r.status}).`);
  }
  return (await r.json()) as PayloadDebugCacheSegmentosVideoNarradoApiTranscribrothers;
}
