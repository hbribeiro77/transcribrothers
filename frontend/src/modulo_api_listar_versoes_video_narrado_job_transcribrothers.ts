import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

export type MetaVersaoVideoNarradoApiTranscribrothers = {
  id: string;
  criado_em: string;
  origem: string;
  escopo_modo: string;
  escopo_titulos: string[];
  voz_tts: string;
  duracao_segundos: number;
  tem_thumbnail: boolean;
  url_thumbnail?: string | null;
  url_download_mp4?: string | null;
};

export type RespostaListaVersoesVideoNarradoApiTranscribrothers = {
  versao_atual_id: string | null;
  versoes: MetaVersaoVideoNarradoApiTranscribrothers[];
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

export async function listarVersoesVideoNarradoJobApiTranscribrothers(
  jobId: string,
): Promise<RespostaListaVersoesVideoNarradoApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/videos-narrados`);
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as RespostaListaVersoesVideoNarradoApiTranscribrothers;
}

export async function tornarVersaoVideoNarradoAtualJobApiTranscribrothers(
  jobId: string,
  versaoId: string,
): Promise<JobStatus> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/videos-narrados/${encodeURIComponent(versaoId)}/tornar-atual`,
    { method: "POST" },
  );
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as JobStatus;
}

export async function apagarVersaoVideoNarradoJobApiTranscribrothers(
  jobId: string,
  versaoId: string,
): Promise<
  RespostaListaVersoesVideoNarradoApiTranscribrothers & {
    ok: boolean;
    job?: JobStatus;
  }
> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/videos-narrados/${encodeURIComponent(versaoId)}`,
    { method: "DELETE" },
  );
  if (!r.ok) throw new Error(await _lerErroHttpTranscribrothers(r));
  return (await r.json()) as RespostaListaVersoesVideoNarradoApiTranscribrothers & {
    ok: boolean;
    job?: JobStatus;
  };
}

export function urlArquivoVersaoVideoNarradoJobTranscribrothers(
  jobId: string,
  versaoId: string,
  nomeArquivo: string,
): string {
  return (
    `/api/jobs/${encodeURIComponent(jobId)}/videos-narrados/` +
    `${encodeURIComponent(versaoId)}/arquivo/${encodeURIComponent(nomeArquivo)}`
  );
}
