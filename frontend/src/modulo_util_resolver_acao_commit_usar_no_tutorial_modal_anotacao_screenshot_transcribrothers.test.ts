import { describe, expect, it } from "vitest";

import {
  ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS,
  ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_PROCESSANDO_MODAL_ANOTACAO_TRANSCRIBROTHERS,
  resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers,
} from "./modulo_util_resolver_acao_commit_usar_no_tutorial_modal_anotacao_screenshot_transcribrothers.ts";

describe("decisão do botão Usar no tutorial na modal de anotação", () => {
  it("o rótulo do commit único é Usar no tutorial", () => {
    expect(ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS).toBe(
      "Usar no tutorial",
    );
    expect(ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_PROCESSANDO_MODAL_ANOTACAO_TRANSCRIBROTHERS).toBe(
      "Aplicando…",
    );
  });

  it("na prévia de outro instante promove o frame, sem gravar anotação", () => {
    const r = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: false,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 1,
    });
    expect(r).toEqual({
      tipo: "promover_previsualizacao_frame",
      precisaPersistirAnotacao: false,
      versaoParaTutorial: null,
    });
  });

  it("na prévia, rabisco ou recorte vai junto para o tutorial como versão anotada", () => {
    const comRabisco = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: false,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 2,
    });
    expect(comRabisco).toEqual({
      tipo: "promover_previsualizacao_frame",
      precisaPersistirAnotacao: true,
      versaoParaTutorial: "anotado",
    });
    const comRecorte = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: false,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: true,
      totalObjetosCanvas: 1,
    });
    expect(comRecorte.precisaPersistirAnotacao).toBe(true);
    expect(comRecorte.versaoParaTutorial).toBe("anotado");
  });

  it("no frame do documento, vendo a original sem rabisco, usa a original e não grava .anotado.png", () => {
    const r = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: true,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 1,
    });
    expect(r).toEqual({
      tipo: "usar_original_no_tutorial",
      precisaPersistirAnotacao: false,
      versaoParaTutorial: "original",
    });
  });

  it("rabisco ou recorte sobre a original vira versão anotada e precisa gravar", () => {
    const comForma = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: true,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 2,
    });
    expect(comForma).toEqual({
      tipo: "usar_anotada_no_tutorial",
      precisaPersistirAnotacao: true,
      versaoParaTutorial: "anotado",
    });
    const comRecorte = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: true,
      versaoExibidaNoEditor: "original",
      recorteFoiAplicado: true,
      totalObjetosCanvas: 1,
    });
    expect(comRecorte.tipo).toBe("usar_anotada_no_tutorial");
    expect(comRecorte.precisaPersistirAnotacao).toBe(true);
  });

  it("vendo a anotada no editor usa a anotada; só regrava se o canvas foi editado", () => {
    const soOlhando = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: true,
      versaoExibidaNoEditor: "anotado",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 1,
    });
    expect(soOlhando).toEqual({
      tipo: "usar_anotada_no_tutorial",
      precisaPersistirAnotacao: false,
      versaoParaTutorial: "anotado",
    });
    const editouDeNovo = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: true,
      versaoExibidaNoEditor: "anotado",
      recorteFoiAplicado: false,
      totalObjetosCanvas: 3,
    });
    expect(editouDeNovo.precisaPersistirAnotacao).toBe(true);
    expect(editouDeNovo.versaoParaTutorial).toBe("anotado");
  });
});
