import { describe, expect, it } from "vitest";
import {
  filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers,
  listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers,
} from "./modulo_util_filtrar_markdown_por_secoes_heading_nivel2_selecionadas_transcribrothers.ts";

const MD = `# Título

Introdução aqui.

## Alpha

Texto A com [link](?t=10).

## Beta

Texto B.

## Gama

Texto C.
`;

describe("escopo seções vídeo narrado", () => {
  it("lista preâmbulo e seções ##", () => {
    const opcoes = listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(MD);
    expect(opcoes.map((o) => o.id)).toEqual(["preambulo", "alpha", "beta", "gama"]);
  });

  it("filtra só seções escolhidas na ordem", () => {
    const out = filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers(MD, ["beta", "alpha"]);
    expect(out).toContain("## Alpha");
    expect(out).toContain("## Beta");
    expect(out).not.toContain("## Gama");
    expect(out.indexOf("## Alpha")).toBeLessThan(out.indexOf("## Beta"));
  });

  it("inclui preâmbulo quando selecionado", () => {
    const out = filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers(MD, [
      "preambulo",
      "gama",
    ]);
    expect(out).toContain("Introdução aqui.");
    expect(out).toContain("## Gama");
    expect(out).not.toContain("## Alpha");
  });
});
