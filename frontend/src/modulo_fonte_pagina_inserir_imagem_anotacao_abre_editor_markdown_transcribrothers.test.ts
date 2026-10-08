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

describe("botão inserir da modal de anotação abre o editor Markdown", () => {
  it("a página usa a decisão de abrir o editor e focar o textarea, sem modo linha tracejada", () => {
    expect(fontePagina).toContain(
      "resolverAcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers",
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
    expect(handler).not.toContain("setInsercaoMarkdownImagemAssetPendente");
    expect(handler).not.toContain("inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers");
    expect(handler).not.toContain("linha tracejada");
  });

  it("o botão da modal explica que a referência vai para o Markdown para colar", () => {
    expect(fonteModalAnotacao).toMatch(/abre o Markdown para você colar/i);
  });
});
