import { describe, expect, it } from "vitest";
import { formatarTextoDebugUltimaVinhetaSeparadorTranscribrothers } from "./modulo_formatar_texto_debug_ultima_vinheta_separador_transcribrothers.ts";

describe("relatório de debug da última vinheta", () => {
  it("monta um bloco copiável com tempos e canvas", () => {
    const texto = formatarTextoDebugUltimaVinhetaSeparadorTranscribrothers({
      gerado_em: "2026-10-12T16:40:00-03:00",
      titulo: "Pré-requisito",
      efeito: "planos-que-abrem-espaco",
      vinheta_id: null,
      largura: 1366,
      altura: 768,
      duracao_pedida_segundos: 5,
      duracao_medida_segundos: 5.02,
      presenca_da_imagem: 60,
      tem_quadro_anterior: true,
      tem_quadro_seguinte: true,
      bytes_mp4: 1_258_000,
      fps: 30,
      quantidade_quadros: 150,
      dissolve_assada_nos_quadros: true,
      tempos_ms: {
        total: 18234,
        captura_png_seguinte: 412,
        captura_png_anterior: 388,
        sonda_dimensoes: 45,
        render_vinhetas: 17120,
        sonda_duracao: 80,
        amostragem_vite_node: 2100,
        desenho_pil: 9800,
        encode_ffmpeg: 4900,
      },
    });

    expect(texto).toContain("Última vinheta");
    expect(texto).toContain("título: Pré-requisito");
    expect(texto).toContain("canvas: 1366×768");
    expect(texto).toContain("total: 18234 ms");
    expect(texto).toContain("amostragem vite-node: 2100 ms");
    expect(texto).toContain("desenho PIL: 9800 ms");
    expect(texto).toContain("encode ffmpeg: 4900 ms");
    expect(texto).toContain("quadros: 150 · 30 fps");
  });

  it("avisa quando ainda não gerou vinheta", () => {
    expect(formatarTextoDebugUltimaVinhetaSeparadorTranscribrothers(null)).toBe(
      "Ainda não há relatório da última vinheta neste job.",
    );
  });
});
