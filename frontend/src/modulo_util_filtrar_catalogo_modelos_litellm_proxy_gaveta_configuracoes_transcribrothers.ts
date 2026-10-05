export type ItemCatalogoModeloLitellmProxyTranscribrothers = {
  id: string;
  owned_by: string;
  categoria: string;
  util_para_tutorial: boolean;
  na_allowlist: boolean;
};

export type RespostaCatalogoModelosLitellmProxyApiTranscribrothers = {
  modelos: ItemCatalogoModeloLitellmProxyTranscribrothers[];
  allowlist_ausente_no_proxy: string[];
};

const ROTULOS_CATEGORIA_CATALOGO_MODELO_LITELLM_TRANSCRIBROTHERS: Record<string, string> = {
  chat: "Tutorial / chat",
  tts: "TTS",
  stt: "STT",
  embedding: "Embedding",
  rerank: "Rerank",
  codigo: "Código",
  especialidade: "Especialidade",
  alias: "Alias",
};

export function rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers(categoria: string): string {
  const chave = (categoria || "").trim().toLowerCase();
  return ROTULOS_CATEGORIA_CATALOGO_MODELO_LITELLM_TRANSCRIBROTHERS[chave] || categoria;
}

export function filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers(
  itens: ItemCatalogoModeloLitellmProxyTranscribrothers[],
  soUteisParaTutorial: boolean,
): ItemCatalogoModeloLitellmProxyTranscribrothers[] {
  const base = soUteisParaTutorial ? itens.filter((i) => i.util_para_tutorial) : [...itens];
  return base.sort((a, b) => {
    if (a.na_allowlist !== b.na_allowlist) {
      return a.na_allowlist ? 1 : -1;
    }
    return a.id.localeCompare(b.id, "pt-BR");
  });
}
