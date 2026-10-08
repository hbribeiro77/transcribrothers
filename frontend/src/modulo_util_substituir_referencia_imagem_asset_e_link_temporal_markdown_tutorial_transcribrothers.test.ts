import { describe, expect, it } from "vitest";
import {
  instanteSegundosDaImagemAssetNoMarkdownTutorialTranscribrothers,
  navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers,
  substituirReferenciaImagemAssetELinkTemporalNoMarkdownTutorialTranscribrothers,
  usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers,
} from "./modulo_util_substituir_referencia_imagem_asset_e_link_temporal_markdown_tutorial_transcribrothers.ts";

describe("trocar o frame da imagem no Markdown", () => {
  it("substitui o ![] e o ?t= logo abaixo", () => {
    const md = [
      "## Passo",
      "![Tela em 0:31](assets/screenshot_offset_ms_0000031700_indice_0004.png)",
      "",
      "[0:31](?t=31.7)",
      "texto",
    ].join("\n");
    const novo = substituirReferenciaImagemAssetELinkTemporalNoMarkdownTutorialTranscribrothers({
      markdown: md,
      nomeArquivoAnterior: "screenshot_offset_ms_0000031700_indice_0004.png",
      nomeArquivoNovo: "screenshot_offset_ms_0000032100_indice_0099.png",
      instanteSegundos: 32.1,
    });
    expect(novo).toContain(
      "![Tela em 0:32](assets/screenshot_offset_ms_0000032100_indice_0099.png)",
    );
    expect(novo).toContain("[0:32](?t=32.1)");
    expect(novo).not.toContain("0000031700");
    expect(novo).toContain("texto");
  });

  it("insere o ?t= quando a imagem não tinha link temporal", () => {
    const md = "![alt](assets/imagem_colada.png)\n\nparágrafo";
    const novo = substituirReferenciaImagemAssetELinkTemporalNoMarkdownTutorialTranscribrothers({
      markdown: md,
      nomeArquivoAnterior: "imagem_colada.png",
      nomeArquivoNovo: "screenshot_offset_ms_0000010000_indice_0001.png",
      instanteSegundos: 10,
    });
    expect(novo).toContain("![Tela em 0:10](assets/screenshot_offset_ms_0000010000_indice_0001.png)");
    expect(novo).toContain("[0:10](?t=10)");
  });

  it("lê o instante do offset_ms ou do ?t= abaixo da figura", () => {
    expect(
      instanteSegundosDaImagemAssetNoMarkdownTutorialTranscribrothers(
        "![](assets/screenshot_offset_ms_0000031700_indice_0004.png)",
        "screenshot_offset_ms_0000031700_indice_0004.png",
      ),
    ).toBe(31.7);
    expect(
      instanteSegundosDaImagemAssetNoMarkdownTutorialTranscribrothers(
        "![x](assets/colada.png)\n\n[1:20](?t=80)",
        "colada.png",
      ),
    ).toBe(80);
    expect(
      instanteSegundosDaImagemAssetNoMarkdownTutorialTranscribrothers("sem imagem", "colada.png"),
    ).toBeNull();
  });

  it("mostra a navegação só com vídeo e instante conhecido", () => {
    expect(
      navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers({
        temVideoEntrada: true,
        instanteSegundos: 12,
      }),
    ).toBe(true);
    expect(
      navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers({
        temVideoEntrada: false,
        instanteSegundos: 12,
      }),
    ).toBe(false);
    expect(
      navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers({
        temVideoEntrada: true,
        instanteSegundos: null,
      }),
    ).toBe(false);
  });

  it("habilita Usar este frame só quando o candidato é outro arquivo", () => {
    expect(
      usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers({
        nomeArquivoNoDocumento: "a.png",
        nomeArquivoCandidato: "b.png",
        capturando: false,
      }),
    ).toBe(true);
    expect(
      usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers({
        nomeArquivoNoDocumento: "a.png",
        nomeArquivoCandidato: "a.png",
        capturando: false,
      }),
    ).toBe(false);
    expect(
      usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers({
        nomeArquivoNoDocumento: "a.png",
        nomeArquivoCandidato: "b.png",
        capturando: true,
      }),
    ).toBe(false);
  });
});
