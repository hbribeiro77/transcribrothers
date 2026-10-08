import { describe, expect, it } from "vitest";
import { mesclarHistoricoServidorPreservandoMensagensLocaisEmVooChatAskAgenteTranscribrothers } from "./modulo_util_mesclar_historico_servidor_preservando_mensagens_locais_em_voo_chat_ask_agente_transcribrothers.ts";

describe("preservar turno local em voo ao recarregar histórico", () => {
  it("mantém a bolha do usuário local se o servidor ainda não a devolveu", () => {
    const mesclado = mesclarHistoricoServidorPreservandoMensagensLocaisEmVooChatAskAgenteTranscribrothers({
      historicoServidor: [
        { id: "srv-1", papel: "agente", texto: "Sugestão anterior." },
      ],
      mensagensLocais: [
        { id: "srv-1", papel: "agente", texto: "Sugestão anterior." },
        { id: "agente-usuario-local-9", papel: "usuario", texto: "pode aplicar" },
        { id: "agente-assistente-stream-9", papel: "agente", texto: "", estado: "escrevendo" },
      ],
    });
    expect(mesclado.map((item) => item.id)).toEqual([
      "srv-1",
      "agente-usuario-local-9",
      "agente-assistente-stream-9",
    ]);
  });

  it("não duplica a bolha do usuário quando o servidor já persistiu o mesmo texto", () => {
    const mesclado = mesclarHistoricoServidorPreservandoMensagensLocaisEmVooChatAskAgenteTranscribrothers({
      historicoServidor: [
        { id: "t0-0-usuario", papel: "usuario", texto: "pode aplicar" },
        { id: "t1-1-agente", papel: "agente", texto: "Confirmado. Vou aplicar agora." },
      ],
      mensagensLocais: [
        { id: "agente-usuario-local-9", papel: "usuario", texto: "pode aplicar" },
        {
          id: "agente-assistente-stream-9",
          papel: "agente",
          texto: "Confirmado. Vou aplicar agora.",
          estado: "escrevendo",
        },
      ],
    });
    expect(mesclado.map((item) => `${item.papel}:${item.texto}`)).toEqual([
      "usuario:pode aplicar",
      "agente:Confirmado. Vou aplicar agora.",
    ]);
  });
});
