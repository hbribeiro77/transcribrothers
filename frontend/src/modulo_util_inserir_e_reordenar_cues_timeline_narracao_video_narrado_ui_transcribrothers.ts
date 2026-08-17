/**
 * Inserir e reordenar cues + janelas na timeline local do editor de vídeo narrado.
 */

import type { JanelaVideoCueLocalUiTranscribrothers } from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import type { CueWebVttParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";

/** Duração do slot (timeline narrada) e da janela provisória no vídeo de entrada. */
export const DURACAO_CUE_NOVA_PROVISORIA_SEGUNDOS_TRANSCRIBROTHERS = 2.5;

export type CueTimelineComIdClienteUiTranscribrothers = CueWebVttParaListaUiTranscribrothers & {
  /** Id estável para Sortable (@dnd-kit); não vai no VTT/API. */
  idCliente: string;
};

export type ResultadoInserirCueTimelineNarracaoUiTranscribrothers = {
  cues: CueTimelineComIdClienteUiTranscribrothers[];
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
  indiceInserido: number;
};

export type ResultadoReordenarCuesTimelineNarracaoUiTranscribrothers = {
  cues: CueTimelineComIdClienteUiTranscribrothers[];
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
};

let contadorIdClienteCueNarracaoUi = 0;

export function gerarIdClienteCueTimelineNarracaoUiTranscribrothers(): string {
  contadorIdClienteCueNarracaoUi += 1;
  return `cue-ui-${Date.now().toString(36)}-${contadorIdClienteCueNarracaoUi}`;
}

export function garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
): CueTimelineComIdClienteUiTranscribrothers[] {
  return cues.map((c) => {
    const comId = c as CueTimelineComIdClienteUiTranscribrothers;
    if (typeof comId.idCliente === "string" && comId.idCliente.trim()) {
      return { ...c, idCliente: comId.idCliente };
    }
    return { ...c, idCliente: gerarIdClienteCueTimelineNarracaoUiTranscribrothers() };
  });
}

/** Remapeia Record por índice após inserir em `indiceInserido`. */
export function remaparRecordPorIndiceAposInserirUiTranscribrothers<T>(
  mapa: Record<number, T>,
  indiceInserido: number,
): Record<number, T> {
  const proximo: Record<number, T> = {};
  for (const [k, v] of Object.entries(mapa)) {
    const i = Number(k);
    if (!Number.isFinite(i)) continue;
    if (i < indiceInserido) proximo[i] = v;
    else proximo[i + 1] = v;
  }
  return proximo;
}

/** Remapeia Record por índice após mover de `de` para `para` (arrayMove). */
export function remaparRecordPorIndiceAposReordenarUiTranscribrothers<T>(
  mapa: Record<number, T>,
  de: number,
  para: number,
): Record<number, T> {
  if (de === para) return { ...mapa };
  const entradas = Object.entries(mapa)
    .map(([k, v]) => ({ i: Number(k), v }))
    .filter((e) => Number.isFinite(e.i))
    .sort((a, b) => a.i - b.i);
  if (entradas.length === 0) return {};

  const maxIdx = Math.max(...entradas.map((e) => e.i), de, para);
  const arr: Array<T | undefined> = [];
  for (let i = 0; i <= maxIdx; i++) arr[i] = undefined;
  for (const e of entradas) arr[e.i] = e.v;

  const item = arr[de];
  arr.splice(de, 1);
  arr.splice(para, 0, item);

  const proximo: Record<number, T> = {};
  arr.forEach((v, i) => {
    if (v !== undefined) proximo[i] = v;
  });
  return proximo;
}

function empacotarTemposCuesPreservandoDuracoesTranscribrothers(
  cues: CueTimelineComIdClienteUiTranscribrothers[],
): CueTimelineComIdClienteUiTranscribrothers[] {
  let t = 0;
  return cues.map((c) => {
    const dur = Math.max(0.15, (c.fimSegundos || 0) - (c.inicioSegundos || 0));
    const inicio = t;
    const fim = t + dur;
    t = fim;
    return { ...c, inicioSegundos: inicio, fimSegundos: fim };
  });
}

