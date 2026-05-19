/**
 * Mesma regra do backend (`extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers`):
 * primeiro `# título` ATX nível 1.
 */
export function extrairTituloH1MarkdownTutorialTranscribrothers(
  markdown: string | null | undefined,
  maxCaracteres = 200,
): string | null {
  if (typeof markdown !== "string") return null;
  const texto = markdown.replace(/\r\n/g, "\n");
  for (const raw of texto.split("\n")) {
    const linha = raw.trim();
    if (!linha || linha[0] !== "#") continue;
    let nivel = 0;
    while (nivel < linha.length && linha[nivel] === "#") nivel += 1;
    if (nivel !== 1) continue;
    let resto = linha.slice(1).trimStart();
    if (!resto) continue;
    let titulo = resto.trimEnd();
    while (titulo.endsWith("#")) {
      titulo = titulo.slice(0, -1).trimEnd();
    }
    if (!titulo) continue;
    if (titulo.length > maxCaracteres) {
      return `${titulo.slice(0, maxCaracteres - 1).trimEnd()}…`;
    }
    return titulo;
  }
  return null;
}

/** Nome seguro para download no Windows (sem extensão). */
export function sanitizarNomeBaseArquivoDownloadTutorialTranscribrothers(
  nomeBruto: string,
  maxCaracteres = 120,
): string {
  let nome = nomeBruto.normalize("NFC").trim();
  nome = nome.replace(/[<>:"/\\|?*\u0000-\u001f]/g, "-");
  nome = nome.replace(/\s+/g, " ").replace(/-+/g, "-");
  nome = nome.replace(/[.\s]+$/g, "");
  if (nome.length > maxCaracteres) {
    nome = nome.slice(0, maxCaracteres).replace(/[.\s-]+$/g, "");
  }
  return nome;
}

/** Título do `# H1` ou fallback `tutorial-transcribrothers-{jobId}`. */
export function obterNomeBaseArquivoDownloadTutorialComTituloH1MarkdownOuJobIdTranscribrothers(
  markdown: string | null | undefined,
  jobId: string,
): string {
  const titulo = extrairTituloH1MarkdownTutorialTranscribrothers(markdown);
  if (titulo) {
    const sanitizado = sanitizarNomeBaseArquivoDownloadTutorialTranscribrothers(titulo);
    if (sanitizado) return sanitizado;
  }
  return `tutorial-transcribrothers-${jobId}`;
}
