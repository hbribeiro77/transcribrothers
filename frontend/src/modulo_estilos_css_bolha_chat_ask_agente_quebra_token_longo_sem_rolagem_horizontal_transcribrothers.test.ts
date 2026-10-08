import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const cssPainelChatAskAgente = readFileSync(
  join(
    dirname(fileURLToPath(import.meta.url)),
    "componente_pagina_principal_formulario_drive_preview_tutorial.css",
  ),
  "utf8",
);

function blocoCssDoSeletorTranscribrothers(seletor: string): string {
  const escapado = seletor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const achado = cssPainelChatAskAgente.match(new RegExp(`${escapado}\\s*\\{([^}]+)\\}`));
  if (!achado?.[1]) {
    throw new Error(`Seletor ausente no CSS do chat: ${seletor}`);
  }
  return achado[1];
}

describe("bolha do chat não estoura largura com token longo", () => {
  it("trava o eixo X da lista e deixa só a rolagem vertical", () => {
    const bloco = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagens");
    expect(bloco).toMatch(/overflow-x:\s*hidden/);
    expect(bloco).toMatch(/overflow-y:\s*auto/);
  });

  it("a bolha cabe na lista e quebra nome de arquivo sem underscore", () => {
    const bolha = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagem");
    expect(bolha).toMatch(/max-width:\s*100%/);
    expect(bolha).toMatch(/min-width:\s*0/);
    expect(bolha).toMatch(/overflow-wrap:\s*anywhere/);
    const texto = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagem-texto");
    expect(texto).toMatch(/overflow-wrap:\s*anywhere/);
    const code = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagem-texto--markdown code");
    expect(code).toMatch(/overflow-wrap:\s*anywhere/);
  });

  it("pre e tabela rolam por dentro, sem empurrar o chat", () => {
    const pre = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagem-texto--markdown pre");
    expect(pre).toMatch(/max-width:\s*100%/);
    expect(pre).toMatch(/overflow-x:\s*auto/);
    const tabela = blocoCssDoSeletorTranscribrothers(".tb-chat-ask-agente-mensagem-texto--markdown table");
    expect(tabela).toMatch(/max-width:\s*100%/);
    expect(tabela).toMatch(/overflow-wrap:\s*anywhere/);
  });
});
