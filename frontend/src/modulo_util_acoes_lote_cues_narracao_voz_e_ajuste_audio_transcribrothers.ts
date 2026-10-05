import type { CueWebVttParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";
import { ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers } from "./modulo_util_ajustar_e_deslocar_cues_timeline_narracao_sem_sobreposicao_ui_transcribrothers.ts";

export function listarIndicesCuesElegiveisNarracaoLoteTranscribrothers(
  janelas: Array<{ semNarracao?: boolean } | null | undefined>,
  selecionados: number[],
): number[] {
  const vistos = new Set<number>();
  const saida: number[] = [];
  for (const bruto of selecionados) {
    const i = Number(bruto);
    if (!Number.isInteger(i) || i < 0 || vistos.has(i)) continue;
    if (janelas[i]?.semNarracao) continue;
    vistos.add(i);
    saida.push(i);
  }
  return saida.sort((a, b) => a - b);
}

export function aplicarVozTtsNasJanelasCuesSelecionadasTranscribrothers<
  T extends { vozTts?: string },
>(janelas: T[], indices: number[], voz: string): T[] {
  const vozNorm = (voz || "").trim();
  if (!vozNorm) return janelas.map((j) => ({ ...j }));
  const alvo = new Set(indices.filter((i) => Number.isInteger(i) && i >= 0));
  return janelas.map((j, i) => (alvo.has(i) ? { ...j, vozTts: vozNorm } : { ...j }));
}

export type ModoAjusteAudioAposNarracaoLoteTranscribrothers =
  | "nao_ajustar"
  | "so_alongar"
  | "ajustar_ao_audio";

export function ajustarCuesSelecionadasAoAudioEmOrdemTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
  indices: number[],
  duracaoPorIndice: Record<number, number | null | undefined>,
  modo: ModoAjusteAudioAposNarracaoLoteTranscribrothers = "ajustar_ao_audio",
): { cues: CueWebVttParaListaUiTranscribrothers[]; ajustadas: number; puladas: number } {
  let atual = cues.map((c) => ({ ...c }));
  let ajustadas = 0;
  let puladas = 0;
  if (modo === "nao_ajustar") {
    return { cues: atual, ajustadas: 0, puladas: indices.length };
  }
  const ordem = [...new Set(indices.filter((i) => Number.isInteger(i) && i >= 0))].sort(
    (a, b) => a - b,
  );
  for (const i of ordem) {
    const dur = duracaoPorIndice[i];
    if (typeof dur !== "number" || !(dur > 0) || !Number.isFinite(dur)) {
      puladas += 1;
      continue;
    }
    const cue = atual[i];
    const duracaoSlot = cue ? cue.fimSegundos - cue.inicioSegundos : 0;
    if (modo === "so_alongar" && !(dur > duracaoSlot)) {
      puladas += 1;
      continue;
    }
    const r = ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(atual, i, dur);
    if (!r.ok) {
      puladas += 1;
      continue;
    }
    atual = r.cues;
    ajustadas += 1;
  }
  return { cues: atual, ajustadas, puladas };
}

export function remaparIndicesSelecionadosAposExcluirTranscribrothers(
  indices: number[],
  indiceExcluido: number,
): number[] {
  const saida: number[] = [];
  for (const i of indices) {
    if (i === indiceExcluido) continue;
    saida.push(i > indiceExcluido ? i - 1 : i);
  }
  return [...new Set(saida)].sort((a, b) => a - b);
}

export function remaparIndicesSelecionadosAposInserirTranscribrothers(
  indices: number[],
  indiceInserido: number,
): number[] {
  return [...new Set(indices.map((i) => (i >= indiceInserido ? i + 1 : i)))].sort((a, b) => a - b);
}

export function remaparIndicesSelecionadosAposReordenarTranscribrothers(
  indices: number[],
  de: number,
  para: number,
): number[] {
  if (de === para) return [...indices].sort((a, b) => a - b);
  const max = Math.max(de, para, ...indices, 0);
  const arr = Array.from({ length: max + 1 }, (_, i) => indices.includes(i));
  const item = arr[de];
  arr.splice(de, 1);
  arr.splice(para, 0, item);
  const saida: number[] = [];
  arr.forEach((marcado, i) => {
    if (marcado) saida.push(i);
  });
  return saida;
}
