import { describe, expect, it } from "vitest";
import {
  montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers,
  rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers,
} from "./modulo_util_trilha_passos_navegacao_frame_video_ancorada_no_documento_tutorial_transcribrothers.ts";

describe("trilha de passos ‹ › ancorada no frame do tutorial", () => {
  it("com você no documento, o traço do meio é casa e atual ao mesmo tempo", () => {
    const trilha = montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers({
      instanteAtualSegundos: 31.7,
      instanteDocumentoSegundos: 31.7,
      duracaoVideoSegundos: 120,
    });
    expect(trilha.tracos).toHaveLength(11);
    const meio = trilha.tracos[5];
    expect(meio?.ehAtual).toBe(true);
    expect(meio?.ehDocumento).toBe(true);
    expect(meio?.instanteSegundos).toBeCloseTo(31.7, 5);
    expect(trilha.documentoForaDaJanelaNaPonta).toBeNull();
    expect(trilha.tracos[0]?.instanteSegundos).toBeCloseTo(29.7, 5);
    expect(trilha.tracos[10]?.instanteSegundos).toBeCloseTo(33.7, 5);
  });

  it("perto da casa o documento não se mexe e o amarelo anda", () => {
    const trilha = montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers({
      instanteAtualSegundos: 32.5,
      instanteDocumentoSegundos: 31.7,
      duracaoVideoSegundos: 120,
    });
    expect(trilha.tracos[5]?.ehDocumento).toBe(true);
    expect(trilha.tracos[5]?.ehAtual).toBe(false);
    expect(trilha.tracos[7]?.ehAtual).toBe(true);
    expect(trilha.tracos[7]?.ehDocumento).toBe(false);
    expect(trilha.tracos[5]?.instanteSegundos).toBeCloseTo(31.7, 5);
    expect(trilha.tracos[7]?.instanteSegundos).toBeCloseTo(32.5, 5);
  });

  it("se sair dos ±5 a janela desliza e a casa gruda na ponta quando ainda cabe", () => {
    const trilha = montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers({
      instanteAtualSegundos: 31.7 + 8 * 0.4,
      instanteDocumentoSegundos: 31.7,
      duracaoVideoSegundos: 120,
    });
    expect(trilha.tracos[10]?.ehAtual).toBe(true);
    expect(trilha.tracos[2]?.ehDocumento).toBe(true);
    expect(trilha.documentoForaDaJanelaNaPonta).toBeNull();
  });

  it("se a casa ficar longe demais, pina a ponta e não finge que o traço da beira é o documento", () => {
    const trilha = montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers({
      instanteAtualSegundos: 31.7 + 15 * 0.4,
      instanteDocumentoSegundos: 31.7,
      duracaoVideoSegundos: 120,
    });
    expect(trilha.tracos[10]?.ehAtual).toBe(true);
    expect(trilha.tracos.every((t) => !t.ehDocumento)).toBe(true);
    expect(trilha.documentoForaDaJanelaNaPonta).toBe("esquerda");
  });

  it("o rótulo diz se o traço é você, o tutorial ou os dois", () => {
    expect(
      rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers({
        instanteSegundos: 31.7,
        ehAtual: true,
        ehDocumento: true,
      }),
    ).toMatch(/tutorial/i);
    expect(
      rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers({
        instanteSegundos: 32.1,
        ehAtual: true,
        ehDocumento: false,
      }),
    ).toMatch(/olhando/i);
  });
});
