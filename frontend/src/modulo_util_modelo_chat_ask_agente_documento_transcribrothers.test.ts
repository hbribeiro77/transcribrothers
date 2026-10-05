import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { modeloLitellmPareceTtsPeloSlugTranscribrothers } from "./modulo_api_gerar_narracao_tts_markdown_job_transcribrothers.ts";
import {
  escolherModeloChatAskAgenteDaListaDisponivelTranscribrothers,
  listarModelosChatAskAgenteDaListaDisponivelTranscribrothers,
  rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers,
} from "./modulo_util_modelo_chat_ask_agente_documento_transcribrothers.ts";

describe("modelo do chat Ask/Agente", () => {
  it("lista só slugs de chat, sem TTS", () => {
    expect(
      listarModelosChatAskAgenteDaListaDisponivelTranscribrothers([
        "gemini/gemini-2.5-flash",
        "gemini/gemini-2.5-flash-tts",
        "eleven_v4",
        "openai/gpt-4o-mini",
      ]),
    ).toEqual(["gemini/gemini-2.5-flash", "openai/gpt-4o-mini"]);
  });

  it("mostra o trecho curto do slug no botão", () => {
    expect(rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers("gemini/gemini-2.5-flash")).toBe(
      "gemini-2.5-flash",
    );
  });

  it("prefere o salvo se ainda for chat e estiver na lista; senão o primeiro chat", () => {
    const lista = ["gemini/gemini-2.5-flash", "openai/gpt-4o-mini", "gemini/gemini-2.5-flash-tts"];
    expect(
      escolherModeloChatAskAgenteDaListaDisponivelTranscribrothers(lista, "openai/gpt-4o-mini"),
    ).toBe("openai/gpt-4o-mini");
    expect(
      escolherModeloChatAskAgenteDaListaDisponivelTranscribrothers(lista, "gemini/gemini-2.5-flash-tts"),
    ).toBe("gemini/gemini-2.5-flash");
    expect(escolherModeloChatAskAgenteDaListaDisponivelTranscribrothers(lista, null)).toBe(
      "gemini/gemini-2.5-flash",
    );
    expect(modeloLitellmPareceTtsPeloSlugTranscribrothers("eleven_v4")).toBe(true);
  });
});

describe("persistência do modelo do chat no navegador", () => {
  const store = new Map<string, string>();

  beforeEach(() => {
    store.clear();
    vi.stubGlobal("window", {
      localStorage: {
        getItem: (chave: string) => store.get(chave) ?? null,
        setItem: (chave: string, valor: string) => {
          store.set(chave, valor);
        },
        clear: () => store.clear(),
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("grava e relê o slug escolhido", async () => {
    const {
      carregarModeloChatAskAgentePreferidoSalvoNoNavegadorTranscribrothers,
      salvarModeloChatAskAgentePreferidoNoNavegadorTranscribrothers,
    } = await import("./modulo_armazenamento_local_modelo_chat_ask_agente_preferido_navegador_transcribrothers.ts");
    expect(carregarModeloChatAskAgentePreferidoSalvoNoNavegadorTranscribrothers()).toBeNull();
    salvarModeloChatAskAgentePreferidoNoNavegadorTranscribrothers("gemini/gemini-2.5-flash");
    expect(carregarModeloChatAskAgentePreferidoSalvoNoNavegadorTranscribrothers()).toBe(
      "gemini/gemini-2.5-flash",
    );
  });
});
