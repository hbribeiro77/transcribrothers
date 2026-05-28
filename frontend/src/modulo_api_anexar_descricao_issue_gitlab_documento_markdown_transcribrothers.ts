/** POST /api/gitlab/issues/append-to-existing-issue-description — anexa Markdown à descrição da issue. */

export type RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers = {
  ok: boolean;
  web_url: string;
  issue_url: string;
  project: string;
  issue_iid: number;
  imagens_png_enviadas_gitlab?: number;
  imagens_png_ignoradas_gitlab?: number;
};

export type ParametrosAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers = {
  issueUrl: string;
  jobId: string;
  incluirImagensPngMarkdown?: boolean;
};

export async function anexarDescricaoIssueGitlabDocumentoMarkdownApiTranscribrothers(
  parametros: ParametrosAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers,
): Promise<RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers> {
  const r = await fetch("/api/gitlab/issues/append-to-existing-issue-description", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      issue_url: parametros.issueUrl.trim(),
      job_id: parametros.jobId,
      incluir_imagens_png_markdown: parametros.incluirImagensPngMarkdown !== false,
    }),
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
  return (await r.json()) as RespostaAnexarDescricaoIssueGitlabDocumentoMarkdownTranscribrothers;
}
