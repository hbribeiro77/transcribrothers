import type { BlocoDaVinheta } from "./modulo_movimento_do_bloco_adicionado_na_vinheta";
import type { CoresDaVinheta } from "./modulo_validacao_de_titulo_e_cores_da_vinheta";

const LIMITE_DE_BLOCOS = 8;

type EfeitoDaVinheta = "planos-que-abrem-espaco" | "linhas-que-desenham-o-lugar" | "barras-que-se-cruzam";

function bloco(
  id: string,
  cor: string,
  entrada: BlocoDaVinheta["entrada"],
  x: number,
  y: number,
  largura_inicial: number,
  altura_inicial: number,
  largura: number,
  altura: number,
  inicio_segundos: number,
  fim_segundos: number,
): BlocoDaVinheta {
  return {
    id,
    cor,
    entrada,
    x,
    y,
    largura_inicial,
    altura_inicial,
    largura,
    altura,
    inicio_segundos,
    fim_segundos,
  };
}

export function blocos_do_modelo_de_abertura(efeito: EfeitoDaVinheta, cores: CoresDaVinheta): BlocoDaVinheta[] {
  const principal = cores.plano_principal;
  const destaque = cores.plano_destaque;
  if (efeito === "linhas-que-desenham-o-lugar") {
    return [
      bloco("linha-de-cima", destaque, "no-lugar", 480, 430, 0, 8, 960, 8, 0, 1.2),
      bloco("linha-de-baixo", destaque, "no-lugar", 480, 642, 0, 8, 960, 8, 0.2, 1.4),
      bloco("linha-esquerda", principal, "no-lugar", 480, 430, 8, 0, 8, 220, 1, 2),
      bloco("linha-direita", principal, "no-lugar", 1432, 430, 8, 0, 8, 220, 1.2, 2.2),
    ];
  }
  if (efeito === "barras-que-se-cruzam") {
    return [
      bloco("barra-de-cima", principal, "esquerda", 1920, 160, 900, 200, 900, 200, 0, 2.2),
      bloco("barra-de-baixo", principal, "direita", -900, 720, 900, 200, 900, 200, 0.2, 2.4),
      bloco("faixa-de-destaque", destaque, "esquerda", 600, 470, 720, 10, 720, 10, 1.6, 2.6),
    ];
  }
  return [
    bloco("plano-de-cima", principal, "esquerda", 0, 0, 1920, 1080, 1920, 400, 0, 2.6),
    bloco("plano-de-baixo", principal, "direita", 0, 680, 1920, 1080, 1920, 400, 0.3, 2.6),
    bloco("faixa-de-destaque", destaque, "esquerda", 600, 376, 720, 12, 720, 12, 1.8, 2.8),
  ];
}

export function blocos_ao_abrir_projeto_salvo(
  efeito: EfeitoDaVinheta,
  cores: CoresDaVinheta,
  blocos: BlocoDaVinheta[],
): BlocoDaVinheta[] {
  const legado = blocos.length === 0 || blocos.some((item) => item.largura_inicial === undefined);
  if (!legado) {
    return blocos;
  }
  const do_modelo = blocos_do_modelo_de_abertura(efeito, cores);
  const salvos = blocos.map((item) => ({
    ...item,
    largura_inicial: item.largura_inicial ?? item.largura,
    altura_inicial: item.altura_inicial ?? item.altura,
  }));
  return [...do_modelo, ...salvos].slice(0, LIMITE_DE_BLOCOS);
}
