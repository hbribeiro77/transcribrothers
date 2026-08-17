import { describe, expect, it } from "vitest";
import {
  DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
  DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
  DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
  DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
  DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
  listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers,
  normalizarDiretrizConteudoLegendasTranscribrothers,
} from "./modulo_diretriz_conteudo_legendas_narracao_transcribrothers.ts";

describe("diretriz conteúdo legendas", () => {
  it("usa padrão conservador e aliases", () => {
    expect(normalizarDiretrizConteudoLegendasTranscribrothers(null)).toBe(
      DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
    );
    expect(normalizarDiretrizConteudoLegendasTranscribrothers("mais-falavel")).toBe(
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
    );
    expect(normalizarDiretrizConteudoLegendasTranscribrothers("didático")).toBe(
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
    );
    expect(normalizarDiretrizConteudoLegendasTranscribrothers("descontraído")).toBe(
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    );
    expect(normalizarDiretrizConteudoLegendasTranscribrothers("xyz")).toBe(
      DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
    );
  });

  it("lista quatro presets", () => {
    expect(listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers().map((o) => o.id)).toEqual([
      DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
      DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    ]);
  });
});
