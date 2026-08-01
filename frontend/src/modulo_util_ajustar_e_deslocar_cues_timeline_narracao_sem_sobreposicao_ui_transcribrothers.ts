import type { CueWebVttParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";

export const DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS = 0.25;
export const DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS = 0.15;
/** Mostra «Ajustar ao áudio» quando a fala ocupa menos que esta fração do slot. */
export const FRACAO_OCUPACAO_MAXIMA_PARA_AJUSTAR_CUE_AO_AUDIO_TRANSCRIBROTHERS = 0.95;

export type ResultadoMutacaoCuesTimelineUiTranscribrothers =
  | { ok: true; cues: CueWebVttParaListaUiTranscribrothers[]; deslocouSegundos: number }
  | { ok: false; motivo: string };

function clonarCuesTimelineUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
): CueWebVttParaListaUiTranscribrothers[] {
  return cues.map((c) => ({ ...c }));
}

/** Encolhe o fim da cue para `início + duraçãoAudio`, abrindo folga à direita. */
export function ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indice: number,
  duracaoAudioSegundos: number,
): ResultadoMutacaoCuesTimelineUiTranscribrothers {
  if (indice < 0 || indice >= cues.length) {
    return { ok: false, motivo: "Cue inválida." };
  }
  if (
    !(duracaoAudioSegundos > 0) ||
    !Number.isFinite(duracaoAudioSegundos) ||
    duracaoAudioSegundos < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
  ) {
    return { ok: false, motivo: "Duração de áudio indisponível para ajustar." };
  }

  const cue = cues[indice];
  const inicio = cue.inicioSegundos;
  const fimAtual = cue.fimSegundos;
  const duracaoCue = fimAtual - inicio;
  if (!(duracaoCue > 0)) {
    return { ok: false, motivo: "A cue tem intervalo inválido." };
  }

  const novoFim = inicio + duracaoAudioSegundos;
  if (novoFim >= fimAtual - 0.02) {
    return { ok: false, motivo: "O áudio já preenche (ou quase) todo o slot desta cue." };
  }
  if (novoFim - inicio < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A duração do áudio é curta demais para a cue." };
  }

  const proxima = cues[indice + 1];
  if (proxima && novoFim > proxima.inicioSegundos + 1e-6) {
    return { ok: false, motivo: "O ajuste ultrapassaria o início da cue seguinte." };
  }

  const copia = clonarCuesTimelineUiTranscribrothers(cues);
  copia[indice] = { ...copia[indice], fimSegundos: novoFim };
  return { ok: true, cues: copia, deslocouSegundos: novoFim - fimAtual };
}

/**
 * Desloca a cue inteira (mantém duração) sem sobrepor vizinhas.
 * `deltaSegundos` negativo = para a esquerda (para trás no tempo).
 */
export function deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indice: number,
  deltaSegundos: number,
): ResultadoMutacaoCuesTimelineUiTranscribrothers {
  if (indice < 0 || indice >= cues.length) {
    return { ok: false, motivo: "Cue inválida." };
  }
  if (!Number.isFinite(deltaSegundos) || Math.abs(deltaSegundos) < 1e-9) {
    return { ok: false, motivo: "Deslocamento inválido." };
  }

  const cue = cues[indice];
  const duracao = cue.fimSegundos - cue.inicioSegundos;
  if (duracao < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A cue é curta demais para deslocar." };
  }

  const limiteEsq = indice > 0 ? cues[indice - 1].fimSegundos : 0;
  const limiteDir =
    indice < cues.length - 1 ? cues[indice + 1].inicioSegundos : Number.POSITIVE_INFINITY;

  let novoInicio = cue.inicioSegundos + deltaSegundos;
  let novoFim = cue.fimSegundos + deltaSegundos;

  if (novoInicio < limiteEsq) {
    novoInicio = limiteEsq;
    novoFim = novoInicio + duracao;
  }
  if (novoFim > limiteDir) {
    novoFim = limiteDir;
    novoInicio = novoFim - duracao;
  }

  if (novoInicio < limiteEsq - 1e-9 || novoFim > limiteDir + 1e-9) {
    return {
      ok: false,
      motivo:
        deltaSegundos < 0
          ? "Sem espaço à esquerda (encostou na cue anterior ou no início)."
          : "Sem espaço à direita (encostou na cue seguinte).",
    };
  }

  const deslocou = novoInicio - cue.inicioSegundos;
  if (Math.abs(deslocou) < 1e-6) {
    return {
      ok: false,
      motivo:
        deltaSegundos < 0
          ? "Sem espaço à esquerda para deslocar."
          : "Sem espaço à direita para deslocar.",
    };
  }

  const copia = clonarCuesTimelineUiTranscribrothers(cues);
  copia[indice] = {
    ...copia[indice],
    inicioSegundos: novoInicio,
    fimSegundos: novoFim,
  };
  return { ok: true, cues: copia, deslocouSegundos: deslocou };
}

