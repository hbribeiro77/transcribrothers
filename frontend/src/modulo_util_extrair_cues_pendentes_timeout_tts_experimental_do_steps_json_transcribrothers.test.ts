import { describe, expect, it } from "vitest";
import {
  extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers,
  jobAguardandoResolucaoTtsTimeoutExperimentalTranscribrothers,
} from "./modulo_util_extrair_cues_pendentes_timeout_tts_experimental_do_steps_json_transcribrothers.ts";

describe("extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers", () => {
  it("retorna vazio sem a chave", () => {
    expect(extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers({})).toEqual([]);
    expect(extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers(null)).toEqual([]);
  });

  it("extrai cues válidas e ignora inválidas", () => {
    const out = extrairCuesPendentesTimeoutTtsExperimentalDoStepsJsonTranscribrothers({
      video_narrado_tts_cues_pendentes_timeout: [
        {
          indice: 2,
          indice_cue: 3,
          texto: "Validação do nome social",
          voz: "Kore",
          motivo: "timeout",
        },
        { texto: "sem indice" },
        null,
      ],
    });
    expect(out).toHaveLength(1);
    expect(out[0]).toEqual({
      indice: 2,
      indiceCue: 3,
      texto: "Validação do nome social",
      voz: "Kore",
      motivo: "timeout",
    });
  });

  it("detecta fase de aguardo", () => {
    expect(
      jobAguardandoResolucaoTtsTimeoutExperimentalTranscribrothers({
        pipeline_fase: "video_narrado_aguardando_resolucao_tts_timeout",
      }),
    ).toBe(true);
    expect(
      jobAguardandoResolucaoTtsTimeoutExperimentalTranscribrothers({
        pipeline_fase: "video_narrado_concluido",
      }),
    ).toBe(false);
  });
});
