import { describe, expect, it } from "vitest";
import { usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers } from "./modulo_util_substituir_referencia_imagem_asset_e_link_temporal_markdown_tutorial_transcribrothers.ts";
import {
  RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS,
  chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers,
  devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers,
  devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers,
  instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers,
  montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers,
  nomesArquivoPreviewParaDescartarNavegacaoFrameTutorialTranscribrothers,
  resolverExibicaoCanvasNavegacaoFrameTutorialTranscribrothers,
  resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers,
  urlPrevisualizacaoFrameNavegacaoTutorialTranscribrothers,
} from "./modulo_util_cache_previsualizacao_frames_video_navegacao_modal_anotacao_tutorial_transcribrothers.ts";

describe("cache de prévia ±5 e slot anotado do documento", () => {
  it("usa raio 5 e não pede confirmação só porque a imagem do documento está anotada", () => {
    expect(RAIO_PREFETCH_FRAMES_NAVEGACAO_TUTORIAL_TRANSCRIBROTHERS).toBe(5);
    expect(
      devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers({
        temMarcacoesNaoSalvasNoCanvas: false,
        temArquivoAnotadoSalvoNoDocumento: true,
        exibindoVersaoAnotada: true,
      }),
    ).toBe(false);
    expect(
      devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers({
        temMarcacoesNaoSalvasNoCanvas: true,
        temArquivoAnotadoSalvoNoDocumento: true,
        exibindoVersaoAnotada: false,
      }),
    ).toBe(true);
  });

  it("ao voltar ao instante do documento reabre a versão anotada, sem recapturar", () => {
    const instanteDocumento = 31.7;
    expect(
      instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(31.7, instanteDocumento),
    ).toBe(true);
    expect(
      instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(32.1, instanteDocumento),
    ).toBe(false);
    const casa = resolverExibicaoCanvasNavegacaoFrameTutorialTranscribrothers({
      instanteAlvoSegundos: 31.7,
      instanteDocumentoSegundos: 31.7,
      nomeArquivoOriginalDocumento: "tela.png",
      nomeArquivoAnotadoDocumento: "tela.anotado.png",
      temArquivoAnotado: true,
      cachePreviewsPorChave: {
        [chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(32.1)]: {
          instanteSegundos: 32.1,
          nomeArquivoPreview: "preview_32.png",
          urlPreview: "/api/jobs/j/previsualizar-frames-video-tutorial/preview_32.png",
        },
      },
    });
    expect(casa.origem).toBe("documento");
    expect(casa.nomeArquivoCanvas).toBe("tela.anotado.png");
    expect(casa.urlImagem).toBeNull();
    const vizinho = resolverExibicaoCanvasNavegacaoFrameTutorialTranscribrothers({
      instanteAlvoSegundos: 32.1,
      instanteDocumentoSegundos: 31.7,
      nomeArquivoOriginalDocumento: "tela.png",
      nomeArquivoAnotadoDocumento: "tela.anotado.png",
      temArquivoAnotado: true,
      cachePreviewsPorChave: {
        [chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(32.1)]: {
          instanteSegundos: 32.1,
          nomeArquivoPreview: "preview_32.png",
          urlPreview: "/api/jobs/j/previsualizar-frames-video-tutorial/preview_32.png",
        },
      },
    });
    expect(vizinho.origem).toBe("previsualizacao");
    expect(vizinho.urlImagem).toContain("preview_32.png");
  });

  it("monta ±5 instantes sem incluir o slot do documento e sem sair da duração", () => {
    const lista = montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers({
      centroSegundos: 31.7,
      instanteDocumentoSegundos: 31.7,
      duracaoVideoSegundos: 120,
    });
    expect(lista).toHaveLength(10);
    expect(lista).not.toContainEqual(expect.closeTo(31.7, 5));
    expect(lista[0]).toBeCloseTo(29.7, 5);
    expect(lista[lista.length - 1]).toBeCloseTo(33.7, 5);
    const noInicio = montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers({
      centroSegundos: 0.4,
      instanteDocumentoSegundos: 0.4,
      duracaoVideoSegundos: 10,
    });
    expect(noInicio.every((t) => t >= 0 && t <= 10)).toBe(true);
    expect(noInicio.some((t) => Math.abs(t - 0.4) < 0.0005)).toBe(false);
  });

  it("descarta só prévias, nunca o PNG do documento nem o .anotado.png", () => {
    const nomes = nomesArquivoPreviewParaDescartarNavegacaoFrameTutorialTranscribrothers({
      nomesPreviewEmCache: ["prev_a.png", "prev_b.png", "tela.png"],
      nomesProtegidosDocumento: ["tela.png", "tela.anotado.png"],
      nomePreviewPromovido: "prev_b.png",
    });
    expect(nomes).toEqual(["prev_a.png"]);
    expect(nomes).not.toContain("tela.png");
    expect(nomes).not.toContain("tela.anotado.png");
  });

  it("avisa na confirmação só ao usar um frame que sai do documento anotado", () => {
    expect(
      devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers({
        temArquivoAnotadoSalvoNoDocumento: true,
        saindoDoSlotDocumento: true,
      }),
    ).toBe(true);
    expect(
      devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers({
        temArquivoAnotadoSalvoNoDocumento: true,
        saindoDoSlotDocumento: false,
      }),
    ).toBe(false);
    expect(
      urlPrevisualizacaoFrameNavegacaoTutorialTranscribrothers("job-1", "prev_a.png"),
    ).toBe("/api/jobs/job-1/previsualizar-frames-video-tutorial/prev_a.png");
  });

  it("no primeiro instante vizinho o Usar no tutorial usa o PNG da prévia já no cache", () => {
    const instanteDocumento = 246.0;
    const instanteVizinho = 246.4;
    const cache = {
      [chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(instanteVizinho)]: {
        instanteSegundos: instanteVizinho,
        nomeArquivoPreview: "preview_navegacao_frame_tutorial_2464.png",
        urlPreview: "/api/jobs/j/previsualizar-frames-video-tutorial/preview_navegacao_frame_tutorial_2464.png",
      },
    };
    const candidato = resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers({
      noSlotDocumento: false,
      instanteExibidoSegundos: instanteVizinho,
      instanteDocumentoSegundos: instanteDocumento,
      cachePreviewsPorChave: cache,
    });
    expect(candidato).toBe("preview_navegacao_frame_tutorial_2464.png");
    expect(
      usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers({
        nomeArquivoNoDocumento: "tela.png",
        nomeArquivoCandidato: candidato,
        capturando: false,
      }),
    ).toBe(true);
    expect(
      resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers({
        noSlotDocumento: true,
        instanteExibidoSegundos: instanteDocumento,
        instanteDocumentoSegundos: instanteDocumento,
        cachePreviewsPorChave: cache,
      }),
    ).toBeNull();
  });
});
