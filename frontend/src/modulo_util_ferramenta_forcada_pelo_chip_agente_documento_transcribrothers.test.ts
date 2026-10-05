import { describe, expect, it } from "vitest";
import {
  chipFerramentaChatAgenteDeveAparecerNaGavetaTranscribrothers,
  ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers,
  propostaFerramentaChatAgenteExigeConfirmacaoForteTranscribrothers,
  rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers,
  textoConfirmacaoPropostaFerramentaChatAgenteTranscribrothers,
} from "./modulo_util_ferramenta_forcada_pelo_chip_agente_documento_transcribrothers.ts";

describe("chip do Agente vira forcar_ferramenta", () => {
  it("sem chip não força ferramenta", () => {
    expect(
      ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers({
        modoPainel: "regeneracao_inteira",
        preset: null,
      }),
    ).toBeNull();
  });

  it("chip edição parcial / revisão profunda / sem vídeo", () => {
    expect(
      ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers({
        modoPainel: "edicao_parcial",
        preset: null,
      }),
    ).toBe("edicao_parcial");
    expect(
      ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers({
        modoPainel: "regeneracao_inteira",
        preset: "revisao_profunda",
      }),
    ).toBe("revisao_profunda");
    expect(
      ferramentaForcadaPeloChipAgenteDocumentoTranscribrothers({
        modoPainel: "regeneracao_inteira",
        preset: "sem_video",
      }),
    ).toBe("sem_video");
  });
});

describe("rótulo do botão da proposta", () => {
  it("fala o que vai acontecer, sem o nome interno da tool", () => {
    expect(rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers("edicao_parcial")).toBe(
      "Aplicar no documento",
    );
    expect(rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers("revisao_profunda")).toBe(
      "Revisar o documento a fundo",
    );
    expect(rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers("sem_video")).toBe(
      "Reescrever sem usar o vídeo",
    );
  });
});

describe("chips das tools na gaveta do Agente", () => {
  it("não mostra Sem vídeo, Revisão profunda nem Edição parcial", () => {
    expect(chipFerramentaChatAgenteDeveAparecerNaGavetaTranscribrothers("edicao_parcial")).toBe(
      false,
    );
    expect(chipFerramentaChatAgenteDeveAparecerNaGavetaTranscribrothers("revisao_profunda")).toBe(
      false,
    );
    expect(chipFerramentaChatAgenteDeveAparecerNaGavetaTranscribrothers("sem_video")).toBe(false);
  });
});

describe("confirmação forte das tools pesadas", () => {
  it("pede confirmação só na revisão a fundo e na reescrita sem vídeo", () => {
    expect(propostaFerramentaChatAgenteExigeConfirmacaoForteTranscribrothers("edicao_parcial")).toBe(
      false,
    );
    expect(
      propostaFerramentaChatAgenteExigeConfirmacaoForteTranscribrothers("revisao_profunda"),
    ).toBe(true);
    expect(propostaFerramentaChatAgenteExigeConfirmacaoForteTranscribrothers("sem_video")).toBe(
      true,
    );
  });

  it("explica o impacto em linguagem humana", () => {
    expect(textoConfirmacaoPropostaFerramentaChatAgenteTranscribrothers("revisao_profunda")).toBe(
      "Isso vai varrer o documento contra a transcrição e pode mudar várias seções. Quer rodar?",
    );
    expect(textoConfirmacaoPropostaFerramentaChatAgenteTranscribrothers("sem_video")).toBe(
      "Isso vai reescrever o documento só com texto e imagens, sem usar o vídeo. Quer continuar?",
    );
    expect(textoConfirmacaoPropostaFerramentaChatAgenteTranscribrothers("edicao_parcial")).toBe("");
  });
});
