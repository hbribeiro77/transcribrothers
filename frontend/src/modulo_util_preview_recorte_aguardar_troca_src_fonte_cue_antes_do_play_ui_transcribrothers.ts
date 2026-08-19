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
