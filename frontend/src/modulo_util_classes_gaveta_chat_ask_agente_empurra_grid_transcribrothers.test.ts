import { describe, expect, it } from "vitest";
import {
  classeGridPreviewRolagemDocumentoQuandoChatAbertoTranscribrothers,
  classesDockGavetaChatAskAgenteDocumentoTranscribrothers,
  classesPainelGavetaChatAskAgenteDocumentoTranscribrothers,
} from "./modulo_util_classes_gaveta_chat_ask_agente_empurra_grid_transcribrothers.ts";

describe("classes da gaveta do chat que empurra o grid", () => {
  it("mantém o dock no preview mesmo com a gaveta fechada, e marca quando está aberta", () => {
    expect(classesDockGavetaChatAskAgenteDocumentoTranscribrothers(false)).toBe(
      "tb-chat-ask-agente-dock-wrapper",
    );
    expect(classesDockGavetaChatAskAgenteDocumentoTranscribrothers(true)).toBe(
      "tb-chat-ask-agente-dock-wrapper tb-chat-ask-agente-dock-wrapper--aberta",
    );
  });

  it("marca o grid para rolar o documento ao lado do Markdown quando o chat está aberto", () => {
    expect(classeGridPreviewRolagemDocumentoQuandoChatAbertoTranscribrothers(false)).toBe("");
    expect(classeGridPreviewRolagemDocumentoQuandoChatAbertoTranscribrothers(true)).toBe(
      "tb-grid-preview--rolagem-documento",
    );
  });

  it("marca o painel aberto para a animação de entrada", () => {
    expect(
      classesPainelGavetaChatAskAgenteDocumentoTranscribrothers({
        aberta: false,
        projetoEmBranco: false,
        arrastando: false,
        processando: false,
      }),
    ).toBe("tb-chat-ask-agente-painel tb-chat-ask-agente-gaveta");
    expect(
      classesPainelGavetaChatAskAgenteDocumentoTranscribrothers({
        aberta: true,
        projetoEmBranco: true,
        arrastando: true,
        processando: true,
      }),
    ).toBe(
      [
        "tb-chat-ask-agente-painel",
        "tb-chat-ask-agente-gaveta",
        "tb-chat-ask-agente-painel--aberta",
        "tb-fab-regen-panel--chat-projeto-em-branco",
        "tb-fab-regen-panel--arrastando-arquivo",
        "tb-fab-regen-panel--processando-anexo",
      ].join(" "),
    );
  });
});
