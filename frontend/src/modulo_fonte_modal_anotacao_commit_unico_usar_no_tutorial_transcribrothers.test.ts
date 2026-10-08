import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const fonteModalAnotacao = readFileSync(
  join(
    dirname(fileURLToPath(import.meta.url)),
    "componente_modal_editor_anotacao_imagem_tutorial_fabric_js_duas_versoes_transcribrothers.tsx",
  ),
  "utf8",
);

describe("commit único Usar no tutorial na modal de anotação", () => {
  it("o rodapé confirma com Usar no tutorial, não com Salvar versão anotada", () => {
    expect(fonteModalAnotacao).toContain(
      "ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS",
    );
    expect(fonteModalAnotacao).toContain("usarNoTutorialOQueEstaNaTelaTranscribrothers");
    expect(fonteModalAnotacao).not.toContain("Salvar versão anotada");
  });

  it("Original e Anotada não aplicam no tutorial ao clicar no toggle", () => {
    expect(fonteModalAnotacao).toContain('aria-label="Versão no editor"');
    expect(fonteModalAnotacao).not.toContain("alternarVersaoImagemExibidaNoModalETutorial");
  });

  it("não há botão Usar este frame na barra ‹ › nem Usar anotada no .md", () => {
    expect(fonteModalAnotacao).not.toContain("Usar este frame");
    expect(fonteModalAnotacao).not.toContain("Usar anotada no .md");
  });

  it("o commit da prévia lê o arquivo no cache visível, sem estado paralelo de candidato", () => {
    expect(fonteModalAnotacao).toContain(
      "resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers",
    );
    expect(fonteModalAnotacao).not.toContain("setNomeArquivoCandidatoFrame");
  });

  it("rabisco na prévia é gravado no PNG novo antes de trocar o Markdown", () => {
    expect(fonteModalAnotacao).toContain("persistirAnotacaoDoCanvas: decisao.precisaPersistirAnotacao");
    expect(fonteModalAnotacao).toContain(
      "persistirCanvasComoPngAnotadoTranscribrothers(promovido.nome_arquivo)",
    );
  });
});
