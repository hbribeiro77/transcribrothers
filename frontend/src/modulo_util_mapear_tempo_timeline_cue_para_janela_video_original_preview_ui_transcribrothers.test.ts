import { describe, expect, it } from "vitest";
import {
  mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers,
  mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers,
  urlVideoEntradaJobParaPreviewUiTranscribrothers,
} from "./modulo_util_mapear_tempo_timeline_cue_para_janela_video_original_preview_ui_transcribrothers.ts";

describe("mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers", () => {
  it("mapeia o início da cue para o início da janela", () => {
    expect(
      mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
        61,
        61,
        63,
        72,
        74,
      ),
    ).toBe(72);
  });

  it("mapeia o meio da cue para o meio da janela", () => {
    expect(
      mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
        62,
        61,
        63,
        72,
        74,
      ),
    ).toBe(73);
  });

  it("mapeia o fim da cue para o fim da janela", () => {
    expect(
      mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
        63,
        61,
        63,
        72,
        74,
      ),
    ).toBe(74);
  });
});

describe("mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers", () => {
  it("é o inverso do mapeamento timeline → janela", () => {
    const janela = mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
      62,
      61,
      63,
      72,
      74,
    );
    expect(
      mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers(
        janela,
        61,
        63,
        72,
        74,
      ),
    ).toBeCloseTo(62, 6);
  });

  it("mapeia o início da janela para o início da cue", () => {
    expect(
      mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers(
        72,
        61,
        63,
        72,
        74,
      ),
    ).toBe(61);
  });
});

describe("urlVideoEntradaJobParaPreviewUiTranscribrothers", () => {
  it("monta a URL do vídeo de entrada do job", () => {
    expect(urlVideoEntradaJobParaPreviewUiTranscribrothers("abc/def")).toBe(
      "/api/jobs/abc%2Fdef/video",
    );
  });
});
