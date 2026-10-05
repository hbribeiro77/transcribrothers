import { describe, expect, it } from "vitest";
import { extrairTextoPlanoParaDownloadTxtTranscricaoDeMarkdownResultadoTranscribrothers } from "./modulo_util_extrair_texto_plano_para_download_txt_transcricao_de_markdown_resultado_transcribrothers.ts";

describe("extrairTextoPlanoParaDownloadTxtTranscricaoDeMarkdownResultadoTranscribrothers", () => {
  it("pega o texto corrido e ignora a lista de segmentos", () => {
    const md = `# Transcrição

Bom dia, vamos falar do prazo.

## Segmentos

- [0.0s–2.0s] Bom dia, vamos falar do prazo.
`;
    expect(extrairTextoPlanoParaDownloadTxtTranscricaoDeMarkdownResultadoTranscribrothers(md)).toBe(
      "Bom dia, vamos falar do prazo.",
    );
  });

  it("devolve o markdown inteiro se não for o molde de só transcrição", () => {
    const md = "# Tutorial\n\nPasso um.";
    expect(extrairTextoPlanoParaDownloadTxtTranscricaoDeMarkdownResultadoTranscribrothers(md)).toBe(md);
  });
});
