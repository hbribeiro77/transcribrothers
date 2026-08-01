export type RespostaGerarNarracaoTtsMarkdownJobApiTranscribrothers = {
  ok: boolean;
  mensagem: string;
  nome_arquivo: string;
  url_asset: string;
  modelo: string;
  texto_caracteres: number;
  texto_truncado: boolean;
};

export function modeloLitellmPareceTtsPeloSlugTranscribrothers(modelo: string): boolean {
  const s = (modelo || "").trim().toLowerCase();
  if (!s) return false;
  return s.includes("-tts") || s.endsWith("/tts") || s.includes("/tts-");
}

export function escolherModeloTtsDaListaDisponivelTranscribrothers(
  modelos: string[],
  preferido?: string | null,
): string | null {
  const pref = (preferido || "").trim();
  if (pref && modeloLitellmPareceTtsPeloSlugTranscribrothers(pref)) return pref;
  for (const m of modelos) {
    if (modeloLitellmPareceTtsPeloSlugTranscribrothers(m)) return m;
  }
  return null;
}

/** Modelo de chat (sem -tts) para limpeza IA / tutorial — prioriza o select das configurações. */
export function escolherModeloChatDaListaDisponivelTranscribrothers(
  modelos: string[],
  preferido?: string | null,
): string | null {
  const pref = (preferido || "").trim();
  if (pref && !modeloLitellmPareceTtsPeloSlugTranscribrothers(pref)) return pref;
  for (const m of modelos) {
    const s = (m || "").trim();
    if (s && !modeloLitellmPareceTtsPeloSlugTranscribrothers(s)) return s;
  }
  return null;
}

export async function gerarNarracaoTtsMarkdownJobApiTranscribrothers(
  jobId: string,
  litellmModel?: string | null,
): Promise<RespostaGerarNarracaoTtsMarkdownJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/gerar-narracao-tts-markdown`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      litellm_model: (litellmModel || "").trim() || null,
    }),
  });
  if (!r.ok) {
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
  return (await r.json()) as RespostaGerarNarracaoTtsMarkdownJobApiTranscribrothers;
}

export function obterUrlAssetNarracaoTtsDosStepsJsonJobTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): string | null {
  const raw = stepsJson?.narracao_tts_documento;
  if (!raw || typeof raw !== "object") return null;
  const url = (raw as { url_asset?: unknown }).url_asset;
  return typeof url === "string" && url.trim() ? url.trim() : null;
}

export type RespostaGerarVideoComNarracaoTtsJobApiTranscribrothers = {
  ok: boolean;
  mensagem: string;
  nome_arquivo: string;
  url_download: string;
};

export async function gerarVideoComNarracaoTtsJobApiTranscribrothers(
  jobId: string,
): Promise<RespostaGerarVideoComNarracaoTtsJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${jobId}/gerar-video-com-narracao-tts`, {
    method: "POST",
  });
  if (!r.ok) {
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
  return (await r.json()) as RespostaGerarVideoComNarracaoTtsJobApiTranscribrothers;
}

export function obterUrlDownloadVideoComNarracaoTtsDosStepsJsonJobTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): string | null {
  const raw = stepsJson?.video_com_narracao_tts;
  if (!raw || typeof raw !== "object") return null;
  const url = (raw as { url_download?: unknown }).url_download;
  return typeof url === "string" && url.trim() ? url.trim() : null;
}
