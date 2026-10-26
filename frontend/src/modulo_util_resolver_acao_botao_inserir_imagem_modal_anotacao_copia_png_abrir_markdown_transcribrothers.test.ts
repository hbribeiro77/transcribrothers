import { describe, expect, it } from "vitest";

import {
  MENSAGEM_TOAST_COLE_PNG_COPIADO_DA_ANOTACAO_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
  inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers,
  resolverAcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngParaMarkdownTranscribrothers,
} from "./modulo_util_resolver_acao_botao_inserir_imagem_modal_anotacao_copia_png_abrir_markdown_transcribrothers.ts";

describe("botão inserir da modal de anotação copia o PNG da tela e abre o Markdown", () => {
  it("copia o frame da tela, não grava no documento e pede Ctrl+V no Markdown", () => {
    const r = resolverAcaoBotaoInserirImagemDaModalAnotacaoComoCopiaPngParaMarkdownTranscribrothers();
    expect(r).toEqual({
      copiarPngDaTelaParaAreaTransferencia: true,
      persistirAnotacaoNoAssetDoDocumento: false,
      promoverPreviaParaSlotDoDocumento: false,
      deveFecharModalAnotacao: true,
      deveAbrirEditorMarkdownFocandoTextareaEsquerdo: true,
      deveEntrarModoLinhaTracejadaNoPreview: false,
      deveInserirSnippetNoCursorDoEditor: false,
      mensagemToastSucesso:
        MENSAGEM_TOAST_COLE_PNG_COPIADO_DA_ANOTACAO_NO_EDITOR_MARKDOWN_TRANSCRIBROTHERS,
    });
    expect(r.mensagemToastSucesso).toMatch(/Ctrl\+V/);
    expect(r.mensagemToastSucesso).toMatch(/não foi substituída/i);
  });

  it("na prévia da trilha o botão continua habilitado", () => {
    expect(
      inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers({
        processando: false,
        carregando: false,
        aguardandoPreviewAtual: false,
        candidatoFramePendente: true,
      }),
    ).toBe(false);
  });

  it("fica desabilitado só enquanto processa, carrega ou espera a prévia", () => {
    expect(
      inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers({
        processando: true,
        carregando: false,
        aguardandoPreviewAtual: false,
        candidatoFramePendente: false,
      }),
    ).toBe(true);
    expect(
      inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers({
        processando: false,
        carregando: true,
        aguardandoPreviewAtual: false,
        candidatoFramePendente: false,
      }),
    ).toBe(true);
    expect(
      inserirImagemDaModalAnotacaoDeveFicarDesabilitadoTranscribrothers({
        processando: false,
        carregando: false,
        aguardandoPreviewAtual: true,
        candidatoFramePendente: true,
      }),
    ).toBe(true);
  });
});
