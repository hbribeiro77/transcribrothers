/** POST /api/gitlab/wikis/create-page-in-project — página wiki em portal-da-defensoria/documentacao (workshop/). */

export type RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers = {
  ok: boolean;
  web_url: string;
  wiki_url: string;
  project: string;
  slug: string;
  titulo: string;
  atualizada?: boolean;
  link_adicionado_no_indice_pasta?: boolean;
  imagens_png_enviadas_gitlab?: number;
  imagens_png_ignoradas_gitlab?: number;
};

export type ParametrosCriarPaginaWikiGitlabDocumentacaoTranscribrothers = {
  titulo: string;
  jobId: string;
  prefixoPastaWiki?: string;
  incluirImagensPngMarkdown?: boolean;
};

export async function criarPaginaWikiGitlabDocumentacaoApiTranscribrothers(
  parametros: ParametrosCriarPaginaWikiGitlabDocumentacaoTranscribrothers,
): Promise<RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers> {
  const body: Record<string, unknown> = {
    title: parametros.titulo.trim(),
    job_id: parametros.jobId,
    incluir_imagens_png_markdown: parametros.incluirImagensPngMarkdown !== false,
  };
  const pasta = (parametros.prefixoPastaWiki ?? "").trim();
  if (pasta) {
    body.prefixo_pasta_wiki = pasta;
  }
  const r = await fetch("/api/gitlab/wikis/create-page-in-project", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
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
  return (await r.json()) as RespostaCriarPaginaWikiGitlabDocumentacaoTranscribrothers;
}
