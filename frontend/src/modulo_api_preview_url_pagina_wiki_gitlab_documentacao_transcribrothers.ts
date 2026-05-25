/** GET /api/gitlab/wikis/preview-create-page-url — URL prevista {pasta}/… (somente leitura). */

export type RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers = {
  slug: string;
  web_url: string;
  wiki_url: string;
  project: string;
  prefixo_pasta_wiki: string;
  web_url_indice_workshop: string;
  pagina_destino_ja_existe_no_gitlab: boolean;
};

export async function previewUrlPaginaWikiGitlabDocumentacaoApiTranscribrothers(
  parametros: { titulo: string; jobId: string; prefixoPastaWiki?: string },
): Promise<RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers> {
  const params = new URLSearchParams({
    title: parametros.titulo.trim(),
    job_id: parametros.jobId.trim(),
  });
  const pasta = (parametros.prefixoPastaWiki ?? "").trim();
  if (pasta) {
    params.set("prefixo_pasta_wiki", pasta);
  }
  const r = await fetch(`/api/gitlab/wikis/preview-create-page-url?${params.toString()}`);
  if (!r.ok) {
    let msg = `Erro HTTP ${r.status}`;
    try {
      const j = (await r.json()) as { detail?: string };
      if (typeof j.detail === "string" && j.detail.trim()) {
        msg = j.detail.trim();
      }
    } catch {
      const texto = await r.text();
      if (texto.trim()) msg = texto.trim();
    }
    throw new Error(msg);
  }
  return (await r.json()) as RespostaPreviewUrlPaginaWikiGitlabDocumentacaoTranscribrothers;
}
