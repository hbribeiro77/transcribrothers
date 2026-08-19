/**
 * Cliente API: checkpoint do editor de vídeo narrado (VTT + manifesto, sem gerar MP4).
 */

export type CueSalvarProjetoEditorVideoNarradoApiTranscribrothers = {
  inicio_segundos: number;
  fim_segundos: number;
  texto: string;
  sem_narracao?: boolean;
  voz_tts?: string;
  texto_tts?: string;
  forcar_regenerar_tts?: boolean;
};

export type JanelaSalvarProjetoEditorVideoNarradoApiTranscribrothers = {
  inicio_video_segundos: number;
  fim_video_segundos: number;
  id_fonte_video?: string;
};

export type RespostaSalvarProjetoEditorVideoNarradoApiTranscribrothers = {
  ok: boolean;
  quantidade_cues: number;
  nome_arquivo_vtt: string;
  url_asset_vtt: string;
  wavs_remapeados: number;
  previews_promovidas?: number;
  indices_previews_promovidas?: number[];
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

export async function salvarProjetoEditorVideoNarradoEdicoesModalJobApiTranscribrothers(
  jobId: string,
  opts: {
    cues: CueSalvarProjetoEditorVideoNarradoApiTranscribrothers[];
    janelas: JanelaSalvarProjetoEditorVideoNarradoApiTranscribrothers[];
  },
): Promise<RespostaSalvarProjetoEditorVideoNarradoApiTranscribrothers> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/editor-video-narrado/salvar-projeto`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cues: opts.cues, janelas: opts.janelas }),
    },
  );
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  return (await r.json()) as RespostaSalvarProjetoEditorVideoNarradoApiTranscribrothers;
}
