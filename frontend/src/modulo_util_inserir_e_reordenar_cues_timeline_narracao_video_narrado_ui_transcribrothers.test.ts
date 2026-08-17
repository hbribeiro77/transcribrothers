import { describe, expect, it } from "vitest";
import type { JanelaVideoCueLocalUiTranscribrothers } from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import {
  DURACAO_CUE_NOVA_PROVISORIA_SEGUNDOS_TRANSCRIBROTHERS,
  alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers,
  garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers,
  inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers,
  remaparRecordPorIndiceAposInserirUiTranscribrothers,
  remaparRecordPorIndiceAposReordenarUiTranscribrothers,
  reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers,
  resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers,
  type CueTimelineComIdClienteUiTranscribrothers,
} from "./modulo_util_inserir_e_reordenar_cues_timeline_narracao_video_narrado_ui_transcribrothers.ts";

function janelaBase(
  ini: number,
  fim: number,
  extra?: Partial<JanelaVideoCueLocalUiTranscribrothers>,
): JanelaVideoCueLocalUiTranscribrothers {
  return {
    inicioVideoSegundos: ini,
    fimVideoSegundos: fim,
    temWav: true,
    urlWav: "/wav",
    textoNarrado: "x",
    textoTtsNarrado: "",
    semNarracao: false,
    vozTts: "Kore",
    vozNarrada: "Kore",
    ...extra,
  };
}

function cuesDuas(): CueTimelineComIdClienteUiTranscribrothers[] {
  return garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers([
    { inicioSegundos: 0, fimSegundos: 3, texto: "a" },
    { inicioSegundos: 3, fimSegundos: 6, texto: "b" },
  ]);
}

describe("inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers", () => {
  it("insere no meio e desloca tempos das cues seguintes", () => {
    const cues = cuesDuas();
    const janelas = [janelaBase(10, 12), janelaBase(20, 25)];
    const r = inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers({
      cues,
      janelas,
      indiceSelecionado: 0,
      duracaoProvisoriaSegundos: 2.5,
    });
    expect(r.indiceInserido).toBe(1);
    expect(r.cues).toHaveLength(3);
    expect(r.janelas).toHaveLength(3);
    expect(r.cues[0].texto).toBe("a");
    expect(r.cues[1].texto).toBe("");
    expect(r.cues[2].texto).toBe("b");
    expect(r.cues[0].inicioSegundos).toBeCloseTo(0);
    expect(r.cues[0].fimSegundos).toBeCloseTo(3);
    expect(r.cues[1].inicioSegundos).toBeCloseTo(3);
    expect(r.cues[1].fimSegundos).toBeCloseTo(5.5);
    expect(r.cues[2].inicioSegundos).toBeCloseTo(5.5);
    expect(r.cues[2].fimSegundos).toBeCloseTo(8.5);
    expect(r.janelas[1].janelaProvisoria).toBe(true);
    expect(r.janelas[1].temWav).toBe(false);
    expect(r.janelas[1].inicioVideoSegundos).toBeCloseTo(12);
    expect(r.janelas[1].fimVideoSegundos).toBeCloseTo(14.5);
  });

  it("lista vazia cria a primeira cue", () => {
    const r = inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers({
      cues: [],
      janelas: [],
      indiceSelecionado: null,
    });
    expect(r.indiceInserido).toBe(0);
    expect(r.cues).toHaveLength(1);
    expect(r.cues[0].fimSegundos - r.cues[0].inicioSegundos).toBeCloseTo(
      DURACAO_CUE_NOVA_PROVISORIA_SEGUNDOS_TRANSCRIBROTHERS,
    );
    expect(r.janelas[0].janelaProvisoria).toBe(true);
  });
});

describe("alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers", () => {
  it("completa janelas faltantes como provisórias", () => {
    const r = alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers({
      quantidadeCues: 3,
      janelas: [janelaBase(0, 2), janelaBase(2, 4)],
      duracaoProvisoriaSegundos: 2.5,
    });
    expect(r).toHaveLength(3);
    expect(r[2].janelaProvisoria).toBe(true);
    expect(r[2].inicioVideoSegundos).toBeCloseTo(4);
    expect(r[2].fimVideoSegundos).toBeCloseTo(6.5);
  });

  it("corta janelas sobrando", () => {
    const r = alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers({
      quantidadeCues: 1,
      janelas: [janelaBase(0, 2), janelaBase(2, 4)],
    });
    expect(r).toHaveLength(1);
    expect(r[0].fimVideoSegundos).toBeCloseTo(2);
  });
});

describe("reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers", () => {
  it("preserva durações e realinha índices de cues/janelas", () => {
    const cues = cuesDuas();
    cues.push({
      idCliente: "c3",
      inicioSegundos: 6,
      fimSegundos: 10,
      texto: "c",
    });
    const janelas = [janelaBase(1, 2), janelaBase(3, 4), janelaBase(5, 6)];
    const r = reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers({
      cues,
      janelas,
      indiceDe: 0,
      indicePara: 2,
    });
    expect(r.cues.map((c) => c.texto)).toEqual(["b", "c", "a"]);
    expect(r.janelas.map((j) => j.inicioVideoSegundos)).toEqual([3, 5, 1]);
    expect(r.cues[0].fimSegundos - r.cues[0].inicioSegundos).toBeCloseTo(3);
    expect(r.cues[1].fimSegundos - r.cues[1].inicioSegundos).toBeCloseTo(4);
    expect(r.cues[2].fimSegundos - r.cues[2].inicioSegundos).toBeCloseTo(3);
    expect(r.cues[0].inicioSegundos).toBeCloseTo(0);
    expect(r.cues[1].inicioSegundos).toBeCloseTo(3);
    expect(r.cues[2].inicioSegundos).toBeCloseTo(7);
  });
});

describe("resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers", () => {
  it("usa cue ativa por tempo quando não houve clique (entrada em 0:00)", () => {
    expect(
      resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers({
        quantidadeCues: 14,
        indiceSelecionadoSolo: null,
        indiceCueAtiva: 0,
      }),
    ).toBe(0);
  });

  it("prioriza o clique (solo) sobre a ativa por tempo", () => {
    expect(
      resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers({
        quantidadeCues: 14,
        indiceSelecionadoSolo: 3,
        indiceCueAtiva: 0,
      }),
    ).toBe(3);
  });

  it("lista vazia retorna null", () => {
    expect(
      resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers({
        quantidadeCues: 0,
        indiceSelecionadoSolo: null,
        indiceCueAtiva: -1,
      }),
    ).toBeNull();
  });
});

describe("remaparRecordPorIndice", () => {
  it("após inserir desloca chaves >= índice", () => {
    const mapa = { 0: "a", 1: "b" };
    expect(remaparRecordPorIndiceAposInserirUiTranscribrothers(mapa, 1)).toEqual({
      0: "a",
      2: "b",
    });
  });

  it("após reordenar move entradas junto com arrayMove", () => {
    const mapa = { 0: "a", 1: "b", 2: "c" };
    expect(remaparRecordPorIndiceAposReordenarUiTranscribrothers(mapa, 0, 2)).toEqual({
      0: "b",
      1: "c",
      2: "a",
    });
  });
});
