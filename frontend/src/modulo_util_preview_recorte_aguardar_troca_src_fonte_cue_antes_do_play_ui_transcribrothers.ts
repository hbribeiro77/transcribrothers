/**
 * No play contínuo em preview de recorte: se a fonte da próxima cue muda o src do
 * &lt;video&gt;, não dispara o play na mídia antiga — deixa o pedido pendente para o
 * effect após `urlVideoPlayerEfetivo` atualizar.
 */

export function previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers(opts: {
  previewRecorteAtivo: boolean;
  urlVideoPlayerAtual: string;
  urlVideoFonteAlvo: string;
}): boolean {
  if (!opts.previewRecorteAtivo) return false;
  const atual = (opts.urlVideoPlayerAtual || "").trim();
  const alvo = (opts.urlVideoFonteAlvo || "").trim();
  if (!alvo) return false;
  return atual !== alvo;
}

function caminhoDaUrlDeMidiaParaCompararPreviewRecorteUiTranscribrothers(url: string): string {
  const bruto = (url || "").trim();
  if (!bruto) return "";
  try {
    const absoluta = new URL(bruto, "http://preview.local");
    return `${absoluta.pathname}${absoluta.search}`;
  } catch {
    return bruto;
  }
}

/** O elemento já tem o arquivo da cue alvo (não o MP4 da cue anterior). */
export function previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers(opts: {
  urlAlvo: string;
  currentSrc: string;
  srcAtributo: string;
  readyState: number;
}): boolean {
  if (opts.readyState < 1) return false;
  const alvo = caminhoDaUrlDeMidiaParaCompararPreviewRecorteUiTranscribrothers(opts.urlAlvo);
  if (!alvo) return false;
  const atual = caminhoDaUrlDeMidiaParaCompararPreviewRecorteUiTranscribrothers(
    opts.currentSrc || opts.srcAtributo,
  );
  return Boolean(atual) && atual === alvo;
}

/** Depois da troca de src, só dá play com quadro no instante da janela (não no frame 0). */
export function previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers(opts: {
  currentTime: number;
  instanteAlvoSegundos: number;
  readyState: number;
  toleranciaSegundos?: number;
}): boolean {
  if (opts.readyState < 2) return false;
  const tolerancia = opts.toleranciaSegundos ?? 0.35;
  const alvo = Number.isFinite(opts.instanteAlvoSegundos) ? opts.instanteAlvoSegundos : 0;
  const atual = Number.isFinite(opts.currentTime) ? opts.currentTime : 0;
  return Math.abs(atual - alvo) <= tolerancia;
}

/** Seek de estacionar apaga o último quadro; não fazer isso se a próxima cue é outro arquivo. */
export function previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers(opts: {
  veioDoEndedDoArquivo: boolean;
  vaiTrocarSrcParaProximaCue: boolean;
}): boolean {
  if (opts.veioDoEndedDoArquivo) return false;
  if (opts.vaiTrocarSrcParaProximaCue) return false;
  return true;
}

/** Fim da janela ou ended do arquivo: avança a cadeia no play contínuo sem fala. */
export function previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers(opts: {
  continuo: boolean;
  semNarracao: boolean;
  previewJanela: boolean;
  audioAindaToca: boolean;
}): boolean {
  if (!opts.continuo) return false;
  if (opts.semNarracao) return true;
  return opts.previewJanela && !opts.audioAindaToca;
}
