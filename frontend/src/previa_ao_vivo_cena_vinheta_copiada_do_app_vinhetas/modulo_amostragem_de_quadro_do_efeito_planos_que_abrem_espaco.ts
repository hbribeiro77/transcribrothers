import type { CoresDaVinheta } from "./modulo_validacao_de_titulo_e_cores_da_vinheta";

export const LARGURA_DA_CENA_DA_VINHETA = 1920;
export const ALTURA_DA_CENA_DA_VINHETA = 1080;
export const DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS = 5;

export type RetanguloDoQuadroDaVinheta = {
  x: number;
  y: number;
  largura: number;
  altura: number;
  cor: string;
  opacidade?: number;
};

export type QuadroDaCenaDaVinheta = {
  largura: number;
  altura: number;
  duracao_segundos: number;
  fundo: string;
  opacidade_da_imagem?: number;
  planos: RetanguloDoQuadroDaVinheta[];
  titulo: {
    texto: string;
    cor: string;
    x: number;
    y: number;
    opacidade: number;
    tamanho_fonte: number;
  };
};

type ProjetoParaAmostrar = {
  titulo: string;
  cores: CoresDaVinheta;
};

export type Marco = { t: number; valor: number };

export function valor_no_tempo(tempo: number, marcos: Marco[]): number {
  const inicio = marcos[0].t;
  const fim = marcos[marcos.length - 1].t;
  const limitado = Math.min(fim, Math.max(inicio, tempo));
  for (let indice = 0; indice < marcos.length - 1; indice += 1) {
    const anterior = marcos[indice];
    const seguinte = marcos[indice + 1];
    if (limitado <= seguinte.t) {
      const intervalo = seguinte.t - anterior.t;
      if (intervalo === 0) {
        return seguinte.valor;
      }
      const progresso = (limitado - anterior.t) / intervalo;
      return anterior.valor + progresso * (seguinte.valor - anterior.valor);
    }
  }
  return marcos[marcos.length - 1].valor;
}

function retangulo_no_tempo(
  tempo: number,
  cor: string,
  x: Marco[],
  y: Marco[],
  largura: Marco[],
  altura: Marco[],
): RetanguloDoQuadroDaVinheta {
  return {
    x: valor_no_tempo(tempo, x),
    y: valor_no_tempo(tempo, y),
    largura: valor_no_tempo(tempo, largura),
    altura: valor_no_tempo(tempo, altura),
    cor,
  };
}

function tamanho_da_fonte_do_titulo(titulo: string): number {
  const tamanho_base = 72;
  const caracteres_confortaveis = 22;
  if (titulo.length <= caracteres_confortaveis) {
    return tamanho_base;
  }
  const reduzido = Math.round((tamanho_base * caracteres_confortaveis) / titulo.length);
  return Math.max(36, reduzido);
}

export function amostrar_quadro_do_efeito_planos_que_abrem_espaco(
  projeto: ProjetoParaAmostrar,
  tempo_segundos: number,
): QuadroDaCenaDaVinheta {
  const plano_de_cima = retangulo_no_tempo(
    tempo_segundos,
    projeto.cores.plano_principal,
    [
      { t: 0, valor: -1920 },
      { t: 1.2, valor: 0 },
      { t: 5, valor: 0 },
    ],
    [
      { t: 0, valor: 0 },
      { t: 5, valor: 0 },
    ],
    [
      { t: 0, valor: 1920 },
      { t: 5, valor: 1920 },
    ],
    [
      { t: 0, valor: 1080 },
      { t: 1.2, valor: 1080 },
      { t: 2.6, valor: 400 },
      { t: 5, valor: 400 },
    ],
  );

  const plano_de_baixo = retangulo_no_tempo(
    tempo_segundos,
    projeto.cores.plano_principal,
    [
      { t: 0, valor: 1920 },
      { t: 0.3, valor: 1920 },
      { t: 1.05, valor: 0 },
      { t: 5, valor: 0 },
    ],
    [
      { t: 0, valor: 0 },
      { t: 1.2, valor: 0 },
      { t: 2.6, valor: 680 },
      { t: 5, valor: 680 },
    ],
    [
      { t: 0, valor: 1920 },
      { t: 5, valor: 1920 },
    ],
    [
      { t: 0, valor: 1080 },
      { t: 1.2, valor: 1080 },
      { t: 2.6, valor: 400 },
      { t: 5, valor: 400 },
    ],
  );

  const linha_de_destaque = retangulo_no_tempo(
    tempo_segundos,
    projeto.cores.plano_destaque,
    [
      { t: 0, valor: -720 },
      { t: 1.8, valor: -720 },
      { t: 2.8, valor: 600 },
      { t: 5, valor: 600 },
    ],
    [
      { t: 0, valor: 376 },
      { t: 5, valor: 376 },
    ],
    [
      { t: 0, valor: 720 },
      { t: 5, valor: 720 },
    ],
    [
      { t: 0, valor: 12 },
      { t: 5, valor: 12 },
    ],
  );

  return {
    largura: LARGURA_DA_CENA_DA_VINHETA,
    altura: ALTURA_DA_CENA_DA_VINHETA,
    duracao_segundos: DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS,
    fundo: projeto.cores.fundo,
    planos: [plano_de_cima, plano_de_baixo, linha_de_destaque],
    titulo: {
      texto: projeto.titulo,
      cor: projeto.cores.texto,
      x: 960,
      y: 540,
      opacidade: valor_no_tempo(tempo_segundos, [
        { t: 0, valor: 0 },
        { t: 2.6, valor: 0 },
        { t: 3.4, valor: 1 },
        { t: 5, valor: 1 },
      ]),
      tamanho_fonte: tamanho_da_fonte_do_titulo(projeto.titulo),
    },
  };
}
