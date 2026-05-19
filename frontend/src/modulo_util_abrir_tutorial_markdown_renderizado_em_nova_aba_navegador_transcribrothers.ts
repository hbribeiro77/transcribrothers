import { marked } from "marked";
import { extrairTituloH1MarkdownTutorialTranscribrothers } from "./modulo_util_extrair_titulo_h1_markdown_e_sanitizar_nome_arquivo_download_tutorial_transcribrothers.ts";
import { gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers } from "./modulo_util_gerar_markdown_tutorial_com_imagens_png_embutidas_data_uri_base64_download_transcribrothers.ts";

const ESTILOS_HTML_LEITURA_TUTORIAL_MARKDOWN_NOVA_ABA_TRANSCRIBROTHERS = `
  :root {
    color-scheme: light;
  }
  * {
    box-sizing: border-box;
  }
  body {
    margin: 0;
    padding: 24px 20px 48px;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #0f172a;
    background: #f8fafc;
  }
  main {
    max-width: 920px;
    margin: 0 auto;
    padding: 28px 32px 40px;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  }
  h1 {
    font-size: 1.65rem;
    margin: 0 0 0.75em;
    line-height: 1.25;
  }
  h2 {
    font-size: 1.2rem;
    margin: 1.25em 0 0.5em;
    line-height: 1.3;
  }
  h3 {
    font-size: 1.05rem;
    margin: 1em 0 0.4em;
  }
  p,
  li {
    margin: 0.4em 0;
  }
  ul,
  ol {
    margin: 0.45em 0 0.7em;
    padding-left: 1.4em;
  }
  img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 12px 0 16px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }
  figure.tb-tutorial-nova-aba-figura {
    margin: 12px 0 16px;
  }
  figure.tb-tutorial-nova-aba-figura img {
    margin: 0;
  }
  pre {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 0.9em;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }
  code {
    font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 0.92em;
    background: #f1f5f9;
    padding: 1px 5px;
    border-radius: 4px;
  }
  pre code {
    background: transparent;
    padding: 0;
  }
  a {
    color: #1d4ed8;
  }
  .tb-tutorial-nova-aba-ts {
    color: #1d4ed8;
    font-weight: 500;
  }
`;

function substituirLinksTimestampVideoPorTextoNoHtmlLeituraTutorialTranscribrothers(html: string): string {
  return html.replace(/<a href="\?t=[^"]*">([^<]*)<\/a>/gi, '<span class="tb-tutorial-nova-aba-ts">$1</span>');
}

function envolverImagensIsoladasEmFigurasParaLeituraTutorialTranscribrothers(html: string): string {
  return html.replace(/<p>\s*(<img\b[^>]*>)\s*<\/p>/gi, '<figure class="tb-tutorial-nova-aba-figura">$1</figure>');
}

function markdownTutorialComImagensEmbutidasParaHtmlCorpoLeituraNovaAbaTranscribrothers(
  markdownComImagensDataUri: string,
): string {
  const bruto = marked.parse(markdownComImagensDataUri, { async: false, gfm: true });
  const html = typeof bruto === "string" ? bruto : "";
  return envolverImagensIsoladasEmFigurasParaLeituraTutorialTranscribrothers(
    substituirLinksTimestampVideoPorTextoNoHtmlLeituraTutorialTranscribrothers(html),
  );
}

function montarDocumentoHtmlCompletoTutorialMarkdownNovaAbaTranscribrothers(
  tituloPagina: string,
  corpoHtml: string,
): string {
  const tituloEscapado = tituloPagina
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${tituloEscapado}</title>
  <style>${ESTILOS_HTML_LEITURA_TUTORIAL_MARKDOWN_NOVA_ABA_TRANSCRIBROTHERS}</style>
</head>
<body>
  <main>${corpoHtml}</main>
</body>
</html>`;
}

export async function abrirTutorialMarkdownRenderizadoEmNovaAbaNavegadorTranscribrothers(
  markdownOriginal: string,
  jobId: string,
  resolverNomeArquivoAssetParaFetch?: (nomeArquivoNoMarkdown: string) => string,
): Promise<void> {
  const markdownComImagens =
    await gerarMarkdownTutorialComImagensPngEmbutidasComoDataUriParaArquivoDownloadTranscribrothers(
      markdownOriginal,
      jobId,
      resolverNomeArquivoAssetParaFetch,
    );
  const corpoHtml = markdownTutorialComImagensEmbutidasParaHtmlCorpoLeituraNovaAbaTranscribrothers(
    markdownComImagens,
  );
  const titulo =
    extrairTituloH1MarkdownTutorialTranscribrothers(markdownComImagens) ??
    `Tutorial TranscriBrothers — ${jobId}`;
  const documentoHtml = montarDocumentoHtmlCompletoTutorialMarkdownNovaAbaTranscribrothers(titulo, corpoHtml);

  const blob = new Blob([documentoHtml], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  // window.open(..., "noopener") costuma retornar null mesmo com sucesso — não usar isso como falha.
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 120_000);
}
