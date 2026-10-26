import { describe, expect, it } from "vitest";

import { listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers } from "./modulo_util_filtrar_markdown_por_secoes_heading_nivel2_selecionadas_transcribrothers.ts";
import {
  chaveCartaoTransicaoSecaoAPartirDaPreferenciaTranscribrothers,
  contarSecoesH2DoEscopoGeracaoVideoNarradoTranscribrothers,
  deveOferecerTransicoesEntreSecoesNaGeracaoVideoNarradoTranscribrothers,
} from "./modulo_util_transicoes_secao_na_geracao_video_narrado_transcribrothers.ts";

const MD = `# Título

Intro.

## Alpha

Texto A.

## Beta

Texto B.
`;

describe("transições na geração do vídeo narrado", () => {
  it("documento inteiro com 2 ## oferece transições", () => {
    const n = contarSecoesH2DoEscopoGeracaoVideoNarradoTranscribrothers({
      modo: "documento_inteiro",
      markdown: MD,
      idsSelecionados: new Set(),
      opcoes: listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(MD),
    });
    expect(n).toBe(2);
    expect(deveOferecerTransicoesEntreSecoesNaGeracaoVideoNarradoTranscribrothers(n)).toBe(true);
  });

  it("uma seção marcada não oferece transições", () => {
    const opcoes = listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(MD);
    const n = contarSecoesH2DoEscopoGeracaoVideoNarradoTranscribrothers({
      modo: "secoes",
      markdown: MD,
      idsSelecionados: new Set(["alpha"]),
      opcoes,
    });
    expect(n).toBe(1);
    expect(deveOferecerTransicoesEntreSecoesNaGeracaoVideoNarradoTranscribrothers(n)).toBe(false);
  });

  it("a vinheta salva vira chave de cartão salva, senão usa o modelo", () => {
    expect(
      chaveCartaoTransicaoSecaoAPartirDaPreferenciaTranscribrothers({
        efeito: "barras-que-se-cruzam",
        vinhetaId: "abc",
      }),
    ).toBe("salva:abc");
    expect(
      chaveCartaoTransicaoSecaoAPartirDaPreferenciaTranscribrothers({
        efeito: "barras-que-se-cruzam",
        vinhetaId: null,
      }),
    ).toBe("modelo:barras-que-se-cruzam");
  });
});
