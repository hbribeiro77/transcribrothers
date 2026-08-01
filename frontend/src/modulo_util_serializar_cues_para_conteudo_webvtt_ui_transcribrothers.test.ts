import { describe, expect, it } from "vitest";
import { parsearConteudoWebVttEmCuesParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";
import {
  formatarSegundosComoTimestampWebVttCompletoUiTranscribrothers,
  serializarCuesParaConteudoWebVttUiTranscribrothers,
} from "./modulo_util_serializar_cues_para_conteudo_webvtt_ui_transcribrothers.ts";

describe("serializarCuesParaConteudoWebVttUiTranscribrothers", () => {
  it("formata timestamp completo com horas", () => {
    expect(formatarSegundosComoTimestampWebVttCompletoUiTranscribrothers(65.5)).toBe(
      "00:01:05.500",
    );
  });

  it("serializa e reparseia preservando texto e tempos", () => {
    const cues = [
      { inicioSegundos: 0, fimSegundos: 1.5, texto: "Olá mundo" },
      { inicioSegundos: 1.5, fimSegundos: 3, texto: "Frase editada" },
    ];
    const vtt = serializarCuesParaConteudoWebVttUiTranscribrothers(cues);
    expect(vtt.startsWith("WEBVTT")).toBe(true);
    expect(vtt).toContain("Frase editada");
    expect(vtt).toContain("line:94% size:96% align:center");
    const deVolta = parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(vtt);
    expect(deVolta).toHaveLength(2);
    expect(deVolta[1].texto).toBe("Frase editada");
    expect(deVolta[0].inicioSegundos).toBeCloseTo(0);
    expect(deVolta[1].fimSegundos).toBeCloseTo(3);
  });

  it("ignora cue sem texto ou com intervalo inválido", () => {
    const vtt = serializarCuesParaConteudoWebVttUiTranscribrothers([
      { inicioSegundos: 0, fimSegundos: 1, texto: "  " },
      { inicioSegundos: 2, fimSegundos: 1, texto: "x" },
      { inicioSegundos: 3, fimSegundos: 4, texto: "ok" },
    ]);
    const deVolta = parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(vtt);
    expect(deVolta).toHaveLength(1);
    expect(deVolta[0].texto).toBe("ok");
  });
});
