import { describe, expect, it } from "vitest";

import {
  filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers,
  rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers,
  type ItemCatalogoModeloLitellmProxyTranscribrothers,
} from "./modulo_util_filtrar_catalogo_modelos_litellm_proxy_gaveta_configuracoes_transcribrothers.ts";

function item(
  parcial: Partial<ItemCatalogoModeloLitellmProxyTranscribrothers> & Pick<ItemCatalogoModeloLitellmProxyTranscribrothers, "id">,
): ItemCatalogoModeloLitellmProxyTranscribrothers {
  return {
    owned_by: "openai",
    categoria: "chat",
    util_para_tutorial: true,
    na_allowlist: false,
    ...parcial,
  };
}

describe("filtrar catálogo LiteLLM na gaveta", () => {
  const itens: ItemCatalogoModeloLitellmProxyTranscribrothers[] = [
    item({ id: "azure_ai/embed-v-4-0", categoria: "embedding", util_para_tutorial: false }),
    item({ id: "gemini/gemini-3.8-flash" }),
    item({ id: "azure_ai/claude-sonnet-4-6", na_allowlist: true }),
    item({ id: "gemini/gemini-2.5-flash-preview-tts", categoria: "tts", util_para_tutorial: false }),
  ];

  it("com só úteis, oculta embed/tts e coloca quem ainda não está na allowlist primeiro", () => {
    const r = filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers(itens, true);
    expect(r.map((x) => x.id)).toEqual([
      "gemini/gemini-3.8-flash",
      "azure_ai/claude-sonnet-4-6",
    ]);
  });

  it("sem filtro, mostra todos ordenados: fora da allowlist, depois id", () => {
    const r = filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers(itens, false);
    expect(r.map((x) => x.id)).toEqual([
      "azure_ai/embed-v-4-0",
      "gemini/gemini-2.5-flash-preview-tts",
      "gemini/gemini-3.8-flash",
      "azure_ai/claude-sonnet-4-6",
    ]);
  });

  it("rotula categorias em pt-BR", () => {
    expect(rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers("chat")).toBe("Tutorial / chat");
    expect(rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers("tts")).toBe("TTS");
    expect(rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers("embedding")).toBe("Embedding");
    expect(rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers("alias")).toBe("Alias");
  });
});
