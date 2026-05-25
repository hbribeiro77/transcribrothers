/**
 * WebM de gravação de tela costuma não expor `duration` até seek ao fim.
 * Retorna função de cancelamento.
 */
export function tentarDescobrirDuracaoVideoPorSeekAoFimNavegadorTranscribrothers(
  video: HTMLVideoElement,
  aoConhecerDuracaoSegundos: (duracaoSegundos: number) => void,
): () => void {
  if (Number.isFinite(video.duration) && video.duration > 0) {
    aoConhecerDuracaoSegundos(video.duration);
    return () => undefined;
  }

  const seekable = video.seekable;
  if (seekable.length > 0) {
    const fim = seekable.end(seekable.length - 1);
    if (Number.isFinite(fim) && fim > 0) {
      aoConhecerDuracaoSegundos(fim);
      return () => undefined;
    }
  }

  if (video.readyState < 1) {
    return () => undefined;
  }

  let cancelado = false;
  const tempoAnterior = video.currentTime;

  const aoSeeked = () => {
    video.removeEventListener("seeked", aoSeeked);
    if (cancelado) return;
    const dur = video.currentTime;
    video.currentTime = tempoAnterior;
    if (Number.isFinite(dur) && dur > 0) {
      aoConhecerDuracaoSegundos(dur);
    }
  };

  video.addEventListener("seeked", aoSeeked);
  try {
    video.currentTime = 1e10;
  } catch {
    video.removeEventListener("seeked", aoSeeked);
  }

  return () => {
    cancelado = true;
    video.removeEventListener("seeked", aoSeeked);
  };
}
