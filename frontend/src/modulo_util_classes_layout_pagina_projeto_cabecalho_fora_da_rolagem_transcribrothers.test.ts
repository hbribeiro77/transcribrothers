import { describe, expect, it } from "vitest";
import { classesLayoutPaginaProjetoCabecalhoForaDaRolagemTranscribrothers } from "./modulo_util_classes_layout_pagina_projeto_cabecalho_fora_da_rolagem_transcribrothers.ts";

describe("classes do layout com cabeçalho fora da rolagem", () => {
  it("mantém o cabeçalho no fluxo, sem position fixed, e isola o corpo rolável", () => {
    const classes = classesLayoutPaginaProjetoCabecalhoForaDaRolagemTranscribrothers();
    expect(classes.pagina).toBe("tb-page");
    expect(classes.cabecalho).toBe("tb-header");
    expect(classes.cabecalho.split(/\s+/)).not.toContain("tb-header-fixed");
    expect(classes.corpoRolavel).toBe("tb-page-corpo-rolavel");
    expect(classes.corpoRolavelInterno).toBe("tb-page-corpo-rolavel-interno");
    expect(classes.vaoCabecalhoPx).toBe(16);
  });
});
