import { PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS } from "./modulo_util_passo_navegacao_instante_frame_video_tutorial_transcribrothers.ts";
import { RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS } from "./modulo_util_cache_previsualizacao_frames_video_navegacao_modal_anotacao_tutorial_transcribrothers.ts";
import { formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers } from "./modulo_util_substituir_referencia_imagem_asset_e_link_temporal_markdown_tutorial_transcribrothers.ts";
import { chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers } from "./modulo_util_cache_previsualizacao_frames_video_navegacao_modal_anotacao_tutorial_transcribrothers.ts";

export type TracoTrilhaNavegacaoFrameTutorialTranscribrothers = {
  instanteSegundos: number;
  ehAtual: boolean;
  ehDocumento: boolean;
};

export type TrilhaPassosNavegacaoFrameTutorialTranscribrothers = {
  tracos: TracoTrilhaNavegacaoFrameTutorialTranscribrothers[];
  documentoForaDaJanelaNaPonta: "esquerda" | "direita" | null;
};

function limitarInstanteNaDuracaoTranscribrothers(t: number, duracao: number): number {
  if (t < 0) return 0;
  if (Number.isFinite(duracao) && duracao > 0 && t > duracao) return duracao;
  return t;
}

function indicePassosRelativosTranscribrothers(atual: number, documento: number, passo: number): number {
  return Math.round((atual - documento) / passo);
}

export function montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers(args: {
  instanteAtualSegundos: number;
  instanteDocumentoSegundos: number;
  duracaoVideoSegundos?: number;
  raio?: number;
  passoSegundos?: number;
}): TrilhaPassosNavegacaoFrameTutorialTranscribrothers {
  const passo = args.passoSegundos ?? PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS;
  const raio = args.raio ?? RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS;
  const n = raio * 2 + 1;
  const atual = Number.isFinite(args.instanteAtualSegundos) ? args.instanteAtualSegundos : 0;
  const documento = Number.isFinite(args.instanteDocumentoSegundos) ? args.instanteDocumentoSegundos : 0;
  const duracao =
    typeof args.duracaoVideoSegundos === "number" && Number.isFinite(args.duracaoVideoSegundos)
      ? args.duracaoVideoSegundos
      : Number.POSITIVE_INFINITY;

  const deltaPassos = indicePassosRelativosTranscribrothers(atual, documento, passo);
  let primeiroInstante: number;
  let documentoForaDaJanelaNaPonta: "esquerda" | "direita" | null = null;

  if (Math.abs(deltaPassos) <= raio) {
    primeiroInstante = documento - raio * passo;
  } else if (deltaPassos > raio) {
    primeiroInstante = atual - (n - 1) * passo;
    const indiceDocumento = n - 1 - deltaPassos;
    if (indiceDocumento < 0) documentoForaDaJanelaNaPonta = "esquerda";
  } else {
    primeiroInstante = atual;
    const indiceDocumento = -deltaPassos;
    if (indiceDocumento > n - 1) documentoForaDaJanelaNaPonta = "direita";
  }

  const chaveAtual = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(atual);
  const chaveDocumento = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(documento);
  const tracos: TracoTrilhaNavegacaoFrameTutorialTranscribrothers[] = [];
  for (let i = 0; i < n; i += 1) {
    const instante = limitarInstanteNaDuracaoTranscribrothers(primeiroInstante + i * passo, duracao);
    const chave = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(instante);
    const ehAtual = chave === chaveAtual;
    const ehDocumento = documentoForaDaJanelaNaPonta == null && chave === chaveDocumento;
    tracos.push({ instanteSegundos: instante, ehAtual, ehDocumento });
  }
  return { tracos, documentoForaDaJanelaNaPonta };
}

export function rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers(
  traco: TracoTrilhaNavegacaoFrameTutorialTranscribrothers,
): string {
  const hora = formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers(traco.instanteSegundos);
  if (traco.ehAtual && traco.ehDocumento) return `Frame do tutorial em ${hora}, você está aqui`;
  if (traco.ehDocumento) return `Frame usado no tutorial em ${hora}`;
  if (traco.ehAtual) return `Olhando o instante ${hora}`;
  return `Ir para ${hora}`;
}
