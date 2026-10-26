import {
  DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS,
  valor_no_tempo,
  type QuadroDaCenaDaVinheta,
  type RetanguloDoQuadroDaVinheta,
} from "./modulo_amostragem_de_quadro_do_efeito_planos_que_abrem_espaco";
import { blocos_do_modelo_de_abertura } from "./modulo_blocos_do_modelo_de_abertura_da_vinheta";
import {
  plano_do_bloco,
  progresso_da_saida_da_vinheta,
  type BlocoDaVinheta,
  type SaidaDaVinheta,
} from "./modulo_movimento_do_bloco_adicionado_na_vinheta";
import { opacidade_da_imagem_de_fundo_no_tempo } from "./modulo_opacidade_da_imagem_de_fundo_da_vinheta";
import type { CoresDaVinheta } from "./modulo_validacao_de_titulo_e_cores_da_vinheta";

export const MODELOS_DE_ABERTURA_DA_VINHETA = [
  { id: "planos-que-abrem-espaco", nome: "Planos que abrem um espaço" },
  { id: "linhas-que-desenham-o-lugar", nome: "Linhas que desenham o lugar" },
  { id: "barras-que-se-cruzam", nome: "Barras que se cruzam" },
] as const;

export const VELOCIDADES_DA_VINHETA = [
  { duracao_segundos: 3, nome: "Rápida" },
  { duracao_segundos: 5, nome: "Normal" },
  { duracao_segundos: 8, nome: "Lenta" },
] as const;

export type EfeitoDaVinheta = (typeof MODELOS_DE_ABERTURA_DA_VINHETA)[number]["id"];

export const EFEITO_PADRAO_DA_VINHETA: EfeitoDaVinheta = "planos-que-abrem-espaco";
export const DURACAO_PADRAO_DA_VINHETA = 5;
export const SAIDAS_DA_VINHETA = [
  { id: "esmaecer", nome: "Esmaecer" },
  { id: "sair", nome: "Sair" },
] as const satisfies readonly { id: SaidaDaVinheta; nome: string }[];
export const SAIDA_PADRAO_DA_VINHETA: SaidaDaVinheta = "esmaecer";
export const TEMPO_DO_QUADRO_ASSENTADO_NA_COREOGRAFIA = 3.8;
export const FRACAO_DE_HOLD_DA_LEITURA_DA_VINHETA = 0.4;

export type TrechosDeReproducaoDaVinhetaComHold = {
  entrada: number;
  hold: number;
  saida: number;
};

export function trechos_de_reproducao_da_vinheta_com_hold_de_leitura(
  duracao_escolhida: number,
): TrechosDeReproducaoDaVinhetaComHold {
  const duracao = duracao_escolhida > 0 ? duracao_escolhida : DURACAO_PADRAO_DA_VINHETA;
  const coreografia = DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS;
  const assentado = TEMPO_DO_QUADRO_ASSENTADO_NA_COREOGRAFIA;
  const saida_maxima = coreografia - assentado;
  let hold = FRACAO_DE_HOLD_DA_LEITURA_DA_VINHETA * duracao;
  const resto = Math.max(0, duracao - hold);
  let entrada = resto * (assentado / coreografia);
  let saida = resto * (saida_maxima / coreografia);
  if (entrada > assentado) {
    hold += entrada - assentado;
    entrada = assentado;
  }
  if (saida > saida_maxima) {
    hold += saida - saida_maxima;
    saida = saida_maxima;
  }
  return { entrada, hold, saida };
}

export function tempo_de_reproducao_do_quadro_assentado(duracao_segundos: number): number {
  const duracao = duracao_segundos > 0 ? duracao_segundos : DURACAO_PADRAO_DA_VINHETA;
  const trechos = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(duracao);
  return trechos.entrada + trechos.hold / 2;
}

type ProjetoDaVinheta = {
  titulo: string;
  cores: CoresDaVinheta;
  efeito?: EfeitoDaVinheta;
  duracao_segundos?: number;
  blocos?: BlocoDaVinheta[];
  presenca_da_imagem?: number;
  saida?: SaidaDaVinheta;
  largura?: number;
  altura?: number;
};

export function tempo_da_coreografia(tempo_reproducao: number, duracao_escolhida: number): number {
  const duracao = duracao_escolhida > 0 ? duracao_escolhida : DURACAO_PADRAO_DA_VINHETA;
  const coreografia = DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS;
  const assentado = TEMPO_DO_QUADRO_ASSENTADO_NA_COREOGRAFIA;
  const { entrada, hold, saida } = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(duracao);
  const t = Math.min(duracao, Math.max(0, tempo_reproducao));
  if (t >= duracao) {
    return coreografia;
  }
  if (t <= entrada) {
    return entrada > 0 ? (t / entrada) * assentado : assentado;
  }
  if (t <= entrada + hold || saida <= 0) {
    return assentado;
  }
  const t_saida = t - entrada - hold;
  return Math.min(coreografia, assentado + (t_saida / saida) * (coreografia - assentado));
}

