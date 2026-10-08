export const PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS = 0.4;

export function instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers(args: {
  instanteAtual: number;
  direcao: -1 | 1;
  duracaoVideoSegundos?: number;
  passoSegundos?: number;
}): number {
  const passo = args.passoSegundos ?? PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS;
  const atual = Number.isFinite(args.instanteAtual) ? args.instanteAtual : 0;
  let proximo = atual + args.direcao * passo;
  if (proximo < 0) proximo = 0;
  const duracao = args.duracaoVideoSegundos;
  if (typeof duracao === "number" && Number.isFinite(duracao) && duracao > 0 && proximo > duracao) {
    proximo = duracao;
  }
  return proximo;
}
