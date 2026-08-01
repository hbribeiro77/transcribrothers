import { describe, expect, it } from "vitest";
import { calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers } from "./modulo_util_obter_duracao_segundos_arquivo_audio_por_url_navegador_transcribrothers.ts";

describe("calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers", () => {
  it("retorna null sem duração de áudio", () => {
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(null, 3)).toBeNull();
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(undefined, 3)).toBeNull();
  });

  it("retorna ~100% quando áudio e cue têm a mesma duração", () => {
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(2.5, 2.5)).toBeCloseTo(100);
  });

  it("retorna menos de 100% quando a fala é mais curta que a cue", () => {
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(1.5, 3)).toBeCloseTo(50);
  });

  it("pode passar de 100% quando a fala é mais longa que a cue", () => {
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(4, 2)).toBeCloseTo(200);
  });

  it("retorna null se a duração da cue for inválida", () => {
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(1, 0)).toBeNull();
    expect(calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(1, -1)).toBeNull();
  });
});