/**
 * Posiciona a cue num novo início absoluto (mantém duração), colada aos limites
 * das vizinhas e, se informado, ao fim do vídeo.
 */
export function posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indice: number,
  novoInicioDesejado: number,
  duracaoVideoMaxSegundos?: number | null,
): ResultadoMutacaoCuesTimelineUiTranscribrothers {
  if (indice < 0 || indice >= cues.length) {
    return { ok: false, motivo: "Cue inválida." };
  }
  if (!Number.isFinite(novoInicioDesejado)) {
    return { ok: false, motivo: "Início inválido." };
  }

  const cue = cues[indice];
  const duracao = cue.fimSegundos - cue.inicioSegundos;
  if (duracao < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A cue é curta demais para deslocar." };
  }

  const limiteEsq = indice > 0 ? cues[indice - 1].fimSegundos : 0;
  let limiteDir =
    indice < cues.length - 1 ? cues[indice + 1].inicioSegundos : Number.POSITIVE_INFINITY;
  if (
    typeof duracaoVideoMaxSegundos === "number" &&
    Number.isFinite(duracaoVideoMaxSegundos) &&
    duracaoVideoMaxSegundos > 0
  ) {
    limiteDir = Math.min(limiteDir, duracaoVideoMaxSegundos);
  }

  const inicioMax = limiteDir - duracao;
  if (inicioMax < limiteEsq - 1e-9) {
    return { ok: false, motivo: "Sem espaço para posicionar esta cue." };
  }

  const novoInicio = Math.max(limiteEsq, Math.min(novoInicioDesejado, inicioMax));
  const novoFim = novoInicio + duracao;
  const deslocou = novoInicio - cue.inicioSegundos;

  if (Math.abs(deslocou) < 1e-9) {
    return { ok: true, cues: clonarCuesTimelineUiTranscribrothers(cues), deslocouSegundos: 0 };
  }

  const copia = clonarCuesTimelineUiTranscribrothers(cues);
  copia[indice] = {
    ...copia[indice],
    inicioSegundos: novoInicio,
    fimSegundos: novoFim,
  };
  return { ok: true, cues: copia, deslocouSegundos: deslocou };
}

export function cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(
  duracaoCueSegundos: number,
  duracaoAudioSegundos: number | null | undefined,
): boolean {
  if (
    typeof duracaoAudioSegundos !== "number" ||
    !Number.isFinite(duracaoAudioSegundos) ||
    duracaoAudioSegundos < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
  ) {
    return false;
  }
  if (!(duracaoCueSegundos > 0)) return false;
  return (
    duracaoAudioSegundos / duracaoCueSegundos <
    FRACAO_OCUPACAO_MAXIMA_PARA_AJUSTAR_CUE_AO_AUDIO_TRANSCRIBROTHERS
  );
}

export function cuePodeDeslocarNaTimelineUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indice: number,
  sentido: "esquerda" | "direita",
): boolean {
  const delta =
    sentido === "esquerda"
      ? -DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
      : DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS;
  return deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(cues, indice, delta).ok;
}
