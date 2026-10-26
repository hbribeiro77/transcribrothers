import { describe, expect, it } from "vitest";

import { PALETA_PADRAO_DA_VINHETA } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_validacao_de_titulo_e_cores_da_vinheta.ts";
import {
  DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  montarReceitaVinhetaDoSeparadorTranscribrothers,
  normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers,
  normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers,
  normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers,
} from "./modulo_util_receita_e_velocidade_da_vinheta_do_separador_de_secao_transcribrothers.ts";

describe("receita e velocidade da vinheta do separador", () => {
  it("o slider vai de 0,5 a 8 segundos de 0,5 em 0,5", () => {
    expect(DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS).toBe(0.5);
    expect(DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS).toBe(8);
    expect(PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS).toBe(0.5);
    expect(normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(4.5)).toBe(4.5);
    expect(normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(0.4)).toBe(0.5);
    expect(normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(8.2)).toBe(8);
    expect(normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(3.24)).toBe(3);
    expect(normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(3.26)).toBe(3.5);
  });

  it("a presença da imagem fica entre 0 e 100 e começa em 60", () => {
    expect(PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS).toBe(60);
    expect(normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(60)).toBe(60);
    expect(normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(-2)).toBe(0);
    expect(normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(140)).toBe(100);
  });

  it("monta a receita com título, efeito, velocidade, presença e paleta", () => {
    expect(
      montarReceitaVinhetaDoSeparadorTranscribrothers({
        chave: "modelo:barras-que-se-cruzam",
        titulo: "  Consulta  ",
        duracaoSegundos: 4.5,
        presencaDaImagem: 60,
        cores: { ...PALETA_PADRAO_DA_VINHETA, texto: "#ffffff" },
      }),
    ).toEqual({
      titulo: "Consulta",
      efeito: "barras-que-se-cruzam",
      vinhetaId: null,
      duracaoSegundos: 4.5,
      presencaDaImagem: 60,
      cores: { ...PALETA_PADRAO_DA_VINHETA, texto: "#ffffff" },
    });
  });

  it("o canvas da vinheta fica com lados pares iguais ao vídeo", () => {
    expect(normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers(1365, 767)).toEqual({
      largura: 1364,
      altura: 766,
    });
    expect(normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers(1280, 720)).toEqual({
      largura: 1280,
      altura: 720,
    });
  });
});
