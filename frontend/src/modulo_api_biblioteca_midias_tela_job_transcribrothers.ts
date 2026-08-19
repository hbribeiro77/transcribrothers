/**
 * Cliente API da biblioteca de mídias de tela (B-roll) por job.
 */

export const ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS = "entrada";

export type ItemBibliotecaMidiaTelaApiTranscribrothers = {
  id: string;
  nome_arquivo: string;
  nome_original: string;
  criado_em: string;
  tamanho_bytes: number;
  duracao_segundos: number | null;
  url_arquivo: string;
  eh_entrada?: boolean;
};

export type RespostaListaBibliotecaMidiasTelaApiTranscribrothers = {
  ok: boolean;
  entrada: ItemBibliotecaMidiaTelaApiTranscribrothers | null;
  itens: ItemBibliotecaMidiaTelaApiTranscribrothers[];
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

export async function listarBibliotecaMidiasTelaJobApiTranscribrothers(
  jobId: string,
): Promise<RespostaListaBibliotecaMidiasTelaApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela`);
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  return (await r.json()) as RespostaListaBibliotecaMidiasTelaApiTranscribrothers;
}

export async function enviarVideoBibliotecaMidiasTelaJobApiTranscribrothers(
  jobId: string,
  arquivo: File,
): Promise<ItemBibliotecaMidiaTelaApiTranscribrothers> {
  const form = new FormData();
  form.append("video", arquivo);
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela`, {
    method: "POST",
    body: form,
  });
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  const j = (await r.json()) as { item: ItemBibliotecaMidiaTelaApiTranscribrothers };
  return j.item;
}

export async function gerarCartaoSecaoBibliotecaMidiasTelaJobApiTranscribrothers(
  jobId: string,
  opts: {
    titulo: string;
    subtitulo?: string | null;
    duracaoSegundos?: number;
    fadeSegundos?: number;
  },
): Promise<ItemBibliotecaMidiaTelaApiTranscribrothers> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela/gerar-cartao-secao`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        titulo: opts.titulo,
        subtitulo: opts.subtitulo === undefined ? undefined : opts.subtitulo,
        duracao_segundos: opts.duracaoSegundos,
        fade_segundos: opts.fadeSegundos,
      }),
    },
  );
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
  const j = (await r.json()) as { item: ItemBibliotecaMidiaTelaApiTranscribrothers };
  return j.item;
}

export async function apagarItemBibliotecaMidiasTelaJobApiTranscribrothers(
  jobId: string,
  idMidia: string,
): Promise<void> {
  const r = await fetch(
    `/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela/${encodeURIComponent(idMidia)}`,
    { method: "DELETE" },
  );
  if (!r.ok) await _lerErroHttpApiTranscribrothers(r);
}

export function urlArquivoBibliotecaMidiasTelaJobUiTranscribrothers(
  jobId: string,
  idFonteVideo: string | null | undefined,
): string {
  const id = (idFonteVideo || "").trim();
  if (!id || id === ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS) {
    return `/api/jobs/${encodeURIComponent(jobId)}/video`;
  }
  return `/api/jobs/${encodeURIComponent(jobId)}/biblioteca-midias-tela/arquivo/${encodeURIComponent(id)}`;
}

export function normalizarIdFonteVideoUiTranscribrothers(
  idFonte: string | null | undefined,
): string {
  const id = (idFonte || "").trim();
  if (!id || id === ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS) {
    return ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS;
  }
  return id;
}
