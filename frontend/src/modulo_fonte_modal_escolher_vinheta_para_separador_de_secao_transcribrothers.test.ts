import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const dir = dirname(fileURLToPath(import.meta.url));
const fontePlayer = readFileSync(
  join(
    dir,
    "componente_modal_assistir_video_narrado_com_legendas_vtt_e_downloads_transcribrothers.tsx",
  ),
  "utf8",
);
const fonteModalVinheta = readFileSync(
  join(dir, "componente_modal_escolher_vinheta_para_separador_de_secao_transcribrothers.tsx"),
  "utf8",
);

describe("inserir separador abre modal de vinhetas com cartões", () => {
  it("o player usa a modal, não o painel inline", () => {
    expect(fontePlayer).toContain(
      "ComponenteModalEscolherVinhetaParaSeparadorDeSecaoTranscribrothers",
    );
    expect(fontePlayer).not.toContain(
      "ComponentePainelEscolherVinhetaParaSeparadorDeSecaoTranscribrothers",
    );
    expect(fontePlayer).not.toContain("tb-painel-escolher-vinheta-separador");
  });

  it("a modal é um dialog com cartões, título, prévia e sem select", () => {
    expect(fonteModalVinheta).toContain('role="dialog"');
    expect(fonteModalVinheta).toContain("montarCartoesVinhetaSeparadorDeSecaoTranscribrothers");
    expect(fonteModalVinheta).toContain("ComponentePreviaAoVivoModeloVinhetaNaModalSeparadorTranscribrothers");
    expect(fonteModalVinheta).not.toContain("<video");
    expect(fonteModalVinheta).not.toContain("montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers");
    expect(fonteModalVinheta).toMatch(/Título/);
    expect(fonteModalVinheta).not.toContain("<select");
    expect(fonteModalVinheta).toContain("createPortal");
  });

  it("a prévia grande usa o quadro do tutorial e os controles de velocidade, presença e paleta", () => {
    expect(fonteModalVinheta).toContain("url_da_imagem_de_fundo");
    expect(fonteModalVinheta).toContain("presenca_da_imagem");
    expect(fonteModalVinheta).toContain('type="range"');
    expect(fonteModalVinheta).toContain("DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS");
    expect(fonteModalVinheta).toContain("DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS");
    expect(fonteModalVinheta).toContain("PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS");
    expect(fonteModalVinheta).toContain('type="color"');
    expect(fonteModalVinheta).toMatch(/Velocidade/);
    expect(fonteModalVinheta).toMatch(/Presença/);
  });

  it("a cue do separador pode reabrir a modal para ajustar a vinheta", () => {
    expect(fontePlayer).toContain("ajustar-vinheta");
    expect(fontePlayer).toContain("mostrarAjustarVinheta");
    expect(fontePlayer).toContain("receitaVinhetaSeparador");
  });

  it("cada cartão mostra um quadro parado do efeito, não o poster roxo", () => {
    expect(fonteModalVinheta).toContain("ComponenteQuadroDaCenaVinheta");
    expect(fonteModalVinheta).toContain("tempo_de_reproducao_do_quadro_assentado");
    expect(fonteModalVinheta).not.toContain("tb-modal-escolher-vinheta-separador-card-poster");
  });

  it("a prévia encaixa o quadro do tutorial sem cortar", () => {
    const fonteQuadro = readFileSync(
      join(dir, "previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/componente_quadro_da_cena_vinheta.tsx"),
      "utf8",
    );
    const fontePrevia = readFileSync(
      join(dir, "componente_previa_ao_vivo_modelo_vinheta_na_modal_separador_transcribrothers.tsx"),
      "utf8",
    );
    expect(fonteQuadro).toContain('preserveAspectRatio="xMidYMid meet"');
    expect(fonteQuadro).not.toContain('preserveAspectRatio="xMidYMid slice"');
    expect(fontePrevia).toContain("largura");
    expect(fontePrevia).toContain("altura");
    expect(fonteModalVinheta).toContain("naturalWidth");
  });
});
