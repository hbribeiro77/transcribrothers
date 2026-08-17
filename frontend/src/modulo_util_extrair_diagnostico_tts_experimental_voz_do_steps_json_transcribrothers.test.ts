import { describe, expect, it } from "vitest";
import { extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers } from "./modulo_util_extrair_diagnostico_tts_experimental_voz_do_steps_json_transcribrothers.ts";

describe("extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers", () => {
  it("retorna null sem o bloco experimental", () => {
    expect(extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers({})).toBeNull();
    expect(extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers(null)).toBeNull();
  });

  it("extrai puladas, falha e resumo_texto", () => {
    const out = extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers({
      video_narrado_tts_diagnostico_experimental: {
        perfil_tts: "experimental_voz",
        timeout_read_segundos: 30,
        quantidade_cues_total: 3,
        quantidade_cues_ok: 1,
        quantidade_cues_puladas: 1,
        quantidade_timeouts: 2,
        latencia_ok_ms_p50: 1200,
        latencia_ok_ms_max: 2000,
        cues_puladas: [
          {
            indice_cue: 2,
            texto_preview: "Remova o grupo",
            motivo: "choices_vazio",
            tentativas: 3,
            ultimo_erro: "sem choices",
            latencia_ms_ultima: 400,
          },
        ],
        falha: {
          indice_cue: 3,
          texto_preview: "Configure DNS",
          motivo: "timeout",
          tentativa: 3,
          erro_curto: "Timeout read 30s",
          latencia_ms: 30010,
        },
        resumo_texto: "DIAGNOSTICO TTS EXPERIMENTAL\n...",
      },
    });
    expect(out).not.toBeNull();
    expect(out!.timeoutReadSegundos).toBe(30);
    expect(out!.quantidadeTimeouts).toBe(2);
    expect(out!.cuesPuladas).toHaveLength(1);
    expect(out!.cuesPuladas[0].indiceCue).toBe(2);
    expect(out!.falha?.motivo).toBe("timeout");
    expect(out!.resumoTexto).toContain("DIAGNOSTICO TTS EXPERIMENTAL");
  });
});
