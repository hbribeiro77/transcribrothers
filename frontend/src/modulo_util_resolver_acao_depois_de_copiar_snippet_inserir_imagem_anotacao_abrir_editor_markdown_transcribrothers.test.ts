import { describe, expect, it } from "vitest";

import {
  MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_ANOTADA_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
  MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
  resolverAcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers,
} from "./modulo_util_resolver_acao_depois_de_copiar_snippet_inserir_imagem_anotacao_abrir_editor_markdown_transcribrothers.ts";

describe("inserir imagem da modal de anotação abre o editor Markdown", () => {
  it("copia o snippet, abre o texto da esquerda e não usa linha tracejada nem cola sozinho", () => {
    const r = resolverAcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers({
      snippetUsaVersaoAnotada: false,
    });
    expect(r).toEqual({
      deveFecharModalAnotacao: true,
      deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true,
      deveEntrarModoLinhaTracejadaNoPreview: false,
      deveInserirSnippetNoCursorDoEditor: false,
      mensagemToastSucesso: MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
    });
    expect(r.mensagemToastSucesso).toMatch(/Ctrl\+V/);
  });

  it("na versão anotada o toast lembra que a original ficou nos assets", () => {
    const r = resolverAcaoDepoisDeCopiarSnippetInserirImagemDaModalAnotacaoTranscribrothers({
      snippetUsaVersaoAnotada: true,
    });
    expect(r.deveEntrarModoLinhaTracejadaNoPreview).toBe(false);
    expect(r.deveInserirSnippetNoCursorDoEditor).toBe(false);
    expect(r.mensagemToastSucesso).toBe(
      MENSAGEM_TOAST_COLE_SNIPPET_IMAGEM_ANOTADA_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
    );
  });
});
