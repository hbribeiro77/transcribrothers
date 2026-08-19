import type { CueWebVttParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";

export const DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS = 0.25;
export const DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS = 0.15;
/** Mostra «Ajustar ao áudio» quando |duração slot − áudio| passa deste limiar. */
export const DELTA_MIN_DISCREPANCIA_CUE_VS_AUDIO_SEGUNDOS_TRANSCRIBROTHERS = 0.2;
/** Mostra «Ajustar à tela» quando |duração slot − janela de tela| passa deste limiar. */
export const DELTA_MIN_DISCREPANCIA_CUE_VS_JANELA_TELA_SEGUNDOS_TRANSCRIBROTHERS = 0.2;

export type ResultadoMutacaoCuesTimelineUiTranscribrothers =
  | { ok: true; cues: CueWebVttParaListaUiTranscribrothers[]; deslocouSegundos: number }
  | { ok: false; motivo: string };

function clonarCuesTimelineUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
): CueWebVttParaListaUiTranscribrothers[] {
  return cues.map((c) => ({ ...c }));
}

/**
 * Ajusta o fim da cue para `início + duraçãoAudio`.
 * Encolher abre folga; esticar empurra as cues seguintes (preserva folgas que já existiam).
 */
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
  if (Math.abs(novoFim - fimAtual) < DELTA_MIN_DISCREPANCIA_CUE_VS_AUDIO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A duração da cue já está alinhada ao áudio." };
  }
  if (novoFim - inicio < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A duração do áudio é curta demais para a cue." };
  }

  const copia = clonarCuesTimelineUiTranscribrothers(cues);
  copia[indice] = { ...copia[indice], fimSegundos: novoFim };

  if (novoFim > fimAtual + 1e-9) {
    let pisoInicio = novoFim;
    for (let i = indice + 1; i < copia.length; i += 1) {
      const atual = copia[i];
      if (atual.inicioSegundos < pisoInicio - 1e-9) {
        const shift = pisoInicio - atual.inicioSegundos;
        for (let j = i; j < copia.length; j += 1) {
          copia[j] = {
            ...copia[j],
            inicioSegundos: copia[j].inicioSegundos + shift,
            fimSegundos: copia[j].fimSegundos + shift,
          };
        }
      }
      pisoInicio = copia[i].fimSegundos;
    }
  }

  return { ok: true, cues: copia, deslocouSegundos: novoFim - fimAtual };
}

/**
 * Ajusta o fim da cue para `início + duração da janela de tela`.
 * Encolher abre folga; esticar empurra as cues seguintes (preserva folgas que já existiam).
 */
export function ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indice: number,
  duracaoJanelaTelaSegundos: number,
): ResultadoMutacaoCuesTimelineUiTranscribrothers {
  if (indice < 0 || indice >= cues.length) {
    return { ok: false, motivo: "Cue inválida." };
  }
  if (
    !(duracaoJanelaTelaSegundos > 0) ||
    !Number.isFinite(duracaoJanelaTelaSegundos) ||
    duracaoJanelaTelaSegundos < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
  ) {
    return { ok: false, motivo: "Duração da janela de tela indisponível para ajustar." };
  }

  const cue = cues[indice];
  const inicio = cue.inicioSegundos;
  const fimAtual = cue.fimSegundos;
  const duracaoCue = fimAtual - inicio;
  if (!(duracaoCue > 0)) {
    return { ok: false, motivo: "A cue tem intervalo inválido." };
  }

  const novoFim = inicio + duracaoJanelaTelaSegundos;
  if (Math.abs(novoFim - fimAtual) < DELTA_MIN_DISCREPANCIA_CUE_VS_JANELA_TELA_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A duração da cue já está alinhada à janela de tela." };
  }
  if (novoFim - inicio < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS) {
    return { ok: false, motivo: "A janela de tela é curta demais para a cue." };
  }

  const copia = clonarCuesTimelineUiTranscribrothers(cues);
  copia[indice] = { ...copia[indice], fimSegundos: novoFim };

  if (novoFim > fimAtual + 1e-9) {
    let pisoInicio = novoFim;
    for (let i = indice + 1; i < copia.length; i += 1) {
      const atual = copia[i];
      if (atual.inicioSegundos < pisoInicio - 1e-9) {
        const shift = pisoInicio - atual.inicioSegundos;
        for (let j = i; j < copia.length; j += 1) {
          copia[j] = {
            ...copia[j],
            inicioSegundos: copia[j].inicioSegundos + shift,
            fimSegundos: copia[j].fimSegundos + shift,
          };
        }
      }
      pisoInicio = copia[i].fimSegundos;
    }
  }

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
    Math.abs(duracaoAudioSegundos - duracaoCueSegundos) >
    DELTA_MIN_DISCREPANCIA_CUE_VS_AUDIO_SEGUNDOS_TRANSCRIBROTHERS
  );
}

export function cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers(
  duracaoCueSegundos: number,
  duracaoJanelaTelaSegundos: number | null | undefined,
): boolean {
  if (
    typeof duracaoJanelaTelaSegundos !== "number" ||
    !Number.isFinite(duracaoJanelaTelaSegundos) ||
    duracaoJanelaTelaSegundos < DURACAO_MINIMA_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
  ) {
    return false;
  }
  if (!(duracaoCueSegundos > 0)) return false;
  return (
    Math.abs(duracaoJanelaTelaSegundos - duracaoCueSegundos) >
    DELTA_MIN_DISCREPANCIA_CUE_VS_JANELA_TELA_SEGUNDOS_TRANSCRIBROTHERS
  );
}

export type PreviewAudioDuracaoParaAjusteCueUiTranscribrothers = {
  texto: string;
  voz: string;
  duracaoSegundos: number;
};

/**
 * Duração a usar em «Ajustar ao áudio».
 * Prefere prévia válida (Prévia ou Regenerar); senão WAV gravado se o narrado ainda vale.
 */
export function resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers(opts: {
  textoFalaAtual: string;
  vozAtual: string;
  audioNarradoDesatualizado: boolean;
  preview: PreviewAudioDuracaoParaAjusteCueUiTranscribrothers | null | undefined;
  duracaoWavGravadoSegundos: number | null | undefined;
}): number | null {
  const preview = opts.preview;
  const previewBate =
    !!preview &&
    typeof preview.duracaoSegundos === "number" &&
    Number.isFinite(preview.duracaoSegundos) &&
    preview.duracaoSegundos > 0 &&
    preview.texto.trim() === (opts.textoFalaAtual || "").trim() &&
    preview.voz.trim().toLowerCase() === (opts.vozAtual || "").trim().toLowerCase();
  if (previewBate && preview) {
    return preview.duracaoSegundos;
  }
  if (opts.audioNarradoDesatualizado) {
    return null;
  }
  const durWav = opts.duracaoWavGravadoSegundos;
  return typeof durWav === "number" && Number.isFinite(durWav) && durWav > 0 ? durWav : null;
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
