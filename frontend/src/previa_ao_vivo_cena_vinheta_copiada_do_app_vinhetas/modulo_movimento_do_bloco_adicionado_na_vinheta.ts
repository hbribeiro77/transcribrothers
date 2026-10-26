import type { RetanguloDoQuadroDaVinheta } from "./modulo_amostragem_de_quadro_do_efeito_planos_que_abrem_espaco";

export const ENTRADAS_DO_BLOCO = [
  { id: "esquerda", nome: "Esquerda" },
  { id: "direita", nome: "Direita" },
  { id: "cima", nome: "De cima" },
  { id: "baixo", nome: "De baixo" },
  { id: "no-lugar", nome: "No lugar" },
] as const;

export type EntradaDoBloco = (typeof ENTRADAS_DO_BLOCO)[number]["id"];

export type SaidaDaVinheta = "esmaecer" | "sair";

export type BlocoDaVinheta = {
  id: string;
  cor: string;
  entrada: EntradaDoBloco;
  x: number;
  y: number;
  largura: number;
  altura: number;
  largura_inicial?: number;
  altura_inicial?: number;
  inicio_segundos: number;
  fim_segundos: number;
};

function tamanho_inicial_do_bloco(bloco: BlocoDaVinheta) {
  return {
    largura: bloco.largura_inicial ?? bloco.largura,
    altura: bloco.altura_inicial ?? bloco.altura,
  };
}

function origem_do_bloco(bloco: BlocoDaVinheta): { x: number; y: number } {
  const tamanho = tamanho_inicial_do_bloco(bloco);
  if (bloco.entrada === "no-lugar") {
    return { x: bloco.x, y: bloco.y };
  }
  if (bloco.entrada === "direita") {
    return { x: 1920, y: bloco.y };
  }
  if (bloco.entrada === "cima") {
    return { x: bloco.x, y: -tamanho.altura };
  }
  if (bloco.entrada === "baixo") {
    return { x: bloco.x, y: 1080 };
  }
  return { x: -tamanho.largura, y: bloco.y };
}

export const INICIO_DA_SAIDA_DA_VINHETA_EM_SEGUNDOS = 4.2;
export const FIM_DA_COREOGRAFIA_DA_VINHETA_EM_SEGUNDOS = 5;

export function progresso_da_saida_da_vinheta(tempo_coreografia: number): number {
  if (tempo_coreografia <= INICIO_DA_SAIDA_DA_VINHETA_EM_SEGUNDOS) {
    return 0;
  }
  const intervalo = FIM_DA_COREOGRAFIA_DA_VINHETA_EM_SEGUNDOS - INICIO_DA_SAIDA_DA_VINHETA_EM_SEGUNDOS;
  return Math.min(1, (tempo_coreografia - INICIO_DA_SAIDA_DA_VINHETA_EM_SEGUNDOS) / intervalo);
}

function progresso_do_bloco(bloco: BlocoDaVinheta, tempo_coreografia: number): number {
  if (tempo_coreografia <= bloco.inicio_segundos) {
    return 0;
  }
  if (tempo_coreografia >= bloco.fim_segundos) {
    return 1;
  }
  return (tempo_coreografia - bloco.inicio_segundos) / (bloco.fim_segundos - bloco.inicio_segundos);
}

function pose_do_bloco(bloco: BlocoDaVinheta, tempo_coreografia: number): RetanguloDoQuadroDaVinheta {
  const origem = origem_do_bloco(bloco);
  const progresso = progresso_do_bloco(bloco, tempo_coreografia);
  const inicial = tamanho_inicial_do_bloco(bloco);
  return {
    x: origem.x + progresso * (bloco.x - origem.x),
    y: origem.y + progresso * (bloco.y - origem.y),
    largura: inicial.largura + progresso * (bloco.largura - inicial.largura),
    altura: inicial.altura + progresso * (bloco.altura - inicial.altura),
    cor: bloco.cor,
  };
}

export function plano_do_bloco(
  bloco: BlocoDaVinheta,
  tempo_coreografia: number,
  saida_da_vinheta: SaidaDaVinheta = "esmaecer",
): RetanguloDoQuadroDaVinheta {
  const pousado = pose_do_bloco(bloco, Math.min(tempo_coreografia, INICIO_DA_SAIDA_DA_VINHETA_EM_SEGUNDOS));
  const progresso = progresso_da_saida_da_vinheta(tempo_coreografia);
  if (saida_da_vinheta === "sair" && progresso > 0) {
    const origem = origem_do_bloco(bloco);
    const inicial = tamanho_inicial_do_bloco(bloco);
    return {
      x: pousado.x + progresso * (origem.x - pousado.x),
      y: pousado.y + progresso * (origem.y - pousado.y),
      largura: pousado.largura + progresso * (inicial.largura - pousado.largura),
      altura: pousado.altura + progresso * (inicial.altura - pousado.altura),
      cor: bloco.cor,
      opacidade: 1,
    };
  }
  return {
    ...pousado,
    opacidade: 1 - progresso,
  };
}

export function bloco_novo_da_vinheta(cor: string): BlocoDaVinheta {
  return {
    id: crypto.randomUUID(),
    cor,
    entrada: "esquerda",
    x: 600,
    y: 400,
    largura: 720,
    altura: 16,
    largura_inicial: 720,
    altura_inicial: 16,
    inicio_segundos: 1,
    fim_segundos: 2.5,
  };
}