function arrayMoveTranscribrothers<T>(itens: T[], de: number, para: number): T[] {
  if (de < 0 || de >= itens.length || para < 0 || para >= itens.length) return [...itens];
  const copia = [...itens];
  const [item] = copia.splice(de, 1);
  copia.splice(para, 0, item);
  return copia;
}

function montarJanelaProvisoriaAncoradaNoVizinhoTranscribrothers(opts: {
  janelaVizinha: JanelaVideoCueLocalUiTranscribrothers | null;
  duracaoJanelaSegundos: number;
  duracaoVideoEntradaSegundos: number | null;
  vozPadrao: string;
}): JanelaVideoCueLocalUiTranscribrothers {
  const dur = Math.max(0.15, opts.duracaoJanelaSegundos);
  const maxVideo =
    typeof opts.duracaoVideoEntradaSegundos === "number" &&
    Number.isFinite(opts.duracaoVideoEntradaSegundos) &&
    opts.duracaoVideoEntradaSegundos > 0
      ? opts.duracaoVideoEntradaSegundos
      : null;

  let inicio = 0;
  if (opts.janelaVizinha) {
    inicio = Math.max(0, opts.janelaVizinha.fimVideoSegundos);
  }
  let fim = inicio + dur;
  if (maxVideo != null) {
    if (fim > maxVideo) {
      fim = maxVideo;
      inicio = Math.max(0, fim - dur);
    }
    if (inicio >= maxVideo) {
      inicio = Math.max(0, maxVideo - dur);
      fim = maxVideo;
    }
  }
  if (fim <= inicio) {
    fim = inicio + Math.min(dur, 0.5);
  }

  const voz = (opts.vozPadrao || "Kore").trim() || "Kore";
  return {
    inicioVideoSegundos: inicio,
    fimVideoSegundos: fim,
    temWav: false,
    urlWav: null,
    textoNarrado: "",
    textoTtsNarrado: "",
    semNarracao: false,
    vozTts: voz,
    vozNarrada: "",
    janelaProvisoria: true,
    idFonteVideo: "entrada",
  };
}

/**
 * Índice depois do qual inserir: clique (solo) tem prioridade; senão a cue destacada
 * por tempo do vídeo (ex.: #1 ao abrir em 0:00); senão a primeira.
 * Lista vazia → null (inserção no começo tratada por `inserirCueDepoisDoIndice...`).
 */
export function resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers(opts: {
  quantidadeCues: number;
  indiceSelecionadoSolo: number | null;
  indiceCueAtiva: number;
}): number | null {
  if (opts.quantidadeCues <= 0) return null;
  const solo = opts.indiceSelecionadoSolo;
  if (solo != null && solo >= 0 && solo < opts.quantidadeCues) return solo;
  if (opts.indiceCueAtiva >= 0 && opts.indiceCueAtiva < opts.quantidadeCues) {
    return opts.indiceCueAtiva;
  }
  return 0;
}

/**
 * Insere cue + janela após `indiceSelecionado` (lista vazia → índice 0).
 * Sem seleção válida com lista não vazia: anexa no final (o UI prefere passar a cue ativa por tempo).
 */
