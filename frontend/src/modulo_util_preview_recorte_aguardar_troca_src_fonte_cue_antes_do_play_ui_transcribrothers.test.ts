import { describe, expect, it } from "vitest";
import {
  previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers,
} from "./modulo_util_preview_recorte_aguardar_troca_src_fonte_cue_antes_do_play_ui_transcribrothers.ts";

describe("previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers", () => {
  it("se preview inativo, não precisa aguardar (ativa e o effect dispara)", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: false,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/biblioteca-midias-tela/arquivo/m1",
      }),
    ).toBe(false);
  });

  it("se preview ativo e mesma URL, toca na hora (não aguarda)", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: true,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/video",
      }),
    ).toBe(false);
  });

  it("se preview ativo e URL de fonte muda, aguarda o effect após troca de src", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: true,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/biblioteca-midias-tela/arquivo/m1",
      }),
    ).toBe(true);
  });
});
