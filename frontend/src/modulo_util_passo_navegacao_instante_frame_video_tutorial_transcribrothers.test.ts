import { describe, expect, it } from "vitest";
import {
  PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
  instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers,
} from "./modulo_util_passo_navegacao_instante_frame_video_tutorial_transcribrothers.ts";

describe("passo ‹ › do frame no vídeo", () => {
  it("avança e recua o passo padrão sem passar de 0 nem da duração", () => {
    expect(PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS).toBe(0.4);
    expect(
      instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers({
        instanteAtual: 31.7,
        direcao: 1,
        duracaoVideoSegundos: 120,
      }),
    ).toBeCloseTo(32.1, 5);
    expect(
      instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers({
        instanteAtual: 0.2,
        direcao: -1,
        duracaoVideoSegundos: 120,
      }),
    ).toBe(0);
    expect(
      instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers({
        instanteAtual: 119.9,
        direcao: 1,
        duracaoVideoSegundos: 120,
      }),
    ).toBe(120);
  });
});
