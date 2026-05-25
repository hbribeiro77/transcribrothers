/** POST /api/jobs/projeto-em-branco — projeto sem vídeo, já concluído. */

export type RespostaJobApiTranscribrothers = {
  id: string;
  status: string;
  source_kind?: string;
  drive_url?: string;
  result_markdown?: string | null;
  steps_json?: Record<string, unknown>;
  updated_at?: string;
  [chave: string]: unknown;
};

export async function criarProjetoEmBrancoJobApiTranscribrothers(): Promise<RespostaJobApiTranscribrothers> {
  const r = await fetch("/api/jobs/projeto-em-branco", { method: "POST" });
  if (!r.ok) {
    const texto = await r.text();
    throw new Error(texto || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as RespostaJobApiTranscribrothers;
}
