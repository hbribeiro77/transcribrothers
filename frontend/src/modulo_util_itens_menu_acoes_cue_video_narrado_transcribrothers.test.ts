import { describe, expect, it } from "vitest";
import { montarItensMenuAcoesCueVideoNarradoTranscribrothers } from "./modulo_util_itens_menu_acoes_cue_video_narrado_transcribrothers.ts";

describe("itens do menu de ações da cue", () => {
  it("lista Fonte, Origem, Regenerar e Excluir por último, em vermelho", () => {
    const itens = montarItensMenuAcoesCueVideoNarradoTranscribrothers({
      fonteDesabilitada: false,
      tituloFonte: "Trocar a origem (vídeo de tela) desta cue",
      origemDesabilitada: true,
      tituloOrigem: "Janela de tela ainda não disponível para esta cue",
      regenerarDesabilitada: true,
      tituloRegenerar: "Cue sem narração — use Ir para ver só o trecho de tela",
      excluirDesabilitada: true,
      tituloExcluir: "É preciso manter ao menos uma cue.",
    });

    expect(itens.map((item) => item.id)).toEqual([
      "fonte",
      "origem",
      "regenerar",
      "excluir",
    ]);
    expect(itens.map((item) => item.rotulo)).toEqual([
      "Fonte",
      "Origem",
      "Regenerar",
      "Excluir",
    ]);
    expect(itens[0]).toMatchObject({
      desabilitado: false,
      perigoso: false,
      titulo: "Trocar a origem (vídeo de tela) desta cue",
    });
    expect(itens[1]?.desabilitado).toBe(true);
    expect(itens[2]?.desabilitado).toBe(true);
    expect(itens[3]).toMatchObject({
      desabilitado: true,
      perigoso: true,
      titulo: "É preciso manter ao menos uma cue.",
    });
  });
});
