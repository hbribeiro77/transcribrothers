import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type ResumoJanelaVideoCueApiTranscribrothers = {
  indice: number;
  texto: string;
  inicio_video_segundos: number;
  fim_video_segundos: number;
  tem_wav: boolean;
  url_wav: string | null;
  sem_narracao?: boolean;
  voz_tts?: string;
  /** Pronúncia para TTS; vazio = igual a `texto`. */
  texto_tts?: string;
};

export type RespostaJanelasVideoCuesNarracaoJobTranscribrothers = {
  ok: boolean;
  quantidade_cues: number;
  cues: ResumoJanelaVideoCueApiTranscribrothers[];
  voz_tts_padrao_job?: string;
};

async function _lerErroHttpApiTranscribrothers(r: Response): Promise<never> {
  const t = await r.text();
  try {
    const j = JSON.parse(t) as { detail?: unknown };
    if (typeof j.detail === "string" && j.detail.trim()) {
      throw new Error(j.detail.trim());
    }
  } catch (e) {
    if (e instanceof Error && !(e instanceof SyntaxError)) throw e;
  }
  throw new Error(t || `Erro HTTP ${r.status}`);
}

export async function listarJanelasVideoCuesNarracaoJobApiTranscribrothers(
  jobId: string,
): Promise<RespostaJanelasVideoCuesNarracaoJobTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/janelas-video-cues-narracao`);
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  return (await r.json()) as RespostaJanelasVideoCuesNarracaoJobTranscribrothers;
}

export async function salvarJanelasVideoCuesNarracaoJobApiTranscribrothers(
  jobId: string,
  janelas: { inicio_video_segundos: number; fim_video_segundos: number }[],
): Promise<RespostaJanelasVideoCuesNarracaoJobTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/janelas-video-cues-narracao`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ janelas }),
  });
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  return (await r.json()) as RespostaJanelasVideoCuesNarracaoJobTranscribrothers;
}

