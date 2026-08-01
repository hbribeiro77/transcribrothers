/**
 * Lê a duração (segundos) de um arquivo de áudio via URL no navegador (metadata).
 * Funciona com URLs de API e com `blob:` de prévia TTS.
 */
export function obterDuracaoSegundosArquivoAudioPorUrlNavegadorTranscribrothers(
  url: string,
): Promise<number> {
  const urlNorm = String(url ?? "").trim();
  if (!urlNorm) {
    return Promise.reject(new Error("URL de áudio vazia."));
  }

  return new Promise((resolve, reject) => {
    const audio = new Audio();
    audio.preload = "metadata";

    const limpar = () => {
      audio.removeEventListener("loadedmetadata", aoMeta);
      audio.removeEventListener("error", aoErro);
      audio.src = "";
    };

    const aoMeta = () => {
      const dur = audio.duration;
      limpar();
      if (Number.isFinite(dur) && dur > 0) {
        resolve(dur);
        return;
      }
      reject(new Error("Duração de áudio indisponível."));
    };

    const aoErro = () => {
      limpar();
      reject(new Error("Falha ao carregar metadados do áudio."));
    };

    audio.addEventListener("loadedmetadata", aoMeta);
    audio.addEventListener("error", aoErro);
    audio.src = urlNorm;
  });
}

/** Percentual da cue preenchido pelo áudio atual; null se ainda não houver duração. */
export function calcularPercentualOcupacaoAudioNaCueTimelineTranscribrothers(
  duracaoAudioSegundos: number | null | undefined,
  duracaoCueSegundos: number,
): number | null {
  if (
    typeof duracaoAudioSegundos !== "number" ||
    !Number.isFinite(duracaoAudioSegundos) ||
    duracaoAudioSegundos < 0
  ) {
    return null;
  }
  if (!(duracaoCueSegundos > 0) || !Number.isFinite(duracaoCueSegundos)) {
    return null;
  }
  return (duracaoAudioSegundos / duracaoCueSegundos) * 100;
}
