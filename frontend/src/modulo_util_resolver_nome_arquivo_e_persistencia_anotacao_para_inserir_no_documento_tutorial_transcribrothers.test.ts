import { describe, expect, it } from "vitest";

import { derivarNomeArquivoPngAnotadoLocalTranscribrothers } from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";
import {
  resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers,
} from "./modulo_util_resolver_nome_arquivo_e_persistencia_anotacao_para_inserir_no_documento_tutorial_transcribrothers.ts";

describe("resolver nome e persistência ao inserir screenshot no documento", () => {
  const nomeOriginal = "screenshot_tutorial_transcribrothers_001.png";
  const nomeAnotado = derivarNomeArquivoPngAnotadoLocalTranscribrothers(nomeOriginal);

  it("insere a original sem gravar quando o canvas não foi editado", () => {
    const r = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal: nomeOriginal,
      recorteFoiAplicado: false,
      totalObjetosCanvas: 1,
      jaExisteArquivoAnotado: false,
      exibindoVersaoAnotadaNoCanvas: false,
    });
    expect(r).toEqual({
      nomeArquivoParaSnippet: nomeOriginal,
      precisaPersistirAnotacao: false,
    });
  });

  it("grava e insere a anotada quando há formas além da imagem de fundo", () => {
    const r = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal: nomeOriginal,
      recorteFoiAplicado: false,
      totalObjetosCanvas: 2,
      jaExisteArquivoAnotado: false,
      exibindoVersaoAnotadaNoCanvas: false,
    });
    expect(r).toEqual({
      nomeArquivoParaSnippet: nomeAnotado,
      precisaPersistirAnotacao: true,
    });
  });

  it("grava e insere a anotada quando houve recorte mesmo com um só objeto", () => {
    const r = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal: nomeOriginal,
      recorteFoiAplicado: true,
      totalObjetosCanvas: 1,
      jaExisteArquivoAnotado: false,
      exibindoVersaoAnotadaNoCanvas: false,
    });
    expect(r).toEqual({
      nomeArquivoParaSnippet: nomeAnotado,
      precisaPersistirAnotacao: true,
    });
  });

  it("insere a anotada já salva sem regravar se o canvas só mostra essa versão", () => {
    const r = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal: nomeOriginal,
      recorteFoiAplicado: false,
      totalObjetosCanvas: 1,
      jaExisteArquivoAnotado: true,
      exibindoVersaoAnotadaNoCanvas: true,
    });
    expect(r).toEqual({
      nomeArquivoParaSnippet: nomeAnotado,
      precisaPersistirAnotacao: false,
    });
  });

  it("regrava a anotada se o usuário editou de novo sobre a versão já salva", () => {
    const r = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal: nomeOriginal,
      recorteFoiAplicado: false,
      totalObjetosCanvas: 3,
      jaExisteArquivoAnotado: true,
      exibindoVersaoAnotadaNoCanvas: true,
    });
    expect(r).toEqual({
      nomeArquivoParaSnippet: nomeAnotado,
      precisaPersistirAnotacao: true,
    });
  });
});
