import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const dir = dirname(fileURLToPath(import.meta.url));
const fontePagina = readFileSync(
  join(dir, "componente_pagina_principal_formulario_drive_preview_tutorial.tsx"),
  "utf8",
);
const fonteModalAnotacao = readFileSync(
  join(dir, "componente_modal_editor_anotacao_imagem_tutorial_fabric_js_duas_versoes_transcribrothers.tsx"),
  "utf8",
);

describe("botão inserir da modal de anotação copia PNG e abre o editor Markdown", () => {
  it("a página abre o editor e foca o textarea, sem snippet nem linha tracejada", () => {
    expect(fontePagina).toContain(
      "resolverAcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngParaMarkdownTranscribrothers",
    );
    const inicio = fontePagina.indexOf(
      "const iniciarInserirImagemAssetNoDocumentoMarkdownTranscribrothers",
    );
    const fim = fontePagina.indexOf(
      "const confirmarInsercaoImagemAssetNaLinhaPreviewTutorialTranscribrothers",
    );
    expect(inicio).toBeGreaterThan(0);
    expect(fim).toBeGreaterThan(inicio);
    const handler = fontePagina.slice(inicio, fim);
    expect(handler).toContain("setModoEdicaoMarkdownTutorialAtivo(true)");
    expect(handler).toContain("textareaMarkdownEdicaoTutorialRef.current?.focus()");
    expect(handler).not.toContain("montarSnippetMarkdownImagemAssetTutorialTranscribrothers");
    expect(handler).not.toContain("copiarTextoParaAreaTransferenciaNavegadorTranscribrothers");
    expect(handler).not.toContain("setInsercaoMarkdownImagemAssetPendente");
    expect(handler).not.toContain("inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers");
    expect(handler).not.toContain("linha tracejada");
  });

  it("o botão da modal copia o PNG da tela e não grava no asset do documento", () => {
    const inicio = fonteModalAnotacao.indexOf(
      "const inserirImagemCanvasNoDocumentoMarkdownTranscribrothers",
    );
    const fim = fonteModalAnotacao.indexOf(
      "const copiarImagemEditadaParaAreaTransferenciaTranscribrothers",
    );
    expect(inicio).toBeGreaterThan(0);
    expect(fim).toBeGreaterThan(inicio);
    const handler = fonteModalAnotacao.slice(inicio, fim);
    expect(handler).toContain("copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers");
    expect(handler).toContain("exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers");
    expect(handler).not.toContain("persistirCanvasComoPngAnotadoTranscribrothers");
    expect(handler).not.toContain(
      "resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers",
    );
    expect(fonteModalAnotacao).toContain(
      "inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers",
    );
    expect(fonteModalAnotacao).toMatch(/Ctrl\+V/i);
    expect(fonteModalAnotacao).toMatch(/Não substitui a imagem do documento/i);
  });
});
