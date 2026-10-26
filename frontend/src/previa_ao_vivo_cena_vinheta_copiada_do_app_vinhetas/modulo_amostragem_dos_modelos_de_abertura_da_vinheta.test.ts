import { describe, expect, it } from "vitest";
import { amostrar_quadro_do_efeito_planos_que_abrem_espaco } from "./modulo_amostragem_de_quadro_do_efeito_planos_que_abrem_espaco";
import {
  amostrar_quadro_da_vinheta,
  tempo_da_coreografia,
  tempo_de_reproducao_do_quadro_assentado,
  trechos_de_reproducao_da_vinheta_com_hold_de_leitura,
} from "./modulo_amostragem_dos_modelos_de_abertura_da_vinheta";

const cores = {
  fundo: "#111111",
  plano_principal: "#222222",
  plano_destaque: "#333333",
  texto: "#444444",
};

const projeto = {
  titulo: "Solicitação de documento",
  cores,
};

function ponto_esta_no_retangulo(
  x: number,
  y: number,
  retangulo: { x: number; y: number; largura: number; altura: number },
) {
  return (
    x >= retangulo.x &&
    x < retangulo.x + retangulo.largura &&
    y >= retangulo.y &&
    y < retangulo.y + retangulo.altura
  );
}

describe("amostrar_quadro_da_vinheta", () => {
  it("usa a receita do modelo quando a lista de blocos está vazia", () => {
    const quadro = amostrar_quadro_da_vinheta(
      {
        ...projeto,
        efeito: "planos-que-abrem-espaco",
        duracao_segundos: 5,
        blocos: [],
        presenca_da_imagem: 60,
      },
      3.8,
    );

    expect(quadro.planos).toHaveLength(3);
    expect(quadro.planos[0]).toMatchObject({ x: 0, y: 0, largura: 1920, altura: 400 });
    expect(quadro.opacidade_da_imagem).toBeCloseTo(0.432);
  });

  it("estaciona 40% da duração no quadro assentado e comprime entrada e saída", () => {
    const dois = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(2);
    expect(dois.hold).toBeCloseTo(0.8);
    expect(dois.entrada).toBeCloseTo(0.912);
    expect(dois.saida).toBeCloseTo(0.288);
    expect(tempo_da_coreografia(0, 2)).toBeCloseTo(0);
    expect(tempo_da_coreografia(dois.entrada, 2)).toBeCloseTo(3.8);
    expect(tempo_da_coreografia(1.3, 2)).toBeCloseTo(3.8);
    expect(tempo_da_coreografia(dois.entrada + dois.hold, 2)).toBeCloseTo(3.8);
    expect(tempo_da_coreografia(2, 2)).toBeCloseTo(5);

    const cinco = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(5);
    expect(cinco.hold).toBeCloseTo(2);
    expect(cinco.entrada).toBeCloseTo(2.28);
    expect(cinco.saida).toBeCloseTo(0.72);
    expect(tempo_da_coreografia(3.5, 5)).toBeCloseTo(3.8);
    expect(tempo_da_coreografia(5, 5)).toBeCloseTo(5);

    const oito = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(8);
    expect(oito.hold).toBeCloseTo(3.2);
    expect(oito.entrada).toBeCloseTo(3.648);
    expect(oito.saida).toBeCloseTo(1.152);
    expect(tempo_da_coreografia(oito.entrada + oito.hold / 2, 8)).toBeCloseTo(3.8);
    expect(tempo_de_reproducao_do_quadro_assentado(2)).toBeCloseTo(dois.entrada + dois.hold / 2);
  });

  it("encaixa a coreografia de 5s na duração escolhida com hold de leitura", () => {
    const acelerada = amostrar_quadro_da_vinheta(
      { ...projeto, efeito: "planos-que-abrem-espaco", duracao_segundos: 2.5 },
      2,
    );
    const coreografia = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 3.8);

    expect(acelerada.duracao_segundos).toBe(2.5);
    expect(acelerada.titulo.opacidade).toBe(coreografia.titulo.opacidade);
    expect(acelerada.planos[0].altura).toBe(coreografia.planos[0].altura);
    expect(acelerada.planos[1].y).toBe(coreografia.planos[1].y);
  });

  it("desenha o retângulo do título com linhas quando a cena está assentada", () => {
    const quadro = amostrar_quadro_da_vinheta(
      { ...projeto, efeito: "linhas-que-desenham-o-lugar", duracao_segundos: 5 },
      3.5,
    );

    expect(quadro.planos[0]).toMatchObject({ x: 480, y: 430, largura: 960, altura: 8, cor: "#333333" });
    expect(quadro.planos[1]).toMatchObject({ x: 480, y: 642, largura: 960, altura: 8, cor: "#333333" });
    expect(quadro.planos[2]).toMatchObject({ x: 480, y: 430, largura: 8, altura: 220, cor: "#222222" });
    expect(quadro.planos[3]).toMatchObject({ x: 1432, y: 430, largura: 8, altura: 220, cor: "#222222" });
    expect(quadro.titulo.opacidade).toBe(1);
    expect(ponto_esta_no_retangulo(960, 540, quadro.planos[0])).toBe(false);
  });

  it("começa as linhas sem desenhar o retângulo", () => {
    const quadro = amostrar_quadro_da_vinheta(
      { ...projeto, efeito: "linhas-que-desenham-o-lugar", duracao_segundos: 5 },
      0,
    );

    expect(quadro.planos[0].largura).toBe(0);
    expect(quadro.titulo.opacidade).toBe(0);
  });

  it("cruza as barras fora do lugar do título e as tira da tela no fim", () => {
    const no_cruzamento = amostrar_quadro_da_vinheta(
      { ...projeto, efeito: "barras-que-se-cruzam", duracao_segundos: 5 },
      1,
    );
    const no_fim = amostrar_quadro_da_vinheta(
      { ...projeto, efeito: "barras-que-se-cruzam", duracao_segundos: 5 },
      3.5,
    );

    expect(ponto_esta_no_retangulo(960, 540, no_cruzamento.planos[0])).toBe(false);
    expect(ponto_esta_no_retangulo(960, 540, no_cruzamento.planos[1])).toBe(false);
    expect(no_cruzamento.planos[0].x + no_cruzamento.planos[0].largura).toBeGreaterThan(0);
    expect(no_fim.planos[0].x).toBeGreaterThanOrEqual(1920);
    expect(no_fim.planos[1].x + no_fim.planos[1].largura).toBeLessThanOrEqual(0);
    expect(no_fim.titulo.opacidade).toBe(1);
    expect(no_fim.titulo.texto).toBe("Solicitação de documento");
  });

  it("escala a coreografia para o canvas do vídeo", () => {
    const quadro = amostrar_quadro_da_vinheta(
      {
        ...projeto,
        titulo: "Consulta",
        efeito: "planos-que-abrem-espaco",
        duracao_segundos: 5,
        largura: 1280,
        altura: 720,
      },
      3.8,
    );

    expect(quadro.largura).toBe(1280);
    expect(quadro.altura).toBe(720);
    expect(quadro.planos[0]).toMatchObject({ x: 0, y: 0, largura: 1280, altura: 400 * (720 / 1080) });
    expect(quadro.titulo.x).toBe(640);
    expect(quadro.titulo.y).toBe(360);
    expect(quadro.titulo.tamanho_fonte).toBe(Math.round(72 * (1280 / 1920)));
  });
});
