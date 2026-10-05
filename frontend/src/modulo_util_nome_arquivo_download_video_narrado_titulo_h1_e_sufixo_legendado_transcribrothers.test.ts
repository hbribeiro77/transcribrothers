import { describe, expect, it } from "vitest";

import {
  montarNomeArquivoDownloadVideoNarradoComTituloTranscribrothers,
  montarUrlDownloadVideoNarradoComNomeArquivoQueryTranscribrothers,
  resolverTituloInicialVideoNarradoAPartirDoH1MarkdownTranscribrothers,
  resolverTituloVideoNarradoPersistidoOuH1Transcribrothers,
} from "./modulo_util_nome_arquivo_download_video_narrado_titulo_h1_e_sufixo_legendado_transcribrothers.ts";

describe("nome de arquivo do vídeo narrado", () => {
  it("usa o título sanitizado e acrescenta legendado no embutido", () => {
    expect(
      montarNomeArquivoDownloadVideoNarradoComTituloTranscribrothers(
        "Tutorial: Integração via WhatsApp",
      ),
    ).toBe("Tutorial- Integração via WhatsApp.mp4");
    expect(
      montarNomeArquivoDownloadVideoNarradoComTituloTranscribrothers(
        "Tutorial: Integração via WhatsApp",
        { legendado: true },
      ),
    ).toBe("Tutorial- Integração via WhatsApp legendado.mp4");
  });

  it("cai no fallback quando o título fica vazio", () => {
    expect(
      montarNomeArquivoDownloadVideoNarradoComTituloTranscribrothers("   ", {
        jobId: "abc-123",
      }),
    ).toBe("video-narrado-abc-123.mp4");
  });

  it("lê o H1 do markdown como título inicial", () => {
    expect(
      resolverTituloInicialVideoNarradoAPartirDoH1MarkdownTranscribrothers(
        "# Tutorial: Integração via WhatsApp\n\nTexto",
      ),
    ).toBe("Tutorial: Integração via WhatsApp");
  });

  it("prefere o título persistido ao H1", () => {
    expect(
      resolverTituloVideoNarradoPersistidoOuH1Transcribrothers(
        "Solicitação de documentos via WhatsApp",
        "# Tutorial: Integração via WhatsApp\n\nTexto",
      ),
    ).toBe("Solicitação de documentos via WhatsApp");
  });

  it("acrescenta nome_arquivo na URL de download", () => {
    expect(
      montarUrlDownloadVideoNarradoComNomeArquivoQueryTranscribrothers(
        "/api/jobs/abc/video-com-narracao-tts-com-legendas-queimadas",
        "Meu video legendado.mp4",
      ),
    ).toBe(
      "/api/jobs/abc/video-com-narracao-tts-com-legendas-queimadas?nome_arquivo=Meu+video+legendado.mp4",
    );
  });
});
