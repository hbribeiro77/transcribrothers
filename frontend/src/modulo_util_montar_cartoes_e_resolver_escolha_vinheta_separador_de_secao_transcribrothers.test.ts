import { describe, expect, it } from "vitest";

import {
  montarCartoesVinhetaSeparadorDeSecaoTranscribrothers,
  montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers,
  resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers,
} from "./modulo_util_montar_cartoes_e_resolver_escolha_vinheta_separador_de_secao_transcribrothers.ts";

describe("cartões da modal de vinheta do separador", () => {
  it("monta modelos e vinhetas salvas, lendo prévia se a API mandar", () => {
    const cartoes = montarCartoesVinhetaSeparadorDeSecaoTranscribrothers({
      modelos: [{ id: "planos-que-abrem-espaco", nome: "Planos que abrem um espaço" }],
      projetos: [
        { id: "abc", titulo: "Abertura", url_preview: "http://vinhetas.test/abc.mp4" },
      ],
    });

    expect(cartoes).toEqual([
      {
        chave: "modelo:planos-que-abrem-espaco",
        rotulo: "Planos que abrem um espaço",
        grupo: "modelo",
        urlPreview: null,
        efeitoPrevia: "planos-que-abrem-espaco",
      },
      {
        chave: "salva:abc",
        rotulo: "Abertura",
        grupo: "salva",
        urlPreview: "http://vinhetas.test/abc.mp4",
        efeitoPrevia: "planos-que-abrem-espaco",
      },
    ]);
  });

  it("a chave do modelo vira efeito e a salva vira vinhetaId", () => {
    expect(
      resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers({
        chave: "modelo:barras-que-se-cruzam",
        titulo: "Nova seção",
      }),
    ).toMatchObject({
      titulo: "Nova seção",
      efeito: "barras-que-se-cruzam",
      vinhetaId: null,
    });
    expect(
      resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers({
        chave: "salva:abc",
        titulo: "  Abertura  ",
      }),
    ).toMatchObject({
      titulo: "Abertura",
      efeito: null,
      vinhetaId: "abc",
    });
  });

  it("a prévia do vídeo usa GET para o player conseguir tocar", () => {
    expect(
      montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers({
        titulo: "Nova seção",
        efeito: "planos-que-abrem-espaco",
        vinhetaId: null,
      }),
    ).toBe(
      "/api/integracao/vinhetas/previsualizar?titulo=Nova+se%C3%A7%C3%A3o&efeito=planos-que-abrem-espaco",
    );
    expect(
      montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers({
        titulo: "Abertura",
        efeito: null,
        vinhetaId: "abc",
      }),
    ).toBe("/api/integracao/vinhetas/previsualizar?titulo=Abertura&vinheta_id=abc");
    expect(
      montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers({
        titulo: "X",
        efeito: null,
        vinhetaId: null,
      }),
    ).toBeNull();
  });
});
