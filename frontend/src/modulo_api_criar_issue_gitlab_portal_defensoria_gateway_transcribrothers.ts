/** POST /api/gitlab/issues/create-in-project — issue no portal-defensoria-gateway (label squad::bravo). */

export type RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers = {
  ok: boolean;
  iid: number;
  web_url: string;
  issue_url: string;
  project: string;
  labels: string;
  imagens_png_enviadas_gitlab?: number;
  imagens_png_ignoradas_gitlab?: number;
};

export type ParametrosCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers = {
  titulo: string;
  jobId: string;
  incluirImagensPngMarkdown?: boolean;
};

export async function criarIssueGitlabPortalDefensoriaGatewayApiTranscribrothers(
  parametros: ParametrosCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers,
): Promise<RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers> {
  const r = await fetch("/api/gitlab/issues/create-in-project", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: parametros.titulo.trim(),
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
  return (await r.json()) as RespostaCriarIssueGitlabPortalDefensoriaGatewayTranscribrothers;
}