export async function agendarRemuxVideoNarradoAposEdicaoJanelasJobApiTranscribrothers(
  jobId: string,
): Promise<JobStatus> {
  const r = await fetch(`/api/jobs/${jobId}/remux-video-narrado-apos-edicao-janelas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  return (await r.json()) as JobStatus;
}

export function urlWavNarracaoPorCueJobTranscribrothers(jobId: string, indice: number): string {
  return `/api/jobs/${jobId}/wavs-narracao-por-cue/${indice}`;
}

const FOLGA_MIN_JANELAS_UI = 0.05;

export function validarJanelasVideoSemSobreposicaoNaUiTranscribrothers(
  janelas: { inicio_video_segundos: number; fim_video_segundos: number }[],
): string | null {
  for (let i = 0; i < janelas.length; i++) {
    const a = janelas[i];
    if (!(a.fim_video_segundos >= a.inicio_video_segundos + FOLGA_MIN_JANELAS_UI)) {
      return `Cue ${i + 1}: o fim da janela deve ser maior que o início.`;
    }
    if (a.inicio_video_segundos < 0 || a.fim_video_segundos < 0) {
      return `Cue ${i + 1}: tempos não podem ser negativos.`;
    }
    if (i > 0) {
      const prev = janelas[i - 1];
      if (a.inicio_video_segundos + 1e-9 < prev.fim_video_segundos + FOLGA_MIN_JANELAS_UI) {
        return `Cue ${i + 1} sobrepõe a cue ${i}. Ajuste o início ou o fim da vizinha.`;
      }
    }
  }
  return null;
}

function temposJanelaDiferemUiTranscribrothers(
  a: { inicioVideoSegundos: number; fimVideoSegundos: number },
  b: { inicioVideoSegundos: number; fimVideoSegundos: number },
): boolean {
  return (
    Math.abs(a.inicioVideoSegundos - b.inicioVideoSegundos) > 1e-6 ||
    Math.abs(a.fimVideoSegundos - b.fimVideoSegundos) > 1e-6
  );
}

/**
 * Avisa só sobreposição envolvendo cues cujo início/fim mudou entre `antes` e `depois`.
 * Ignora conflitos pré-existentes entre cues intocadas (evita toast enganoso no apply).
 */
export function avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(
  antes: JanelaVideoCueLocalUiTranscribrothers[],
  depois: JanelaVideoCueLocalUiTranscribrothers[],
): string | null {
  if (antes.length !== depois.length) {
    return validarJanelasVideoSemSobreposicaoNaUiTranscribrothers(
      depois.map((j) => ({
        inicio_video_segundos: j.inicioVideoSegundos,
        fim_video_segundos: j.fimVideoSegundos,
      })),
    );
  }
  const indicesAlterados: number[] = [];
  for (let i = 0; i < depois.length; i++) {
    if (temposJanelaDiferemUiTranscribrothers(antes[i], depois[i])) {
      indicesAlterados.push(i);
    }
  }
  if (indicesAlterados.length === 0) return null;

  for (const indice of indicesAlterados) {
    const atual = depois[indice];
    if (!(atual.fimVideoSegundos >= atual.inicioVideoSegundos + FOLGA_MIN_JANELAS_UI)) {
      return `Cue ${indice + 1}: o fim da janela deve ser maior que o início.`;
    }
    if (atual.inicioVideoSegundos < 0 || atual.fimVideoSegundos < 0) {
      return `Cue ${indice + 1}: tempos não podem ser negativos.`;
    }
    const aviso = detectarAvisoSobreposicaoJanelaCueUiTranscribrothers(depois, indice, atual);
    if (aviso) return aviso;
  }
  return null;
}

export type JanelaVideoCueLocalUiTranscribrothers = {
  inicioVideoSegundos: number;
  fimVideoSegundos: number;
  temWav: boolean;
  urlWav: string | null;
  /**
   * Texto efetivo da última narração gravada (override TTS ou legenda).
   * Usado para saber se o áudio está desatualizado.
   */
  textoNarrado: string;
  /** Override de pronúncia persistido no manifesto (vazio = igual à legenda). */
  textoTtsNarrado: string;
  /** Trecho só com vídeo (silêncio no export; sem TTS). */
  semNarracao: boolean;
  /** Voz Gemini selecionada para esta cue (pode diferir da narrada). */
  vozTts: string;
  /** Voz com que o WAV atual foi gerado. */
  vozNarrada: string;
  /**
   * Usuário pediu nova narração (botão Regenerar): no export, força TTS/promoção
   * da prévia mesmo sem mudança de texto/voz.
   */
  forcarRegenerarTts?: boolean;
};

export function cueVozDifereDaNarradaTranscribrothers(vozAtual: string, vozNarrada: string): boolean {
  return (vozAtual || "").trim().toLowerCase() !== (vozNarrada || "").trim().toLowerCase();
}

export function normalizarTextoCueParaComparacaoUiTranscribrothers(texto: string): string {
  return (texto || "").replace(/\s+/g, " ").trim();
}

/** Texto que a TTS deve falar: override preenchido ou a legenda. */
export function textoEfetivoParaTtsCueUiTranscribrothers(
  textoLegenda: string,
  textoTts?: string | null,
): string {
  const override = normalizarTextoCueParaComparacaoUiTranscribrothers(textoTts || "");
  if (override) return override;
  return normalizarTextoCueParaComparacaoUiTranscribrothers(textoLegenda);
}

export function cueTextoDifereDoNarradoTranscribrothers(
  textoAtual: string,
  textoNarrado: string,
): boolean {
  return (
    normalizarTextoCueParaComparacaoUiTranscribrothers(textoAtual) !==
    normalizarTextoCueParaComparacaoUiTranscribrothers(textoNarrado)
  );
}

export async function gerarPreviewTtsCueNarracaoTextoAtualJobApiTranscribrothers(
  jobId: string,
  opts: {
    indice: number;
    texto: string;
    litellmModel?: string | null;
    voz?: string | null;
  },
): Promise<Blob> {
  const r = await fetch(`/api/jobs/${jobId}/preview-tts-cue-narracao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      indice: opts.indice,
      texto: opts.texto,
      litellm_model: (opts.litellmModel || "").trim() || null,
      voz: (opts.voz || "").trim() || null,
    }),
  });
  if (!r.ok) {
    await _lerErroHttpApiTranscribrothers(r);
  }
  return await r.blob();
}

export function aplicarNudgeJanelaVideoCueUiTranscribrothers(
  janelas: JanelaVideoCueLocalUiTranscribrothers[],
  indice: number,
  campo: "inicio" | "fim",
  delta: number,
): { ok: true; janelas: JanelaVideoCueLocalUiTranscribrothers[] } | { ok: false; motivo: string } {
  if (indice < 0 || indice >= janelas.length) {
    return { ok: false, motivo: "Índice inválido." };
  }
  const atual = janelas[indice];
  if (!atual) return { ok: false, motivo: "Índice inválido." };
  const novoInicio =
    campo === "inicio" ? Math.max(0, atual.inicioVideoSegundos + delta) : atual.inicioVideoSegundos;
  const novoFim =
    campo === "fim" ? Math.max(0, atual.fimVideoSegundos + delta) : atual.fimVideoSegundos;
  return aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, indice, novoInicio, novoFim);
}

