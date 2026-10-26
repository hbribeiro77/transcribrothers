import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const dir = dirname(fileURLToPath(import.meta.url));
const fonte = readFileSync(
  join(
    dir,
    "componente_modal_escolher_escopo_geracao_video_narrado_documento_ou_secoes_transcribrothers.tsx",
  ),
  "utf8",
);
const css = readFileSync(
  join(dir, "componente_pagina_principal_formulario_drive_preview_tutorial.css"),
  "utf8",
);

describe("modal de escopo oferece transições entre seções", () => {
  it("tem o bloco compacto de efeito e duração", () => {
    expect(fonte).toContain("Incluir transições entre seções");
    expect(fonte).toContain("Usa o título de cada seção");
    expect(fonte).toContain("incluirTransicoesSecao");
    expect(fonte).toContain("MODELOS_DE_ABERTURA_DA_VINHETA");
    expect(fonte).toContain("listarVinhetasDisponiveisParaSeparadorApiTranscribrothers");
    expect(fonte).toContain("montarCartoesVinhetaSeparadorDeSecaoTranscribrothers");
    expect(fonte).toContain("vinhetaIdTransicaoSecao");
    expect(fonte).toContain("tempo_de_reproducao_do_quadro_assentado");
    expect(fonte).toContain("aria-pressed={duracaoTransicaoSecaoSegundos === 2}");
    expect(fonte).toContain("tb-escopo-video-narrado-transicoes-duracao-btn--ativa");
    expect(css).toContain(".tb-escopo-video-narrado-transicoes-duracao-btn--ativa");
    expect(css).toMatch(
      /\.tb-escopo-video-narrado-transicoes-duracao-btn--ativa\s*\{[^}]*background:\s*#eff6ff/,
    );
  });

  it("não apaga as vinhetas salvas quando as props da modal mudam", () => {
    expect(fonte).not.toMatch(
      /setDuracaoTransicaoSecaoSegundos\(pref\.duracaoSegundos\);\s*setCartoesTransicao\(CARTOES_MODELOS_TRANSICAO_ESCOPO_PADRAO_TRANSCRIBROTHERS\)/,
    );
  });
});
