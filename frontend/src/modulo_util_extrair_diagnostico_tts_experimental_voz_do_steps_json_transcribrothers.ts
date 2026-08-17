/** Extrai o diagnóstico TTS do perfil experimental_voz em `steps_json`. */

export type CuePuladaDiagnosticoTtsExperimentalUiTranscribrothers = {
  indiceCue: number;
  textoPreview: string;
  motivo: string;
  tentativas: number;
  ultimoErro: string;
  latenciaMsUltima: number;
};

export type FalhaDiagnosticoTtsExperimentalUiTranscribrothers = {
  indiceCue: number;
  textoPreview: string;
  motivo: string;
  tentativa: number;
  erroCurto: string;
  latenciaMs: number;
};

export type DiagnosticoTtsExperimentalVozStepsJsonTranscribrothers = {
  perfilTts: string;
  timeoutReadSegundos: number | null;
  quantidadeCuesTotal: number;
  quantidadeCuesOk: number;
  quantidadeCuesPuladas: number;
  quantidadeTimeouts: number;
  latenciaOkMsP50: number | null;
  latenciaOkMsMax: number | null;
  cuesPuladas: CuePuladaDiagnosticoTtsExperimentalUiTranscribrothers[];
  falha: FalhaDiagnosticoTtsExperimentalUiTranscribrothers | null;
  resumoTexto: string;
};

function numeroOuNull(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

export function extrairDiagnosticoTtsExperimentalVozDoStepsJsonTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): DiagnosticoTtsExperimentalVozStepsJsonTranscribrothers | null {
  const raw = steps?.video_narrado_tts_diagnostico_experimental;
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const cuesPuladas: CuePuladaDiagnosticoTtsExperimentalUiTranscribrothers[] = [];
  if (Array.isArray(o.cues_puladas)) {
    for (const item of o.cues_puladas) {
      if (!item || typeof item !== "object") continue;
      const p = item as Record<string, unknown>;
      const indiceCue = numeroOuNull(p.indice_cue);
      if (indiceCue === null) continue;
      cuesPuladas.push({
        indiceCue,
        textoPreview: typeof p.texto_preview === "string" ? p.texto_preview : "",
        motivo: typeof p.motivo === "string" ? p.motivo : "",
        tentativas: numeroOuNull(p.tentativas) ?? 0,
        ultimoErro: typeof p.ultimo_erro === "string" ? p.ultimo_erro : "",
        latenciaMsUltima: numeroOuNull(p.latencia_ms_ultima) ?? 0,
      });
    }
  }
  let falha: FalhaDiagnosticoTtsExperimentalUiTranscribrothers | null = null;
  if (o.falha && typeof o.falha === "object") {
    const f = o.falha as Record<string, unknown>;
    const indiceCue = numeroOuNull(f.indice_cue);
    if (indiceCue !== null) {
      falha = {
        indiceCue,
        textoPreview: typeof f.texto_preview === "string" ? f.texto_preview : "",
        motivo: typeof f.motivo === "string" ? f.motivo : "",
        tentativa: numeroOuNull(f.tentativa) ?? 0,
        erroCurto: typeof f.erro_curto === "string" ? f.erro_curto : "",
        latenciaMs: numeroOuNull(f.latencia_ms) ?? 0,
      };
    }
  }
  return {
    perfilTts: typeof o.perfil_tts === "string" ? o.perfil_tts : "experimental_voz",
    timeoutReadSegundos: numeroOuNull(o.timeout_read_segundos),
    quantidadeCuesTotal: numeroOuNull(o.quantidade_cues_total) ?? 0,
    quantidadeCuesOk: numeroOuNull(o.quantidade_cues_ok) ?? 0,
    quantidadeCuesPuladas: numeroOuNull(o.quantidade_cues_puladas) ?? cuesPuladas.length,
    quantidadeTimeouts: numeroOuNull(o.quantidade_timeouts) ?? 0,
    latenciaOkMsP50: numeroOuNull(o.latencia_ok_ms_p50),
    latenciaOkMsMax: numeroOuNull(o.latencia_ok_ms_max),
    cuesPuladas,
    falha,
    resumoTexto: typeof o.resumo_texto === "string" ? o.resumo_texto : "",
  };
}
