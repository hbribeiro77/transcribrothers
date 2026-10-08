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

describe("chrome compacto da modal de anotação para destacar a imagem", () => {
  it("cabeçalho e rodapé ficam baixos", () => {
    const cab = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-cabecalho");
    expect(cab).toMatch(/padding:\s*8px 40px 8px 12px/);
    const rodape = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-rodape");
    expect(rodape).toMatch(/padding:\s*8px 12px/);
  });

  it("a barra de ferramentas é uma faixa única e baixa", () => {
    const barra = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-ferramentas");
    expect(barra).toMatch(/padding:\s*6px 12px/);
    const icone = blocoCssDoSeletorTranscribrothers(".tb-anotacao-ferramenta-icone");
    expect(icone).toMatch(/width:\s*28px/);
    expect(icone).toMatch(/height:\s*28px/);
  });

  it("‹ › entra na barra de ferramentas, sem faixa extra alta", () => {
    const nav = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-navegacao-frame");
    expect(nav).toMatch(/padding:\s*0/);
    expect(nav).toMatch(/background:\s*transparent/);
    const seta = blocoCssDoSeletorTranscribrothers(".tb-anotacao-modal-navegacao-frame-seta");
    expect(seta).toMatch(/min-width:\s*28px/);
    expect(seta).toMatch(/min-height:\s*28px/);
  });

  it("o rótulo Cores some visualmente; o grupo continua acessível", () => {
    const rotulo = blocoCssDoSeletorTranscribrothers(".tb-anotacao-seletor-cor-rotulo");
    expect(rotulo).toMatch(/position:\s*absolute/);
    expect(rotulo).toMatch(/width:\s*1px/);
  });

  it("a trilha de passos é baixa; o atual é amarelo e a casa não é vermelho de perigo", () => {
    const trilha = blocoCssDoSeletorTranscribrothers(".tb-anotacao-trilha-passos-navegacao-frame");
    expect(trilha).toMatch(/display:\s*flex/);
    const atual = blocoCssDoSeletorTranscribrothers(".tb-anotacao-trilha-traco--atual");
    expect(atual).toMatch(/#eab308/);
    const casa = blocoCssDoSeletorTranscribrothers(".tb-anotacao-trilha-traco--documento");
    expect(casa).toMatch(/#9f1239/);
    expect(casa).not.toMatch(/#dc2626/);
  });
});
