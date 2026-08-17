import { describe, expect, it } from "vitest";

import type { JanelaVideoCueLocalUiTranscribrothers } from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import {
  montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers,
  resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers,
} from "./modulo_util_resolver_url_audio_narracao_cue_trecho_original_ui_transcribrothers.ts";

function janelaBase(
  parcial: Partial<JanelaVideoCueLocalUiTranscribrothers> = {},
): JanelaVideoCueLocalUiTranscribrothers {
  return {
    inicioVideoSegundos: 0,
    fimVideoSegundos: 2,
    temWav: false,
    urlWav: "",
    ...parcial,
  };
}

describe("resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers", () => {
  it("usa prévia do editor quando não há WAV gravado", () => {
    const url = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
      janelaBase({ temWav: false }),
      0,
      { 0: "blob:http://local/previa" },
    );
    expect(url).toBe("blob:http://local/previa");
  });

  it("prefere prévia do editor ao WAV do job", () => {
    const url = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
      janelaBase({ temWav: true, urlWav: "/jobs/1/wav/0.wav" }),
      1,
      { 1: "blob:http://local/nova" },
    );
    expect(url).toBe("blob:http://local/nova");
  });

  it("cai no WAV do job sem prévia", () => {
    const url = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
      janelaBase({ temWav: true, urlWav: "/jobs/1/wav/0.wav" }),
      0,
      {},
    );
    expect(url).toBe("/jobs/1/wav/0.wav");
  });

  it("retorna null com semNarracao mesmo com prévia", () => {
    const url = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
      janelaBase({ semNarracao: true, temWav: true, urlWav: "/x.wav" }),
      0,
      { 0: "blob:y" },
    );
    expect(url).toBeNull();
  });
});

describe("montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers", () => {
  it("não altera blob URL", () => {
    expect(montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers("blob:abc")).toBe("blob:abc");
  });

  it("adiciona cache-bust em URL http", () => {
    const src = montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers("/jobs/1/a.wav");
    expect(src.startsWith("/jobs/1/a.wav?")).toBe(true);
    expect(src).toMatch(/[?&]v=\d+/);
  });
});
