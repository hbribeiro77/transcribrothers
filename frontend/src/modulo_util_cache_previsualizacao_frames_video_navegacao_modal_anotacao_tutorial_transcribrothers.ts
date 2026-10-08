import { PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS } from "./modulo_util_passo_navegacao_instante_frame_video_tutorial_transcribrothers.ts";

export const RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS = 5;

export type ItemCachePreviewFrameNavegacaoTutorialTranscribrothers = {
  instanteSegundos: number;
  nomeArquivoPreview: string;
  urlPreview: string;
};

export type ExibicaoCanvasNavegacaoFrameTutorialTranscribrothers = {
  origem: "documento" | "previsualizacao" | "faltando";
  nomeArquivoCanvas: string | null;
  urlImagem: string | null;
};

export function chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(segundos: number): string {
  const t = Number.isFinite(segundos) ? segundos : 0;
  return (Math.round(t * 10) / 10).toFixed(1);
}

export function instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(
  instanteAlvoSegundos: number,
  instanteDocumentoSegundos: number | null,
): boolean {
  if (instanteDocumentoSegundos == null || !Number.isFinite(instanteDocumentoSegundos)) return false;
  return (
    chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(instanteAlvoSegundos) ===
    chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(instanteDocumentoSegundos)
  );
}

export function devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers(args: {
  temMarcacoesNaoSalvasNoCanvas: boolean;
  temArquivoAnotadoSalvoNoDocumento: boolean;
  exibindoVersaoAnotada: boolean;
}): boolean {
  void args.temArquivoAnotadoSalvoNoDocumento;
  void args.exibindoVersaoAnotada;
  return args.temMarcacoesNaoSalvasNoCanvas;
}

export function devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers(args: {
  temArquivoAnotadoSalvoNoDocumento: boolean;
  saindoDoSlotDocumento: boolean;
}): boolean {
  return args.temArquivoAnotadoSalvoNoDocumento && args.saindoDoSlotDocumento;
}

export function urlPrevisualizacaoFrameNavegacaoTutorialTranscribrothers(
  jobId: string,
  nomeArquivoPreview: string,
): string {
  return `/api/jobs/${jobId}/previsualizar-frames-video-tutorial/${encodeURIComponent(nomeArquivoPreview)}`;
}

export function montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers(args: {
  centroSegundos: number;
  instanteDocumentoSegundos: number | null;
  duracaoVideoSegundos?: number;
  raio?: number;
  passoSegundos?: number;
}): number[] {
  const passo = args.passoSegundos ?? PASSO_SEGUNDOS_NAVEGACAO_FRAME_VIDEO_TUTORIAL_TRANSCRIBROTHERS;
  const raio = args.raio ?? RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS;
  const centro = Number.isFinite(args.centroSegundos) ? args.centroSegundos : 0;
  const duracao =
    typeof args.duracaoVideoSegundos === "number" &&
    Number.isFinite(args.duracaoVideoSegundos) &&
    args.duracaoVideoSegundos > 0
      ? args.duracaoVideoSegundos
      : Number.POSITIVE_INFINITY;
  const saida: number[] = [];
  const vistos = new Set<string>();
  for (let k = -raio; k <= raio; k += 1) {
    if (k === 0) continue;
    let t = centro + k * passo;
    if (t < 0) t = 0;
    if (t > duracao) t = duracao;
    if (instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(t, args.instanteDocumentoSegundos)) {
      continue;
    }
    const chave = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(t);
    if (vistos.has(chave)) continue;
    vistos.add(chave);
    saida.push(t);
  }
  return saida;
}

export function resolverExibicaoCanvasNavegacaoFrameTutorialTranscribrothers(args: {
  instanteAlvoSegundos: number;
  instanteDocumentoSegundos: number | null;
  nomeArquivoOriginalDocumento: string;
  nomeArquivoAnotadoDocumento?: string | null;
  temArquivoAnotado: boolean;
  cachePreviewsPorChave: Record<string, ItemCachePreviewFrameNavegacaoTutorialTranscribrothers>;
}): ExibicaoCanvasNavegacaoFrameTutorialTranscribrothers {
  if (
    instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(
      args.instanteAlvoSegundos,
      args.instanteDocumentoSegundos,
    )
  ) {
    const anotado = (args.nomeArquivoAnotadoDocumento || "").trim();
    const nomeCanvas =
      args.temArquivoAnotado && anotado ? anotado : args.nomeArquivoOriginalDocumento;
    return { origem: "documento", nomeArquivoCanvas: nomeCanvas, urlImagem: null };
  }
  const chave = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(args.instanteAlvoSegundos);
  const preview = args.cachePreviewsPorChave[chave];
  if (preview?.urlPreview) {
    return { origem: "previsualizacao", nomeArquivoCanvas: preview.nomeArquivoPreview, urlImagem: preview.urlPreview };
  }
  return { origem: "faltando", nomeArquivoCanvas: null, urlImagem: null };
}

export function resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers(args: {
  noSlotDocumento: boolean;
  instanteExibidoSegundos: number | null;
  instanteDocumentoSegundos: number | null;
  cachePreviewsPorChave: Record<string, ItemCachePreviewFrameNavegacaoTutorialTranscribrothers>;
}): string | null {
  if (args.noSlotDocumento) return null;
  if (args.instanteExibidoSegundos == null || !Number.isFinite(args.instanteExibidoSegundos)) {
    return null;
  }
  const exibicao = resolverExibicaoCanvasNavegacaoFrameTutorialTranscribrothers({
    instanteAlvoSegundos: args.instanteExibidoSegundos,
    instanteDocumentoSegundos: args.instanteDocumentoSegundos,
    nomeArquivoOriginalDocumento: "",
    temArquivoAnotado: false,
    cachePreviewsPorChave: args.cachePreviewsPorChave,
  });
  if (exibicao.origem !== "previsualizacao") return null;
  const nome = (exibicao.nomeArquivoCanvas || "").trim();
  return nome || null;
}

export function nomesArquivoPreviewParaDescartarNavegacaoFrameTutorialTranscribrothers(args: {
  nomesPreviewEmCache: string[];
  nomesProtegidosDocumento: string[];
  nomePreviewPromovido?: string | null;
}): string[] {
  const protegidos = new Set(
    args.nomesProtegidosDocumento.map((n) => n.trim()).filter(Boolean),
  );
  const promovido = (args.nomePreviewPromovido || "").trim();
  if (promovido) protegidos.add(promovido);
  const vistos = new Set<string>();
  const saida: string[] = [];
  for (const bruto of args.nomesPreviewEmCache) {
    const nome = bruto.trim();
    if (!nome || protegidos.has(nome) || vistos.has(nome)) continue;
    vistos.add(nome);
    saida.push(nome);
  }
  return saida;
}
