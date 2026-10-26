import { describe, expect, it } from "vitest";
import { amostrar_quadro_do_efeito_planos_que_abrem_espaco } from "./modulo_amostragem_de_quadro_do_efeito_planos_que_abrem_espaco";
import type { CoresDaVinheta } from "./modulo_validacao_de_titulo_e_cores_da_vinheta";

const cores: CoresDaVinheta = {
  fundo: "#111111",
  plano_principal: "#222222",
  plano_destaque: "#333333",
  texto: "#444444",
};

const projeto = {
  titulo: "Consulta de intimações",
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

describe("amostrar_quadro_do_efeito_planos_que_abrem_espaco", () => {
  it("começa com os planos fora da tela e o título invisível", () => {
    const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 0);

    expect(quadro.largura).toBe(1920);
    expect(quadro.altura).toBe(1080);
    expect(quadro.duracao_segundos).toBe(5);
    expect(quadro.fundo).toBe("#111111");
    expect(quadro.planos[0]).toMatchObject({
      x: -1920,
      y: 0,
      largura: 1920,
      altura: 1080,
      cor: "#222222",
    });
    expect(quadro.planos[1].x).toBeGreaterThanOrEqual(1920);
    expect(quadro.planos[2].x + quadro.planos[2].largura).toBeLessThanOrEqual(0);
    expect(quadro.planos[2].cor).toBe("#333333");
    expect(quadro.titulo.opacidade).toBe(0);
    expect(quadro.titulo.texto).toBe("Consulta de intimações");
    expect(quadro.titulo.cor).toBe("#444444");
  });

  it("abre o miolo aos 2,6s com o título ainda invisível", () => {
    const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 2.6);
    const centro = { x: 960, y: 540 };

    for (const plano of quadro.planos) {
      expect(ponto_esta_no_retangulo(centro.x, centro.y, plano)).toBe(false);
    }
    expect(quadro.planos[0]).toMatchObject({ x: 0, y: 0, largura: 1920, altura: 400 });
    expect(quadro.planos[1]).toMatchObject({ x: 0, y: 680, largura: 1920, altura: 400 });
    expect(quadro.titulo.opacidade).toBe(0);
    expect(quadro.titulo.x).toBe(960);
    expect(quadro.titulo.y).toBe(540);
  });

  it("não deixa o fundo vazar no canto inferior esquerdo enquanto os planos se encontram", () => {
    for (const tempo of [1.25, 1.4, 1.55]) {
      const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, tempo);
      const canto_coberto_pelo_plano_principal = quadro.planos
        .slice(0, 2)
        .some((plano) => ponto_esta_no_retangulo(40, 1040, plano));

      expect(canto_coberto_pelo_plano_principal).toBe(true);
    }
  });

  it("cobre o centro enquanto os planos ainda atravessam a tela", () => {
    const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 1.2);

    expect(ponto_esta_no_retangulo(960, 540, quadro.planos[0])).toBe(true);
  });

  it("assenta o título e a linha de destaque no fim da cena", () => {
    const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 5);

    expect(quadro.titulo.opacidade).toBe(1);
    expect(quadro.planos[2]).toMatchObject({
      x: 600,
      y: 376,
      largura: 720,
      altura: 12,
      cor: "#333333",
    });
    expect(quadro.planos[2].y + quadro.planos[2].altura).toBeLessThanOrEqual(400);
  });

  it("revela o título pela metade entre 2,6s e 3,4s", () => {
    const quadro = amostrar_quadro_do_efeito_planos_que_abrem_espaco(projeto, 3);

    expect(quadro.titulo.opacidade).toBeCloseTo(0.5, 5);
  });

  it("reduz a fonte quando o título é longo", () => {
    const curto = amostrar_quadro_do_efeito_planos_que_abrem_espaco(
      { titulo: "Portal", cores },
      5,
    );
    const longo = amostrar_quadro_do_efeito_planos_que_abrem_espaco(
      { titulo: "a".repeat(48), cores },
      5,
    );

    expect(curto.titulo.tamanho_fonte).toBe(72);
    expect(longo.titulo.tamanho_fonte).toBe(36);
  });
});
