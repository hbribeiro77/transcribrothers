import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const cssModalAnotacao = readFileSync(
  join(
    dirname(fileURLToPath(import.meta.url)),
    "estilos_css_modal_editor_anotacao_imagem_tutorial_fabric_js_transcribrothers.css",
  ),
  "utf8",
);

function blocoCssDoSeletorTranscribrothers(seletor: string): string {
  const escapado = seletor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const achado = cssModalAnotacao.match(new RegExp(`${escapado}\\s*\\{([^}]+)\\}`));
  if (!achado?.[1]) {
    throw new Error(`Seletor ausente no CSS da modal de anotação: ${seletor}`);
  }
  return achado[1];
}

describe("barra ‹ › na modal de anotação", () => {
  it("a barra não encolhe e não cria rolagem horizontal", () => {
    const bloco = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-navegacao-frame");
    expect(bloco).toMatch(/display:\s*flex/);
    expect(bloco).toMatch(/overflow-x:\s*hidden/);
  });

  it("as setas têm alvo de clique usável e o commit único fica no rodapé", () => {
    const seta = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-navegacao-frame-seta");
    expect(seta).toMatch(/min-width:\s*28px/);
    expect(seta).toMatch(/min-height:\s*28px/);
    const rodape = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-rodape .tb-primary");
    expect(rodape).toMatch(/min-height:\s*32px/);
    expect(cssModalAnotacao).not.toContain(".tb-anotacao-modal-btn-usar-este-frame");
  });
});
