import { describe, expect, it } from "vitest";
import { mensagemEhConfirmacaoExecutarPedidoChatAgenteTranscribrothers } from "./modulo_util_mensagem_confirmacao_executar_pedido_chat_agente_transcribrothers.ts";

describe("confirmação do Agente", () => {
  it("reconhece pode fazer / pode prosseguir e rejeita pedido novo", () => {
    expect(mensagemEhConfirmacaoExecutarPedidoChatAgenteTranscribrothers("beleza, pode fazer")).toBe(
      true,
    );
    expect(mensagemEhConfirmacaoExecutarPedidoChatAgenteTranscribrothers("pode prosseguir")).toBe(
      true,
    );
    expect(
      mensagemEhConfirmacaoExecutarPedidoChatAgenteTranscribrothers(
        "isso deve estar na transcrição",
      ),
    ).toBe(false);
  });
});
