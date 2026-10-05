import type { RespostaCatalogoModelosLitellmProxyApiTranscribrothers } from "./modulo_util_filtrar_catalogo_modelos_litellm_proxy_gaveta_configuracoes_transcribrothers.ts";

export async function obterCatalogoModelosLitellmNoProxyApiTranscribrothers(): Promise<RespostaCatalogoModelosLitellmProxyApiTranscribrothers> {
  const r = await fetch("/api/config/transcribrothers/modelos-litellm-no-proxy");
  if (!r.ok) {
    const t = await r.text();
    let detalhe = t;
    try {
      const j = JSON.parse(t) as { detail?: unknown };
      if (typeof j.detail === "string" && j.detail.trim()) {
        detalhe = j.detail.trim();
      }
    } catch {
      /* corpo não é JSON */
    }
    throw new Error(detalhe || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as RespostaCatalogoModelosLitellmProxyApiTranscribrothers;
}