export function inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers(opts: {
  cues: CueTimelineComIdClienteUiTranscribrothers[];
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
  indiceSelecionado: number | null;
  duracaoVideoEntradaSegundos?: number | null;
  vozPadrao?: string;
  duracaoProvisoriaSegundos?: number;
}): ResultadoInserirCueTimelineNarracaoUiTranscribrothers {
  const dur =
    opts.duracaoProvisoriaSegundos ?? DURACAO_CUE_NOVA_PROVISORIA_SEGUNDOS_TRANSCRIBROTHERS;
  const cues = [...opts.cues];
  const janelas = [...opts.janelas];

  let indiceInserido: number;
  if (cues.length === 0) {
    indiceInserido = 0;
  } else if (
    opts.indiceSelecionado == null ||
    opts.indiceSelecionado < 0 ||
    opts.indiceSelecionado >= cues.length
  ) {
    indiceInserido = cues.length;
  } else {
    indiceInserido = opts.indiceSelecionado + 1;
  }

  const vizinha =
    indiceInserido > 0
      ? janelas[indiceInserido - 1] ?? null
      : janelas[0] ?? null;

  const novaCue: CueTimelineComIdClienteUiTranscribrothers = {
    idCliente: gerarIdClienteCueTimelineNarracaoUiTranscribrothers(),
    inicioSegundos: 0,
    fimSegundos: dur,
    texto: "",
    textoTts: "",
  };
  const novaJanela = montarJanelaProvisoriaAncoradaNoVizinhoTranscribrothers({
    janelaVizinha: vizinha,
    duracaoJanelaSegundos: dur,
    duracaoVideoEntradaSegundos: opts.duracaoVideoEntradaSegundos ?? null,
    vozPadrao: opts.vozPadrao || "Kore",
  });

  cues.splice(indiceInserido, 0, novaCue);
  janelas.splice(indiceInserido, 0, novaJanela);

  return {
    cues: empacotarTemposCuesPreservandoDuracoesTranscribrothers(cues),
    janelas,
    indiceInserido,
  };
}

export function reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers(opts: {
  cues: CueTimelineComIdClienteUiTranscribrothers[];
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
  indiceDe: number;
  indicePara: number;
}): ResultadoReordenarCuesTimelineNarracaoUiTranscribrothers {
  const { indiceDe, indicePara } = opts;
  if (
    indiceDe < 0 ||
    indicePara < 0 ||
    indiceDe >= opts.cues.length ||
    indicePara >= opts.cues.length
  ) {
    return { cues: [...opts.cues], janelas: [...opts.janelas] };
  }
  const cuesMovidas = arrayMoveTranscribrothers(opts.cues, indiceDe, indicePara);
  const janelasMovidas = arrayMoveTranscribrothers(opts.janelas, indiceDe, indicePara);
  return {
    cues: empacotarTemposCuesPreservandoDuracoesTranscribrothers(cuesMovidas),
    janelas: janelasMovidas,
  };
}

/**
 * Garante 1 janela por cue: corta sobras ou completa com janelas provisórias ancoradas.
 * Necessário após VTT e manifesto divergirem (ex.: geração falhou depois de gravar o VTT).
 */
export function alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers(opts: {
  quantidadeCues: number;
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
  duracaoVideoEntradaSegundos?: number | null;
  vozPadrao?: string;
  duracaoProvisoriaSegundos?: number;
}): JanelaVideoCueLocalUiTranscribrothers[] {
  const n = Math.max(0, Math.floor(opts.quantidadeCues));
  if (n === 0) return [];
  const dur =
    opts.duracaoProvisoriaSegundos ?? DURACAO_CUE_NOVA_PROVISORIA_SEGUNDOS_TRANSCRIBROTHERS;
  const voz = (opts.vozPadrao || "Kore").trim() || "Kore";
  let lista = opts.janelas.map((j) => ({ ...j }));
  if (lista.length > n) {
    return lista.slice(0, n);
  }
  while (lista.length < n) {
    const vizinha = lista.length > 0 ? lista[lista.length - 1] : null;
    lista = [
      ...lista,
      montarJanelaProvisoriaAncoradaNoVizinhoTranscribrothers({
        janelaVizinha: vizinha,
        duracaoJanelaSegundos: dur,
        duracaoVideoEntradaSegundos: opts.duracaoVideoEntradaSegundos ?? null,
        vozPadrao: voz,
      }),
    ];
  }
  return lista;
}