export type ResultadoAplicarJanelaVideoCueUiTranscribrothers =
  | {
      ok: true;
      janelas: JanelaVideoCueLocalUiTranscribrothers[];
      /** Aviso de sobreposição (não bloqueia quando `avisarSobreposicaoSemBloquear`). */
      avisoSobreposicao: string | null;
    }
  | { ok: false; motivo: string };

function detectarAvisoSobreposicaoJanelaCueUiTranscribrothers(
  janelas: JanelaVideoCueLocalUiTranscribrothers[],
  indice: number,
  atual: JanelaVideoCueLocalUiTranscribrothers,
): string | null {
  const n = indice + 1;
  if (indice > 0) {
    const prev = janelas[indice - 1];
    if (atual.inicioVideoSegundos < prev.fimVideoSegundos + FOLGA_MIN_JANELAS_UI) {
      return `Atenção: a cue ${n} (recorte) sobrepõe a cue ${indice} (fim da anterior em ${prev.fimVideoSegundos.toFixed(3)}s).`;
    }
  }
  if (indice < janelas.length - 1) {
    const prox = janelas[indice + 1];
    if (atual.fimVideoSegundos + FOLGA_MIN_JANELAS_UI > prox.inicioVideoSegundos) {
      return `Atenção: a cue ${n} (recorte) sobrepõe a cue ${indice + 2} (início da seguinte em ${prox.inicioVideoSegundos.toFixed(3)}s).`;
    }
  }
  return null;
}

/**
 * Define início/fim absolutos da janela de tela de uma cue (vídeo original).
 * Por padrão bloqueia sobreposição (nudge no editor). Com
 * `avisarSobreposicaoSemBloquear`, aceita e devolve `avisoSobreposicao`.
 */
export function aplicarJanelaVideoCueAbsolutaUiTranscribrothers(
  janelas: JanelaVideoCueLocalUiTranscribrothers[],
  indice: number,
  inicioVideoSegundos: number,
  fimVideoSegundos: number,
  opcoes?: { avisarSobreposicaoSemBloquear?: boolean },
): ResultadoAplicarJanelaVideoCueUiTranscribrothers {
  if (indice < 0 || indice >= janelas.length) {
    return { ok: false, motivo: "Índice inválido." };
  }
  const copia = janelas.map((j) => ({ ...j }));
  const atual = {
    ...copia[indice],
    inicioVideoSegundos: Math.max(0, inicioVideoSegundos),
    fimVideoSegundos: Math.max(0, fimVideoSegundos),
  };
  if (atual.fimVideoSegundos < atual.inicioVideoSegundos + FOLGA_MIN_JANELAS_UI) {
    return { ok: false, motivo: "A janela ficaria curta demais." };
  }
  const avisoSobreposicao = detectarAvisoSobreposicaoJanelaCueUiTranscribrothers(
    copia,
    indice,
    atual,
  );
  if (avisoSobreposicao && !opcoes?.avisarSobreposicaoSemBloquear) {
    return { ok: false, motivo: avisoSobreposicao.replace(/^Atenção:\s*/i, "") };
  }
  copia[indice] = atual;
  return { ok: true, janelas: copia, avisoSobreposicao };
}

/**
 * Desliza a janela mantendo a duração atual: marca início → fim = início + duração;
 * marca fim → início = fim − duração (início não fica negativo).
 */
export function deslizarJanelaVideoCuePeloPontoUiTranscribrothers(
  janelas: JanelaVideoCueLocalUiTranscribrothers[],
  indice: number,
  campo: "inicio" | "fim",
  tempoSegundos: number,
): ResultadoAplicarJanelaVideoCueUiTranscribrothers {
  if (indice < 0 || indice >= janelas.length) {
    return { ok: false, motivo: "Índice inválido." };
  }
  const atual = janelas[indice];
  if (!atual) return { ok: false, motivo: "Índice inválido." };
  const duracao = Math.max(
    FOLGA_MIN_JANELAS_UI,
    atual.fimVideoSegundos - atual.inicioVideoSegundos,
  );
  const t = Math.max(0, tempoSegundos);
  let novoInicio: number;
  let novoFim: number;
  if (campo === "inicio") {
    novoInicio = t;
    novoFim = t + duracao;
  } else {
    novoFim = Math.max(t, FOLGA_MIN_JANELAS_UI);
    novoInicio = Math.max(0, novoFim - duracao);
    // Se bateu no zero, mantém a duração empurrando o fim.
    if (novoInicio === 0 && novoFim - novoInicio < duracao - 1e-9) {
      novoFim = duracao;
    }
  }
  return aplicarJanelaVideoCueAbsolutaUiTranscribrothers(janelas, indice, novoInicio, novoFim, {
    avisarSobreposicaoSemBloquear: true,
  });
}
