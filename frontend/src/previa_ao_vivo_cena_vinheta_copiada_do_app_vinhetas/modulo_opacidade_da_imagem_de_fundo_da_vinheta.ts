import { progresso_da_saida_da_vinheta } from "./modulo_movimento_do_bloco_adicionado_na_vinheta";

const OPACIDADE_MAXIMA_DA_IMAGEM_DE_FUNDO_LAVADA = 0.72;

export function opacidade_da_imagem_de_fundo(presenca: number): number {
  const limitada = Math.min(100, Math.max(0, presenca));
  return (limitada / 100) * OPACIDADE_MAXIMA_DA_IMAGEM_DE_FUNDO_LAVADA;
}

export function opacidade_da_imagem_de_fundo_no_tempo(presenca: number, tempo_coreografia: number): number {
  const lavada = opacidade_da_imagem_de_fundo(presenca);
  if (lavada <= 0) {
    return 0;
  }
  const saida = progresso_da_saida_da_vinheta(tempo_coreografia);
  return lavada + (1 - lavada) * saida;
}
