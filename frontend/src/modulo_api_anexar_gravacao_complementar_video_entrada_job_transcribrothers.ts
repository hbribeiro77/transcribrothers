/** Cliente API: anexar gravação complementar e unificar video_entrada do job. */

export type RespostaJobAposAnexarGravacaoComplementarTranscribrothers = {
  id: string;
  status: string;
  result_markdown?: string | null;
  steps_json?: Record<string, unknown>;
  source_kind?: string;
  error_message?: string | null;
};

async function _lerErroHttpTranscribrothers(r: Response): Promise<string> {
  const texto = await r.text();
  try {
    const j = JSON.parse(texto) as { detail?: unknown };
    if (typeof j.detail === "string" && j.detail.trim()) return j.detail.trim();
  } catch {
    /* texto bruto */
  }
  return texto || `Falha HTTP ${r.status}.`;
}

export async function anexarGravacaoComplementarVideoEntradaJobApiTranscribrothers(
  jobId: string,
  arquivoVideo: File,
): Promise<RespostaJobAposAnexarGravacaoComplementarTranscribrothers> {
  const form = new FormData();
  form.append("video", arquivoVideo, arquivoVideo.name || "complementar.mp4");
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/anexar-gravacao-complementar-video-entrada`,
    { method: "POST", body: form },
  );
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as RespostaJobAposAnexarGravacaoComplementarTranscribrothers;
}