export function tempo_de_reproducao_para_o_instante_da_coreografia(
  instante_coreografia: number,
  duracao_escolhida: number,
): number {
  const duracao = duracao_escolhida > 0 ? duracao_escolhida : DURACAO_PADRAO_DA_VINHETA;
  const coreografia = DURACAO_DA_CENA_DA_VINHETA_EM_SEGUNDOS;
  const assentado = TEMPO_DO_QUADRO_ASSENTADO_NA_COREOGRAFIA;
  const { entrada, hold, saida } = trechos_de_reproducao_da_vinheta_com_hold_de_leitura(duracao);
  const u = Math.min(coreografia, Math.max(0, instante_coreografia));
  if (u <= 0) return 0;
  if (u >= coreografia) return duracao;
  if (u < assentado) {
    return entrada > 0 ? (u / assentado) * entrada : 0;
  }
  if (u === assentado || saida <= 0) {
    return entrada;
  }
  return entrada + hold + ((u - assentado) / (coreografia - assentado)) * saida;
}

function lado_par_do_canvas_da_vinheta(valor: number): number {
  const inteiro = Math.floor(valor);
  return Math.max(2, inteiro - (inteiro % 2));
}

export function escalar_quadro_da_vinheta_para_o_canvas(
  quadro: QuadroDaCenaDaVinheta,
  largura?: number,
  altura?: number,
): QuadroDaCenaDaVinheta {
  if (!largura || !altura) {
    return quadro;
  }
  const alvoLargura = lado_par_do_canvas_da_vinheta(largura);
  const alvoAltura = lado_par_do_canvas_da_vinheta(altura);
  if (alvoLargura === quadro.largura && alvoAltura === quadro.altura) {
    return quadro;
  }
  const sx = alvoLargura / quadro.largura;
  const sy = alvoAltura / quadro.altura;
  const fonte = Math.min(sx, sy);
  return {
    ...quadro,
    largura: alvoLargura,
    altura: alvoAltura,
    planos: quadro.planos.map((plano) => ({
      ...plano,
      x: plano.x * sx,
      y: plano.y * sy,
      largura: plano.largura * sx,
      altura: plano.altura * sy,
    })),
    titulo: {
      ...quadro.titulo,
      x: quadro.titulo.x * sx,
      y: quadro.titulo.y * sy,
      tamanho_fonte: Math.max(1, Math.round(quadro.titulo.tamanho_fonte * fonte)),
    },
  };
}

function quadro_base(
  projeto: ProjetoDaVinheta,
  duracao: number,
  planos: RetanguloDoQuadroDaVinheta[],
  opacidade: number,
  opacidade_da_imagem: number,
): QuadroDaCenaDaVinheta {
  return {
    largura: 1920,
    altura: 1080,
    duracao_segundos: duracao,
    fundo: projeto.cores.fundo,
    opacidade_da_imagem,
    planos,
    titulo: {
      texto: projeto.titulo,
      cor: projeto.cores.texto,
      x: 960,
      y: 540,
      opacidade,
      tamanho_fonte: projeto.titulo.length <= 22 ? 72 : Math.max(36, Math.round((72 * 22) / projeto.titulo.length)),
    },
  };
}

function opacidade_do_titulo(efeito: EfeitoDaVinheta, tempo: number): number {
  if (efeito === "linhas-que-desenham-o-lugar") {
    return valor_no_tempo(tempo, [
      { t: 0, valor: 0 },
      { t: 2.2, valor: 0 },
      { t: 3, valor: 1 },
      { t: 5, valor: 1 },
    ]);
  }
  if (efeito === "barras-que-se-cruzam") {
    return valor_no_tempo(tempo, [
      { t: 0, valor: 0 },
      { t: 2.4, valor: 0 },
      { t: 3.2, valor: 1 },
      { t: 5, valor: 1 },
    ]);
  }
  return valor_no_tempo(tempo, [
    { t: 0, valor: 0 },
    { t: 2.6, valor: 0 },
    { t: 3.4, valor: 1 },
    { t: 5, valor: 1 },
  ]);
}

export function amostrar_quadro_da_vinheta(
  projeto: ProjetoDaVinheta,
  tempo_reproducao: number,
): QuadroDaCenaDaVinheta {
  const duracao = projeto.duracao_segundos ?? DURACAO_PADRAO_DA_VINHETA;
  const tempo = tempo_da_coreografia(tempo_reproducao, duracao);
  const efeito = projeto.efeito ?? EFEITO_PADRAO_DA_VINHETA;
  const saida = projeto.saida ?? SAIDA_PADRAO_DA_VINHETA;
  const blocos =
    projeto.blocos && projeto.blocos.length > 0
      ? projeto.blocos
      : blocos_do_modelo_de_abertura(efeito, projeto.cores);
  return escalar_quadro_da_vinheta_para_o_canvas(
    quadro_base(
      projeto,
      duracao,
      blocos.map((bloco) => plano_do_bloco(bloco, tempo, saida)),
      opacidade_do_titulo(efeito, tempo) * (1 - progresso_da_saida_da_vinheta(tempo)),
      opacidade_da_imagem_de_fundo_no_tempo(projeto.presenca_da_imagem ?? 0, tempo),
    ),
    projeto.largura,
    projeto.altura,
  );
}
