import { describe, expect, it } from "vitest";
import { obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers } from "./modulo_api_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers.ts";

describe("obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers", () => {
  it("prefere legendas_documento_alinhadas sobre pipeline.url_asset_vtt obsoleto", () => {
    const url = obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers({
      pipeline_video_narrado_documento: {
        url_asset_vtt: "/api/jobs/x/assets/legendas.vtt?v=antigo",
      },
      legendas_documento_alinhadas: {
        url_asset: "/api/jobs/x/assets/legendas.vtt?v=fresco",
      },
    });
    expect(url).toBe("/api/jobs/x/assets/legendas.vtt?v=fresco");
  });

  it("usa pipeline.url_asset_vtt quando o working set canônico não tem URL", () => {
    const url = obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers({
      pipeline_video_narrado_documento: {
        url_asset_vtt: "/api/jobs/x/assets/legendas.vtt?v=so-pipeline",
      },
    });
    expect(url).toBe("/api/jobs/x/assets/legendas.vtt?v=so-pipeline");
  });
});
