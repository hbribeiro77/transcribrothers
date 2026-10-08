import { describe, expect, it } from "vitest";
import { instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers } from "./modulo_util_instante_segundos_de_offset_ms_no_nome_png_asset_tutorial_transcribrothers.ts";

describe("instante no nome do PNG do tutorial", () => {
  it("lê offset_ms do arquivo de captura da pipeline", () => {
    expect(
      instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers(
        "screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000031700_indice_0004.png",
      ),
    ).toBe(31.7);
  });

  it("aceita caminho assets/ e ignora query", () => {
    expect(
      instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers(
        "assets/screenshot_offset_ms_0000015000_indice_0001.png?v=2",
      ),
    ).toBe(15);
  });

  it("devolve null quando não há offset no nome", () => {
    expect(
      instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers("imagem_colada_clipboard.png"),
    ).toBeNull();
  });
});
