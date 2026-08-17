/** Perfis de motor TTS: padrão (sagrado) vs experimental (voz). */

export const PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = "padrao";
export const PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS = "experimental_voz";

export const PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS = 3;
export const PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS = 1;
export const PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS = 9;

export const TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS = 0.2;
export const TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS = 1.0;
export const TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS = 0.1;
export const TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = 0.4;

export const RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS = "lento";
export const RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS = "normal";
export const RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS = "rapido";
export const RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS = "muito_rapido";
export const RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS = RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS;

export type PerfilTtsNarracaoTranscribrothers =
  | typeof PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS
  | typeof PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS;

export type RitmoTtsNarracaoTranscribrothers =
  | typeof RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS
  | typeof RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS
  | typeof RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS
  | typeof RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS;

export type OpcaoPerfilTtsNarracaoUiTranscribrothers = {
  id: PerfilTtsNarracaoTranscribrothers;
  rotulo: string;
  descricao: string;
};

export function listarOpcoesPerfilTtsNarracaoParaUiTranscribrothers(): OpcaoPerfilTtsNarracaoUiTranscribrothers[] {
  return [
    {
      id: PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      rotulo: "Padrão (estável)",
      descricao: "Motor sagrado: comportamento estável. Use no dia a dia.",
    },
    {
      id: PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS,
      rotulo: "Experimental (voz)",
      descricao:
        "Motor isolado: notas do diretor (tom calmo estável, ritmo moderado, carioca leve). O padrão permanece texto puro.",
    },
  ];
}

export function normalizarPerfilTtsNarracaoTranscribrothers(
  valor: unknown,
): PerfilTtsNarracaoTranscribrothers {
  const t = String(valor ?? "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_")
    .replace(/\s+/g, "_");
  if (!t || t === "padrao" || t === "padrão" || t === "default" || t === "sagrado") {
    return PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
  }
  if (t === "experimental" || t === "experimental_voz" || t === "exp") {
    return PERFIL_TTS_NARRACAO_EXPERIMENTAL_VOZ_TRANSCRIBROTHERS;
  }
  return PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
}

export function rotuloPerfilTtsNarracaoParaUiTranscribrothers(perfil: unknown): string {
  const id = normalizarPerfilTtsNarracaoTranscribrothers(perfil);
  const op = listarOpcoesPerfilTtsNarracaoParaUiTranscribrothers().find((o) => o.id === id);
  return op?.rotulo ?? id;
}

export function normalizarParalelismoTtsCuesExperimentalTranscribrothers(
  valor: unknown,
): number {
  if (valor == null || valor === "") {
    return PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS;
  }
  const n = typeof valor === "number" ? valor : Number.parseInt(String(valor).trim(), 10);
  if (
    !Number.isFinite(n) ||
    n < PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS ||
    n > PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS
  ) {
    return PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS;
  }
  return Math.trunc(n);
}

export function listarOpcoesParalelismoTtsCuesExperimentalParaUiTranscribrothers(): number[] {
  const out: number[] = [];
  for (
    let i = PARALELISMO_TTS_CUES_EXPERIMENTAL_MIN_TRANSCRIBROTHERS;
    i <= PARALELISMO_TTS_CUES_EXPERIMENTAL_MAX_TRANSCRIBROTHERS;
    i += 1
  ) {
    out.push(i);
  }
  return out;
}

/** Clamp 0.2–1.0 e snap a 0.1 (half-up). Vazio/inválido → 0.4. */
export function normalizarTemperaturaTtsNarracaoTranscribrothers(valor: unknown): number {
  if (valor == null || valor === "") {
    return TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
  }
  const f = typeof valor === "number" ? valor : Number.parseFloat(String(valor).trim());
  if (!Number.isFinite(f)) {
    return TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
  }
  const clamped = Math.max(
    TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS,
    Math.min(TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS, f),
  );
  const passo = TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS;
  const n = Math.floor(clamped / passo + 0.5 + 1e-9);
  return Math.round(n * passo * 10) / 10;
}

export function formatarTemperaturaTtsNarracaoParaUiTranscribrothers(valor: number): string {
  const n = normalizarTemperaturaTtsNarracaoTranscribrothers(valor);
  return n.toFixed(1).replace(".", ",");
}

export type OpcaoRitmoTtsNarracaoUiTranscribrothers = {
  id: RitmoTtsNarracaoTranscribrothers;
  rotulo: string;
  descricao: string;
};

export function listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers(): OpcaoRitmoTtsNarracaoUiTranscribrothers[] {
  return [
    {
      id: RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS,
      rotulo: "Lento",
      descricao: "Fala mais pausada e clara.",
    },
    {
      id: RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS,
      rotulo: "Normal (padrão)",
      descricao: "Ritmo moderado do dia a dia.",
    },
    {
      id: RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS,
      rotulo: "Rápido",
      descricao: "Um pouco mais ágil, ainda inteligível.",
    },
    {
      id: RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS,
      rotulo: "Muito rápido",
      descricao: "Entrega acelerada; prioriza fluidez.",
    },
  ];
}

export function normalizarRitmoTtsNarracaoTranscribrothers(
  valor: unknown,
): RitmoTtsNarracaoTranscribrothers {
  const t = String(valor ?? "")
    .trim()
    .toLowerCase()
    .replace(/-/g, "_")
    .replace(/\s+/g, "_");
  if (!t || t === "normal" || t === "padrao" || t === "padrão" || t === "default" || t === "moderado") {
    return RITMO_TTS_NARRACAO_NORMAL_TRANSCRIBROTHERS;
  }
  if (t === "lento" || t === "slow" || t === "calmo") {
    return RITMO_TTS_NARRACAO_LENTO_TRANSCRIBROTHERS;
  }
  if (t === "rapido" || t === "rápido" || t === "fast" || t === "agil" || t === "ágil") {
    return RITMO_TTS_NARRACAO_RAPIDO_TRANSCRIBROTHERS;
  }
  if (t === "muito_rapido" || t === "muito_rápido" || t === "very_fast") {
    return RITMO_TTS_NARRACAO_MUITO_RAPIDO_TRANSCRIBROTHERS;
  }
  return RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
}

export function rotuloRitmoTtsNarracaoParaUiTranscribrothers(ritmo: unknown): string {
  const id = normalizarRitmoTtsNarracaoTranscribrothers(ritmo);
  const op = listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers().find((o) => o.id === id);
  return op?.rotulo ?? id;
}
