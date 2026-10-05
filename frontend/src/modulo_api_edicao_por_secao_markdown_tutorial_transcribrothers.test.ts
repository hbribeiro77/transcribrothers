import { afterEach, describe, expect, it, vi } from "vitest";
import { pedirRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers } from "./modulo_api_edicao_por_secao_markdown_tutorial_transcribrothers.ts";

describe("API edição por seção", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("POST regenerate-markdown-section envia edição cirúrgica e PNGs do chat", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ id: "job-1" }),
      text: async () => "{}",
    }));
    vi.stubGlobal("fetch", fetchMock);
    await pedirRegeneracaoSecaoMarkdownTutorialJobApiTranscribrothers("job-1", {
      tituloSecaoHeading: "O que foi discutido",
      instrucoesRevisor: "Aprofunde Assistido Digital.",
      edicaoCirurgicaChatAgente: true,
      caminhosAssetsPngContextoFab: ["assets/tela_chat_758.png"],
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/jobs/job-1/regenerate-markdown-section",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          titulo_secao_heading: "O que foi discutido",
          indice_secao: null,
          instrucoes_revisor: "Aprofunde Assistido Digital.",
          litellm_model: null,
          modo_escopo_edicao: "trecho_local",
          trecho_ancora: null,
          interpretar_escopo_automaticamente: false,
          edicao_cirurgica_chat_agente: true,
          propostas: null,
          caminhos_assets_png_contexto_fab: ["assets/tela_chat_758.png"],
          textos_contexto_fab: null,
        }),
      }),
    );
  });
});
