import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import {
  previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers,
  previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers,
  previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers,
  previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers,
  previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers,
} from "./modulo_util_preview_recorte_aguardar_troca_src_fonte_cue_antes_do_play_ui_transcribrothers.ts";

const fontePlayer = readFileSync(
  join(
    dirname(fileURLToPath(import.meta.url)),
    "componente_modal_assistir_video_narrado_com_legendas_vtt_e_downloads_transcribrothers.tsx",
  ),
  "utf8",
);

describe("previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers", () => {
  it("se preview inativo, não precisa aguardar (ativa e o effect dispara)", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: false,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/biblioteca-midias-tela/arquivo/m1",
      }),
    ).toBe(false);
  });

  it("se preview ativo e mesma URL, toca na hora (não aguarda)", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: true,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/video",
      }),
    ).toBe(false);
  });

  it("se preview ativo e URL de fonte muda, aguarda o effect após troca de src", () => {
    expect(
      previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
        previewRecorteAtivo: true,
        urlVideoPlayerAtual: "/api/jobs/j/video",
        urlVideoFonteAlvo: "/api/jobs/j/biblioteca-midias-tela/arquivo/m1",
      }),
    ).toBe(true);
  });
});

describe("previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers", () => {
  it("não toca se o elemento ainda tem o arquivo antigo, mesmo com readyState alto", () => {
    expect(
      previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers({
        urlAlvo: "/api/jobs/j/video",
        currentSrc: "http://localhost:5183/api/jobs/j/biblioteca-midias-tela/arquivo/vinheta",
        srcAtributo: "/api/jobs/j/biblioteca-midias-tela/arquivo/vinheta",
        readyState: 4,
      }),
    ).toBe(false);
  });

  it("toca quando currentSrc já é o alvo e há metadata", () => {
    expect(
      previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers({
        urlAlvo: "/api/jobs/j/video",
        currentSrc: "http://localhost:5183/api/jobs/j/video",
        srcAtributo: "/api/jobs/j/video",
        readyState: 1,
      }),
    ).toBe(true);
  });

  it("espera metadata se a URL bate mas o arquivo ainda não carregou", () => {
    expect(
      previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers({
        urlAlvo: "/api/jobs/j/video",
        currentSrc: "http://localhost:5183/api/jobs/j/video",
        srcAtributo: "/api/jobs/j/video",
        readyState: 0,
      }),
    ).toBe(false);
  });
});

describe("previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers", () => {
  it("no play contínuo, o fim do arquivo da vinheta (sem fala) avança para a próxima cue", () => {
    expect(
      previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers({
        continuo: true,
        semNarracao: true,
        previewJanela: true,
        audioAindaToca: false,
      }),
    ).toBe(true);
  });

  it("não avança no Ir de uma cue só", () => {
    expect(
      previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers({
        continuo: false,
        semNarracao: true,
        previewJanela: true,
        audioAindaToca: false,
      }),
    ).toBe(false);
  });

  it("não avança se a narração da cue ainda está tocando", () => {
    expect(
      previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers({
        continuo: true,
        semNarracao: false,
        previewJanela: true,
        audioAindaToca: true,
      }),
    ).toBe(false);
  });
});

describe("previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers", () => {
  it("não toca só com metadata se o currentTime ainda não é o instante da cue", () => {
    expect(
      previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers({
        currentTime: 0,
        instanteAlvoSegundos: 12.4,
        readyState: 4,
      }),
    ).toBe(false);
    expect(
      previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers({
        currentTime: 12.4,
        instanteAlvoSegundos: 12.4,
        readyState: 1,
      }),
    ).toBe(false);
  });

  it("toca quando há quadro no instante alvo", () => {
    expect(
      previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers({
        currentTime: 12.41,
        instanteAlvoSegundos: 12.4,
        readyState: 2,
      }),
    ).toBe(true);
    expect(
      previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers({
        currentTime: 0,
        instanteAlvoSegundos: 0,
        readyState: 2,
      }),
    ).toBe(true);
  });
});

describe("previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers", () => {
  it("não dá seek no fim da cue quando a próxima fonte é outro arquivo", () => {
    expect(
      previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers({
        veioDoEndedDoArquivo: false,
        vaiTrocarSrcParaProximaCue: true,
      }),
    ).toBe(false);
  });

  it("não dá seek quando o arquivo já acabou no ended", () => {
    expect(
      previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers({
        veioDoEndedDoArquivo: true,
        vaiTrocarSrcParaProximaCue: false,
      }),
    ).toBe(false);
  });

  it("estaciona no fim quando a próxima cue é o mesmo arquivo", () => {
    expect(
      previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers({
        veioDoEndedDoArquivo: false,
        vaiTrocarSrcParaProximaCue: false,
      }),
    ).toBe(true);
  });
});

describe("player de preview trata o ended do vídeo na cadeia", () => {
  it("escuta ended do vídeo e só dá play quando o src alvo já carregou", () => {
    expect(fontePlayer).toContain('addEventListener("ended", aoFimDoArquivoVideoPreviewRecorte');
    expect(fontePlayer).toContain("previewRecorteVideoJaCarregouSrcAlvoParaPlayUiTranscribrothers");
    expect(fontePlayer).toContain("previewRecorteDeveAvancarCadeiaNoFimDaCueSemNarracaoUiTranscribrothers");
  });

  it("congela o último quadro, não remonta o vídeo e espera o seeked antes do play", () => {
    const fontePlayerControles = readFileSync(
      join(
        dirname(fileURLToPath(import.meta.url)),
        "componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx",
      ),
      "utf8",
    );
    expect(fontePlayer).toContain("preview-recorte-tela");
    expect(fontePlayer).not.toContain("keyVideo={urlVideoPlayerEfetivo}");
    expect(fontePlayer).toContain("previewRecorteVideoJaBuscouInstanteAlvoParaPlayUiTranscribrothers");
    expect(fontePlayer).toContain('addEventListener("seeked"');
    expect(fontePlayer).toContain("capturarQuadroAtualDoElementoVideoComoDataUrlPngTranscribrothers");
    expect(fontePlayer).toContain("urlQuadroCongeladoDuranteTrocaSrc");
    expect(fontePlayerControles).toContain("urlQuadroCongeladoDuranteTrocaSrc");
    expect(fontePlayerControles).toContain("tb-video-player-quadro-congelado-durante-troca-src");
  });

  it("captura o quadro antes do seek de estacionar e só solta o freeze no primeiro frame pintado", () => {
    const inicioEncerrar = fontePlayer.indexOf(
      "encerrarJanelaDaCueSoloEAvancarCadeiaSeContinuo",
    );
    const trechoEncerrar = fontePlayer.slice(
      inicioEncerrar,
      fontePlayer.indexOf("aoFimDoArquivoVideoPreviewRecorte"),
    );
    const iCaptura = trechoEncerrar.indexOf(
      "capturarQuadroAtualDoElementoVideoComoDataUrlPngTranscribrothers",
    );
    const iEstacionar = trechoEncerrar.indexOf("video.currentTime = estacionarEm");
    expect(iCaptura).toBeGreaterThan(0);
    expect(iEstacionar).toBeGreaterThan(0);
    expect(iCaptura).toBeLessThan(iEstacionar);
    expect(fontePlayer).toContain(
      "previewRecorteDeveEstacionarSeekNoFimDaJanelaAntesDeAvancarUiTranscribrothers",
    );
    expect(fontePlayer).toContain("requestVideoFrameCallback");
  });
});
